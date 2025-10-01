package core

import (
	"encoding/binary"
	"hash"

	"github.com/pierrec/xxHash/xxHash32"
)

// HashHelper 提供哈希和随机种子计算功能
// 基于 Underscore76 的实现
type HashHelper struct {
	hasher hash.Hash32
}

// NewHashHelper 创建新的 HashHelper 实例
func NewHashHelper() *HashHelper {
	return &HashHelper{
		hasher: xxHash32.New(0),
	}
}

// GetHashFromString 从字符串获取确定性哈希值
func (h *HashHelper) GetHashFromString(value string) int32 {
	data := []byte(value)
	return h.GetHashFromBytes(data)
}

// GetHashFromArray 从整数数组获取确定性哈希值
func (h *HashHelper) GetHashFromArray(values ...int) int32 {
	data := make([]byte, len(values)*4)
	for i, v := range values {
		binary.LittleEndian.PutUint32(data[i*4:], uint32(v))
	}
	return h.GetHashFromBytes(data)
}

// GetHashFromBytes 从字节数组获取确定性哈希值
func (h *HashHelper) GetHashFromBytes(data []byte) int32 {
	// 重置哈希器到初始状态
	h.hasher.Reset()
	h.hasher.Write(data)
	hash32 := h.hasher.Sum32()

	// 模拟C#的BitConverter.ToInt32行为
	// BitConverter.ToInt32将字节数组转换为有符号32位整数
	return int32(hash32)
}

// GetRandomSeed 计算随机种子
// 模拟 StardewValley.Utility.CreateRandomSeed()
func (h *HashHelper) GetRandomSeed(a, b, c, d, e int, useLegacyRandom bool) int {
	// 确保参数在有效范围内
	a = a % 2147483647
	b = b % 2147483647
	c = c % 2147483647
	d = d % 2147483647
	e = e % 2147483647

	if useLegacyRandom {
		// 旧随机：简单相加取模
		sum := int64(a) + int64(b) + int64(c) + int64(d) + int64(e)
		return int(sum % 2147483647)
	} else {
		// 新随机：使用 XXHash
		return int(h.GetHashFromArray(a, b, c, d, e))
	}
}

// 全局实例，方便使用
var DefaultHashHelper = NewHashHelper()

// 使用全局实例的便利函数（线程安全版本）
func GetHashFromString(value string) int32 {
	helper := NewHashHelper()
	return helper.GetHashFromString(value)
}

func GetHashFromArray(values ...int) int32 {
	helper := NewHashHelper()
	return helper.GetHashFromArray(values...)
}

func GetRandomSeed(a, b, c, d, e int, useLegacyRandom bool) int {
	helper := NewHashHelper()
	return helper.GetRandomSeed(a, b, c, d, e, useLegacyRandom)
}
