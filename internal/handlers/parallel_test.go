package handlers

import (
	"sort"
	"stardew-seed-searcher/internal/features"
	"stardew-seed-searcher/internal/models"
	"sync"
	"sync/atomic"
	"testing"
)

// TestParallelSearchConsistency 测试多线程搜索与单线程搜索的一致性
func TestParallelSearchConsistency(t *testing.T) {
	testCases := []struct {
		name              string
		startSeed         int
		endSeed           int
		useLegacyRandom   bool
		weatherConditions []models.WeatherCondition
		outputLimit       int
	}{
		{
			name:            "多线程一致性测试1: 春季前10天7个雨天",
			startSeed:       0,
			endSeed:         100000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 7},
			},
			outputLimit: 100,
		},
		{
			name:            "多线程一致性测试2: 春夏秋各28天10个雨天",
			startSeed:       0,
			endSeed:         1000000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 28, MinRainDays: 10},
				{Season: models.Summer, StartDay: 1, EndDay: 28, MinRainDays: 10},
				{Season: models.Fall, StartDay: 1, EndDay: 28, MinRainDays: 10},
			},
			outputLimit: 20,
		},
		{
			name:            "多线程一致性测试3: 1亿到1.001亿范围",
			startSeed:       100000000,
			endSeed:         100100000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 15, MinRainDays: 6},
				{Season: models.Summer, StartDay: 1, EndDay: 15, MinRainDays: 7},
				{Season: models.Fall, StartDay: 1, EndDay: 15, MinRainDays: 6},
			},
			outputLimit: 20,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 单线程搜索
			singleThreadResults := performSingleThreadSearch(tc.startSeed, tc.endSeed, tc.weatherConditions, tc.useLegacyRandom, tc.outputLimit)

			// 多线程搜索（模拟4个线程）
			multiThreadResults := performMultiThreadSearch(tc.startSeed, tc.endSeed, tc.weatherConditions, tc.useLegacyRandom, tc.outputLimit, 4)

			// 对结果进行排序（多线程结果可能不是有序的）
			sort.Ints(singleThreadResults)
			sort.Ints(multiThreadResults)

			// 比较结果
			if len(singleThreadResults) != len(multiThreadResults) {
				t.Errorf("结果数量不匹配: 单线程 %d 个，多线程 %d 个", len(singleThreadResults), len(multiThreadResults))
				t.Errorf("单线程结果: %v", singleThreadResults)
				t.Errorf("多线程结果: %v", multiThreadResults)
				return
			}

			// 比较每个种子
			for i, singleSeed := range singleThreadResults {
				if i >= len(multiThreadResults) {
					t.Errorf("多线程结果数量不足")
					break
				}
				if singleSeed != multiThreadResults[i] {
					t.Errorf("第 %d 个种子不匹配: 单线程 %d，多线程 %d", i+1, singleSeed, multiThreadResults[i])
					t.Errorf("单线程结果: %v", singleThreadResults)
					t.Errorf("多线程结果: %v", multiThreadResults)
					break
				}
			}

			t.Logf("✓ 多线程一致性测试通过: 找到 %d 个匹配的种子", len(singleThreadResults))
		})
	}
}

// performSingleThreadSearch 执行单线程搜索
func performSingleThreadSearch(startSeed, endSeed int, conditions []models.WeatherCondition, useLegacyRandom bool, outputLimit int) []int {
	predictor := features.NewWeatherPredictor()
	for _, condition := range conditions {
		predictor.AddCondition(condition)
	}

	var results []int
	for seed := startSeed; seed <= endSeed && len(results) < outputLimit; seed++ {
		if predictor.Check(seed, useLegacyRandom) {
			results = append(results, seed)
		}
	}

	return results
}

// performMultiThreadSearch 执行多线程搜索（模拟handlers.go中的逻辑）
func performMultiThreadSearch(startSeed, endSeed int, conditions []models.WeatherCondition, useLegacyRandom bool, outputLimit, numWorkers int) []int {
	totalSeeds := endSeed - startSeed + 1
	seedsPerWorker := totalSeeds / numWorkers
	if seedsPerWorker == 0 {
		seedsPerWorker = 1
	}

	var (
		results      []int
		resultsMutex sync.Mutex
		shouldStop   int32
	)

	// 预分配结果切片
	results = make([]int, 0, outputLimit)

	var wg sync.WaitGroup
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()

			// 为每个工作线程创建独立的功能实例
			workerPredictor := features.NewWeatherPredictor()
			for _, condition := range conditions {
				workerPredictor.AddCondition(condition)
			}

			// 使用轮询分配策略，确保负载均衡
			for seed := startSeed + workerID; seed <= endSeed; seed += numWorkers {
				if atomic.LoadInt32(&shouldStop) == 1 {
					return
				}

				if workerPredictor.Check(seed, useLegacyRandom) {
					resultsMutex.Lock()
					if len(results) < outputLimit {
						results = append(results, seed)
						resultCount := len(results)
						resultsMutex.Unlock()

						if resultCount >= outputLimit {
							atomic.StoreInt32(&shouldStop, 1)
							return
						}
					} else {
						resultsMutex.Unlock()
						atomic.StoreInt32(&shouldStop, 1)
						return
					}
				}
			}
		}(i)
	}

	wg.Wait()
	return results
}
