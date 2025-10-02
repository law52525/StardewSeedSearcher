package features

import (
	"stardew-seed-searcher/internal/models"
	"testing"
)

func TestWeatherPredictor_Check(t *testing.T) {
	predictor := NewWeatherPredictor()

	// 测试无条件情况（应该返回 true）
	if !predictor.Check(12345, false) {
		t.Error("没有设置条件时应该返回 true")
	}

	// Test with conditions
	condition := models.WeatherCondition{
		Season:      models.Spring,
		StartDay:    1,
		EndDay:      28,
		MinRainDays: 5,
	}
	predictor.AddCondition(condition)

	// 测试特定种子
	result := predictor.Check(12345, false)
	t.Logf("Weather check result for seed 12345: %v", result)
}

func TestWeatherPredictor_PredictWeather(t *testing.T) {
	predictor := NewWeatherPredictor()
	weather := predictor.PredictWeather(12345, false)

	// 检查我们有所有 84 天的天气数据
	if len(weather) != 84 {
		t.Errorf("应该有 84 天的天气数据，得到 %d", len(weather))
	}

	// 检查所有日期都存在
	for day := 1; day <= 84; day++ {
		if _, exists := weather[day]; !exists {
			t.Errorf("缺少第 %d 天的天气数据", day)
		}
	}

	// 检查春季前10天的固定天气规则
	// 第1、2、4、5天应该是晴天
	if weather[1] {
		t.Error("春季第 1 天应该是晴天")
	}
	if weather[2] {
		t.Error("春季第 2 天应该是晴天")
	}
	if weather[4] {
		t.Error("春季第 4 天应该是晴天")
	}
	if weather[5] {
		t.Error("春季第 5 天应该是晴天")
	}

	// 第3天应该是雨天
	if !weather[3] {
		t.Error("春季第 3 天应该是雨天")
	}

	// 第6-10天使用通用逻辑，这里只检查它们不是固定晴天
	// 具体是否下雨取决于随机数，所以不强制检查
}

func TestWeatherPredictor_PredictSpringRain(t *testing.T) {
	predictor := NewWeatherPredictor()
	rainyDays := predictor.PredictSpringRain(12345, false)

	t.Logf("Spring rainy days for seed 12345: %v", rainyDays)

	// 检查雨天数在有效范围内
	for _, day := range rainyDays {
		if day < 1 || day > 28 {
			t.Errorf("无效的雨天数: %d (应该是 1-28)", day)
		}
	}
}

func TestWeatherPredictor_String(t *testing.T) {
	predictor := NewWeatherPredictor()

	// Test with no conditions
	desc := predictor.GetConfigDescription()
	if desc != "无筛选条件" {
		t.Errorf("期望 '无筛选条件'，得到 '%s'", desc)
	}

	// Test with conditions
	condition := models.WeatherCondition{
		Season:      models.Spring,
		StartDay:    1,
		EndDay:      28,
		MinRainDays: 5,
	}
	predictor.AddCondition(condition)

	desc = predictor.GetConfigDescription()
	t.Logf("Config description with conditions: %s", desc)
}

func TestWeatherCondition_AbsoluteDays(t *testing.T) {
	// 测试春季
	springCondition := models.WeatherCondition{
		Season:   models.Spring,
		StartDay: 1,
		EndDay:   28,
	}
	if springCondition.AbsoluteStartDay() != 1 {
		t.Errorf("春季绝对开始日期应该是 1，得到 %d", springCondition.AbsoluteStartDay())
	}
	if springCondition.AbsoluteEndDay() != 28 {
		t.Errorf("春季绝对结束日期应该是 28，得到 %d", springCondition.AbsoluteEndDay())
	}

	// 测试夏季
	summerCondition := models.WeatherCondition{
		Season:   models.Summer,
		StartDay: 1,
		EndDay:   28,
	}
	if summerCondition.AbsoluteStartDay() != 29 {
		t.Errorf("夏季绝对开始日期应该是 29，得到 %d", summerCondition.AbsoluteStartDay())
	}
	if summerCondition.AbsoluteEndDay() != 56 {
		t.Errorf("夏季绝对结束日期应该是 56，得到 %d", summerCondition.AbsoluteEndDay())
	}

	// 测试秋季
	fallCondition := models.WeatherCondition{
		Season:   models.Fall,
		StartDay: 1,
		EndDay:   28,
	}
	if fallCondition.AbsoluteStartDay() != 57 {
		t.Errorf("秋季绝对开始日期应该是 57，得到 %d", fallCondition.AbsoluteStartDay())
	}
	if fallCondition.AbsoluteEndDay() != 84 {
		t.Errorf("秋季绝对结束日期应该是 84，得到 %d", fallCondition.AbsoluteEndDay())
	}
}
