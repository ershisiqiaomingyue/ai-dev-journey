# phase2/ingest/code_parser.py
#
# 代码文件解析器 —— 按函数/类结构切分代码，而非简单按字符数切割

import ast
from pathlib import Path


def parse_python_file(file_path: str) -> list[dict]:
    """
    解析 Python 文件，按函数和类定义切分

    返回:
        [
            {
                "type": "function" | "class" | "module",
                "name": "函数名/类名",
                "content": "代码内容",
                "start_line": 起始行号,
                "end_line": 结束行号,
            }
        ]
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(content)
    except SyntaxError:
        # 解析失败时，返回整个文件作为一个块
        return [{"type": "module", "name": path.name, "content": content, "start_line": 1, "end_line": len(content.splitlines())}]

    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunk_content = ast.get_source_segment(content, node) or ""
            chunks.append({
                "type": "function",
                "name": node.name,
                "content": chunk_content,
                "start_line": node.lineno,
                "end_line": node.end_lineno or node.lineno,
            })
        elif isinstance(node, ast.ClassDef):
            # 类定义（不含方法体，方法会单独作为一个 chunk）
            chunk_content = ast.get_source_segment(content, node) or ""
            chunks.append({
                "type": "class",
                "name": node.name,
                "content": chunk_content[:500],  # 类定义截断，避免太长
                "start_line": node.lineno,
                "end_line": node.lineno + 10,  # 只取类定义头部
            })

    # 如果没有找到函数/类，返回整个文件
    if not chunks:
        chunks = [{"type": "module", "name": path.name, "content": content, "start_line": 1, "end_line": len(content.splitlines())}]

    return chunks


# TODO: 可以添加更多语言的解析器
# def parse_javascript_file(file_path: str) -> list[dict]: ...
# def parse_java_file(file_path: str) -> list[dict]: ...
