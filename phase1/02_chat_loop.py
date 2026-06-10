# phase1/02_chat_loop.py
#
# 功能：多轮对话 —— 通过 while 循环实现连续对话，理解 messages 数组
# 运行：python phase1/02_chat_loop.py
# 学习要点：
#   - messages 数组的结构（system/user/assistant 三种角色）
#   - 上下文窗口：对话越长，token 消耗越多
#   - 如何手动截断历史消息（保留最近 N 轮）

import os
import sys
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

# --- 对话历史 ---
# TODO: 尝试修改 max_history 的值，观察对话记忆的效果
max_history = 10  # 保留最近多少轮对话

messages = [
    {"role": "system", "content": "你是一个有帮助的 AI 助手，请用中文回答。"},
]

# --- 主循环 ---
print("=" * 50)
print("多轮对话模式（输入 'quit' 或 'exit' 退出）")
print("=" * 50)

while True:
    user_input = input("\n你：").strip()

    if user_input.lower() in ("quit", "exit", "q"):
        print("再见！")
        break

    if not user_input:
        continue

    # 添加用户消息
    messages.append({"role": "user", "content": user_input})

    # TODO: 在这里添加历史截断逻辑
    # 如果 messages 太长，只保留 system + 最近 max_history 条消息
    # 提示：messages = [messages[0]] + messages[-(max_history * 2):]

    # 调用 API
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except Exception as e:
        print(f"[错误] API 调用失败：{e}")
        continue

    reply = response.choices[0].message.content

    # 添加助手回复到历史
    messages.append({"role": "assistant", "content": reply})

    print(f"\nAI：{reply}")

# --- 统计 ---
print(f"\n本次对话共 {len(messages) - 1} 轮交互")
