# phase2/03_rag_qa.py
#
# 功能：RAG 问答 —— 检索相关内容，让 LLM 基于这些内容回答问题
# 运行：python phase2/03_rag_qa.py
# 学习要点：
#   - RAG 的完整流程：问题 → 检索 → 拼接 Prompt → LLM 回答
#   - 如何把检索结果拼入 system prompt
#   - "基于以下内容回答"的提示词技巧

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
# 检索函数（简化版，用硬编码数据演示 RAG 流程）
# ============================================================

# 模拟的知识库（实际项目中应该从向量数据库检索）
KNOWLEDGE_BASE = {
    "python": "Python 是一种解释型、高级编程语言。支持多种编程范式，包括面向对象和函数式编程。Python 的包管理器 pip 可以方便地安装第三方库。",
    "rust": "Rust 是一种系统编程语言，注重安全性和性能。Rust 的所有权系统可以在编译期防止内存错误。",
    "java": "Java 是一种广泛使用的面向对象编程语言，具有跨平台特性。Spring Boot 是 Java 最常用的 Web 框架。",
}


def retrieve(query: str, top_k: int = 2) -> list[str]:
    """
    模拟检索：根据关键词从知识库中返回相关内容

    在实际项目中，这里应该调用向量数据库的 search 函数
    """
    results = []
    query_lower = query.lower()
    for key, content in KNOWLEDGE_BASE.items():
        if key in query_lower or any(word in query_lower for word in key.split()):
            results.append(content)

    # 如果没找到相关内容，返回所有知识（实际项目中应该返回空或最相关的）
    if not results:
        results = list(KNOWLEDGE_BASE.values())[:top_k]

    return results[:top_k]


# ============================================================
# RAG 问答核心函数
# ============================================================

def rag_answer(question: str):
    """
    RAG 问答：检索 + 生成

    流程：
    1. 从知识库检索与问题相关的内容
    2. 把检索结果拼入 system prompt
    3. 让 LLM 基于这些内容回答问题
    """
    # 1. 检索
    context_chunks = retrieve(question)
    context = "\n\n".join(context_chunks)

    print(f"\n检索到的内容：\n{context}")
    print("-" * 40)

    # 2. 拼接 Prompt
    system_prompt = f"""你是一个知识库问答助手，请用中文回答。
请基于以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请诚实说明"根据现有资料无法回答这个问题"。

参考资料：
{context}"""

    # 3. 调用 LLM
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("RAG 问答演示")
    print("（使用硬编码知识库演示，后续替换为向量数据库）")
    print("输入 'quit' 退出")
    print("=" * 50)

    while True:
        question = input("\n你的问题：").strip()
        if question.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        if not question:
            continue

        answer = rag_answer(question)
        print(f"\n回答：{answer}")


if __name__ == "__main__":
    main()
