# phase1/04_react_agent.py
#
# 功能：ReAct Agent —— 推理(Reason) + 行动(Act) + 观察(Observe) 循环
# 运行：python phase1/04_react_agent.py
# 学习要点：
#   - ReAct 模式：模型先思考要做什么，再执行工具，观察结果，循环直到完成
#   - 与 03_function_call.py 的区别：这里是全自动循环，不需要每步确认
#   - 终止条件：模型不再请求工具调用时，说明它认为任务完成

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
# 工具定义
# ============================================================

def get_current_time():
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str):
    """计算数学表达式（如 '2 + 3 * 4'）"""
    try:
        # 安全起见，只允许数字和基本运算符
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误：表达式包含非法字符"
        result = eval(expression)  # 注意：生产环境不要用 eval，这里仅做演示
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"


def get_word_count(text: str):
    """统计文本的字符数和单词数"""
    char_count = len(text)
    word_count = len(text.split())
    return f"字符数：{char_count}，单词/词数：{word_count}"


# 工具名称 → 函数的映射
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "get_word_count": get_word_count,
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
            "description": "计算数学表达式，如 '2 + 3 * 4'",
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
            "name": "get_word_count",
            "description": "统计文本的字符数和单词数",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要统计的文本"},
                },
                "required": ["text"],
            },
        },
    },
]


# ============================================================
# ReAct Agent 核心循环
# ============================================================

# 最大步数限制（防止无限循环）
MAX_STEPS = 10

SYSTEM_PROMPT = """你是一个智能助手，请用中文回答。
你可以使用提供的工具来辅助回答。
如果需要多步操作，请一步步来，每一步使用合适的工具。
最终用自然语言总结结果给用户。"""


def run_agent(user_query: str):
    """运行 ReAct Agent 处理用户请求"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    print(f"\n{'='*50}")
    print(f"用户问题：{user_query}")
    print(f"{'='*50}")

    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- 第 {step} 步 ---")

        # 调用 API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message

        # 情况1：模型没有调用工具 → 认为任务完成
        if not message.tool_calls:
            reply = message.content or "(无回复)"
            print(f"\n最终回复：{reply}")
            return reply

        # 情况2：模型请求调用工具
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  思考：需要调用 {func_name}({func_args})")

            # 执行工具
            if func_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[func_name](**func_args)
            else:
                result = f"错误：未知工具 {func_name}"

            print(f"  观察：{result}")

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

print("=" * 50)
print("ReAct Agent —— 自动推理 + 工具调用循环")
print("试试问：")
print("  - '现在几点？然后帮我算 123 * 456 + 789'")
print("  - '统计一下\"hello world 你好世界\"有多少字符'")
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
