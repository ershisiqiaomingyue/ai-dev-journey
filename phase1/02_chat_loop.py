# phase1/02_chat_loop.py
#
# 功能：多轮对话 —— 流式输出 + 对话历史保存
# 运行：python phase1/02_chat_loop.py
#
# 学习要点：
#   1. 【AI 的"记忆"原理】
#      - LLM 本身没有记忆！每次调用都是独立的
#      - 所谓的"记住"，是因为我们把完整历史每次都发给 API
#      - messages 数组越长 → token 消耗越多 → 成本越高
#      - 当历史太长时，需要截断（只保留最近 N 轮）
#
#   2. 【SSE 流式输出】
#      - stream=True 让 API 逐字返回，而非等全部生成完再返回
#      - 用户体验更好（打字机效果）
#      - 实际生产环境都用流式（ChatGPT、Claude 等）
#
#   3. 【对话历史持久化】
#      - 内存中的 messages 列表，程序关掉就没了
#      - 保存到 JSON 文件，下次启动可以加载继续聊
#      - 实际项目中会用数据库（SQLite、PostgreSQL 等）

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 把项目根目录加入 Python 路径（这样才能 import utils）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.AiClient import AiClient

# ============================================================
# 配置
# ============================================================

model = os.getenv("LLM_MODEL", "deepseek-v4-flash")
client = AiClient().client

# 保留最近多少轮对话（1轮 = 1条user + 1条assistant）
# TODO: 试试改成 5 或 20，观察 AI 的"记忆"变化
MAX_HISTORY = 10

# 对话历史保存路径
HISTORY_DIR = Path(__file__).resolve().parent / "history"
HISTORY_DIR.mkdir(exist_ok=True)


# ============================================================
# 对话历史的保存和加载
# ============================================================

def save_history(messages: list, filename: str):
    """
    把对话历史保存到 JSON 文件

    为什么要保存？
    - 程序重启后内存中的 messages 会丢失
    - 保存后可以下次加载继续聊
    - 也可以回顾之前的对话内容
    """
    if filename is None:
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    filepath = HISTORY_DIR / filename

    data = {
        "created_at": datetime.now().isoformat(),
        "message_count": len(messages),
        "messages": messages,
    }

    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return filepath


def load_history(filename: str) -> list:
    """
    从 JSON 文件加载对话历史

    使用场景：
    - 程序重启后，加载上次的对话继续聊
    - 加载后 AI 就能"记住"之前聊过的内容
    """
    filepath = HISTORY_DIR / filename

    if not filepath.exists():
        print(f"[错误] 文件不存在：{filepath}")
        return []

    data = json.loads(filepath.read_text(encoding="utf-8"))
    print(f"  已加载 {data['message_count']} 条消息（创建于 {data['created_at']}）")
    return data["messages"]


def list_history() -> list[str]:
    """列出所有保存的对话历史文件"""
    files = sorted(HISTORY_DIR.glob("chat_*.json"))
    return [f.name for f in files]


# ============================================================
# 历史截断（控制 token 消耗）
# ============================================================

def trim_history(messages: list, max_rounds: int) -> list:
    """
    截断对话历史，只保留最近 N 轮

    为什么要截断？
    - LLM 有上下文窗口限制（如 128K tokens）
    - 历史越长，每次调用消耗的 token 越多
    - 太长的历史可能导致 API 报错（超出限制）

    策略：保留 system prompt + 最近 max_rounds 轮对话
    """
    if len(messages) <= 1:  # 只有 system prompt
        return messages

    system = messages[0]  # system prompt
    history = messages[1:]  # user/assistant 交替

    # 每轮 = 2 条消息（user + assistant）
    max_messages = max_rounds * 2
    if len(history) > max_messages:
        history = history[-max_messages:]

    return [system] + history


# ============================================================
# 流式输出（SSE）
# ============================================================

def stream_chat(messages: list) -> str:
    """
    流式调用 API —— 逐字输出，而非等全部生成完

    stream=True 的原理：
    - API 不会一次性返回完整回复
    - 而是返回一个迭代器，每次 yield 一小块内容（chunk）
    - 我们逐块打印，实现"打字机"效果
    - 这就是 ChatGPT 等产品使用的技术（SSE: Server-Sent Events）
    """
    try:
        # 关键：stream=True
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,  # ← 开启流式输出
        )

        full_reply = ""

        # 逐块读取并打印
        for chunk in stream:
            # 每个 chunk 包含一小段内容
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)  # end="" 不换行，flush=True 立即输出
                full_reply += content

        print()  # 最后换行
        return full_reply

    except Exception as e:
        print(f"\n[错误] API 调用失败：{e}")
        return ""


# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 50)
    print("多轮对话（流式输出 + 历史保存）")
    print("=" * 50)

    # 初始化对话历史
    messages = [
        {"role": "system", "content": "你是一个有帮助的 AI 助手，请用中文回答。"},
    ]

    # 检查是否有可加载的历史
    history_files = list_history()
    if history_files:
        print(f"\n发现 {len(history_files)} 个历史对话：")
        for i, f in enumerate(history_files[-5:], 1):  # 只显示最近5个
            print(f"  {i}. {f}")
        choice = input("输入编号加载，或直接回车开始新对话：").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(history_files[-5:]):
            loaded = load_history(history_files[-5:][int(choice) - 1])
            if loaded:
                messages = loaded

    print("\n命令：")
    print("  quit/exit/q - 退出并保存对话")
    print("  save        - 手动保存当前对话")
    print("  history     - 显示对话统计")
    print("  trim N      - 截断历史到最近 N 轮")
    print("=" * 50)

    # --- 主循环 ---
    while True:
        user_input = input("\n你：").strip()

        if not user_input:
            continue

        # 处理命令
        if user_input.lower() in ("quit", "exit", "q"):
            filepath = save_history(messages)
            print(f"对话已保存：{filepath}")
            print(f"本次对话共 {len(messages) - 1} 条消息")
            print("再见！")
            break

        if user_input.lower() == "save":
            filepath = save_history(messages)
            print(f"对话已保存：{filepath}")
            continue

        if user_input.lower() == "history":
            user_msgs = [m for m in messages if m["role"] == "user"]
            assistant_msgs = [m for m in messages if m["role"] == "assistant"]
            print(f"  系统消息：1 条")
            print(f"  用户消息：{len(user_msgs)} 条")
            print(f"  助手消息：{len(assistant_msgs)} 条")
            print(f"  总计：{len(messages)} 条")
            # TODO: 可以加上 token 估算（1 汉字 ≈ 2 tokens）
            continue

        if user_input.lower().startswith("trim"):
            try:
                n = int(user_input.split()[1])
                messages = trim_history(messages, n)
                print(f"历史已截断到最近 {n} 轮，当前共 {len(messages)} 条消息")
            except (IndexError, ValueError):
                print("用法：trim 5（截断到最近 5 轮）")
            continue

        # 添加用户消息
        messages.append({"role": "user", "content": user_input})

        # 截断历史（防止 token 超限）
        messages = trim_history(messages, MAX_HISTORY)

        # 流式调用 API
        print("\nAI：", end="")
        reply = stream_chat(messages)

        if reply:
            # 添加助手回复到历史
            messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
