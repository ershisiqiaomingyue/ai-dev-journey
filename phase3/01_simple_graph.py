# phase3/01_simple_graph.py
#
# 功能：LangGraph 入门 —— 用最简单的例子理解状态图
# 运行：python phase3/01_simple_graph.py
# 学习要点：
#   - StateGraph 的定义方式
#   - Node 是普通的 Python 函数
#   - Edge 连接节点，定义执行顺序
#   - 状态（State）在节点间传递和更新

# TODO: 安装依赖后取消注释
# from typing import TypedDict, Annotated
# from langgraph.graph import StateGraph, START, END
# import operator


# ============================================================
# 第一步：定义状态（State）
# ============================================================

# TODO: 取消注释并运行
#
# class AgentState(TypedDict):
#     """Agent 的状态定义"""
#     input: str                              # 用户输入
#     current_step: str                       # 当前步骤
#     result: str                             # 最终结果
#     history: Annotated[list, operator.add]  # 历史记录（自动追加）


# ============================================================
# 第二步：定义节点（Node）—— 每个节点是一个 Python 函数
# ============================================================

# def think_node(state: AgentState) -> dict:
#     """思考节点：分析用户输入"""
#     print("[思考节点] 分析输入...")
#     return {
#         "current_step": "thinking",
#         "history": [f"收到输入：{state['input']}"],
#     }
#
#
# def act_node(state: AgentState) -> dict:
#     """行动节点：执行操作"""
#     print("[行动节点] 执行操作...")
#     # 这里可以调用工具
#     result = f"对 '{state['input']}' 的处理结果"
#     return {
#         "current_step": "acting",
#         "result": result,
#         "history": [f"执行结果：{result}"],
#     }
#
#
# def respond_node(state: AgentState) -> dict:
#     """回复节点：生成最终回答"""
#     print("[回复节点] 生成回答...")
#     return {
#         "current_step": "responding",
#         "history": ["生成最终回复"],
#     }


# ============================================================
# 第三步：构建图
# ============================================================

# def build_graph():
#     """构建并编译状态图"""
#     # 创建图
#     graph = StateGraph(AgentState)
#
#     # 添加节点
#     graph.add_node("think", think_node)
#     graph.add_node("act", act_node)
#     graph.add_node("respond", respond_node)
#
#     # 添加边（定义执行顺序）
#     graph.add_edge(START, "think")      # 入口 → 思考
#     graph.add_edge("think", "act")      # 思考 → 行动
#     graph.add_edge("act", "respond")    # 行动 → 回复
#     graph.add_edge("respond", END)      # 回复 → 结束
#
#     # 编译图
#     return graph.compile()


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("LangGraph 入门演示")
    print("=" * 50)

    # TODO: 安装 langgraph 后取消注释
    #
    # app = build_graph()
    #
    # # 运行图
    # result = app.invoke({
    #     "input": "帮我查一下今天的天气",
    #     "current_step": "",
    #     "result": "",
    #     "history": [],
    # })
    #
    # print(f"\n最终结果：{result['result']}")
    # print(f"执行历史：{result['history']}")

    print("\n[待实现] 请先安装 langgraph: pip install langgraph")
    print("然后取消注释相关代码，运行完整流程。")
    print("\n这个例子展示了一个最简单的线性图：")
    print("  思考 → 行动 → 回复")
    print("后续会加入条件边，让图能够根据情况选择不同的路径。")


if __name__ == "__main__":
    main()
