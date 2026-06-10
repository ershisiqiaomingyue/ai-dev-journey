# 第二阶段：RAG 与检索（第5-10周）

## 目标

让 Agent 能读取代码项目，实现"基于知识的问答"（Retrieval-Augmented Generation）。  
**关键认知**：RAG 不是万能的，本阶段会学"什么场景用 RAG、什么场景用 ripgrep"的判断。

## 任务列表

- [ ] `01_embed_and_store.py` — 文本切块、向量化、存入向量数据库
- [ ] `02_retrieval_search.py` — 语义检索：给定问题，返回最相关的文本块
- [ ] `03_rag_qa.py` — RAG 问答：检索结果 + LLM 生成回答
- [ ] `04_code_qa_agent.py` — 综合项目：代码库问答 Agent
- [ ] `05_hybrid_search.py` — **【借鉴 Codex CLI】** 混合搜索：ripgrep（精确）+ RAG（语义）双路召回
- [ ] `06_append_only_cache.py` — **【借鉴 Reasonix】** Append-Only 日志：模拟 DeepSeek 前缀缓存的命中率优化

## 运行方式

```bash
# 1. 安装额外依赖
pip install chromadb tiktoken

# 2. 先运行向量化脚本（需要先准备数据）
python phase2/01_embed_and_store.py

# 3. 然后运行检索/问答脚本
python phase2/02_retrieval_search.py
python phase2/03_rag_qa.py

# 4. （可选）安装 ripgrep（混合搜索任务用）
# Windows: choco install ripgrep
# macOS:   brew install ripgrep
# Linux:   apt install ripgrep
```

## 核心概念

- **RAG（检索增强生成）**：先从知识库中检索相关内容，再让 LLM 基于这些内容回答
- **Embedding（向量化）**：把文本转换为高维向量，相似文本的向量距离更近
- **Chunk（文本块）**：把长文档切成小段，便于精确检索
- **向量数据库**：存储和检索向量的专用数据库（本项目用 ChromaDB）
- **混合搜索**：根据场景在"全文精确匹配"和"语义近似匹配"之间切换

## 目录结构

```
phase2/
├── README.md              # 本文件
├── 01_embed_and_store.py  # 文本向量化 + 存储
├── 02_retrieval_search.py # 语义检索
├── 03_rag_qa.py           # RAG 问答
├── 04_code_qa_agent.py    # 代码问答 Agent
├── 05_hybrid_search.py    # 混合搜索（Codex 路线）
├── 06_append_only_cache.py# 缓存命中率优化（Reasonix 路线）
├── ingest/                # 数据处理工具
│   ├── __init__.py
│   ├── code_parser.py     # 代码文件解析
│   └── chunker.py         # 文本分块策略
└── data/                  # 向量数据库存储（git ignored）
    └── .gitkeep
```

---

## 混合搜索（05）— 借鉴自 Codex CLI

> **为什么加这个任务**：学完前面 4 个脚本你会发现一个矛盾——**对代码来说 RAG 经常"答非所问"**（搜 `login` 给你返回 `logout`），但 ripgrep 又没法搜"性能相关的所有函数"。
>
> Codex CLI 的解法是**按场景选工具**：默认用 ripgrep，搜不到时再走 RAG。我们来复刻这个判断逻辑。

### 双路召回架构

```
用户提问: "哪里处理用户登录？"
        ↓
    ┌───────┴───────┐
    ↓               ↓
  [路 A]         [路 B]
  ripgrep        RAG 检索
  "login"        "登录" 的 embedding
    ↓               ↓
  精确结果        语义结果
  auth.py:42     utils/auth.py:15
    ↓               ↓
    └───────┬───────┘
            ↓
       去重 + 排序
            ↓
       返回给 LLM
```

### 路由策略

| 场景 | 优先用 | 原因 |
|---|---|---|
| 搜函数名 / 类名 / 变量名 | ripgrep | 精确匹配 |
| 搜报错信息 / 异常名 | ripgrep | 字符串精确 |
| 搜"性能 / 优化 / 缓存相关的代码" | RAG | 语义概念 |
| 搜中文笔记 / 文档 | RAG | 跨语种 |
| 搜"在哪定义 / 在哪调用" | ripgrep | 元数据问题 |
| 搜"怎么实现 / 怎么用" | RAG | 开放问题 |

### 学习目标

- [ ] 调用 `subprocess.run(["rg", ...])` 跑 ripgrep
- [ ] 实现一个 `route_query()` 函数，根据关键词/词性判断走哪条路
- [ ] 合并两路结果并去重
- [ ] 在 `04_code_qa_agent.py` 里替换原检索函数
- [ ] 对比测试：纯 RAG vs 混合搜索，答对率

### 经验出处

参考项目：[Codex CLI](https://github.com/openai/codex) / [Aider](https://github.com/Aider-AI/aider)  
**核心思想**：**代码搜索用精确匹配，文档搜索用语义匹配**。混合架构比单 RAG 准，比纯 grep 灵活。

---

## Append-Only 缓存层（06）— 借鉴自 DeepSeek-Reasonix

> **为什么加这个任务**：你在 phase 2 第 10 周会做"成本观察"，会发现一个痛点——**多轮对话成本线性增长**。每轮都要把全部历史重发一遍，token 烧得很快。
>
> DeepSeek 的官方解法是"前缀缓存"：如果请求前缀字节完全相同，缓存命中只收 10% 费用。Reasonix 把这个机制用到了极致，做到 99.82% 命中率。
>
> 我们这个任务做"教学级"复刻——**在本地用 SQLite 模拟前缀缓存**，体会这个设计思想。

### 核心思想

```
传统 Agent（破坏缓存）：
  轮3: [system, user1, assistant1, user2, assistant2, user3]
  轮4: [system, user1, assistant2, user1, assistant3, user4]   ← 重新排序了
       ↑ 缓存失效，要为所有 token 重新付费

Append-Only（保住缓存）：
  轮3: [system, user1, assistant1, user2, assistant2, user3]
  轮4: [system, user1, assistant1, user2, assistant2, user3, assistant3, user4]
       ↑ 只在末尾追加，前缀字节完全相同，缓存命中
```

### 三层结构

```python
class AppendOnlyCache:
    def __init__(self):
        # 第1层：不可变前缀（system prompt + 工具声明 + 早期固定对话）
        # 永远不动，作为缓存键
        self.immutable_prefix = []

        # 第2层：追加日志（新的对话和工具结果）
        # 严格按时间顺序，只加不改
        self.append_only_log = []

        # 第3层：易失性草稿（不发给 API）
        # 临时计算过程、思考链
        self.volatile_drafts = []

    def get_request_messages(self):
        """组装发给 LLM 的消息 = 不可变前缀 + 追加日志"""
        return self.immutable_prefix + self.append_only_log

    def append(self, message):
        """只在末尾追加，不允许修改历史"""
        self.append_only_log.append(message)

    def cache_key(self):
        """缓存键 = 不可变前缀 + 当前日志长度的哈希"""
        prefix = json.dumps(self.immutable_prefix, sort_keys=True)
        return hashlib.md5(f"{prefix}|len={len(self.append_only_log)}".encode()).hexdigest()
```

### 模拟实现

```python
import sqlite3
import json
import hashlib

class MockCacheDB:
    """用 SQLite 模拟 DeepSeek 的前缀缓存"""
    def __init__(self, db_path="cache.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                response TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost REAL
            )
        """)

    def get(self, cache_key: str):
        row = self.conn.execute(
            "SELECT response, input_tokens, output_tokens, cost FROM cache WHERE key = ?",
            (cache_key,)
        ).fetchone()
        if row:
            print(f"  [CACHE HIT] 节省 {(1 - 0.1) * 100:.0f}% 输入成本")
            return {"response": row[0], "input_tokens": row[1], "output_tokens": row[2], "cost": row[3]}
        return None

    def put(self, cache_key: str, response: str, input_tokens: int, output_tokens: int, cost: float):
        self.conn.execute(
            "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?, ?)",
            (cache_key, response, input_tokens, output_tokens, cost)
        )
        self.conn.commit()
```

### 学习目标

- [ ] 实现 `AppendOnlyCache` 三层结构
- [ ] 实现 `MockCacheDB` 模拟 DeepSeek 缓存
- [ ] 对比测试：同一段对话，破坏前缀 vs 保持前缀，统计"成本节省率"
- [ ] 写一个报告：哪种改动会破坏缓存（重排序、删消息、改 system prompt 等）
- [ ] 反思：为什么我们项目用 append-only 会牺牲一些灵活性

### 经验出处

参考项目：[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) — 它的整个架构就是为"保住缓存前缀"设计的。  
**核心思想**：**为了缓存命中率，放弃对历史消息的"优化整理"**。这是反直觉的工程决策，理解了它就理解了"系统经济性优先"的开发哲学。
