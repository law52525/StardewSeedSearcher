package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"runtime"
	"stardew-seed-searcher/pkg/features"
	"stardew-seed-searcher/pkg/models"
	"stardew-seed-searcher/pkg/websocket"
	"sync"
	"sync/atomic"
	"time"
)

// min 返回两个整数中的较小值
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// SearchHandler 处理搜索请求
type SearchHandler struct {
	hub *websocket.Hub
}

// NewSearchHandler 创建新的 SearchHandler
func NewSearchHandler(hub *websocket.Hub) *SearchHandler {
	return &SearchHandler{hub: hub}
}

// HandleSearch 处理搜索 API 端点
func (h *SearchHandler) HandleSearch(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var request models.SearchRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid JSON: "+err.Error(), http.StatusBadRequest)
		return
	}

	// Validate request
	if request.StartSeed >= request.EndSeed {
		http.Error(w, "End seed must be greater than start seed", http.StatusBadRequest)
		return
	}

	if request.EndSeed > 2147483647 {
		http.Error(w, "End seed cannot exceed 2147483647", http.StatusBadRequest)
		return
	}

	// Start search in a goroutine
	go h.performSearch(request)

	// Return immediately
	response := models.SearchResponse{Message: "Search started."}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// performSearch 执行实际搜索（并行化版本）
func (h *SearchHandler) performSearch(request models.SearchRequest) {
	startTime := time.Now()
	totalSeeds := request.EndSeed - request.StartSeed + 1

	// 配置功能模板（用于创建工作实例）
	var searchFeatureTemplate []features.SearchFeature
	log.Printf("天气条件数量: %d", len(request.WeatherConditions))
	if len(request.WeatherConditions) > 0 {
		predictor := features.NewWeatherPredictor()
		predictor.SetEnabled(true)

		for _, conditionDto := range request.WeatherConditions {
			log.Printf("添加天气条件: %s", conditionDto.String())
			predictor.AddCondition(conditionDto)
		}

		searchFeatureTemplate = append(searchFeatureTemplate, predictor)
		log.Printf("配置了 %d 个搜索功能", len(searchFeatureTemplate))
	} else {
		log.Printf("没有天气条件，将匹配所有种子")
	}

	// 发送开始消息
	startMessage := models.StartMessage{
		WebSocketMessage: models.WebSocketMessage{Type: "start"},
		Total:            totalSeeds,
	}
	if data, err := json.Marshal(startMessage); err == nil {
		h.hub.Broadcast(data)
	}

	// 并行搜索配置 - 基于实际CPU核心数动态调整
	maxWorkers := runtime.NumCPU()
	numWorkers := maxWorkers

	if totalSeeds < 10000 {
		numWorkers = 1 // 小范围搜索使用单线程
	} else if totalSeeds < 100000 {
		// 中等范围：使用2个线程或CPU核心数的一半，取较小值
		numWorkers = min(2, maxWorkers/2)
		if numWorkers < 1 {
			numWorkers = 1
		}
	} else if totalSeeds < 1000000 {
		// 大范围：使用4个线程或CPU核心数的一半，取较小值
		numWorkers = min(4, maxWorkers/2)
		if numWorkers < 1 {
			numWorkers = 1
		}
	} else {
		// 超大范围：使用8个线程或CPU核心数，取较小值
		numWorkers = min(8, maxWorkers)
		if numWorkers < 1 {
			numWorkers = 1
		}
	}
	log.Printf("使用 %d 个并行工作线程", numWorkers)

	// 线程安全的共享状态
	var (
		checkedCount int64
		results      []int
		resultsMutex sync.Mutex
		lastProgress int64
		shouldStop   int32 // 原子标志，用于通知所有工作线程停止
	)

	// 预分配结果切片，减少内存重新分配
	results = make([]int, 0, request.OutputLimit)

	// 使用工作池模式，减少通道通信开销
	// 将种子范围分割给每个工作线程
	seedsPerWorker := totalSeeds / numWorkers
	if seedsPerWorker == 0 {
		seedsPerWorker = 1
	}

	// 启动工作协程 - 使用范围分割模式
	var wg sync.WaitGroup
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()

			// 为每个工作协程创建独立的功能实例（优化：减少内存分配）
			var workerFeatures []features.SearchFeature
			for _, template := range searchFeatureTemplate {
				// 创建新的天气预测器实例
				if predictor, ok := template.(*features.WeatherPredictor); ok {
					newPredictor := features.NewWeatherPredictor()
					newPredictor.SetEnabled(predictor.IsEnabled())
					// 直接复制条件，避免重复创建
					conditions := predictor.GetConditions()
					for i := range conditions {
						newPredictor.AddCondition(conditions[i])
					}
					workerFeatures = append(workerFeatures, newPredictor)
				}
			}

			// 计算当前工作线程负责的种子范围
			startSeed := int64(request.StartSeed) + int64(workerID)*int64(seedsPerWorker)
			endSeed := startSeed + int64(seedsPerWorker) - 1
			if workerID == numWorkers-1 {
				// 最后一个工作线程处理剩余的所有种子
				endSeed = int64(request.EndSeed)
			}

			log.Printf("工作线程 %d 处理种子范围: %d-%d", workerID, startSeed, endSeed)

			// 处理分配的种子范围
			for seed := startSeed; seed <= endSeed; seed++ {
				// 检查是否应该停止
				if atomic.LoadInt32(&shouldStop) == 1 {
					return
				}

				// 检查种子是否符合所有启用的功能条件
				allMatch := true
				for _, feature := range workerFeatures {
					if feature.IsEnabled() && !feature.Check(int(seed), request.UseLegacyRandom) {
						allMatch = false
						break
					}
				}

				if allMatch {
					// 线程安全地添加结果（优化：减少锁持有时间）
					resultsMutex.Lock()
					if len(results) < request.OutputLimit {
						results = append(results, int(seed))
						resultCount := len(results)
						resultsMutex.Unlock()

						log.Printf("工作线程 %d 找到匹配种子: %d", workerID, seed)

						// 立即推送找到的种子
						foundMessage := models.FoundMessage{
							WebSocketMessage: models.WebSocketMessage{Type: "found"},
							Seed:             int(seed),
						}
						if data, err := json.Marshal(foundMessage); err == nil {
							h.hub.Broadcast(data)
						}

						// 检查是否达到输出限制
						if resultCount >= request.OutputLimit {
							log.Printf("工作线程 %d 检测到达到输出限制 %d", workerID, request.OutputLimit)
							// 设置停止标志，通知所有工作线程停止
							atomic.StoreInt32(&shouldStop, 1)
							return
						}
					} else {
						resultsMutex.Unlock()
						// 结果已满，设置停止标志
						atomic.StoreInt32(&shouldStop, 1)
						return
					}
				}

				// 原子性地增加检查计数
				currentCount := atomic.AddInt64(&checkedCount, 1)

				// 更新进度（优化：使用更高效的进度更新策略）
				updateInterval := int64(5000) // 进一步增加更新间隔，减少锁竞争
				if totalSeeds < 10000 {
					updateInterval = 1000
				}
				if currentCount%updateInterval == 0 || currentCount == int64(totalSeeds) {
					// 使用原子操作检查是否需要更新
					oldProgress := atomic.LoadInt64(&lastProgress)
					if currentCount-oldProgress >= updateInterval {
						if atomic.CompareAndSwapInt64(&lastProgress, oldProgress, currentCount) {
							h.updateProgress(currentCount, int64(totalSeeds), startTime)
						}
					}
				}
			}
		}(i)
	}

	// 开始搜索 - 使用范围分割模式，无需通道
	log.Printf("开始搜索: 种子范围 %d-%d, 总数量 %d", request.StartSeed, request.EndSeed, totalSeeds)

	// 等待所有工作线程完成
	wg.Wait()

	elapsed := math.Round(time.Since(startTime).Seconds()*100) / 100
	finalCount := atomic.LoadInt64(&checkedCount)

	log.Printf("搜索完成: 检查了 %d 个种子，找到 %d 个匹配的种子", finalCount, len(results))

	// 发送最终进度更新
	h.updateProgress(finalCount, int64(totalSeeds), startTime)

	// 广播完成消息
	completeMessage := models.CompleteMessage{
		WebSocketMessage: models.WebSocketMessage{Type: "complete"},
		TotalFound:       len(results),
		Elapsed:          elapsed,
	}
	if data, err := json.Marshal(completeMessage); err == nil {
		log.Printf("发送完成消息: %s", string(data))
		h.hub.Broadcast(data)
		log.Printf("完成消息已发送")
	} else {
		log.Printf("完成消息序列化失败: %v", err)
	}
}

// updateProgress 线程安全的进度更新方法
func (h *SearchHandler) updateProgress(checkedCount, totalSeeds int64, startTime time.Time) {
	elapsed := math.Round(time.Since(startTime).Seconds()*100) / 100
	progress := math.Round(float64(checkedCount)/float64(totalSeeds)*100*100) / 100

	// 防止除零错误和无穷大值
	var speed float64
	if elapsed > 0 {
		speed = math.Round(float64(checkedCount) / elapsed)
	} else {
		speed = 0
	}

	// log.Printf("进度更新: 已检查 %d/%d (%.2f%%), 速度 %.0f 种子/秒", checkedCount, totalSeeds, progress, speed)

	progressMessage := models.ProgressMessage{
		WebSocketMessage: models.WebSocketMessage{Type: "progress"},
		CheckedCount:     int(checkedCount),
		Total:            int(totalSeeds),
		Progress:         progress,
		Speed:            speed,
		Elapsed:          elapsed,
	}
	if data, err := json.Marshal(progressMessage); err == nil {
		h.hub.Broadcast(data)
	} else {
		log.Printf("进度消息序列化失败: %v", err)
	}
}

// HandleHealth 处理健康检查端点
func HandleHealth(w http.ResponseWriter, r *http.Request) {
	response := models.HealthResponse{
		Status:  "ok",
		Version: "1.0",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// HandleRoot 处理根端点 - 提供 HTML 页面
func HandleRoot(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <title>星露谷种子搜索器 API</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .card {
            background: white;
            color: #333;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 { margin-top: 0; color: #667eea; }
        .status { color: #4caf50; font-weight: bold; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class='card'>
        <h1>🌾 星露谷种子搜索器 API</h1>
        <p>服务器运行 <span class='status'>正常</span>！</p>
        <p>请打开 <code>index.html</code> 开始使用。</p>
        <hr style='margin: 20px 0; border: none; border-top: 1px solid #eee;'>
        <p style='color: #666; font-size: 0.9em; margin: 0;'>
            端口: 5000 | 状态: 运行中<br>
            WebSocket: ws://localhost:5000/ws
        </p>
    </div>
</body>
</html>`

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprint(w, html)
}
