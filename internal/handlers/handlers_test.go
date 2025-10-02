package handlers

import (
	"stardew-seed-searcher/internal/features"
	"stardew-seed-searcher/internal/models"
	"testing"
)

// TestSearchConsistencySample1 测试样例1: 春季前10天5个雨天
func TestSearchConsistencySample1(t *testing.T) {
	// 测试样例1: 春季前10天5个雨天
	startSeed := 0
	endSeed := 1000
	useLegacyRandom := false
	weatherConditions := []models.WeatherCondition{
		{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 5},
	}
	outputLimit := 100
	expectedSeeds := []int{59, 73, 101, 142, 659, 932, 938}

	// 创建天气预测器
	predictor := features.NewWeatherPredictor()
	predictor.SetEnabled(true)
	for _, condition := range weatherConditions {
		predictor.AddCondition(condition)
	}

	// 执行搜索
	var results []int
	for seed := startSeed; seed <= endSeed; seed++ {
		if predictor.Check(seed, useLegacyRandom) {
			results = append(results, seed)
			if len(results) >= outputLimit {
				break
			}
		}
	}

	// 验证结果
	if len(results) != len(expectedSeeds) {
		t.Errorf("期望找到 %d 个种子，实际找到 %d 个", len(expectedSeeds), len(results))
		return
	}

	for i, expectedSeed := range expectedSeeds {
		if i >= len(results) || results[i] != expectedSeed {
			t.Errorf("第 %d 个种子期望 %d，实际 %d", i+1, expectedSeed, results[i])
		}
	}

	t.Logf("样例1测试通过: 找到 %d 个符合条件的种子", len(results))
}

// TestSearchConsistency 测试Go版本和C#版本的搜索结果一致性
func TestSearchConsistency(t *testing.T) {
	testCases := []struct {
		name              string
		startSeed         int
		endSeed           int
		useLegacyRandom   bool
		weatherConditions []models.WeatherCondition
		outputLimit       int
		expectedSeeds     []int
	}{
		{
			name:            "测试样例1: 春季前10天5个雨天",
			startSeed:       0,
			endSeed:         1000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 5},
			},
			outputLimit:   100,
			expectedSeeds: []int{59, 73, 101, 142, 659, 932, 938},
		},
		{
			name:            "测试样例2: 春夏秋各28天10个雨天",
			startSeed:       0,
			endSeed:         1000000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 28, MinRainDays: 10},
				{Season: models.Summer, StartDay: 1, EndDay: 28, MinRainDays: 10},
				{Season: models.Fall, StartDay: 1, EndDay: 28, MinRainDays: 10},
			},
			outputLimit:   20,
			expectedSeeds: []int{107180, 371222, 403543, 433877, 443151, 567995, 690980},
		},
		{
			name:            "测试样例3: 春夏秋各前10天5个雨天",
			startSeed:       0,
			endSeed:         1000000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 5},
				{Season: models.Summer, StartDay: 1, EndDay: 10, MinRainDays: 5},
				{Season: models.Fall, StartDay: 1, EndDay: 10, MinRainDays: 5},
			},
			outputLimit:   20,
			expectedSeeds: []int{270393},
		},
		{
			name:            "测试样例4: 0到10万范围，春夏各前10天",
			startSeed:       0,
			endSeed:         100000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 5},
				{Season: models.Summer, StartDay: 1, EndDay: 10, MinRainDays: 6},
			},
			outputLimit:   20,
			expectedSeeds: []int{58038},
		},
		{
			name:            "测试样例5: 1亿到1.001亿范围，春夏秋各前15天",
			startSeed:       100000000,
			endSeed:         100100000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 15, MinRainDays: 6},
				{Season: models.Summer, StartDay: 1, EndDay: 15, MinRainDays: 7},
				{Season: models.Fall, StartDay: 1, EndDay: 15, MinRainDays: 6},
			},
			outputLimit:   20,
			expectedSeeds: []int{100066501, 100077568},
		},
		{
			name:            "测试样例6: 春夏秋各前15天不同雨天要求",
			startSeed:       0,
			endSeed:         1000000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 15, MinRainDays: 5},
				{Season: models.Summer, StartDay: 1, EndDay: 15, MinRainDays: 6},
				{Season: models.Fall, StartDay: 1, EndDay: 15, MinRainDays: 6},
			},
			outputLimit:   20,
			expectedSeeds: []int{4604, 15278, 27396, 34586, 43362, 44159, 50668, 51835, 55234, 55873, 63250, 66882, 69723, 73556, 74213, 76395, 86007, 92201, 100574, 101222},
		},
		{
			name:            "测试样例7: 1亿到1.1亿范围，春夏秋各前15天7个雨天",
			startSeed:       100000000,
			endSeed:         110000000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 15, MinRainDays: 7},
				{Season: models.Summer, StartDay: 1, EndDay: 15, MinRainDays: 7},
				{Season: models.Fall, StartDay: 1, EndDay: 15, MinRainDays: 7},
			},
			outputLimit:   20,
			expectedSeeds: []int{100728737, 101328491, 102189128, 108581614},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 创建天气预测器
			predictor := features.NewWeatherPredictor()
			for _, condition := range tc.weatherConditions {
				predictor.AddCondition(condition)
			}

			// 执行搜索
			var foundSeeds []int
			for seed := tc.startSeed; seed <= tc.endSeed && len(foundSeeds) < tc.outputLimit; seed++ {
				if predictor.Check(seed, tc.useLegacyRandom) {
					foundSeeds = append(foundSeeds, seed)
				}
			}

			// 验证结果
			if len(foundSeeds) != len(tc.expectedSeeds) {
				t.Errorf("种子数量不匹配: 期望 %d 个，实际 %d 个", len(tc.expectedSeeds), len(foundSeeds))
				t.Errorf("期望种子: %v", tc.expectedSeeds)
				t.Errorf("实际种子: %v", foundSeeds)
				return
			}

			// 验证每个种子
			for i, expectedSeed := range tc.expectedSeeds {
				if i >= len(foundSeeds) {
					t.Errorf("种子数量不足: 期望至少 %d 个，实际只有 %d 个", i+1, len(foundSeeds))
					break
				}
				if foundSeeds[i] != expectedSeed {
					t.Errorf("第 %d 个种子不匹配: 期望 %d，实际 %d", i+1, expectedSeed, foundSeeds[i])
					t.Errorf("期望种子: %v", tc.expectedSeeds)
					t.Errorf("实际种子: %v", foundSeeds)
					break
				}
			}

			// 如果所有种子都匹配，输出成功信息
			if len(foundSeeds) == len(tc.expectedSeeds) {
				allMatch := true
				for i, expectedSeed := range tc.expectedSeeds {
					if foundSeeds[i] != expectedSeed {
						allMatch = false
						break
					}
				}
				if allMatch {
					t.Logf("✓ 测试通过: 找到 %d 个匹配的种子", len(foundSeeds))
				}
			}
		})
	}
}

// TestSearchConsistencyWithLegacyRandom 测试旧随机模式的一致性
func TestSearchConsistencyWithLegacyRandom(t *testing.T) {
	testCases := []struct {
		name              string
		startSeed         int
		endSeed           int
		weatherConditions []models.WeatherCondition
		outputLimit       int
		expectedSeeds     []int
	}{
		{
			name:      "旧随机模式测试: 春季前10天7个雨天",
			startSeed: 0,
			endSeed:   100000,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 7},
			},
			outputLimit:   100,
			expectedSeeds: []int{}, // 需要实际测试后填入
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 创建天气预测器
			predictor := features.NewWeatherPredictor()
			for _, condition := range tc.weatherConditions {
				predictor.AddCondition(condition)
			}

			// 执行搜索（使用旧随机模式）
			var foundSeeds []int
			for seed := tc.startSeed; seed <= tc.endSeed && len(foundSeeds) < tc.outputLimit; seed++ {
				if predictor.Check(seed, true) { // 使用旧随机模式
					foundSeeds = append(foundSeeds, seed)
				}
			}

			t.Logf("旧随机模式找到 %d 个种子: %v", len(foundSeeds), foundSeeds)

			// 如果期望种子为空，只记录结果
			if len(tc.expectedSeeds) == 0 {
				return
			}

			// 验证结果
			if len(foundSeeds) != len(tc.expectedSeeds) {
				t.Errorf("种子数量不匹配: 期望 %d 个，实际 %d 个", len(tc.expectedSeeds), len(foundSeeds))
				return
			}

			// 验证每个种子
			for i, expectedSeed := range tc.expectedSeeds {
				if foundSeeds[i] != expectedSeed {
					t.Errorf("第 %d 个种子不匹配: 期望 %d，实际 %d", i+1, expectedSeed, foundSeeds[i])
					break
				}
			}
		})
	}
}
