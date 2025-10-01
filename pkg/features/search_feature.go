package features

// SearchFeature 所有搜索功能的接口
// 所有筛选功能都实现此接口
type SearchFeature interface {
	// Name 返回功能名称
	Name() string

	// IsEnabled 返回此功能是否启用
	IsEnabled() bool

	// SetEnabled 设置此功能是否启用
	SetEnabled(enabled bool)

	// Check 检查种子是否符合此功能的筛选条件
	// gameID: 游戏种子
	// useLegacyRandom: 是否使用旧随机模式
	// 返回 true 表示符合条件，false 表示不符合
	Check(gameID int, useLegacyRandom bool) bool

	// GetConfigDescription 返回此功能的配置说明
	GetConfigDescription() string
}
