# Pytest 测试示例

本文档提供各种测试场景的示例代码。

## 基本测试示例

### 1. 简单断言测试

```python
def test_basic_assertion():
    """基本断言测试示例"""
    assert 1 + 1 == 2
    assert "hello" in "hello world"
    assert len([1, 2, 3]) == 3
```

### 2. 使用Fixtures

```python
def test_weather_predictor_with_fixture(weather_predictor, spring_condition):
    """使用fixtures的测试示例"""
    weather_predictor.add_condition(spring_condition)
    result = weather_predictor.check(59, False)
    assert result is True
```

### 3. 参数化测试

```python
@pytest.mark.parametrize("seed,expected", [
    (59, True),
    (73, True),
    (0, False),
    (1, False),
])
def test_specific_seeds(weather_predictor, spring_condition, seed, expected):
    """参数化测试示例"""
    weather_predictor.add_condition(spring_condition)
    result = weather_predictor.check(seed, False)
    assert result == expected
```

## GPU测试示例

### 1. 基本GPU测试

```python
@pytest.mark.gpu
def test_gpu_acceleration_available():
    """测试GPU加速是否可用"""
    from internal.gpu_pure_accelerator import get_pure_gpu_info
    
    gpu_info = get_pure_gpu_info()
    assert gpu_info['available'] is True
    assert 'device_name' in gpu_info
```

### 2. 纯GPU搜索测试

```python
@pytest.mark.asyncio
@pytest.mark.gpu
async def test_pure_gpu_search():
    """测试纯GPU搜索功能"""
    from internal.gpu_pure_accelerator import PureGPUSeedSearcher
    from internal.models import WeatherCondition, Season
    
    # 创建天气条件
    conditions = [
        WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
    ]
    
    # 创建GPU搜索器
    searcher = PureGPUSeedSearcher(conditions, use_legacy_random=False)
    
    # 执行GPU搜索
    results = await searcher.search_seeds_pure_gpu(0, 10000, 10)
    
    # 验证结果
    assert len(results) > 0
    assert all(isinstance(seed, int) for seed in results)
```

### 3. GPU性能基准测试

```python
@pytest.mark.gpu
def test_gpu_performance_benchmark(benchmark):
    """GPU性能基准测试"""
    from internal.gpu_pure_accelerator import PureGPUSeedSearcher
    from internal.models import WeatherCondition, Season
    import asyncio
    
    conditions = [
        WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
    ]
    
    searcher = PureGPUSeedSearcher(conditions, use_legacy_random=False)
    
    def gpu_search():
        return asyncio.run(searcher.search_seeds_pure_gpu(0, 50000, 100))
    
    # 基准测试
    benchmark(gpu_search)
```

### 4. GPU与CPU一致性测试

```python
@pytest.mark.asyncio
@pytest.mark.gpu
async def test_gpu_cpu_consistency():
    """测试GPU和CPU结果一致性"""
    from internal.gpu_pure_accelerator import PureGPUSeedSearcher
    from internal.features import WeatherPredictor
    from internal.models import WeatherCondition, Season
    
    conditions = [
        WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
    ]
    
    # GPU搜索
    gpu_searcher = PureGPUSeedSearcher(conditions, use_legacy_random=False)
    gpu_results = await gpu_searcher.search_seeds_pure_gpu(0, 1000, 10)
    
    # CPU搜索
    cpu_predictor = WeatherPredictor()
    for condition in conditions:
        cpu_predictor.add_condition(condition)
    
    cpu_results = []
    for seed in range(0, 1001):
        if cpu_predictor.check(seed, False):
            cpu_results.append(seed)
            if len(cpu_results) >= 10:
                break
    
    # 验证结果一致性
    assert set(gpu_results) == set(cpu_results)
```

## 高级测试示例

### 1. 异常测试

```python
def test_validation_error():
    """测试异常抛出"""
    with pytest.raises(ValidationError) as exc_info:
        WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=15  # 无效值
        )
    
    assert "min_rain_days" in str(exc_info.value)
```

### 2. 模拟测试

```python
def test_with_mock(mocker):
    """使用mock的测试示例"""
    # 模拟外部依赖
    mock_hash = mocker.patch('internal.core.get_hash_from_string')
    mock_hash.return_value = 12345
    
    result = get_hash_from_string("test")
    assert result == 12345
    mock_hash.assert_called_once_with("test")
```

### 3. 异步测试

```python
@pytest.mark.asyncio
async def test_async_function():
    """异步函数测试示例"""
    result = await some_async_function()
    assert result is not None
```

## 测试标记示例

### 1. 标记测试

```python
@pytest.mark.unit
def test_unit_function():
    """单元测试标记"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """慢测试标记"""
    pass

@pytest.mark.weather
def test_weather_prediction():
    """天气测试标记"""
    pass
```

### 2. 跳过测试

```python
@pytest.mark.skip(reason="功能未实现")
def test_unimplemented_feature():
    """跳过测试示例"""
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Windows不支持")
def test_unix_only():
    """条件跳过测试"""
    pass
```

## 性能测试示例

### 1. 基准测试

```python
def test_performance_benchmark(benchmark):
    """性能基准测试示例"""
    def expensive_operation():
        return sum(range(1000))
    
    result = benchmark(expensive_operation)
    assert result == 499500
```

### 2. 内存使用测试

```python
def test_memory_usage():
    """内存使用测试示例"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 执行操作
    data = [i for i in range(10000)]
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 内存增长应该在合理范围内
    assert memory_increase < 10 * 1024 * 1024  # 10MB
```

## 数据驱动测试示例

### 1. 从文件读取测试数据

```python
@pytest.fixture
def test_data():
    """从JSON文件加载测试数据"""
    import json
    with open('tests/data/test_cases.json', 'r') as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", test_data())
def test_with_external_data(test_case):
    """使用外部数据的测试"""
    assert test_case['input'] is not None
    assert test_case['expected'] is not None
```

### 2. 动态生成测试数据

```python
def pytest_generate_tests(metafunc):
    """动态生成测试参数"""
    if "test_range" in metafunc.fixturenames:
        metafunc.parametrize("test_range", [
            (0, 100),
            (100, 1000),
            (1000, 10000),
        ])

def test_with_dynamic_data(test_range):
    """使用动态生成的数据测试"""
    start, end = test_range
    assert start < end
```

## 测试配置示例

### 1. 自定义fixture

```python
@pytest.fixture
def sample_weather_conditions():
    """自定义天气条件fixture"""
    return [
        WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        ),
        WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=10,
            min_rain_days=6
        )
    ]

def test_with_custom_fixture(sample_weather_conditions):
    """使用自定义fixture的测试"""
    assert len(sample_weather_conditions) == 2
```

### 2. 测试设置和清理

```python
@pytest.fixture
def temp_file():
    """临时文件fixture"""
    import tempfile
    import os
    
    # 设置
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"test data")
    temp_file.close()
    
    yield temp_file.name
    
    # 清理
    os.unlink(temp_file.name)

def test_with_temp_file(temp_file):
    """使用临时文件的测试"""
    with open(temp_file, 'r') as f:
        content = f.read()
    assert content == "test data"
```

## 测试报告示例

### 1. 自定义测试输出

```python
def test_with_custom_output(capsys):
    """自定义测试输出示例"""
    print("测试开始")
    assert 1 + 1 == 2
    print("测试完成")
    
    captured = capsys.readouterr()
    assert "测试开始" in captured.out
    assert "测试完成" in captured.out
```

### 2. 测试日志

```python
def test_with_logging(caplog):
    """测试日志输出示例"""
    import logging
    
    logger = logging.getLogger("test")
    logger.info("测试信息")
    logger.warning("测试警告")
    
    assert "测试信息" in caplog.text
    assert "测试警告" in caplog.text
```

## 集成测试示例

### 1. API测试

```python
@pytest.mark.integration
def test_api_endpoint(client):
    """API端点测试示例"""
    response = client.post("/api/search", json={
        "startSeed": 0,
        "endSeed": 1000,
        "weatherConditions": [{
            "season": "Spring",
            "startDay": 1,
            "endDay": 10,
            "minRainDays": 5
        }]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "seeds" in data
```

### 2. 数据库测试

```python
@pytest.fixture
def db_session():
    """数据库会话fixture"""
    # 创建测试数据库会话
    session = create_test_session()
    yield session
    session.close()

def test_database_operation(db_session):
    """数据库操作测试示例"""
    # 测试数据库操作
    result = db_session.query(Model).filter_by(id=1).first()
    assert result is not None
```

## 测试最佳实践

### 1. 测试命名

```python
# 好的测试命名
def test_weather_predictor_should_return_true_for_valid_seed():
    """描述性的测试名称"""
    pass

# 避免的测试命名
def test1():
    """不描述性的测试名称"""
    pass
```

### 2. 测试组织

```python
class TestWeatherPredictor:
    """天气预测器测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        pass
    
    def test_add_condition(self):
        """测试添加条件"""
        pass
    
    def test_check_seed(self):
        """测试种子检查"""
        pass
```

### 3. 断言消息

```python
def test_with_assertion_message():
    """带断言消息的测试"""
    result = some_function()
    assert result == expected, f"期望 {expected}，实际得到 {result}"
```

---

更多示例请查看项目中的实际测试文件。
