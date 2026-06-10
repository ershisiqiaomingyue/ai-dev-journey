# phase3/graphs/coder.py
#
# 编码型 Agent 图 —— 擅长代码生成和修改

# TODO: 实现编码型 Agent 的 LangGraph 图定义
#
# 功能设计：
# 1. 接收编码任务
# 2. 分析现有代码（读取、理解）
# 3. 生成/修改代码
# 4. 运行测试验证
# 5. 返回结果
#
# 可复用的节点：
# - analyze_node: 代码分析
# - generate_node: 代码生成
# - test_node: 运行测试
# - fix_node: 根据测试错误修复代码
