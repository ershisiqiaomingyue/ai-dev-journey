# phase1/04_react_agent.py
#
# 功能：ReAct Agent —— 推理(Reason) + 行动(Act) + 观察(Observe) 循环
# 运行：python phase1/04_react_agent.py
# 学习要点：
#   - ReAct 模式：模型先思考要做什么，再执行工具，观察结果，循环直到完成
#   - 与 03_function_call.py 的区别：这里是全自动循环，不需要每步确认
#   - 递进调用：前一个工具的结果会成为后一个工具的输入（LLM 自己编排）
#   - 终止条件：模型不再请求工具调用时，说明它认为任务完成

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 把项目根目录加入 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.AiClient import AiClient

aiClient = AiClient()
client = aiClient.client
model = aiClient.model


# ============================================================
# 工具定义
# ============================================================

# --- 基础工具 ---

def get_current_time():
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str):
    """计算数学表达式（如 '2 + 3 * 4'）"""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误：表达式包含非法字符"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"


# --- 文件操作工具（用于演示递进调用）---
# 这些工具之间有依赖关系：
#   list_files → 返回文件列表
#   read_file  → 读取某个文件（需要知道文件名，来自 list_files 的结果）
#   count_text → 统计文本信息（需要文件内容，来自 read_file 的结果）
#   calculate  → 对统计结果做运算（需要数字，来自 count_text 的结果）

# Agent 只能操作这个目录（安全限制）
WORKSPACE = Path(__file__).resolve().parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)


def list_files(directory: str = "."):
    """列出指定目录下的文件"""
    try:
        target = (WORKSPACE / directory).resolve()
        if not target.exists():
            return f"目录不存在：{directory}"
        items = []
        for item in sorted(target.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                items.append(f"{item.name} ({size} bytes)")
            elif item.is_dir():
                items.append(f"[目录] {item.name}")
        return "\n".join(items) if items else "(空目录)"
    except Exception as e:
        return f"错误：{e}"


def read_file(filename: str):
    """读取文件内容（路径相对于 workspace 目录）"""
    try:
        target = (WORKSPACE / filename).resolve()
        if not target.exists():
            return f"错误：文件不存在 {filename}"
        content = target.read_text(encoding="utf-8")
        if len(content) > 3000:
            return content[:3000] + f"\n...(已截断，共 {len(content)} 字符)"
        return content
    except Exception as e:
        return f"错误：{e}"


def count_text(text: str):
    """统计文本的行数、字符数、单词数"""
    lines = text.count("\n") + 1
    chars = len(text)
    words = len(text.split())
    return f"行数: {lines}, 字符数: {chars}, 单词数: {words}"


# 工具名称 → 函数的映射
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "list_files": list_files,
    "read_file": read_file,
    "count_text": count_text,
}

# 工具的 JSON Schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，如 '2 + 3 * 4'、'100 / 7'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出 workspace 目录下的文件和子目录。返回文件名和大小。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "子目录路径，默认为根目录", "default": "."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取 workspace 目录下指定文件的全部内容。参数为文件名。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名（如 hello.txt、script.py）"},
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_text",
            "description": "统计一段文本的行数、字符数和单词数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要统计的文本内容"},
                },
                "required": ["text"],
            },
        },
    },
]


# ============================================================
# 创建一些示例文件（用于演示递进调用）
# ============================================================

def setup_demo_files():
    """在 workspace 目录创建示例文件"""
    demo_files = {
        "hello.txt": "你好世界\nHello World\n这是一段测试文本\n用于演示 Agent 的文件分析能力",
        "numbers.txt": "100\n200\n300\n400\n500",
        "notes.md": "# 学习笔记\n\n## Python\n- 列表推导式很强大\n- 装饰器是高阶函数\n\n## AI Agent\n- ReAct 模式\n- Function Calling\n- 工具链编排\n",
    }
    for name, content in demo_files.items():
        (WORKSPACE / name).write_text(content, encoding="utf-8")


# ============================================================
# ReAct Agent 核心循环
# ============================================================

MAX_STEPS = 10

SYSTEM_PROMPT = """你是一个智能助手，请用中文回答。
你可以使用提供的工具来辅助回答。
如果需要多步操作，请一步步来，每一步使用合适的工具。
前一个工具的结果可以帮你决定下一步该做什么。
最终用自然语言总结结果给用户。"""


def run_agent(user_query: str):
    """
    运行 ReAct Agent 处理用户请求

    递进调用的关键：
    - 所有工具结果都会加入 messages
    - LLM 看到上一步结果后，自己决定下一步
    - 你不需要编排调用顺序，LLM 自己会判断
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    print(f"\n{'='*50}")
    print(f"用户问题：{user_query}")
    print(f"{'='*50}")

    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- 第 {step} 步 ---")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message

        # 模型没有调用工具 → 认为任务完成
        if not message.tool_calls:
            reply = message.content or "(无回复)"
            print(f"\n最终回复：{reply}")
            return reply

        # 模型请求调用工具
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  调用：{func_name}({func_args})")

            if func_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[func_name](**func_args)
            else:
                result = f"错误：未知工具 {func_name}"

            print(f"  结果：{result[:100]}{'...' if len(str(result)) > 100 else ''}")

            # ★ 关键：工具结果回传到 messages，LLM 下一步能看到
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    print(f"\n[警告] 达到最大步数限制 ({MAX_STEPS})，停止执行")
    return None


# ============================================================
# 主程序
# ============================================================

def main():
    # 创建示例文件
    setup_demo_files()

    print("=" * 50)
    print("ReAct Agent —— 自动推理 + 工具链调用")
    print(f"工作目录：{WORKSPACE}")
    print("=" * 50)
    print()
    print("试试这些递进调用场景：")
    print("  1. '看看 workspace 里有哪些文件，然后读取 hello.txt 的内容'")
    print("     → list_files → read_file（文件名来自第1步结果）")
    print()
    print("  2. '读取 notes.md，统计它有多少行，再算 行数 * 10'")
    print("     → read_file → count_text → calculate（每步依赖上一步）")
    print()
    print("  3. '读取 numbers.txt，把所有数字加起来'")
    print("     → read_file → calculate（用文件内容构造表达式）")
    print()
    print("  4. '现在几点？'")
    print("     → get_current_time（单步调用）")
    print()
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


if __name__ == "__main__":
    main()
