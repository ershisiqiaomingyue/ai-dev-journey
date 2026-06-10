# phase2/04_code_qa_agent.py
#
# 功能：代码库问答 Agent —— 扫描项目代码，回答问题（第二阶段综合项目）
# 运行：python phase2/04_code_qa_agent.py
# 学习要点：
#   - 如何遍历和解析代码文件
#   - 代码感知的分块策略（按函数/类切分）
#   - 带元数据的检索（显示文件路径、行号）
#   - 对话记忆：支持追问

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# --- 加载配置 ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL", "deepseek-v4-flash")

if not api_key or api_key == "your-api-key-here":
    print("[错误] LLM_API_KEY 未配置，请编辑 .env 文件")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url=base_url)


# ============================================================
# 代码扫描（简化版）
# ============================================================

# 支持的文件扩展名
CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".kt", ".rs", ".go", ".cpp", ".c", ".h"}


def scan_project(project_path: str) -> list[dict]:
    """
    扫描项目目录，收集代码文件内容

    返回:
        [{"path": "相对路径", "content": "文件内容", "language": "语言"}]
    """
    project = Path(project_path)
    if not project.exists():
        print(f"[错误] 项目路径不存在：{project_path}")
        return []

    files = []
    for file_path in project.rglob("*"):
        if file_path.suffix in CODE_EXTENSIONS:
            # 跳过常见的非源码目录
            if any(skip in str(file_path) for skip in [".git", "node_modules", "__pycache__", ".venv", "target"]):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                files.append({
                    "path": str(file_path.relative_to(project)),
                    "content": content,
                    "language": file_path.suffix[1:],
                })
            except Exception as e:
                print(f"  [跳过] {file_path}: {e}")

    return files


# ============================================================
# TODO: 集成向量数据库
# ============================================================

def index_code_files(files: list[dict]):
    """
    将代码文件向量化并存入数据库

    TODO: 实现以下步骤
    1. 对每个文件进行智能分块（按函数/类，而非简单字符切割）
    2. 为每个块添加元数据（文件路径、起始行号）
    3. 存入 ChromaDB
    """
    print(f"\n[待实现] 索引 {len(files)} 个代码文件到向量数据库")
    for f in files[:5]:  # 只打印前5个
        lines = f["content"].count("\n") + 1
        print(f"  - {f['path']} ({f['language']}, {lines} 行)")
    if len(files) > 5:
        print(f"  ... 还有 {len(files) - 5} 个文件")


def search_code(query: str, top_k: int = 3) -> list[dict]:
    """
    从向量数据库中检索与问题相关的代码块

    TODO: 调用 ChromaDB 的 query 方法
    """
    # 模拟返回
    return [{"path": "example.py", "content": "# 模拟结果", "relevance": 0.95}]


# ============================================================
# RAG 问答
# ============================================================

def ask(question: str, conversation_history: list = None):
    """
    代码问答：检索代码 → 拼接上下文 → LLM 回答
    """
    if conversation_history is None:
        conversation_history = []

    # 检索相关代码
    results = search_code(question)
    context = "\n\n".join(
        f"文件: {r['path']}\n```\n{r['content']}\n```"
        for r in results
    )

    system_prompt = f"""你是一个代码问答助手，请用中文回答。
基于以下代码片段回答用户的问题。
回答时请引用具体的文件路径和代码行。

相关代码片段：
{context}"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("代码库问答 Agent")
    print("=" * 50)

    # TODO: 让用户输入要扫描的项目路径
    # project_path = input("请输入要分析的项目路径：").strip()
    project_path = "."  # 默认扫描当前项目

    print(f"\n正在扫描项目：{project_path}")
    files = scan_project(project_path)
    print(f"找到 {len(files)} 个代码文件")

    if files:
        index_code_files(files)

    print("\n" + "=" * 50)
    print("开始问答（输入 'quit' 退出）")
    print("试试问：'login 函数在哪个文件？' 或 '这个项目用了哪些框架？'")
    print("=" * 50)

    # 对话历史（支持追问）
    history = []

    while True:
        question = input("\n你：").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        if not question:
            continue

        answer = ask(question, history)
        print(f"\nAI：{answer}")

        # 保存到历史
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        # 限制历史长度
        if len(history) > 20:
            history = history[-20:]


if __name__ == "__main__":
    main()
