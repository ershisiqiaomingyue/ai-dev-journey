# phase2/02_retrieval_search.py
#
# 功能：语义检索 —— 给定问题，从向量库中找到最相关的文本块
# 运行：python phase2/02_retrieval_search.py
# 学习要点：
#   - 向量相似度搜索的原理（余弦相似度）
#   - top_k 参数：返回多少个最相关的结果
#   - 如何评估检索质量

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


def search(query: str, top_k: int = 3):
    """
    从向量库中检索与 query 最相关的文本

    参数:
        query: 用户问题
        top_k: 返回多少个结果

    返回:
        检索结果列表，每个结果包含文本、距离、元数据
    """
    # TODO: 实现检索逻辑
    #
    # client = chromadb.PersistentClient(path="./phase2/data")
    # collection = client.get_collection(
    #     name="demo",
    #     embedding_function=embedding_functions.DefaultEmbeddingFunction()
    # )
    #
    # results = collection.query(
    #     query_texts=[query],
    #     n_results=top_k,
    # )
    #
    # return results

    print("[待实现] 请先运行 01_embed_and_store.py 创建向量库")
    return None


def main():
    print("=" * 50)
    print("语义检索演示")
    print("=" * 50)

    # 示例查询
    queries = [
        "Python 有什么特点？",
        "Rust 和内存安全有什么关系？",
        "哪种语言适合 Web 开发？",
    ]

    for query in queries:
        print(f"\n问题：{query}")
        results = search(query, top_k=2)
        if results:
            for i, doc in enumerate(results.get("documents", [[]])[0]):
                distance = results["distances"][0][i]
                print(f"  结果 {i+1} (距离={distance:.4f}): {doc}")


if __name__ == "__main__":
    main()
