# phase3/04_multi_agent.py
#
# 功能：多 Agent 协作 —— 主管 Agent 调度子 Agent
# 运行：python phase3/04_multi_agent.py
# 学习要点：
#   - 多 Agent 架构：Supervisor（主管） + Workers（工人）
#   - 如何让主管决定调用哪个子 Agent
#   - 子 Agent 之间如何传递信息

# TODO: 安装依赖后实现


# ============================================================
# Agent 角色设计
# ============================================================

# 主管 Agent：
#   - 接收用户需求
#   - 决定调用哪个子 Agent
#   - 汇总子 Agent 的结果
#
# Coder Agent：
#   - 负责写代码
#   - 工具：代码生成、代码修改
#
# Reviewer Agent：
#   - 负责审查代码
#   - 工具：代码分析、问题检测
#
# 工作流程：
#   用户需求 → 主管 → Coder（写代码）→ 主管 → Reviewer（审查）→ 主管 → 用户


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("多 Agent 协作演示")
    print("=" * 50)
    print("\nAgent 角色：")
    print("  - Supervisor（主管）：任务分配和结果汇总")
    print("  - Coder（编码员）：写代码")
    print("  - Reviewer（审查员）：审查代码质量")
    print("\n图的拓扑结构：")
    print("  START → supervisor → coder ──────┐")
    print("               ↑       ↓           │")
    print("               └── reviewer ───────┘")
    print("               ↓")
    print("              END")
    print("\n示例任务：'写一个快速排序算法，然后帮我审查代码质量'")

    print("\n[待实现] 请先安装 langgraph: pip install langgraph langchain-openai")


if __name__ == "__main__":
    main()
