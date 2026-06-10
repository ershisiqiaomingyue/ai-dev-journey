# phase2/01_embed_and_store.py
#
# 功能：文本向量化 + 存入向量数据库
# 运行：python phase2/01_embed_and_store.py
# 学习要点：
#   - Embedding 的原理：文本 → 高维向量
#   - ChromaDB 的基本用法：创建集合、添加文档、查询
#   - 文本分块策略：chunk_size 和 overlap 的影响

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# --- 加载配置 ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# TODO: 安装依赖后取消注释
# import chromadb
# from chromadb.utils import embedding_functions


# ============================================================
# 示例文本（后续会替换为真实文件内容）
# ============================================================

sample_texts = [
    "Python 是一种解释型、高级编程语言，由 Guido van Rossum 于 1991 年发布。",
    "Python 支持多种编程范式，包括面向对象、函数式和过程式编程。",
    "Python 的包管理器 pip 可以方便地安装第三方库。",
    "Rust 是一种系统编程语言，注重安全性、并发性和性能。",
    "Rust 的所有权系统是其最独特的特性，可以在编译期防止内存错误。",
    "Java 是一种广泛使用的面向对象编程语言，具有'一次编写，到处运行'的特性。",
    "JavaScript 最初是为网页添加交互性而设计的，现在已成为全栈开发语言。",
]


# ============================================================
# 文本分块函数
# ============================================================

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    将长文本切分为多个块

    参数:
        text: 原始文本
        chunk_size: 每块的最大字符数
        overlap: 相邻块之间的重叠字符数

    返回:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 50)
    print("文本向量化 + 存储演示")
    print("=" * 50)

    # TODO: 实现以下步骤
    #
    # 1. 初始化 ChromaDB 客户端
    #    client = chromadb.Client()  # 内存模式（演示用）
    #    # client = chromadb.PersistentClient(path="./phase2/data")  # 持久化模式
    #
    # 2. 创建或获取集合
    #    collection = client.get_or_create_collection(
    #        name="demo",
    #        embedding_function=embedding_functions.DefaultEmbeddingFunction()
    #    )
    #
    # 3. 添加文本到集合（ChromaDB 会自动向量化）
    #    for i, text in enumerate(sample_texts):
    #        collection.add(
    #            documents=[text],
    #            ids=[f"doc_{i}"],
    #            metadatas=[{"source": "sample", "index": i}],
    #        )
    #
    # 4. 验证存储结果
    #    print(f"集合中有 {collection.count()} 个文档")
    #
    # 5. 测试分块函数
    #    long_text = "这是一段很长的文本..." * 100
    #    chunks = chunk_text(long_text, chunk_size=100, overlap=20)
    #    print(f"长文本被切分为 {len(chunks)} 块")

    print("\n[待实现] 请先安装 chromadb: pip install chromadb")
    print("然后取消注释相关代码，运行完整流程。")

    # 演示分块函数
    long_text = "人工智能正在改变我们的生活方式。" * 20
    chunks = chunk_text(long_text, chunk_size=50, overlap=10)
    print(f"\n分块演示：长文本 ({len(long_text)} 字符) 被切分为 {len(chunks)} 块")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  块 {i+1}: {chunk[:40]}...")


if __name__ == "__main__":
    main()
