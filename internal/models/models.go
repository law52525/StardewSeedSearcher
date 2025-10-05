package models

import "fmt"

// Season 表示游戏季节
type Season int

const (
	Spring Season = iota
	Summer
	Fall
)

// String 返回季节的字符串表示
func (s Season) String() string {
	switch s {
	case Spring:
		return "Spring"
	case Summer:
		return "Summer"
	case Fall:
		return "Fall"
	default:
		return "Unknown"
	}
}

// MarshalJSON 实现 json.Marshaler 接口
func (s Season) MarshalJSON() ([]byte, error) {
	return []byte(`"` + s.String() + `"`), nil
}

// UnmarshalJSON 实现 json.Unmarshaler 接口
func (s *Season) UnmarshalJSON(data []byte) error {
	str := string(data)
	// 移除引号
	if len(str) >= 2 && str[0] == '"' && str[len(str)-1] == '"' {
		str = str[1 : len(str)-1]
	}

	switch str {
	case "Spring":
		*s = Spring
	case "Summer":
		*s = Summer
	case "Fall":
		*s = Fall
	default:
		return fmt.Errorf("无效的季节: %s", str)
	}
	return nil
}

// WeatherCondition 表示天气筛选条件
type WeatherCondition struct {
	Season      Season `json:"season"`
	StartDay    int    `json:"startDay"`
	EndDay      int    `json:"endDay"`
	MinRainDays int    `json:"minRainDays"`
}

// AbsoluteStartDay 返回绝对开始日期 (1-84)
func (wc WeatherCondition) AbsoluteStartDay() int {
	return int(wc.Season)*28 + wc.StartDay
}

// AbsoluteEndDay 返回绝对结束日期 (1-84)
func (wc WeatherCondition) AbsoluteEndDay() int {
	return int(wc.Season)*28 + wc.EndDay
}

// String 返回人类可读的字符串表示
func (wc WeatherCondition) String() string {
	seasonName := wc.Season.String()
	switch wc.Season {
	case Spring:
		seasonName = "春"
	case Summer:
		seasonName = "夏"
	case Fall:
		seasonName = "秋"
	}
	return fmt.Sprintf("%s%d-%s%d: 最少%d个雨天", seasonName, wc.StartDay, seasonName, wc.EndDay, wc.MinRainDays)
}

// SearchRequest 表示来自前端的搜索请求
type SearchRequest struct {
	StartSeed         int                `json:"startSeed"`
	EndSeed           int                `json:"endSeed"`
	UseLegacyRandom   bool               `json:"useLegacyRandom"`
	WeatherConditions []WeatherCondition `json:"weatherConditions"`
	OutputLimit       int                `json:"outputLimit"`
}

// SearchResponse 表示搜索请求的响应
type SearchResponse struct {
	Message string `json:"message"`
}

// HealthResponse 表示健康检查响应
type HealthResponse struct {
	Status  string `json:"status"`
	Version string `json:"version"`
}

// WebSocketMessage 表示通过 WebSocket 发送的消息基类
type WebSocketMessage struct {
	Type string `json:"type"`
}

// StartMessage 表示搜索开始消息
type StartMessage struct {
	WebSocketMessage
	Total int `json:"total"`
}

// ProgressMessage 表示进度更新消息
type ProgressMessage struct {
	WebSocketMessage
	CheckedCount int     `json:"checkedCount"`
	Total        int     `json:"total"`
	Progress     float64 `json:"progress"`
	Speed        float64 `json:"speed"`
	Elapsed      float64 `json:"elapsed"`
}

// WeatherDetail 表示天气详情
type WeatherDetail struct {
	SpringRain   []int `json:"springRain"`   // 春季雨天日期
	SummerRain   []int `json:"summerRain"`   // 夏季雨天日期
	FallRain     []int `json:"fallRain"`     // 秋季雨天日期
	GreenRainDay int   `json:"greenRainDay"` // 绿雨日
}

// FoundMessage 表示找到种子消息
type FoundMessage struct {
	WebSocketMessage
	Seed          int            `json:"seed"`
	WeatherDetail *WeatherDetail `json:"weatherDetail,omitempty"`
}

// CompleteMessage 表示搜索完成消息
type CompleteMessage struct {
	WebSocketMessage
	TotalFound int     `json:"totalFound"`
	Elapsed    float64 `json:"elapsed"`
}
