# 第四阶段：成本优化与副业级项目（第19-29周）

## 目标

让 Agent 低成本、稳定运行，并完成可展示的完整项目。  
**关键认知**：成本不是"加缓存就完事"，本阶段会学"成本可观测 → 找出瓶颈 → 针对性优化"的完整链路。

## 任务列表

- [ ] `01_cost_optimizer.py` — Prompt 缓存、模型路由、成本追踪
- [ ] `02_reliability.py` — 错误重试、步数限制、人工接管
- [ ] `03_cost_dashboard.py` — **【借鉴 Reasonix 桌面端】** 成本仪表盘：实时显示 token / 缓存命中率 / 费用
- [ ] `telegram_bot/` — 将 Agent 接入 Telegram Bot
- [ ] `knowledge_base/` — 个人知识库 RAG Agent（副业项目）
- [ ] `portfolio/` — 作品集整理与展示

## 运行方式

```bash
# 1. 安装额外依赖
pip install python-telegram-bot rich

# 2. 运行 Telegram Bot
python -m phase4.telegram_bot.bot

# 3. 运行成本优化演示
python phase4/01_cost_optimizer.py

# 4. 启动成本仪表盘（终端版）
python phase4/03_cost_dashboard.py
```

## 核心概念

- **前缀缓存（Prefix Caching）**：重复使用的 system prompt 可以缓存，减少 token 计费
- **模型路由**：简单问题用便宜模型，复杂问题用强模型
- **Append-Only 日志**：保持消息历史稳定，最大限度命中前缀缓存（Phase 2 学的）
- **可靠性工程**：重试、超时、步数限制、错误降级
- **多用户隔离**：每个用户独立的对话历史和上下文
- **成本可观测**：把"花了多少、为什么花"做成可视化

## 目录结构

```
phase4/
├── README.md                # 本文件
├── 01_cost_optimizer.py     # 成本优化策略
├── 02_reliability.py        # 可靠性工程
├── 03_cost_dashboard.py     # 成本仪表盘（Reasonix 路线）
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

---

## 成本仪表盘（03）— 借鉴自 DeepSeek-Reasonix 桌面端

> **为什么加这个任务**：在 `01_cost_optimizer.py` 里你会发现——**优化成本的前提是"看见"成本**。光打印 `print(usage)` 没法看清趋势，Excel 统计又太慢。
>
> Reasonix 桌面端最亮眼的功能就是**实时成本仪表盘**：累计 token、缓存命中率、按工具分摊的费用、调用延迟，一目了然。
>
> 我们用 Python 的 `rich` 库做终端版（不依赖前端），把 phase 2-3 收集的指标可视化。

### 仪表盘布局

```
┌────────────────────────────────────────────────────────┐
│  AI Agent 成本仪表盘           2026-12-15 14:30:22     │
├────────────────────────────────────────────────────────┤
│  累计统计                                                │
│  ─────────────────────────────────────────              │
│  总调用次数:        247 次                              │
│  输入 token:        1,234,567  ($ 0.12)                 │
│  输出 token:        456,789    ($ 0.91)                 │
│  缓存命中:          142,890 次  (命中率 57.8%)           │
│  缓存节省:          $ 1.08                             │
│  实际花费:          $ 1.03                             │
├────────────────────────────────────────────────────────┤
│  按工具分摊                                              │
│  ─────────────────────────────────────────              │
│  read_file     ████████████  $ 0.42  (40.8%)           │
│  search_code   ███████       $ 0.25  (24.3%)           │
│  edit_file     ████          $ 0.15  (14.6%)           │
│  shell         ███           $ 0.12  (11.7%)           │
│  write_file    ██            $ 0.09  ( 8.6%)           │
├────────────────────────────────────────────────────────┤
│  最近 10 次调用                                          │
│  ─────────────────────────────────────────              │
│  14:30:15  read_file     in= 1,234 out=  89  $ 0.0003  │
│  14:30:18  search_code   in=   567 out= 234  $ 0.0002  │
│  14:30:22  edit_file     in= 2,345 out= 178  $ 0.0007  │
│  ...                                                    │
└────────────────────────────────────────────────────────┘
```

### 核心实现

```python
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from datetime import datetime
from collections import defaultdict
import time

class CostTracker:
    def __init__(self):
        self.calls = []  # 所有调用记录
        self.total_input = 0
        self.total_output = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.by_tool = defaultdict(lambda: {"input": 0, "output": 0, "count": 0, "cost": 0})
        # 价格表
        self.prices = {
            "input": 0.14 / 1_000_000,   # DeepSeek-V3 输入
            "output": 0.28 / 1_000_000,  # DeepSeek-V3 输出
            "cached": 0.014 / 1_000_000, # 缓存命中
        }

    def record(self, tool_name: str, input_tokens: int, output_tokens: int, cached: bool = False):
        cost = (input_tokens * (self.prices["cached"] if cached else self.prices["input"])
                + output_tokens * self.prices["output"])
        call = {
            "ts": datetime.now(),
            "tool": tool_name,
            "input": input_tokens,
            "output": output_tokens,
            "cached": cached,
            "cost": cost
        }
        self.calls.append(call)
        self.total_input += input_tokens
        self.total_output += output_tokens
        if cached: self.cache_hits += 1
        else: self.cache_misses += 1
        self.by_tool[tool_name]["input"] += input_tokens
        self.by_tool[tool_name]["output"] += output_tokens
        self.by_tool[tool_name]["count"] += 1
        self.by_tool[tool_name]["cost"] += cost

    def render(self) -> Layout:
        """渲染终端仪表盘"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="summary", size=8),
            Layout(name="tools", size=10),
            Layout(name="recent", size=12)
        )
        # ... 填充各区域
        return layout


def dashboard_loop(tracker: CostTracker):
    """实时刷新仪表盘"""
    console = Console()
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            live.update(tracker.render())
            time.sleep(1)
```

### 集成到 Agent

```python
# 在 utils/AiClient.py 中间件改造
class TrackedAiClient:
    def __init__(self, tracker: CostTracker):
        self.client = OpenAI(...)
        self.tracker = tracker

    def chat(self, **kwargs):
        response = self.client.chat.completions.create(**kwargs)
        usage = response.usage
        cached = getattr(usage, "cached_tokens", 0) > 0
        tool_name = kwargs.get("tools", [{}])[0].get("function", {}).get("name", "chat")
        self.tracker.record(
            tool_name=tool_name,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            cached=cached
        )
        return response
```

### 学习目标

- [ ] 实现 `CostTracker` 类
- [ ] 用 `rich` 库渲染实时仪表盘
- [ ] 改造 `utils/AiClient.py`，所有调用走追踪
- [ ] 在 `01_cost_optimizer.py` 里加上"运行仪表盘 5 分钟看趋势"
- [ ] 输出报告：哪个工具最贵、什么时段调用最多、缓存命中率从多少优化到多少
- [ ] 可选：用 `streamlit` / `gradio` 做 Web 版仪表盘

### 经验出处

参考项目：[DeepSeek-Reasonix 桌面端](https://github.com/esengine/DeepSeek-Reasonix) — Tauri 实现的实时成本面板。  
**核心思想**：**成本优化从"看见"开始**。一个 5 分钟的仪表盘能让你发现"原来 search_code 占了 40% 费用"——这种洞察光看日志是看不出来的。

---

## 完整阶段总结

| 周 | 重点 | 借鉴来源 |
|---|---|---|
| 19-20 | 缓存、Prompt 优化、模型路由 | Anthropic / DeepSeek 官方 |
| 21-22 | Telegram Bot 多用户 | python-telegram-bot |
| 23-24 | 知识库 RAG + Web UI | Streamlit / Gradio |
| 25-26 | 可靠性工程 | - |
| **贯穿全程** | **成本仪表盘（新增）** | **Reasonix 桌面端** |

**3 个里程碑项目**（贯穿 phase 1-4）：
1. `file_agent.py` —— 体现 ReAct 循环 + 工具自愈
2. `code_qa_agent.py` —— 体现 RAG + 混合搜索 + Append-Only 缓存
3. `telegram_bot` / 知识库 Agent —— 体现 Plan 模式 + 审批门 + Checkpoint + 成本可控
