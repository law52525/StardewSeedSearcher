# Pytest 测试使用文档

本文档介绍如何使用项目中的pytest测试体系。

## 目录结构

```
tests/
├── README.md                    # 本文档
├── __init__.py                  # Python包标识
├── conftest.py                  # pytest配置和fixtures
├── test_api_endpoints.py        # API端点测试
├── test_benchmark.py            # 性能基准测试
├── test_consistency.py          # 与Go版本一致性测试
├── test_data_validation.py      # 数据验证测试
├── test_gpu_acceleration.py     # GPU加速测试
├── test_weather_predictor.py    # 天气预测器测试
└── test_websocket_messages.py   # WebSocket消息测试
```

## 快速开始

### 1. 激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. 运行所有测试

```bash
# 使用测试运行器（推荐）
python run_pytest.py all

# 或直接使用pytest
pytest

# 运行GPU测试（需要CUDA支持）
python run_pytest.py gpu
```

## 测试运行器使用

项目提供了 `run_pytest.py` 脚本，支持多种测试配置：

### 基本命令

```bash
python run_pytest.py [命令] [选项]
```

### 可用命令

| 命令 | 描述 | 包含的测试 |
|------|------|------------|
| `all` | 运行所有测试 | 所有测试类型 |
| `unit` | 单元测试 | 核心功能测试 |
| `integration` | 集成测试 | API端点测试 |
| `weather` | 天气预测器测试 | 天气相关功能 |
| `validation` | 数据验证测试 | 输入验证 |
| `websocket` | WebSocket测试 | 消息格式测试 |
| `consistency` | 一致性测试 | 与Go版本对比 |
| `benchmark` | 性能基准测试 | 性能测试 |
| `fast` | 快速测试 | 排除慢测试 |
| `coverage` | 覆盖率测试 | 带覆盖率报告 |

### 示例

```bash
# 运行单元测试
python run_pytest.py unit

# 运行天气预测器测试
python run_pytest.py weather

# 运行快速测试（排除耗时测试）
python run_pytest.py fast

# 运行带覆盖率的测试
python run_pytest.py coverage
```

## 直接使用pytest

### 基本命令

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示最慢的10个测试
pytest --durations=10

# 并行执行
pytest -n auto
```

### 运行特定测试

```bash
# 运行特定文件
pytest tests/test_consistency.py

# 运行特定测试类
pytest tests/test_weather_predictor.py::TestWeatherPredictor

# 运行特定测试方法
pytest tests/test_consistency.py::TestConsistencyWithGo::test_sample1_consistency

# 运行包含特定关键词的测试
pytest -k "sample1"

# 运行特定标记的测试
pytest -m unit
pytest -m consistency
pytest -m gpu
pytest -m "not slow"
```

### 输出选项

```bash
# 简短错误信息
pytest --tb=short

# 显示print输出
pytest -s

# 彩色输出
pytest --color=yes

# 静默模式
pytest -q
```

## 测试标记

项目使用pytest标记来分类测试：

| 标记 | 描述 | 示例 |
|------|------|------|
| `unit` | 单元测试 | 核心功能测试 |
| `integration` | 集成测试 | API端点测试 |
| `slow` | 慢测试 | 大范围搜索测试 |
| `api` | API测试 | HTTP端点测试 |
| `weather` | 天气测试 | 天气预测器测试 |
| `validation` | 验证测试 | 数据验证测试 |
| `websocket` | WebSocket测试 | 消息格式测试 |
| `consistency` | 一致性测试 | 与Go版本对比 |
| `benchmark` | 基准测试 | 性能测试 |
| `gpu` | GPU测试 | GPU加速功能测试 |

### 使用标记

```bash
# 只运行单元测试
pytest -m unit

# 排除慢测试
pytest -m "not slow"

# 运行多个标记
pytest -m "unit or weather"

# 运行GPU测试
pytest -m gpu

# 排除多个标记
pytest -m "not slow and not benchmark"
```

## 测试配置

### pytest.ini 配置

项目使用 `pytest.ini` 进行配置：

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# 输出选项
addopts = --verbose --tb=short --color=yes --durations=10

# 标记定义
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    # ... 更多标记

# 覆盖率配置
addopts = --cov=internal --cov-report=html --cov-report=term-missing
```

### conftest.py 配置

`conftest.py` 包含：
- 测试fixtures
- 测试数据
- 全局配置

## 测试报告

### HTML报告

测试运行后自动生成HTML报告：

```bash
# 生成HTML报告
pytest --html=reports/pytest_report.html --self-contained-html

# 查看报告
# 打开 reports/pytest_report.html
```

### 覆盖率报告

**所有测试命令都会自动生成覆盖率报告！**

```bash
# 所有测试命令都包含覆盖率报告
python run_pytest.py all          # 包含覆盖率报告
python run_pytest.py unit         # 包含覆盖率报告
python run_pytest.py gpu          # 包含覆盖率报告
python run_pytest.py fast         # 包含覆盖率报告

# 手动生成覆盖率报告
pytest --cov=internal --cov-report=html --cov-report=term-missing

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

**覆盖率报告类型**：
- **HTML报告**：`htmlcov/index.html` - 交互式网页报告
- **终端报告**：`--cov-report=term-missing` - 显示未覆盖的行
- **XML报告**：`coverage.xml` - 用于CI/CD集成

## 性能测试

### 基准测试

```bash
# 运行基准测试
python run_pytest.py benchmark

# 或直接使用pytest
pytest tests/test_benchmark.py
```

### 性能分析

基准测试会显示：
- 操作次数/秒 (OPS)
- 平均执行时间
- 最小/最大时间
- 标准差

## 调试测试

### 调试单个测试

```bash
# 运行单个测试并进入调试器
pytest tests/test_consistency.py::TestConsistencyWithGo::test_sample1_consistency --pdb

# 在失败时进入调试器
pytest --pdb
```

### 详细输出

```bash
# 显示详细输出
pytest -vv

# 显示所有输出
pytest -s

# 显示测试发现过程
pytest --collect-only
```

## 测试数据

### Fixtures

项目提供以下fixtures：

| Fixture | 描述 | 用途 |
|---------|------|------|
| `weather_predictor` | 天气预测器实例 | 天气测试 |
| `spring_condition` | 春季天气条件 | 天气测试 |
| `summer_condition` | 夏季天气条件 | 天气测试 |
| `fall_condition` | 秋季天气条件 | 天气测试 |
| `expected_seeds_sample1` | 样例1期望种子 | 一致性测试 |
| `sample_search_request` | 示例搜索请求 | API测试 |

### 使用Fixtures

```python
def test_example(weather_predictor, spring_condition):
    """使用fixtures的测试示例"""
    weather_predictor.add_condition(spring_condition)
    result = weather_predictor.check(59, False)
    assert result is True
```

## 常见问题

### 1. 测试失败

```bash
# 查看详细错误信息
pytest -v --tb=long

# 只运行失败的测试
pytest --lf
```

### 2. 测试超时

```bash
# 设置超时时间
pytest --timeout=300

# 跳过超时测试
pytest -m "not slow"
```

### 3. 内存问题

```bash
# 限制并行进程数
pytest -n 2

# 运行单个测试
pytest tests/test_consistency.py::TestConsistencyWithGo::test_sample1_consistency
```

## 最佳实践

### 1. 测试命名

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 2. 测试组织

- 按功能模块组织测试文件
- 使用描述性的测试名称
- 使用fixtures共享测试数据

### 3. 测试数据

- 使用fixtures管理测试数据
- 避免硬编码测试数据
- 使用参数化测试处理多组数据

### 4. 断言

- 使用具体的断言消息
- 一个测试一个断言（理想情况）
- 使用pytest的断言重写功能

## 持续集成

### GitHub Actions

项目包含 `.github/workflows/test.yml` 用于CI/CD：

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

### 本地CI模拟

```bash
# 模拟CI环境运行测试
pytest --tb=short --disable-warnings
```

## 扩展测试

### 添加新测试

1. 在相应的测试文件中添加测试方法
2. 使用适当的标记
3. 添加必要的fixtures
4. 更新文档

### 添加新测试文件

1. 创建 `test_*.py` 文件
2. 导入必要的模块
3. 定义测试类和方法
4. 更新本文档

## 参考资源

- [pytest官方文档](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest markers](https://docs.pytest.org/en/stable/mark.html)
- [pytest parametrize](https://docs.pytest.org/en/stable/parametrize.html)
- [pytest coverage](https://pytest-cov.readthedocs.io/)

---

如有问题，请查看项目根目录的 `README.md` 或联系开发团队。
