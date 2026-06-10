# phase2/ingest/chunker.py
#
# 文本分块策略 —— 把长文本切分成适合向量化的块

from typing import Literal


def chunk_by_characters(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    按字符数分块（最基础的策略）

    参数:
        text: 原始文本
        chunk_size: 每块的最大字符数
        overlap: 相邻块之间的重叠字符数（保持上下文连贯）

    返回:
        [{"content": "块内容", "index": 块序号}]
    """
    if len(text) <= chunk_size:
        return [{"content": text, "index": 0}]

    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({"content": chunk, "index": idx})
        start = end - overlap
        idx += 1

    return chunks


def chunk_by_paragraphs(text: str) -> list[dict]:
    """
    按段落分块（适合 Markdown、文档）

    以空行为分隔符，将文本切分为段落
    """
    paragraphs = text.split("\n\n")
    chunks = []

    for i, para in enumerate(paragraphs):
        para = para.strip()
        if para:
            chunks.append({"content": para, "index": i})

    return chunks


def chunk_by_lines(text: str, lines_per_chunk: int = 50) -> list[dict]:
    """
    按行数分块（适合代码文件）

    参数:
        text: 原始文本
        lines_per_chunk: 每块包含多少行
    """
    lines = text.splitlines()
    chunks = []

    for i in range(0, len(lines), lines_per_chunk):
        chunk_lines = lines[i:i + lines_per_chunk]
        chunks.append({
            "content": "\n".join(chunk_lines),
            "index": i // lines_per_chunk,
            "start_line": i + 1,
            "end_line": i + len(chunk_lines),
        })

    return chunks


# ============================================================
# 策略选择
# ============================================================

ChunkStrategy = Literal["characters", "paragraphs", "lines"]


def chunk_text(
    text: str,
    strategy: ChunkStrategy = "characters",
    **kwargs,
) -> list[dict]:
    """
    统一的分块入口，根据策略选择不同的分块方法

    用法:
        chunks = chunk_text(text, strategy="characters", chunk_size=500)
        chunks = chunk_text(text, strategy="paragraphs")
        chunks = chunk_text(text, strategy="lines", lines_per_chunk=30)
    """
    if strategy == "characters":
        return chunk_by_characters(text, **kwargs)
    elif strategy == "paragraphs":
        return chunk_by_paragraphs(text)
    elif strategy == "lines":
        return chunk_by_lines(text, **kwargs)
    else:
        raise ValueError(f"未知分块策略：{strategy}")
