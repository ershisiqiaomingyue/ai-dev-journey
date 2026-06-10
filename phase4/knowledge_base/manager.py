# phase4/knowledge_base/manager.py
#
# 功能：知识库管理 —— 文档的增删改查
# 学习要点：
#   - 知识库的生命周期管理
#   - 文档更新策略（增量更新 vs 全量重建）
#   - 元数据管理（来源、时间、分类）

from pathlib import Path
from datetime import datetime


class KnowledgeBase:
    """知识库管理器"""

    def __init__(self, storage_path: str = "./phase4/knowledge_base/data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add_document(self, title: str, content: str, category: str = "general"):
        """
        添加文档到知识库

        TODO: 实现以下步骤
        1. 生成文档 ID（可以用 hash 或 UUID）
        2. 切块 + 向量化
        3. 存入向量数据库
        4. 记录元数据（标题、分类、添加时间）
        """
        doc_id = f"{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"  [添加] {doc_id}: {title}")
        # TODO: 实际存入 ChromaDB
        return doc_id

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        搜索知识库

        TODO: 调用向量数据库的 query 方法
        """
        print(f"  [搜索] '{query}'")
        # TODO: 实际从 ChromaDB 检索
        return []

    def list_documents(self) -> list[dict]:
        """列出所有文档"""
        # TODO: 从向量数据库获取所有文档元数据
        return []

    def delete_document(self, doc_id: str):
        """删除文档"""
        # TODO: 从向量数据库中删除
        print(f"  [删除] {doc_id}")

    def update_document(self, doc_id: str, content: str):
        """
        更新文档

        策略：删除旧版本，添加新版本（简化实现）
        """
        self.delete_document(doc_id)
        # TODO: 重新添加
        print(f"  [更新] {doc_id}")


# ============================================================
# 使用示例
# ============================================================

def main():
    print("=" * 50)
    print("知识库管理演示")
    print("=" * 50)

    kb = KnowledgeBase()

    # 添加示例文档
    print("\n添加文档：")
    kb.add_document("Android Framework 学习笔记", "Activity 生命周期...")
    kb.add_document("Python 异步编程笔记", "asyncio 基础...")

    # 搜索示例
    print("\n搜索：")
    results = kb.search("Activity 生命周期")
    print(f"  找到 {len(results)} 个结果")

    print("\n[待实现] 接入向量数据库后完善功能")


if __name__ == "__main__":
    main()
