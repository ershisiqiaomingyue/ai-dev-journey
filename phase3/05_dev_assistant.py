# phase3/05_dev_assistant.py
#
# 功能：开发助手 Agent —— 能够修改代码的综合项目（第三阶段综合项目）
# 运行：python phase3/05_dev_assistant.py
# 学习要点：
#   - 将前面学到的所有技巧整合：ReAct + 多步 + 工具调用
#   - 人工介入（Human-in-the-loop）：修改文件前需要用户确认
#   - 回滚机制：修改出错时可以恢复
#   - 安全性：备份原文件再修改

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# --- 加载配置 ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


# ============================================================
# 开发助手的功能设计
# ============================================================

# 工具列表（TODO: 实现）
#
# 1. read_file(path)
#    - 读取文件内容
#
# 2. write_file(path, content)
#    - 写入文件（自动备份原文件到 .backup/）
#
# 3. run_command(cmd)
#    - 执行 Shell 命令（有权限限制）
#    - 允许：git status, pytest, python xxx.py
#    - 禁止：rm -rf, sudo, etc.
#
# 4. get_diff(path)
#    - 显示文件修改前后的 diff
#
# 5. rollback(path)
#    - 回滚文件到修改前


# ============================================================
# 人工介入机制
# ============================================================

# TODO: 使用 LangGraph 的 interrupt / resume
#
# 1. Agent 决定要修改文件
# 2. 显示修改方案（diff）
# 3. 等待用户确认（Y/n）
# 4. 用户确认后执行修改
# 5. 运行测试验证
# 6. 测试失败则自动回滚


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("开发助手 Agent（第三阶段综合项目）")
    print("=" * 50)
    print("\n功能：")
    print("  - 读取代码文件")
    print("  - 根据需求修改代码")
    print("  - 显示修改的 diff")
    print("  - 运行测试验证")
    print("  - 修改前需要用户确认")
    print("  - 出错时可以回滚")
    print("\n示例任务：")
    print("  - '为 utils.py 的 parse_config 函数添加异常处理'")
    print("  - '运行测试，如果失败则尝试修复'")
    print("  - '重构这个函数，提取重复代码'")

    print("\n[待实现] 这是第三阶段的综合项目")
    print("请先完成 01-04 的学习，再来实现这个脚本。")


if __name__ == "__main__":
    main()
