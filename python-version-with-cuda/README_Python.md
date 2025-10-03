# StardewSeedSearcher - Python Version

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

星露谷物语种子搜索器 - Python版本 (从Go版本转换而来)

## 功能特性

- 天气预测：预测第一年春夏秋的天气情况
- 种子搜索：根据天气条件搜索符合条件的种子
- **GPU加速**：使用CUDA进行高性能并行计算
- **纯GPU实现**：完全在GPU上运行的天气预测算法
- Web界面：提供友好的Web界面进行搜索
- 实时进度：通过WebSocket实时显示搜索进度

## 技术栈

- 后端：Python 3.9+ + FastAPI
- 前端：HTML + CSS + JavaScript (保持不变)
- 通信：WebSocket + REST API
- 哈希：xxHash (Python版本)
- **GPU加速**：CUDA + CuPy + Numba
- **并行计算**：纯GPU天气预测算法

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- **CUDA 13.0+** (用于GPU加速)
- **NVIDIA GPU** (支持CUDA)
- 现代浏览器（支持WebSocket）

### 运行步骤

1. 克隆项目
```bash
git clone https://github.com/law52525/StardewSeedSearcher.git
cd StardewSeedSearcher
```

2. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt
```

3. 运行后端服务
```bash
python main.py
```

4. 打开前端页面
在浏览器中打开 `http://localhost:5000`

5. 开始搜索
- 设置种子范围
- 配置天气条件
- 点击"开始搜索"

### 使用启动脚本

项目提供了便捷的启动脚本：

**Windows:**
```bash
# 双击运行或在命令行执行
start.bat
```

**Linux/macOS:**
```bash
# 添加执行权限并运行
chmod +x start.sh
./start.sh
```

### 运行测试

```bash
# 运行所有测试
python run_pytest.py all

# 运行快速测试（推荐日常使用）
python run_pytest.py fast
```

### 测试文档

- 📖 [完整测试文档](tests/README.md) - 详细的pytest使用指南
- ⚡ [快速开始](tests/QUICK_START.md) - 常用命令快速参考
- 💡 [测试示例](tests/EXAMPLES.md) - 各种测试场景示例

### 测试类型

- **单元测试** (`unit`)：测试各个组件的功能
- **集成测试** (`integration`)：测试组件间的交互
- **一致性测试** (`consistency`)：确保与Go版本的结果一致
- **性能测试** (`benchmark`)：测试搜索性能
- **验证测试** (`validation`)：测试数据验证
- **WebSocket测试** (`websocket`)：测试消息格式
- **GPU测试** (`gpu`)：测试GPU加速功能

### 测试报告

- **HTML报告**：`reports/pytest_report.html`
- **覆盖率报告**：`htmlcov/index.html`

## 项目结构

```
StardewSeedSearcher/
├── internal/                  # 核心代码
│   ├── __init__.py
│   ├── models.py              # 数据模型
│   ├── core.py                # 核心功能 (哈希计算)
│   ├── features.py            # 搜索功能
│   ├── handlers.py            # HTTP 处理器
│   ├── websocket.py           # WebSocket 功能
│   ├── server.py              # Web 服务器配置
│   └── gpu_pure_accelerator.py # GPU加速实现
├── tests/                     # 测试代码
│   ├── README.md              # 测试文档
│   ├── QUICK_START.md         # 快速开始
│   ├── EXAMPLES.md            # 测试示例
│   ├── conftest.py            # pytest配置
│   ├── test_*.py              # 各种测试文件
│   └── __init__.py
├── reports/                   # 测试报告
│   └── pytest_report.html     # HTML测试报告
├── main.py                    # 主程序入口
├── run_pytest.py              # 测试运行器
├── pytest.ini                # pytest配置
├── pyproject.toml             # 项目配置
├── requirements.txt           # Python 依赖文件
├── index.html                 # 前端页面 (保持不变)
├── start.bat                  # Windows 启动脚本
├── start.sh                   # Linux/macOS 启动脚本
└── README_Python.md           # Python版本说明
```

## API 接口

### POST /api/search
搜索符合条件的种子

**请求体：**
```json
{
  "startSeed": 0,
  "endSeed": 100000,
  "useLegacyRandom": false,
  "weatherConditions": [
    {
      "season": "Spring",
      "startDay": 1,
      "endDay": 28,
      "minRainDays": 10
    }
  ],
  "outputLimit": 20
}
```

### GET /api/health
健康检查

**响应：**
```json
{
  "status": "ok",
  "version": "1.0"
}
```

### GET /api/gpu-info
GPU信息检查

**响应：**
```json
{
  "available": true,
  "device_name": "NVIDIA GeForce RTX 4090",
  "memory_total": "24576 MB",
  "memory_free": "24000 MB",
  "cuda_version": "13.0"
}
```

### WebSocket /ws
实时通信，用于推送搜索进度和结果

## 从Go版本迁移

此Python版本是从Go版本转换而来，保持了相同的功能和API接口：

- 相同的天气预测算法
- 相同的WebSocket消息格式
- 相同的前端界面
- 相同的搜索逻辑

主要改进：
- 更简洁的代码结构
- 更好的类型安全 (Pydantic)
- 更现代的异步处理
- 更易于扩展和维护
- **GPU加速支持**：使用CUDA进行高性能并行计算
- **纯GPU实现**：完全在GPU上运行的天气预测算法
- **批次处理**：支持大规模种子搜索（21亿种子）
- **性能提升**：相比CPU版本提升上万倍性能

## 功能愿望单

### 天气

游戏里每天有不同天气，我想搜索雨天等特定天气。 

星露谷一年有4个季节（春夏秋冬），每个季节有一个月（真奇怪！），每个月有28天。我希望设定开始和结束日期，在这个范围里，筛选至少包含X个雨天的种子。 

例：春1-春28，至少有8个雨天 

注意，这个功能默认筛选第一年。后续年份不参与筛选。 

另外，我希望可以多个条件嵌套。例如： 

春10-春28，至少8个雨天，而且夏1-夏20，至少5个雨天。 

注意，"雨天"包括"雨（Rain）"、"雷雨（storm）"、"绿雨（Green rain）"

### 猪车（旅行商人）

在游戏里，某些特定天数会有猪车出现，并随机售卖一些物品。 

### 仙子

每天晚上有概率出现"仙子" 

### 矿井宝箱

矿井有120层，其中特定层数有宝箱，我想预测宝箱里的内容 

### 沙漠节

节日期间（春15-17）有村民（villager）会来摆摊，我想预测是谁来摆摊 

### 怪物层

矿井有120层，每天会有特定层数为"怪物层"，我想预测在特定天数下，怪物层有哪些 

### 每日菜品

酒吧每天出售一个特定菜品，我想预测游戏第一天（春1）的菜品

另外，这个菜品受游戏开局动画（春0）的步数影响，我也想预测，在特定的种子下，不同的步数分别对应什么菜品 

### 垃圾桶

游戏里有好几个垃圾桶，我想搜索"酒吧"的垃圾桶，在特定日期产出的物品 

### 晶球

游戏里有几种不同的晶球，打破后会有不同产物，我想预测前n个晶球中是否出现特定物品 

### 齐先生任务

每周齐先生会提供两个任务，我想预测在特定日期任务会是什么 目前就想要这些功能，我想挨个开发。后面可能还会加入更多功能。

### 矿+1

使用矮人雕像，每天会有两个加成buff，我想预测出现"矿+1"这个buff的日期

## 许可证

MIT License
