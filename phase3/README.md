# 第三阶段：Agent 框架与复杂任务（第11-18周）

## 目标

使用 LangGraph 构建能完成多步任务的 Agent，理解状态图、节点、边的概念。

## 脚本列表

| 文件 | 周次 | 学习要点 |
|------|------|---------|
| `01_simple_graph.py` | W11 | LangGraph 基础：StateGraph, Node, Edge |
| `02_react_graph.py` | W11 | 用 LangGraph 重写 ReAct Agent |
| `03_multi_step.py` | W12 | 多步任务编排：Plan-and-Execute 模式 |
| `04_multi_agent.py` | W13 | 多 Agent 协作：主管 + 子 Agent |
| `05_dev_assistant.py` | W14-16 | 综合项目：开发助手 Agent |

## 运行方式

```bash
# 1. 安装额外依赖
pip install langgraph langchain-openai langchain-core

# 2. 运行
python phase3/01_simple_graph.py
```

## 核心概念

- **StateGraph（状态图）**：定义 Agent 的状态和状态转换规则
- **Node（节点）**：图中的处理单元，每个节点执行一个操作
- **Edge（边）**：连接节点，定义控制流
- **Conditional Edge（条件边）**：根据状态决定下一步走哪个节点
- **Interrupt / Resume**：人工介入机制，暂停等待用户确认

## 目录结构

```
phase3/
├── README.md              # 本文件
├── 01_simple_graph.py     # LangGraph 入门
├── 02_react_graph.py      # 用 LangGraph 实现 ReAct
├── 03_multi_step.py       # Plan-and-Execute
├── 04_multi_agent.py      # 多 Agent 协作
├── 05_dev_assistant.py    # 开发助手
└── graphs/                # 可复用的图定义
    ├── __init__.py
    ├── researcher.py      # 研究型 Agent 图
    └── coder.py           # 编码型 Agent 图
```
