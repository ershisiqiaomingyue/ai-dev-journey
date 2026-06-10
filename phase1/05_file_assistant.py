# phase1/05_file_assistant.py
#
# 功能：文件系统助手 —— 一个能读写文件的 Agent（第一阶段综合项目）
# 运行：python phase1/05_file_assistant.py
# 学习要点：
#   - 将多个工具组合到一个 Agent 中
#   - 安全边界：限制 Agent 只能操作指定目录
#   - 错误处理：文件不存在、权限不足等情况
#   - 这是前4个脚本的综合应用

import os
import sys
import json
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
# 安全设置：Agent 只能操作这个目录
# ============================================================

# TODO: 可以修改这个路径，让 Agent 操作其他目录
WORKSPACE = Path(__file__).resolve().parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)


def safe_path(filename: str) -> Path:
    """确保文件路径在 workspace 目录内（防止路径穿越攻击）"""
    target = (WORKSPACE / filename).resolve()
    if not str(target).startswith(str(WORKSPACE.resolve())):
        raise ValueError(f"安全限制：不允许访问 workspace 外的路径")
    return target


# ============================================================
# 工具定义
# ============================================================

def list_files(directory: str = "."):
    """列出指定目录下的文件和子目录"""
    try:
        target = safe_path(directory)
        items = []
        for item in target.iterdir():
            prefix = "[目录]" if item.is_dir() else "[文件]"
            size = item.stat().st_size if item.is_file() else 0
            items.append(f"{prefix} {item.name} ({size} bytes)")
        return "\n".join(items) if items else "(空目录)"
    except Exception as e:
        return f"错误：{e}"


def read_file(filename: str):
    """读取文件内容"""
    try:
        target = safe_path(filename)
        if not target.exists():
            return f"错误：文件不存在 {filename}"
        content = target.read_text(encoding="utf-8")
        # 限制返回长度
        if len(content) > 2000:
            return content[:2000] + f"\n... (已截断，共 {len(content)} 字符)"
        return content
    except Exception as e:
        return f"错误：{e}"


def write_file(filename: str, content: str):
    """写入内容到文件（覆盖写入）"""
    try:
        target = safe_path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"成功写入 {filename}（{len(content)} 字符）"
    except Exception as e:
        return f"错误：{e}"


def append_file(filename: str, content: str):
    """追加内容到文件末尾"""
    try:
        target = safe_path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as f:
            f.write(content)
        return f"成功追加到 {filename}（{len(content)} 字符）"
    except Exception as e:
        return f"错误：{e}"


def delete_file(filename: str):
    """删除文件"""
    try:
        target = safe_path(filename)
        if not target.exists():
            return f"错误：文件不存在 {filename}"
        target.unlink()
        return f"已删除 {filename}"
    except Exception as e:
        return f"错误：{e}"


# 工具名称 → 函数的映射
TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "delete_file": delete_file,
}

# 工具的 JSON Schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定目录下的文件和子目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目录路径，默认为当前目录", "default": "."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名或相对路径"},
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入内容到文件（覆盖写入）",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名或相对路径"},
                    "content": {"type": "string", "description": "要写入的内容"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "追加内容到文件末尾",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名或相对路径"},
                    "content": {"type": "string", "description": "要追加的内容"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名或相对路径"},
                },
                "required": ["filename"],
            },
        },
    },
]


# ============================================================
# Agent 核心循环
# ============================================================

MAX_STEPS = 15

SYSTEM_PROMPT = f"""你是一个文件系统助手，请用中文回答。
你可以帮用户查看、创建和编辑文件。
所有文件操作限制在 {WORKSPACE} 目录内。
操作文件前，请先用 list_files 查看目录结构。
写入文件时，请确保内容完整、格式正确。"""


def run_agent(user_query: str):
    """运行文件系统 Agent"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    print(f"\n{'='*50}")
    print(f"用户请求：{user_query}")
    print(f"{'='*50}")

    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message

        # 没有工具调用 → 任务完成
        if not message.tool_calls:
            reply = message.content or "(无回复)"
            print(f"\n最终回复：{reply}")
            return reply

        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  [{step}] {func_name}({func_args})")

            if func_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[func_name](**func_args)
            else:
                result = f"错误：未知工具 {func_name}"

            print(f"       → {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    print(f"\n[警告] 达到最大步数限制 ({MAX_STEPS})")
    return None


# ============================================================
# 主程序
# ============================================================

print("=" * 50)
print("文件系统助手 Agent")
print(f"工作目录：{WORKSPACE}")
print("试试说：")
print("  - '帮我创建一个 hello.txt，写上 Hello World'")
print("  - '列出当前目录的文件'")
print("  - '读取 hello.txt 的内容'")
print("  - '创建一个 Python 脚本，计算 1+2+...+100'")
print("输入 'quit' 退出")
print("=" * 50)

while True:
    user_input = input("\n你：").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        print("再见！")
        break
    if not user_input:
        continue

    run_agent(user_input)
