# phase4/01_cost_optimizer.py
#
# 功能：成本优化 —— 缓存、模型路由、Token 追踪
# 运行：python phase4/01_cost_optimizer.py
# 学习要点：
#   - 前缀缓存（Prefix Caching）的原理和 API
#   - 模型路由：根据问题复杂度选择不同模型
#   - Token 用量追踪和成本计算

import os
import sys
import time
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
# Token 成本追踪
# ============================================================

class CostTracker:
    """追踪 API 调用的 Token 用量和成本"""

    # TODO: 根据实际模型价格更新
    PRICE_PER_1K_INPUT = 0.001   # 每 1000 输入 token 的价格（美元）
    PRICE_PER_1K_OUTPUT = 0.002  # 每 1000 输出 token 的价格（美元）

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

    def record(self, input_tokens: int, output_tokens: int):
        """记录一次调用"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_requests += 1

    def total_cost(self) -> float:
        """计算总成本（美元）"""
        input_cost = self.total_input_tokens / 1000 * self.PRICE_PER_1K_INPUT
        output_cost = self.total_output_tokens / 1000 * self.PRICE_PER_1K_OUTPUT
        return input_cost + output_cost

    def summary(self):
        """打印统计摘要"""
        print(f"\n{'='*40}")
        print(f"调用统计：")
        print(f"  总请求数：{self.total_requests}")
        print(f"  输入 tokens：{self.total_input_tokens}")
        print(f"  输出 tokens：{self.total_output_tokens}")
        print(f"  总 tokens ：{self.total_input_tokens + self.total_output_tokens}")
        print(f"  估算成本：${self.total_cost():.4f}")
        print(f"{'='*40}")


# ============================================================
# 模型路由（简化版）
# ============================================================

def classify_complexity(question: str) -> str:
    """
    简单判断问题复杂度，决定用哪个模型

    TODO: 可以用一个轻量级模型（或规则）来做分类
    """
    # 简单规则：问题越短越简单
    if len(question) < 20:
        return "simple"
    elif len(question) < 100:
        return "medium"
    else:
        return "complex"


def smart_ask(question: str, tracker: CostTracker):
    """
    智能问答：根据问题复杂度选择不同策略

    - 简单问题：直接回答（用便宜模型 / 短 prompt）
    - 中等问题：标准回答
    - 复杂问题：详细回答（用强模型 / 长 prompt）
    """
    complexity = classify_complexity(question)

    # TODO: 实际项目中可以为不同复杂度配置不同模型
    # simple  → gpt-3.5-turbo / qwen-turbo（便宜快速）
    # medium  → deepseek-chat（平衡）
    # complex → gpt-4 / claude-sonnet（强力但贵）

    if complexity == "simple":
        system_prompt = "简洁回答，不超过50字。"
    elif complexity == "medium":
        system_prompt = "请用中文回答，适度详细。"
    else:
        system_prompt = "请用中文详细回答，包含示例和解释。"

    print(f"  [复杂度: {complexity}, 提示词策略: {system_prompt}]")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    usage = response.usage
    tracker.record(usage.prompt_tokens, usage.completion_tokens)

    return response.choices[0].message.content


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("成本优化演示")
    print("=" * 50)
    print("\n策略：")
    print("  1. 根据问题复杂度选择不同提示词长度")
    print("  2. 追踪每次调用的 Token 用量")
    print("  3. 会话结束后统计总成本")
    print("\n输入 'quit' 退出，输入 'cost' 查看当前成本统计")
    print("=" * 50)

    tracker = CostTracker()

    while True:
        question = input("\n你：").strip()

        if question.lower() in ("quit", "exit", "q"):
            tracker.summary()
            print("再见！")
            break

        if question.lower() == "cost":
            tracker.summary()
            continue

        if not question:
            continue

        answer = smart_ask(question, tracker)
        print(f"\nAI：{answer}")


if __name__ == "__main__":
    main()
