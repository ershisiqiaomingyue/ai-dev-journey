# phase4/portfolio/demo.py
#
# 功能：作品集演示 —— 汇总展示所有阶段的项目
# 运行：python phase4/portfolio/demo.py
# 用途：面试/接单时展示你的 AI Agent 开发能力

import sys
from pathlib import Path


# ============================================================
# 项目清单
# ============================================================

PROJECTS = [
    {
        "name": "文件系统助手",
        "phase": "Phase 1",
        "file": "phase1/05_file_assistant.py",
        "description": "一个能读写文件的 ReAct Agent，支持 list/read/write/delete 操作",
        "skills": ["Function Calling", "ReAct 循环", "安全边界"],
    },
    {
        "name": "代码问答 Agent",
        "phase": "Phase 2",
        "file": "phase2/04_code_qa_agent.py",
        "description": "基于 RAG 的代码库问答系统，能回答'某个函数在哪个文件'类问题",
        "skills": ["RAG", "向量数据库", "代码解析", "文本分块"],
    },
    {
        "name": "开发助手 Agent",
        "phase": "Phase 3",
        "file": "phase3/05_dev_assistant.py",
        "description": "使用 LangGraph 构建的多步 Agent，支持代码修改、测试、回滚",
        "skills": ["LangGraph", "状态图", "人工介入", "多步编排"],
    },
    {
        "name": "Telegram 代码助手 Bot",
        "phase": "Phase 4",
        "file": "phase4/telegram_bot/bot.py",
        "description": "接入 Telegram 的 AI 助手，支持多用户隔离和代码审查",
        "skills": ["Bot 开发", "多用户隔离", "异步处理", "产品化"],
    },
    {
        "name": "个人知识库 Agent",
        "phase": "Phase 4",
        "file": "phase4/knowledge_base/manager.py",
        "description": "垂直领域的知识库问答系统（如 Android Framework 笔记）",
        "skills": ["知识库管理", "成本优化", "垂直领域"],
    },
]


# ============================================================
# 演示函数
# ============================================================

def show_projects():
    """展示所有项目"""
    print("=" * 60)
    print("AI Agent 开发作品集")
    print("=" * 60)

    for i, project in enumerate(PROJECTS, 1):
        print(f"\n{i}. {project['name']} [{project['phase']}]")
        print(f"   文件：{project['file']}")
        print(f"   描述：{project['description']}")
        print(f"   技能：{', '.join(project['skills'])}")

    print(f"\n{'='*60}")
    print(f"共 {len(PROJECTS)} 个项目")


def run_project(index: int):
    """运行指定项目"""
    if index < 0 or index >= len(PROJECTS):
        print(f"无效的项目编号：{index + 1}")
        return

    project = PROJECTS[index]
    file_path = Path(__file__).resolve().parent.parent.parent / project["file"]

    if not file_path.exists():
        print(f"文件不存在：{project['file']}")
        return

    print(f"\n运行：{project['name']}")
    print(f"命令：python {project['file']}")
    print("-" * 40)

    import subprocess
    subprocess.run([sys.executable, str(file_path)])


# ============================================================
# 主程序
# ============================================================

def main():
    show_projects()

    print("\n操作：")
    print("  输入项目编号 (1-5) 运行演示")
    print("  输入 'quit' 退出")

    while True:
        choice = input("\n选择：").strip()
        if choice.lower() in ("quit", "exit", "q"):
            break
        try:
            idx = int(choice) - 1
            run_project(idx)
            show_projects()
        except ValueError:
            print("请输入有效的数字")


if __name__ == "__main__":
    main()
