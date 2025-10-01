package handlers

import (
	"stardew-seed-searcher/internal/features"
	"stardew-seed-searcher/internal/models"
	"testing"
)

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
			name:            "测试样例1: 春季前10天7个雨天",
			startSeed:       0,
			endSeed:         100000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 7},
			},
			outputLimit:   100,
			expectedSeeds: []int{61522, 82965},
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
			expectedSeeds: []int{257828, 270393, 421293, 937986},
		},
		{
			name:            "测试样例4: 10万到20万范围，春夏各前10天",
			startSeed:       100000,
			endSeed:         200000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 10, MinRainDays: 5},
				{Season: models.Summer, StartDay: 1, EndDay: 10, MinRainDays: 6},
			},
			outputLimit:   20,
			expectedSeeds: []int{190625},
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
			expectedSeeds: []int{100019234, 100036091, 100066501, 100077568},
		},
		{
			name:            "测试样例6: 春夏秋各前15天不同雨天要求",
			startSeed:       0,
			endSeed:         1000000,
			useLegacyRandom: false,
			weatherConditions: []models.WeatherCondition{
				{Season: models.Spring, StartDay: 1, EndDay: 15, MinRainDays: 6},
				{Season: models.Summer, StartDay: 1, EndDay: 15, MinRainDays: 7},
				{Season: models.Fall, StartDay: 1, EndDay: 15, MinRainDays: 7},
			},
			outputLimit:   20,
			expectedSeeds: []int{812673},
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
			expectedSeeds: []int{100728737, 101328491, 102189128, 102660901, 108581614},
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
