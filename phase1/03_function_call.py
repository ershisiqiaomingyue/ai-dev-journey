# phase1/03_function_call.py
#
# 功能：Function Calling —— 让模型调用你定义的"工具"
# 运行：python phase1/03_function_call.py
# 学习要点：
#   - 如何定义工具的 JSON Schema（名称、描述、参数）
#   - 模型返回 tool_calls 时如何解析
#   - 如何将工具执行结果回传给模型


import json
from datetime import datetime
from utils.AiClient import AiClient

aiClient = AiClient()
client = aiClient.client
model = aiClient.model


# ============================================================
# 第一步：定义工具（函数）
# ============================================================

def get_current_time():
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_numbers(a: int, b: int):
    """计算两个数字的和"""
    return a + b


# 工具名称 → 函数的映射
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "add_numbers": add_numbers,
}

# ============================================================
# 第二步：定义工具的 JSON Schema（告诉模型有哪些工具可用）
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "计算两个整数的和",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "第一个数字"},
                    "b": {"type": "integer", "description": "第二个数字"},
                },
                "required": ["a", "b"],
            },
        },
    },
    # TODO: 尝试添加更多工具，比如：
    # - multiply_numbers: 计算乘积
    # - get_weather: 返回模拟的天气信息
]


# ============================================================
# 第三步：执行工具调用
# ============================================================

def execute_tool_call(tool_call):
    """解析并执行一个 tool_call"""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    print(f"  → 调用工具：{func_name}({func_args})")

    if func_name not in TOOL_FUNCTIONS:
        return f"错误：未知工具 {func_name}"

    result = TOOL_FUNCTIONS[func_name](**func_args)
    print(f"  → 工具结果：{result}")
    return str(result)


# ============================================================
# 第四步：主循环 —— 带工具调用的对话
# ============================================================

print("=" * 50)
print("Function Calling 演示")
print("试试问：'现在几点了？' 或 '123 + 456 等于多少？'")
print("输入 'quit' 退出")
print("=" * 50)

messages = [
    {"role": "system", "content": "你是一个有帮助的 AI 助手，请用中文回答。你可以使用提供的工具来辅助回答。"},
]

while True:
    user_input = input("\n你：").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        print("再见！")
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    # 调用 API（传入 tools 参数）
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
    except Exception as e:
        print(f"[错误] API 调用失败：{e}")
        continue

    message = response.choices[0].message

    # 检查模型是否要调用工具
    if message.tool_calls:
        print("\n[模型请求调用工具]")

        # 先把 assistant 的消息（含 tool_calls）加入历史
        messages.append(message)

        # 逐个执行工具调用，并把结果加入历史
        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # 再次调用 API，让模型根据工具结果生成最终回复
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message

    # 打印最终回复
    reply = message.content or "(无回复)"
    messages.append({"role": "assistant", "content": reply})
    print(f"\nAI：{reply}")
