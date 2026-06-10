# phase3/03_multi_step.py
#
# 功能：多步任务编排 —— Plan-and-Execute 模式
# 运行：python phase3/03_multi_step.py
# 学习要点：
#   - Plan-and-Execute：先让 LLM 制定计划，再逐步执行
#   - 多节点协作：Planner → Executor → Reviewer
#   - 循环与退出条件

# TODO: 安装依赖后实现
# from typing import TypedDict, Annotated, Literal
# from langgraph.graph import StateGraph, START, END
# from langchain_openai import ChatOpenAI
# import operator


# ============================================================
# 状态定义
# ============================================================

# class PlanState(TypedDict):
#     """计划-执行 Agent 的状态"""
#     task: str                               # 原始任务
#     plan: list[str]                         # 计划步骤列表
#     current_step: int                       # 当前执行到第几步
#     step_results: Annotated[list, operator.add]  # 每步的执行结果
#     final_result: str                       # 最终结果


# ============================================================
# 节点定义
# ============================================================

# def planner_node(state: PlanState) -> dict:
#     """规划节点：让 LLM 将任务分解为步骤"""
#     llm = ChatOpenAI(model=..., api_key=..., base_url=...)
#     response = llm.invoke(f"将以下任务分解为具体步骤（每步一个操作）：\n{state['task']}")
#     # 解析步骤（简化：按行分割）
#     steps = [line.strip() for line in response.content.split("\n") if line.strip()]
#     return {"plan": steps, "current_step": 0}
#
#
# def executor_node(state: PlanState) -> dict:
#     """执行节点：执行当前步骤"""
#     step = state["plan"][state["current_step"]]
#     # TODO: 调用工具执行
#     result = f"步骤 {state['current_step'] + 1} 执行结果"
#     return {
#         "step_results": [result],
#         "current_step": state["current_step"] + 1,
#     }
#
#
# def reviewer_node(state: PlanState) -> dict:
#     """审查节点：检查所有步骤的结果，生成最终报告"""
#     llm = ChatOpenAI(model=..., api_key=..., base_url=...)
#     summary = "\n".join(state["step_results"])
#     response = llm.invoke(f"基于以下执行结果，生成最终报告：\n{summary}")
#     return {"final_result": response.content}


# ============================================================
# 条件边
# ============================================================

# def should_continue(state: PlanState) -> Literal["executor", "reviewer"]:
#     """判断是否还有未执行的步骤"""
#     if state["current_step"] < len(state["plan"]):
#         return "executor"
#     return "reviewer"


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("Plan-and-Execute 多步任务编排")
    print("=" * 50)
    print("\n工作流程：")
    print("  1. Planner：将任务分解为步骤列表")
    print("  2. Executor：逐步执行每个步骤")
    print("  3. Reviewer：汇总结果，生成报告")
    print("\n图的拓扑结构：")
    print("  START → planner → executor ←─┐")
    print("                    ↓          │")
    print("                 reviewer ─────┘")
    print("                    ↓")
    print("                   END")
    print("\n示例任务：'查找项目中的 log 文件，统计 ERROR 次数，生成报告'")

    print("\n[待实现] 请先安装 langgraph: pip install langgraph langchain-openai")


if __name__ == "__main__":
    main()
