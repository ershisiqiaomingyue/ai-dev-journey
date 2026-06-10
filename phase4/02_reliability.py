# phase4/02_reliability.py
#
# 功能：可靠性工程 —— 重试、超时、步数限制、人工接管
# 运行：python phase4/02_reliability.py
# 学习要点：
#   - API 限流（Rate Limit）和指数退避重试
#   - 最大步数限制（防止 Agent 无限循环）
#   - 人工接管模式（Agent 不确定时求助用户）
#   - 超时处理

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APITimeoutError, APIConnectionError

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
# 重试机制
# ============================================================

def call_with_retry(messages, max_retries=3, timeout=30):
    """
    带重试的 API 调用

    策略：指数退避（1s → 2s → 4s）
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=timeout,
            )
            return response

        except RateLimitError:
            wait_time = 2 ** attempt  # 1, 2, 4 秒
            print(f"  [限流] 第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
            time.sleep(wait_time)

        except APITimeoutError:
            print(f"  [超时] 请求超过 {timeout} 秒，第 {attempt + 1} 次重试...")
            time.sleep(1)

        except APIConnectionError as e:
            print(f"  [连接错误] {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise

    raise Exception(f"API 调用失败，已重试 {max_retries} 次")


# ============================================================
# 步数限制
# ============================================================

class StepLimitExceeded(Exception):
    """超出最大步数限制"""
    pass


def run_with_step_limit(task: str, max_steps: int = 10):
    """
    带步数限制的 Agent 执行

    防止 Agent 陷入无限循环（特别是工具调用场景）
    """
    print(f"\n任务：{task}")
    print(f"最大步数：{max_steps}")

    messages = [
        {"role": "system", "content": "你是一个有帮助的 AI 助手，请用中文回答。"},
        {"role": "user", "content": task},
    ]

    for step in range(1, max_steps + 1):
        print(f"\n--- 第 {step}/{max_steps} 步 ---")

        response = call_with_retry(messages)
        reply = response.choices[0].message.content
        print(f"AI：{reply}")

        # TODO: 在 ReAct Agent 中，这里应该检查是否有工具调用
        # 如果没有工具调用，说明任务完成
        if not response.choices[0].message.tool_calls:
            print(f"\n任务完成（共 {step} 步）")
            return reply

        messages.append({"role": "assistant", "content": reply})

    raise StepLimitExceeded(f"超出最大步数限制 ({max_steps})，任务未完成")


# ============================================================
# 人工接管模式
# ============================================================

def ask_human(question: str) -> str:
    """
    当 Agent 不确定时，请求用户帮助

    在实际项目中，可以通过 Telegram/邮件通知人工介入
    """
    print(f"\n{'!'*40}")
    print(f"[人工接管] Agent 需要帮助：")
    print(f"  {question}")
    print(f"{'!'*40}")
    answer = input("你的回答：").strip()
    return answer


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("可靠性工程演示")
    print("=" * 50)
    print("\n功能：")
    print("  1. 指数退避重试（应对 API 限流）")
    print("  2. 最大步数限制（防止无限循环）")
    print("  3. 超时处理（防止卡死）")
    print("  4. 人工接管（Agent 不确定时求助）")
    print("\n输入 'quit' 退出")
    print("=" * 50)

    while True:
        task = input("\n你的任务：").strip()
        if task.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        if not task:
            continue

        try:
            run_with_step_limit(task, max_steps=5)
        except StepLimitExceeded as e:
            print(f"\n[警告] {e}")
            choice = input("是否继续？(y/n): ").strip()
            if choice.lower() == "y":
                run_with_step_limit(task, max_steps=10)


if __name__ == "__main__":
    main()
