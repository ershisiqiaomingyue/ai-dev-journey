# phase1/01_hello_agent.py
#
# 功能：第一次 LLM API 调用 —— 发送消息，打印回复和 token 用量
# 运行：python phase1/01_hello_agent.py
# 前置条件：
#   1. 复制 .env.example 为 .env
#   2. 在 .env 中填入你的 LLM_API_KEY
#   3. pip install openai python-dotenv

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import openai

# --- 加载配置 ---
# .env 在项目根目录，这个脚本在 phase1/ 下
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")

if not api_key or api_key == "your-api-key-here":
    print("[错误] LLM_API_KEY 未配置")
    print("  请编辑 .env 文件，填入你的实际 API Key")
    print("  文件位置：", env_path)
    sys.exit(1)

# --- 创建客户端 ---
client = openai.OpenAI(api_key=api_key, base_url=base_url)

# --- 发送请求 ---
try:
    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "你是一个有帮助的 AI 助手，请用中文回答。"},
            {"role": "user", "content": "你好！请简单介绍一下你自己，告诉我你能做什么。"},
        ],
    )
except openai.AuthenticationError:
    print("[错误] 认证失败 —— API Key 无效")
    print("  请检查 .env 中的 LLM_API_KEY")
    sys.exit(1)
except openai.APIConnectionError as e:
    print(f"[错误] 连接失败 —— 无法访问 {base_url}")
    print(f"  详情：{e}")
    sys.exit(1)

# --- 打印结果 ---
reply = response.choices[0].message.content
usage = response.usage

print("=" * 50)
print("模型回复：")
print("-" * 50)
print(reply)
print("=" * 50)
print("Token 用量：")
print(f"  输入 tokens：{usage.prompt_tokens}")
print(f"  输出 tokens：{usage.completion_tokens}")
print(f"  总 tokens ：{usage.total_tokens}")
print("=" * 50)
