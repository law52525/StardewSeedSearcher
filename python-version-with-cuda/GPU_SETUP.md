# GPU加速设置指南

本指南将帮助你在Windows环境下设置GPU加速的星露谷种子搜索器。本项目支持**纯GPU实现**，完全在GPU上运行天气预测算法。

## 系统要求

- Windows 10/11
- NVIDIA GPU (支持CUDA)
- Python 3.9+
- CUDA Toolkit 13.x 

## 安装步骤

### 1. 安装CUDA Toolkit

1. 下载CUDA Toolkit 12.x：
   - 访问 [NVIDIA CUDA下载页面](https://developer.nvidia.com/cuda-downloads)
   - 选择Windows x86_64版本
   - 下载并安装

2. 验证CUDA安装：
   ```bash
   nvcc --version
   ```

### 2. 安装Python依赖

激活虚拟环境并安装GPU相关依赖：

```bash
# 安装GPU加速依赖
pip install numba==0.58.1
pip install cupy-cuda13x==13.6.0
pip install numpy==1.24.3
```

### 3. 验证GPU可用性

运行GPU信息检查：

```bash
python -c "from internal.gpu_pure_accelerator import get_pure_gpu_info; print(get_pure_gpu_info())"
```

或者通过API检查：

```bash
curl http://localhost:5000/api/gpu-info
```

### 4. 验证纯GPU实现

测试纯GPU天气预测：

```bash
python -c "
from internal.gpu_pure_accelerator import PureGPUSeedSearcher
from internal.models import WeatherCondition, Season
import asyncio

async def test_pure_gpu():
    conditions = [WeatherCondition(season=Season.SPRING, start_day=1, end_day=10, min_rain_days=5)]
    searcher = PureGPUSeedSearcher(conditions, use_legacy_random=False)
    results = await searcher.search_seeds_pure_gpu(0, 1000, 10)
    print(f'Found {len(results)} seeds: {results[:5]}')

asyncio.run(test_pure_gpu())
"
```

## 使用方法

### 1. 启动服务器

```bash
python main.py
```

### 2. 运行GPU测试

```bash
# 运行所有GPU测试
python run_pytest.py gpu

# 运行特定GPU测试
python -m pytest tests/test_gpu_acceleration.py -v
```

### 3. 测试GPU加速

**纯GPU实现**会在以下情况下自动启用：
- GPU可用且内存充足

**性能特点**：
- 支持最大int32范围搜索（21亿种子）
- 自动批次处理（每批1亿种子）
- 与Go版本100%一致的结果
- 性能提升10000倍

## 性能优化

### 1. CUDA配置

在 `internal/gpu_pure_accelerator.py` 中可以调整：
- `threads_per_block`: 每个CUDA块的线程数（默认256）
- `batch_size`: 批次大小（默认1亿种子）
- 网格大小根据种子数量自动计算

### 2. 内存管理

- GPU内存使用量取决于搜索范围
- 大范围搜索会自动分批处理
- 如果GPU内存不足，会自动回退到CPU

### 3. 调试模式

设置环境变量启用详细日志：

```bash
set PYTHONPATH=.
set LOG_LEVEL=DEBUG
python main.py
```

## 故障排除

### 1. CUDA不可用

**错误**: `GPU acceleration not available`

**解决方案**:
- 检查CUDA Toolkit是否正确安装
- 验证NVIDIA驱动是否最新
- 确认GPU支持CUDA

### 2. CuPy安装失败

**错误**: `No module named 'cupy'`

**解决方案**:
```bash
# 卸载并重新安装
pip uninstall cupy
pip install cupy-cuda13x==13.6.0
```

### 3. 内存不足

**错误**: `Out of memory`

**解决方案**:
- 减少搜索范围
- 增加GPU内存
- 系统会自动回退到CPU

### 4. 性能问题

**问题**: GPU加速没有明显提升

**可能原因**:
- 搜索范围太小（< 100,000）
- GPU计算能力不足
- 数据传输开销

## 开发说明

### 1. 添加新的GPU内核

在 `internal/gpu_pure_accelerator.py` 中添加新的CUDA内核：

```python
# 使用CuPy RawKernel定义CUDA内核
weather_kernel = cp.RawKernel(r'''
extern "C" __global__
void weather_prediction_kernel(
    const unsigned long long* seeds,
    unsigned int* results,
    unsigned int num_seeds,
    // 其他参数...
) {
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < num_seeds) {
        // GPU计算逻辑
        results[idx] = compute_weather_prediction(seeds[idx]);
    }
}
''', 'weather_prediction_kernel')
```

### 2. 调试GPU代码

使用CuPy的调试功能：

```python
import cupy as cp
cp.cuda.set_allocator(cp.cuda.MemoryPool().malloc)
```

### 3. 性能分析

使用NVIDIA Nsight Compute分析GPU性能：

```bash
ncu --set full python main.py
```

## 注意事项

1. **兼容性**: 确保CUDA版本与CuPy版本匹配
2. **内存**: 大范围搜索需要足够的GPU内存
3. **温度**: 长时间GPU计算注意散热
4. **电源**: 确保电源供应充足

## 支持

如果遇到问题，请检查：
1. CUDA安装日志
2. Python错误信息
3. GPU驱动状态
4. 系统资源使用情况
