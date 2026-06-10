# 第四阶段：成本优化与副业级项目（第19-29周）

## 目标

让 Agent 低成本、稳定运行，并完成可展示的完整项目。

## 脚本列表

| 文件/目录 | 周次 | 学习要点 |
|----------|------|---------|
| `01_cost_optimizer.py` | W19-20 | Prompt 缓存、模型路由、成本追踪 |
| `telegram_bot/` | W21-22 | 将 Agent 接入 Telegram Bot |
| `knowledge_base/` | W23-24 | 个人知识库 RAG Agent（副业项目） |
| `02_reliability.py` | W25-26 | 错误重试、步数限制、人工接管 |
| `portfolio/` | W27-28 | 作品集整理与展示 |

## 运行方式

```bash
# 1. 安装额外依赖
pip install python-telegram-bot

# 2. 运行 Telegram Bot
python -m phase4.telegram_bot.bot

# 3. 运行成本优化演示
python phase4/01_cost_optimizer.py
```

## 核心概念

- **前缀缓存（Prefix Caching）**：重复使用的 system prompt 可以缓存，减少 token 计费
- **模型路由**：简单问题用便宜模型，复杂问题用强模型
- **可靠性工程**：重试、超时、步数限制、错误降级
- **多用户隔离**：每个用户独立的对话历史和上下文

## 目录结构

```
phase4/
├── README.md                # 本文件
├── 01_cost_optimizer.py     # 成本优化策略
├── 02_reliability.py        # 可靠性工程
├── telegram_bot/            # Telegram Bot
│   ├── __init__.py
│   ├── bot.py               # Bot 入口
│   └── handlers.py          # 消息处理器
├── knowledge_base/          # 知识库管理
│   ├── __init__.py
│   └── manager.py           # 知识库增删改查
└── portfolio/               # 作品集展示
    ├── __init__.py
    └── demo.py              # 演示脚本
```
