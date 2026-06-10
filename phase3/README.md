# 第三阶段：Agent 框架与复杂任务（第11-18周）

## 目标

使用 LangGraph 构建能完成多步任务的 Agent，理解状态图、节点、边的概念。  
**关键认知**：框架解决的是"复杂任务的流程控制"，本阶段会学"Plan 模式"、"审批门"、"Checkpoint 回滚"三个生产级特性。

## 任务列表

- [ ] `01_simple_graph.py` — LangGraph 基础：StateGraph, Node, Edge
- [ ] `02_react_graph.py` — 用 LangGraph 重写 ReAct Agent
- [ ] `03_multi_step.py` — 多步任务编排：Plan-and-Execute 模式
- [ ] `04_multi_agent.py` — 多 Agent 协作：主管 + 子 Agent
- [ ] `05_dev_assistant.py` — 综合项目：开发助手 Agent
- [ ] `06_plan_mode.py` — **【借鉴 Claude Code】** Plan 模式：执行前先出计划，用户审批后再动手
- [ ] `07_checkpoint.py` — **【借鉴 Reasonix】** 自动快照：每次修改前保存文件快照，出问题可回滚

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
- **Plan-and-Execute**：先规划任务步骤，再逐步执行的模式
- **Checkpoint（检查点）**：保存中间状态，用于回滚或恢复

## 目录结构

```
phase3/
├── README.md              # 本文件
├── 01_simple_graph.py     # LangGraph 入门
├── 02_react_graph.py      # 用 LangGraph 实现 ReAct
├── 03_multi_step.py       # Plan-and-Execute
├── 04_multi_agent.py      # 多 Agent 协作
├── 05_dev_assistant.py    # 开发助手
├── 06_plan_mode.py        # Plan 模式 + 审批门（Claude Code 路线）
├── 07_checkpoint.py       # 自动快照与回滚（Reasonix 路线）
└── graphs/                # 可复用的图定义
    ├── __init__.py
    ├── researcher.py      # 研究型 Agent 图
    └── coder.py           # 编码型 Agent 图
```

---

## Plan 模式 + 审批门（06）— 借鉴自 Claude Code

> **为什么加这个任务**：在 `05_dev_assistant.py` 里你会遇到一个实际问题——**Agent 改代码太"冲动"**。用户说"帮我优化 utils.py"，它可能直接改了 20 处还没法撤销。
>
> Claude Code 的解法是 **Plan 模式**：执行前先让 Agent 输出一份"我要做什么"的计划，**用户审批后才动手**。这是生产级 Agent 的标配。

### 工作流

```
用户: "帮我优化 utils.py 的性能"
        ↓
[Planner 节点]
  Agent 输出计划:
    1. 读取 utils.py 全文
    2. 用 cProfile 找热点函数
    3. 优化热点函数（3 处）
    4. 运行 pytest 验证
    5. 输出 diff 给用户
        ↓
[审批门 - Interrupt]
  等待用户输入: y/n/edit
    y   → 继续执行
    n   → 终止
    edit → 用户修改计划后再继续
        ↓
[Executor 节点]
  按计划逐步执行（每步可调用工具）
        ↓
[Verifier 节点]
  验证结果（运行测试 / 编译）
        ↓
[Reporter 节点]
  输出 diff 和报告
```

### LangGraph 实现骨架

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Literal

class AgentState(TypedDict):
    user_request: str
    plan: list[str]
    plan_approved: bool
    current_step: int
    execution_results: list
    final_report: str

def planner_node(state: AgentState):
    """让 LLM 制定计划"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个任务规划助手。把用户需求分解为可执行的步骤列表。"},
            {"role": "user", "content": f"需求：{state['user_request']}\n\n输出 JSON 格式：{{\"steps\": [\"步骤1\", \"步骤2\", ...]}}"},
        ]
    )
    plan = json.loads(response.choices[0].message.content)["steps"]
    return {"plan": plan, "current_step": 0}

def approval_gate(state: AgentState) -> Literal["execute", "end"]:
    """审批门 - 等待用户确认"""
    print("\n=== Agent 计划 ===")
    for i, step in enumerate(state["plan"], 1):
        print(f"  {i}. {step}")
    print("==================")
    user_input = input("\n是否执行？(y/n/edit): ").strip().lower()
    if user_input == "y":
        return "execute"
    elif user_input == "edit":
        # 用户修改计划
        new_plan = input("修改后的计划（每行一步）: ").strip().split("\n")
        state["plan"] = new_plan
        return "execute"
    else:
        return "end"

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("reporter", reporter_node)
workflow.add_edge("planner", "approval_gate")
workflow.add_conditional_edges("approval_gate", approval_gate, {"execute": "executor", "end": END})
workflow.add_edge("executor", "reporter")
workflow.add_edge("reporter", END)
workflow.set_entry_point("planner")
```

### 学习目标

- [ ] 实现 `planner_node` —— LLM 输出结构化计划
- [ ] 实现 `approval_gate` —— Interrupt 机制等待用户输入
- [ ] 在 `05_dev_assistant.py` 上改造，所有修改前必经审批
- [ ] 测试场景：用户审批 / 拒绝 / 修改计划 3 种情况
- [ ] 思考：什么类型的任务适合 Plan 模式？什么类型不需要？

### 经验出处

参考项目：[Claude Code](https://claude.com/product/claude-code) / [Cursor](https://cursor.sh/)  
**核心思想**：**让用户保持控制权**。Agent 再强也不能"擅自行动"，涉及文件修改 / 命令执行的任务必须有审批门。这是 B 端产品的合规要求。

---

## Checkpoint 自动快照（07）— 借鉴自 DeepSeek-Reasonix

> **为什么加这个任务**：在 `05_dev_assistant.py` 里还有个痛点——**Agent 改完代码出错了，怎么回滚？** 手动 `git checkout` 太重，全靠"希望它改对"太脆。
>
> Reasonix 的解法是**自动 Checkpoint**：每次修改文件前，先把原文件存到 `.checkpoint/<时间戳>/` 下。出问题一键回滚。
>
> 我们用 `git stash` 或文件快照实现这个机制。

### 工作流

```
Agent 决定修改 utils.py
        ↓
[Checkpoint 节点]
  1. 创建 .checkpoint/2026-09-15_143022/ 目录
  2. 复制 utils.py → .checkpoint/2026-09-15_143022/utils.py.bak
  3. 记录元数据:
     {
       "timestamp": "2026-09-15_143022",
       "files": ["utils.py"],
       "agent_reason": "添加异常处理",
       "session_id": "..."
     }
        ↓
[执行修改]
  修改 utils.py
        ↓
[验证]
  跑 pytest
        ↓
  ├─ 通过 → 清理旧 checkpoint（保留最近 5 个）
  └─ 失败 → 用户选择"回滚到上一个 checkpoint"
```

### 核心代码骨架

```python
import shutil
from pathlib import Path
from datetime import datetime
import json

class CheckpointManager:
    def __init__(self, project_root: str, keep_last: int = 5):
        self.root = Path(project_root)
        self.checkpoint_dir = self.root / ".checkpoint"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.keep_last = keep_last
        self.history = []

    def create(self, files: list[str], reason: str) -> str:
        """在修改前创建快照"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = self.checkpoint_dir / ts
        snapshot_dir.mkdir()

        for file_path in files:
            src = self.root / file_path
            if src.exists():
                dst = snapshot_dir / Path(file_path).name
                shutil.copy2(src, dst)

        meta = {
            "timestamp": ts,
            "files": files,
            "reason": reason,
            "snapshot_dir": str(snapshot_dir)
        }
        (snapshot_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        self.history.append(meta)
        return ts

    def rollback(self, timestamp: str = None):
        """回滚到指定 checkpoint（默认上一个）"""
        if timestamp is None:
            timestamp = self.history[-1]["timestamp"]
        meta = next(m for m in self.history if m["timestamp"] == timestamp)
        for file_path in meta["files"]:
            src = Path(meta["snapshot_dir"]) / Path(file_path).name
            dst = self.root / file_path
            if src.exists():
                shutil.copy2(src, dst)
        return meta

    def cleanup(self):
        """只保留最近 N 个 checkpoint"""
        all_snapshots = sorted(self.checkpoint_dir.iterdir(), reverse=True)
        for old in all_snapshots[self.keep_last:]:
            shutil.rmtree(old)
```

### 学习目标

- [ ] 实现 `CheckpointManager` 类
- [ ] 集成到 `05_dev_assistant.py` —— 修改前自动 `create()`
- [ ] 实现"一键回滚"命令
- [ ] 测试场景：故意让 Agent 改坏代码，然后回滚
- [ ] 对比 git stash：checkpoint 比 git 轻量，不污染提交历史

### 经验出处

参考项目：[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) — 它的自动检查点机制是"Agent 操作可逆"的关键。  
**核心思想**：**让 Agent 的修改永远可逆**。生产环境里"操作可回滚"比"操作成功"更重要——前者是底线，后者是目标。
