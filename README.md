# StardewSeedSearcher

[![Go Tests](https://github.com/law52525/StardewSeedSearcher/workflows/Go%20Tests/badge.svg)](https://github.com/law52525/StardewSeedSearcher/actions)
[![Go Version](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://golang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

星露谷物语种子搜索器 - 脆音音版本 (Go 重构版)

## 功能特性

- 天气预测：预测第一年春夏秋的天气情况
- 种子搜索：根据天气条件搜索符合条件的种子
- Web界面：提供友好的Web界面进行搜索
- 实时进度：通过WebSocket实时显示搜索进度

## 技术栈

- 后端：Go 1.21+
- 前端：HTML + CSS + JavaScript
- 通信：WebSocket + REST API
- 哈希：xxHash32

## 快速开始

### 环境要求

- Go 1.21 或更高版本
- 现代浏览器（支持WebSocket）

### 运行步骤

1. 克隆项目
```bash
git clone https://github.com/law52525/StardewSeedSearcher.git
cd StardewSeedSearcher
```

2. 安装依赖
```bash
go mod tidy
```

3. 运行后端服务
```bash
go run main.go
```

4. 打开前端页面
在浏览器中打开 `index.html`

5. 开始搜索
- 设置种子范围
- 配置天气条件
- 点击"开始搜索"

### 构建可执行文件

```bash
# 构建
go build -o stardew-seed-searcher.exe .

# 运行
./stardew-seed-searcher.exe
```

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
go test ./...

# 运行特定包的测试
go test ./internal/features
go test ./internal/core
go test ./internal/handlers
```

### 下载预编译版本

不想自己编译？可以直接下载预编译的可执行文件：

1. 访问 [Releases 页面](https://github.com/law52525/StardewSeedSearcher/releases)
2. 下载对应操作系统的版本：
   - Windows: `stardew-seed-searcher.exe`
   - Linux: `stardew-seed-searcher`
   - macOS: `stardew-seed-searcher`
3. 直接运行即可，无需安装 Go 环境

**注意：** 预编译版本已包含所有依赖，开箱即用！


## 项目结构

```
StardewSeedSearcher/
├── internal/
│   ├── core/              # 核心功能
│   │   ├── hash_helper.go
│   │   └── hash_helper_test.go
│   ├── features/          # 搜索功能
│   │   ├── search_feature.go
│   │   ├── weather_predictor.go
│   │   └── weather_predictor_test.go
│   ├── handlers/          # HTTP 处理器
│   │   ├── handlers.go
│   │   ├── handlers_test.go
│   │   └── parallel_test.go
│   ├── models/            # 数据模型
│   │   └── models.go
│   ├── server/            # Web 服务器
│   │   └── server.go
│   └── websocket/         # WebSocket 功能
│       ├── client.go
│       └── hub.go
├── main.go                # 主程序入口
├── go.mod                 # Go 模块文件
├── go.sum                 # 依赖校验文件
├── index.html             # 前端页面
├── start.bat              # Windows 启动脚本
├── start.sh               # Linux/macOS 启动脚本
└── LICENSE                # 许可证文件
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

### WebSocket /ws
实时通信，用于推送搜索进度和结果

### 代码结构说明

- `internal/core/`: 核心功能，如哈希计算
- `internal/features/`: 搜索功能实现
- `internal/handlers/`: HTTP 请求处理
- `internal/models/`: 数据模型定义
- `internal/server/`: Web 服务器配置
- `internal/websocket/`: WebSocket 通信

## 从 C# 版本迁移

此版本是从 C# 版本重构而来，保持了相同的功能和 API 接口：

- 相同的天气预测算法
- 相同的 WebSocket 消息格式
- 相同的前端界面
- 相同的搜索逻辑

主要改进：
- 更快的启动时间
- 更快的枚举时间（速度提升3600%，30w seed/s）
- 更好的并发性能

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