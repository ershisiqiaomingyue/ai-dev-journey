# 第二阶段：RAG 与检索（第5-10周）

## 目标

让 Agent 能读取代码项目，实现"基于知识的问答"（Retrieval-Augmented Generation）。

## 任务列表

- [ ] `01_embed_and_store.py` — 文本切块、向量化、存入向量数据库
- [ ] `02_retrieval_search.py` — 语义检索：给定问题，返回最相关的文本块
- [ ] `03_rag_qa.py` — RAG 问答：检索结果 + LLM 生成回答
- [ ] `04_code_qa_agent.py` — 综合项目：代码库问答 Agent

## 运行方式

```bash
# 1. 安装额外依赖
pip install chromadb tiktoken

# 2. 先运行向量化脚本（需要先准备数据）
python phase2/01_embed_and_store.py

# 3. 然后运行检索/问答脚本
python phase2/02_retrieval_search.py
python phase2/03_rag_qa.py
```

## 核心概念

- **RAG（检索增强生成）**：先从知识库中检索相关内容，再让 LLM 基于这些内容回答
- **Embedding（向量化）**：把文本转换为高维向量，相似文本的向量距离更近
- **Chunk（文本块）**：把长文档切成小段，便于精确检索
- **向量数据库**：存储和检索向量的专用数据库（本项目用 ChromaDB）

## 目录结构

```
phase2/
├── README.md              # 本文件
├── 01_embed_and_store.py  # 文本向量化 + 存储
├── 02_retrieval_search.py # 语义检索
├── 03_rag_qa.py           # RAG 问答
├── 04_code_qa_agent.py    # 代码问答 Agent
├── ingest/                # 数据处理工具
│   ├── __init__.py
│   ├── code_parser.py     # 代码文件解析
│   └── chunker.py         # 文本分块策略
└── data/                  # 向量数据库存储（git ignored）
    └── .gitkeep
```
