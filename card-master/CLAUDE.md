# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Card Master 是一个信用卡返现排行工具，使用 AI Agent 从银行官网自动采集信用卡信息，并提供按消费类别排序的 Web 界面。

## 技术栈

- **后端**: FastAPI + Pydantic
- **前端**: HTML + Tailwind CSS + Alpine.js (单页应用)
- **AI Agent**: Agno Framework (支持多 LLM 提供商)
- **网页采集**: Crawl4ai, Playwright
- **数据存储**: SQLite (主) + JSON (兼容旧数据)

## 快速启动

```bash
# 一键启动 (自动初始化环境)
./start.sh

# 指定端口
./start.sh -p 3000

# 仅安装依赖，不启动服务
./start.sh --install-only
```

## 手动命令

```bash
# 使用 uv 创建虚拟环境
uv venv .venv --python 3.13
uv pip install -r requirements.txt

# 安装 Playwright 浏览器 (采集功能必需)
playwright install

# 启动开发服务器 (必须用 --loop asyncio 避免与 nest_asyncio 冲突)
uvicorn main:app --reload --port 8000 --loop asyncio
```

## 项目架构

```
card-master/
├── main.py                    # FastAPI 入口，配置 asyncio 和模板
├── src/
│   ├── models/
│   │   └── credit_card.py     # Pydantic 数据模型 (CreditCard, RewardRule, SpendingCategory)
│   ├── api/
│   │   └── routes.py          # FastAPI 路由 (/api/*)
│   ├── services/
│   │   ├── card_service.py    # 业务逻辑层，卡片查询和排名
│   │   ├── storage.py         # JSON 文件存储 (兼容层)
│   │   └── database.py        # SQLite 数据库操作
│   ├── agents/
│   │   ├── card_collector_agent.py  # Agno Agent 主采集器
│   │   ├── bank_scraper.py          # Playwright 银行页面采集
│   │   └── card_analyzer.py         # LLM 卡片信息解析
│   └── web/templates/
│       └── index.html         # 前端单页应用
├── scripts/                   # 辅助脚本
│   ├── collect_cards.py       # 批量采集脚本
│   └── import_savevia_data.py # 导入外部数据
└── data/
    └── cards.db               # SQLite 数据库
```

## 核心概念

### 双存储后端
- `Database` (SQLite): 主存储，用于采集的卡片数据
- `CardStorage` (JSON): 兼容层，支持旧格式导入
- `CardService`: 业务层自动选择有数据的后端

### 消费类别 (SpendingCategory)
DINING, GROCERY, GAS, TRAVEL, TRANSIT, STREAMING, ENTERTAINMENT, PERSONAL_SERVICES, RETAIL, HOME_IMPROVEMENT, RECURRING, PHARMACY, FOREIGN, ONLINE_SHOPPING, EV_CHARGING, TELECOM, INSURANCE, RENT, WHOLESALE, OTHER

### LLM 提供商配置
支持: volces(火山引擎/默认), openai, claude, gemini, groq, deepseek, ollama

通过环境变量配置：
- `DEFAULT_LLM_PROVIDER`: 默认提供商
- `DEFAULT_LLM_MODEL`: 默认模型
- `VOLCES_API_KEY` / `VOLCES_BASE_URL`: 火山引擎配置
- 其他提供商对应的 API_KEY

## 关键 API 端点

| 端点 | 说明 |
|------|------|
| `GET /api/cards` | 获取所有卡片，支持 bank/no_annual_fee/no_fx_fee 过滤 |
| `GET /api/cards/rank/{category}` | 按消费类别返回排名 |
| `GET /api/categories` | 获取有卡片的消费类别列表 |
| `POST /api/agent/collect` | 使用 Agent 采集单张卡片 |
| `POST /api/agent/collect-bank` | 采集银行所有卡片 |
| `POST /api/banks` | 添加新银行配置 |

## 注意事项

- **启动必须用 `--loop asyncio`**: uvloop 与 nest_asyncio 不兼容，会报 `Can't patch loop of type uvloop.Loop`
- main.py 必须在 import uvicorn 前禁用 uvloop，否则 Crawl4ai 报错
- 使用 `nest_asyncio.apply()` 解决 FastAPI 中的嵌套事件循环问题
- Pydantic 模型使用 `from_api()` 方法兼容 savevia.app camelCase 格式
- 数据库默认初始化加拿大 12 家主要银行配置
