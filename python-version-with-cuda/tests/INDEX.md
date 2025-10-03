# 测试文档索引

欢迎来到StardewSeedSearcher项目的测试文档！

## 📚 文档导航

### 主要文档

| 文档 | 描述 | 适用人群 |
|------|------|----------|
| [README.md](README.md) | 完整的pytest使用指南 | 所有用户 |
| [QUICK_START.md](QUICK_START.md) | 快速开始和常用命令 | 新用户 |
| [EXAMPLES.md](EXAMPLES.md) | 各种测试场景示例 | 开发者 |

### 快速链接

- 🚀 [开始测试](QUICK_START.md#快速开始)
- 📖 [详细文档](README.md#快速开始)
- 💡 [测试示例](EXAMPLES.md#基本测试示例)
- 🔧 [配置说明](README.md#测试配置)

## 🎯 根据需求选择文档

### 我是新用户
👉 先看 [QUICK_START.md](QUICK_START.md)，然后根据需要查看 [README.md](README.md)

### 我是开发者
👉 先看 [README.md](README.md)，然后参考 [EXAMPLES.md](EXAMPLES.md) 中的示例

### 我需要快速运行测试
👉 直接看 [QUICK_START.md](QUICK_START.md#快速开始)

### 我需要了解测试配置
👉 查看 [README.md](README.md#测试配置)

### 我需要编写新测试
👉 参考 [EXAMPLES.md](EXAMPLES.md) 中的示例

## 📋 测试概览

### 测试类型

| 类型 | 文件 | 描述 |
|------|------|------|
| 单元测试 | `test_weather_predictor.py` | 核心功能测试 |
| 一致性测试 | `test_consistency.py` | 与Go版本对比 |
| 验证测试 | `test_data_validation.py` | 数据验证测试 |
| WebSocket测试 | `test_websocket_messages.py` | 消息格式测试 |
| API测试 | `test_api_endpoints.py` | HTTP端点测试 |
| 性能测试 | `test_benchmark.py` | 性能基准测试 |
| GPU测试 | `test_gpu_acceleration.py` | GPU加速功能测试 |

### 测试标记

| 标记 | 用途 | 运行命令 |
|------|------|----------|
| `unit` | 单元测试 | `pytest -m unit` |
| `integration` | 集成测试 | `pytest -m integration` |
| `weather` | 天气测试 | `pytest -m weather` |
| `consistency` | 一致性测试 | `pytest -m consistency` |
| `validation` | 验证测试 | `pytest -m validation` |
| `websocket` | WebSocket测试 | `pytest -m websocket` |
| `benchmark` | 性能测试 | `pytest -m benchmark` |
| `gpu` | GPU测试 | `pytest -m gpu` |
| `slow` | 慢测试 | `pytest -m slow` |

## 🛠️ 常用命令速查

### 基本命令

```bash
# 激活环境
venv\Scripts\activate

# 运行所有测试
python run_pytest.py all

# 运行快速测试
python run_pytest.py fast

# 运行GPU测试
python run_pytest.py gpu
```

### 特定测试

```bash
# 单元测试
python run_pytest.py unit

# 一致性测试
python run_pytest.py consistency

# 性能测试
python run_pytest.py benchmark
```

### 直接使用pytest

```bash
# 基本运行
pytest

# 详细输出
pytest -v

# 特定标记
pytest -m unit

# 特定文件
pytest tests/test_consistency.py
```

## 📊 测试报告

- **HTML报告**: `reports/pytest_report.html`
- **覆盖率报告**: `htmlcov/index.html` (所有测试自动生成)
- **XML报告**: `coverage.xml` (用于CI/CD)

## ❓ 常见问题

### Q: 如何运行特定测试？
A: 查看 [QUICK_START.md](QUICK_START.md#运行特定测试)

### Q: 如何添加新测试？
A: 参考 [EXAMPLES.md](EXAMPLES.md#添加新测试)

### Q: 如何调试测试？
A: 查看 [README.md](README.md#调试测试)

### Q: 测试失败了怎么办？
A: 查看 [README.md](README.md#常见问题)

## 🔗 相关链接

- [项目主页](../README_Python.md)
- [pytest官方文档](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest markers](https://docs.pytest.org/en/stable/mark.html)

---

**提示**: 如果找不到需要的信息，请查看 [README.md](README.md) 的完整文档。
