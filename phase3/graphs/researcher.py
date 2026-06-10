# phase3/graphs/researcher.py
#
# 研究型 Agent 图 —— 擅长信息收集和总结

# TODO: 实现研究型 Agent 的 LangGraph 图定义
#
# 功能设计：
# 1. 接收研究问题
# 2. 分解为子问题
# 3. 对每个子问题进行搜索/检索
# 4. 汇总信息，生成研究报告
#
# 可复用的节点：
# - decompose_node: 问题分解
# - search_node: 信息检索（可接入 RAG 或 Web 搜索）
# - summarize_node: 信息汇总
