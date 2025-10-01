package core

import (
	"testing"
)

func TestHashHelper_GetHashFromString(t *testing.T) {
	helper := NewHashHelper()

	// 测试空字符串
	hash1 := helper.GetHashFromString("")
	hash2 := helper.GetHashFromString("")
	if hash1 != hash2 {
		t.Error("相同输入的哈希应该是确定性的")
	}

	// 测试不同字符串
	hash3 := helper.GetHashFromString("test")
	hash4 := helper.GetHashFromString("test")
	if hash3 != hash4 {
		t.Error("相同输入的哈希应该是确定性的")
	}

	if hash1 == hash3 {
		t.Error("不同输入应该产生不同的哈希")
	}
}

func TestHashHelper_GetHashFromArray(t *testing.T) {
	helper := NewHashHelper()

	// 测试相同数组
	hash1 := helper.GetHashFromArray(1, 2, 3, 4, 5)
	hash2 := helper.GetHashFromArray(1, 2, 3, 4, 5)
	if hash1 != hash2 {
		t.Error("相同输入的哈希应该是确定性的")
	}

	// 测试不同数组
	hash3 := helper.GetHashFromArray(1, 2, 3, 4, 6)
	if hash1 == hash3 {
		t.Error("不同输入应该产生不同的哈希")
	}
}

func TestHashHelper_GetRandomSeed(t *testing.T) {
	helper := NewHashHelper()

	// 测试旧随机模式
	seed1 := helper.GetRandomSeed(1, 2, 3, 4, 5, true)
	seed2 := helper.GetRandomSeed(1, 2, 3, 4, 5, true)
	if seed1 != seed2 {
		t.Error("旧随机模式对相同输入应该是确定性的")
	}

	// 测试新随机模式
	seed3 := helper.GetRandomSeed(1, 2, 3, 4, 5, false)
	seed4 := helper.GetRandomSeed(1, 2, 3, 4, 5, false)
	if seed3 != seed4 {
		t.Error("新随机模式对相同输入应该是确定性的")
	}

	// 测试旧随机和新随机产生不同结果
	if seed1 == seed3 {
		t.Error("旧随机和新随机应该产生不同结果")
	}

	// 测试参数范围限制
	largeSeed := helper.GetRandomSeed(3000000000, 3000000000, 3000000000, 3000000000, 3000000000, true)
	if largeSeed < 0 || largeSeed >= 2147483647 {
		t.Errorf("种子应该在有效范围内，得到 %d", largeSeed)
	}
}

func TestConvenienceFunctions(t *testing.T) {
	// 测试便利函数
	hash1 := GetHashFromString("test")
	hash2 := GetHashFromString("test")
	if hash1 != hash2 {
		t.Error("便利函数应该是确定性的")
	}

	seed1 := GetRandomSeed(1, 2, 3, 4, 5, false)
	seed2 := GetRandomSeed(1, 2, 3, 4, 5, false)
	if seed1 != seed2 {
		t.Error("便利函数应该是确定性的")
	}
}
