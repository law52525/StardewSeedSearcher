package features

import (
	"fmt"
	"stardew-seed-searcher/internal/core"
	"stardew-seed-searcher/internal/models"
)

// 预计算的哈希常量，避免重复计算
var (
	summerRainChanceHash = int(core.GetHashFromString("summer_rain_chance"))
	locationWeatherHash  = int(core.GetHashFromString("location_weather"))
)

// WeatherPredictor 实现天气预测功能
type WeatherPredictor struct {
	conditions []models.WeatherCondition
	enabled    bool
	// 重用天气map，减少内存分配
	weatherCache map[int]bool
}

// NewWeatherPredictor 创建新的 WeatherPredictor 实例
func NewWeatherPredictor() *WeatherPredictor {
	return &WeatherPredictor{
		conditions:   make([]models.WeatherCondition, 0),
		enabled:      true,
		weatherCache: make(map[int]bool, 84), // 预分配84个元素的容量
	}
}

// Name 返回功能名称
func (wp *WeatherPredictor) Name() string {
	return "天气预测"
}

// IsEnabled 返回此功能是否启用
func (wp *WeatherPredictor) IsEnabled() bool {
	return wp.enabled
}

// SetEnabled 设置此功能是否启用
func (wp *WeatherPredictor) SetEnabled(enabled bool) {
	wp.enabled = enabled
}

// AddCondition 添加天气条件
func (wp *WeatherPredictor) AddCondition(condition models.WeatherCondition) {
	wp.conditions = append(wp.conditions, condition)
}

// GetConditions 返回所有条件
func (wp *WeatherPredictor) GetConditions() []models.WeatherCondition {
	return wp.conditions
}

// Check 检查种子是否符合筛选条件
func (wp *WeatherPredictor) Check(gameID int, useLegacyRandom bool) bool {
	// 如果没有条件，视为不筛选（全部通过）
	if len(wp.conditions) == 0 {
		return true
	}

	// 预测第一年春夏秋所有天气（1-84天）
	allWeather := wp.PredictWeather(gameID, useLegacyRandom)

	// 检查每个条件
	for _, condition := range wp.conditions {
		rainCount := wp.countRainInRange(allWeather, condition)
		if rainCount < condition.MinRainDays {
			return false
		}
	}

	return true
}

// GetConfigDescription 返回配置说明
func (wp *WeatherPredictor) GetConfigDescription() string {
	if len(wp.conditions) == 0 {
		return "无筛选条件"
	}

	descriptions := make([]string, len(wp.conditions))
	for i, condition := range wp.conditions {
		descriptions[i] = condition.String()
	}
	return fmt.Sprintf("%v", descriptions)
}

// countRainInRange 统计指定范围内的雨天数量
func (wp *WeatherPredictor) countRainInRange(weather map[int]bool, condition models.WeatherCondition) int {
	count := 0
	for day := condition.AbsoluteStartDay(); day <= condition.AbsoluteEndDay(); day++ {
		if isRainy, exists := weather[day]; exists && isRainy {
			count++
		}
	}
	return count
}

// PredictWeather 预测第一年春夏秋所有天气（1-84天）
func (wp *WeatherPredictor) PredictWeather(gameID int, useLegacyRandom bool) map[int]bool {
	// 清空缓存并重用
	for k := range wp.weatherCache {
		delete(wp.weatherCache, k)
	}

	for absoluteDay := 1; absoluteDay <= 84; absoluteDay++ {
		season := (absoluteDay - 1) / 28 // 0=春季, 1=夏季, 2=秋季
		dayOfMonth := ((absoluteDay - 1) % 28) + 1

		isRain := wp.isRainyDay(season, dayOfMonth, absoluteDay, gameID, useLegacyRandom)
		wp.weatherCache[absoluteDay] = isRain
	}

	return wp.weatherCache
}

// isRainyDay 判断某一天是否下雨
func (wp *WeatherPredictor) isRainyDay(season, dayOfMonth, absoluteDay, gameID int, useLegacyRandom bool) bool {
	// 固定天气规则

	// 春季 (season 0)
	if season == 0 {
		if dayOfMonth == 1 || dayOfMonth == 2 || dayOfMonth == 4 {
			return false // 晴天
		}
		if dayOfMonth == 3 {
			return true // 雨天
		}
		if dayOfMonth == 13 || dayOfMonth == 24 {
			return false // 节日固定晴天
		}
		// 春季没有return，会继续执行后面的通用逻辑
	} else if season == 1 {
		// 夏季 (season 1)
		// 夏季特殊：绿雨日确定
		year := 1 // 第一年
		greenRainSeed := core.GetRandomSeed(year*777, gameID, 0, 0, 0, useLegacyRandom)
		// 使用与C#相同的Random.Next()逻辑
		greenRainDays := []int{5, 6, 7, 14, 15, 16, 18, 23}
		greenRainDay := greenRainDays[wp.RandomNext(greenRainSeed, len(greenRainDays))]

		if dayOfMonth == greenRainDay {
			return true // 绿雨（算作雨天）
		}
		if dayOfMonth == 11 || dayOfMonth == 28 {
			return false // 节日固定晴天
		}
		if dayOfMonth%13 == 0 { // 第13, 26天
			return true // 雷雨（算作雨天）
		}

		// 普通雨天：概率随日期增加
		rainSeed := core.GetRandomSeed(absoluteDay-1, gameID/2, summerRainChanceHash, 0, 0, useLegacyRandom)
		// 使用与C#相同的Random.NextDouble()逻辑
		normalizedSeed := wp.RandomNextDouble(rainSeed)
		rainChance := 0.12 + 0.003*float64(dayOfMonth-1)
		return normalizedSeed < rainChance
	} else if season == 2 {
		// 秋季 (season 2)
		if dayOfMonth == 16 || dayOfMonth == 27 {
			return false // 节日固定晴天
		}
		// 秋季没有return，会继续执行后面的通用逻辑
	}

	// 春季和秋季普通日子：18.3%概率
	seed := core.GetRandomSeed(locationWeatherHash, gameID, absoluteDay-1, 0, 0, useLegacyRandom)
	// 使用与C#相同的Random.NextDouble()逻辑
	normalizedSeed := wp.RandomNextDouble(seed)
	return normalizedSeed < 0.183
}

// RandomNext 模拟C#的Random.Next(maxValue)方法
// 使用与.NET 9 Net5CompatSeedImpl相同的公式
func (wp *WeatherPredictor) RandomNext(seed int, maxValue int) int {
	if maxValue <= 0 {
		return 0
	}

	// 使用与randomNextDouble相同的公式
	firstRand := wp.getFirstRand(seed)

	// C#的Random.Next()使用不同的逻辑
	// 它使用 (int)((long)firstRand * maxValue / int32Max)
	// 而不是简单的模运算
	const int32Max = 2147483647
	return int((int64(firstRand) * int64(maxValue)) / int64(int32Max))
}

// getFirstRand 获取第一个随机数，使用.NET Random.Next()的精确公式
func (wp *WeatherPredictor) getFirstRand(seed int) int {
	const (
		multiplier = 1121899819
		constant   = 1559595546
		int32Max   = 2147483647
	)

	// C#的Random构造函数对负数种子取绝对值
	if seed < 0 {
		seed = -seed
	}

	// 使用int64避免溢出，然后转换为int32
	// 计算 y = (1121899819 * x + 1559595546) % 2147483647
	result := int64(multiplier)*int64(seed) + int64(constant)
	firstRand := int(result % int64(int32Max))
	if firstRand < 0 {
		firstRand += int32Max
	}

	return firstRand
}

// RandomNextDouble 模拟C#的Random.NextDouble()方法
// 返回 [0.0, 1.0) 范围内的浮点数
func (wp *WeatherPredictor) RandomNextDouble(seed int) float64 {
	// 获取第一个随机数
	firstRand := wp.getFirstRand(seed)

	// C#的NextDouble() = Sample() * (1.0 / int.MaxValue)
	// 其中Sample()返回[0, int.MaxValue)范围内的整数
	return float64(firstRand) / float64(0x7FFFFFFF)
}

// PredictSpringRain 预测春季雨天日期（保留此方法用于测试脚本）
func (wp *WeatherPredictor) PredictSpringRain(gameID int, useLegacyRandom bool) []int {
	weather := wp.PredictWeather(gameID, useLegacyRandom)
	var rainyDays []int

	for day := 1; day <= 28; day++ {
		if isRainy, exists := weather[day]; exists && isRainy {
			rainyDays = append(rainyDays, day)
		}
	}

	return rainyDays
}
