# Pytest 快速开始

## 激活环境并运行测试

```bash
# 1. 激活虚拟环境
venv\Scripts\activate

# 2. 运行所有测试
python run_pytest.py all

# 3. 运行快速测试（推荐日常使用）
python run_pytest.py fast

# 4. 运行GPU测试（需要CUDA支持）
python run_pytest.py gpu
```

## 常用命令

### 使用测试运行器

```bash
python run_pytest.py unit          # 单元测试
python run_pytest.py weather       # 天气预测器测试
python run_pytest.py consistency   # 一致性测试
python run_pytest.py validation    # 验证测试
python run_pytest.py benchmark     # 性能测试
python run_pytest.py gpu           # GPU加速测试
python run_pytest.py coverage      # 带覆盖率报告
```

### 直接使用pytest

```bash
pytest                           # 运行所有测试
pytest -v                        # 详细输出
pytest -m unit                   # 只运行单元测试
pytest -m gpu                    # 只运行GPU测试
pytest -k "sample1"              # 运行包含"sample1"的测试
pytest --durations=10            # 显示最慢的10个测试
```

## 测试报告

- **HTML报告**: `reports/pytest_report.html`
- **覆盖率报告**: `htmlcov/index.html` (所有测试自动生成)
- **XML报告**: `coverage.xml` (用于CI/CD)

## 测试分类

| 标记 | 描述 | 运行命令 |
|------|------|----------|
| `unit` | 单元测试 | `pytest -m unit` |
| `weather` | 天气测试 | `pytest -m weather` |
| `consistency` | 一致性测试 | `pytest -m consistency` |
| `validation` | 验证测试 | `pytest -m validation` |
| `benchmark` | 性能测试 | `pytest -m benchmark` |
| `gpu` | GPU测试 | `pytest -m gpu` |
| `slow` | 慢测试 | `pytest -m slow` |

## 调试

```bash
# 运行单个测试
pytest tests/test_consistency.py::TestConsistencyWithGo::test_sample1_consistency

# 调试模式
pytest --pdb

# 详细输出
pytest -vv
```

## 性能优化

```bash
# 并行执行
pytest -n auto

# 排除慢测试
pytest -m "not slow"

# 只运行失败的测试
pytest --lf
```

---

详细文档请查看 `tests/README.md`
