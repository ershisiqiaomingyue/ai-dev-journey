# phase3/02_react_graph.py
#
# 功能：用 LangGraph 实现 ReAct Agent（对比 phase1 的手写版本）
# 运行：python phase3/02_react_graph.py
# 学习要点：
#   - 条件边（Conditional Edge）：根据状态决定下一步
#   - 与 phase1/04_react_agent.py 的对比：LangGraph 的优势
#   - 工具调用在 LangGraph 中的实现方式

# TODO: 安装依赖后取消注释
# from typing import TypedDict, Annotated, Literal
# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode
# from langchain_openai import ChatOpenAI
# import operator
# import os
# from pathlib import Path
# from dotenv import load_dotenv


# ============================================================
# 状态定义
# ============================================================

# TODO: 取消注释
#
# class AgentState(TypedDict):
#     """ReAct Agent 的状态"""
#     messages: Annotated[list, operator.add]  # 对话历史


# ============================================================
# 工具定义（可以复用 phase1 的工具）
# ============================================================

# from langchain_core.tools import tool
#
# @tool
# def get_current_time() -> str:
#     """获取当前的日期和时间"""
#     from datetime import datetime
#     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
# @tool
# def calculate(expression: str) -> str:
#     """计算数学表达式"""
#     try:
#         result = eval(expression)
#         return str(result)
#     except Exception as e:
#         return f"计算错误：{e}"
#
# tools = [get_current_time, calculate]


# ============================================================
# 图构建
# ============================================================

# def build_react_graph():
#     """构建 ReAct 状态图"""
#
#     # 初始化 LLM（绑定工具）
#     env_path = Path(__file__).resolve().parent.parent / ".env"
#     load_dotenv(env_path)
#
#     llm = ChatOpenAI(
#         model=os.getenv("LLM_MODEL", "deepseek-v4-flash"),
#         api_key=os.getenv("LLM_API_KEY"),
#         base_url=os.getenv("LLM_BASE_URL"),
#     ).bind_tools(tools)
#
#     def call_model(state: AgentState) -> dict:
#         """调用 LLM"""
#         response = llm.invoke(state["messages"])
#         return {"messages": [response]}
#
#     def should_continue(state: AgentState) -> Literal["tools", END]:
#         """判断是否需要继续调用工具"""
#         last_message = state["messages"][-1]
#         if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#             return "tools"
#         return END
#
#     # 构建图
#     graph = StateGraph(AgentState)
#
#     # 添加节点
#     graph.add_node("agent", call_model)
#     graph.add_node("tools", ToolNode(tools))
#
#     # 添加边
#     graph.add_edge(START, "agent")
#     graph.add_conditional_edges("agent", should_continue)  # 条件边！
#     graph.add_edge("tools", "agent")  # 工具执行后回到 agent
#
#     return graph.compile()


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("用 LangGraph 实现 ReAct Agent")
    print("=" * 50)
    print("\n与 phase1/04_react_agent.py 的对比：")
    print("  phase1：手写 while 循环，手动判断是否调用工具")
    print("  phase3：LangGraph 用条件边自动处理循环")
    print("\n图的拓扑结构：")
    print("  START → agent ←→ tools")
    print("              ↓")
    print("             END")

    # TODO: 安装依赖后取消注释
    #
    # app = build_react_graph()
    #
    # from langchain_core.messages import HumanMessage
    # result = app.invoke({
    #     "messages": [HumanMessage(content="现在几点？然后帮我算 123 * 456")]
    # })
    #
    # print(f"\n最终回复：{result['messages'][-1].content}")

    print("\n[待实现] 请先安装 langgraph: pip install langgraph langchain-openai")


if __name__ == "__main__":
    main()
