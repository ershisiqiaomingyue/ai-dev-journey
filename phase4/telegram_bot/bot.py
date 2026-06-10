# phase4/telegram_bot/bot.py
#
# 功能：Telegram Bot 入口 —— 将 Agent 接入 Telegram
# 运行：python -m phase4.telegram_bot.bot
# 学习要点：
#   - python-telegram-bot 框架的基本用法
#   - 多用户隔离（每个用户独立的对话历史）
#   - 异步处理

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# --- 加载配置 ---
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

# TODO: 在 .env 中添加 TELEGRAM_BOT_TOKEN
# TELEGRAM_BOT_TOKEN=your-bot-token-here

# TODO: 安装依赖后取消注释
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters
# from .handlers import handle_message, handle_start, handle_clear


# ============================================================
# Bot 配置
# ============================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


# ============================================================
# 用户会话管理
# ============================================================

# 每个用户的对话历史（简化版，实际项目应该用数据库）
user_sessions: dict[int, list] = {}


def get_session(user_id: int) -> list:
    """获取用户的对话历史"""
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system", "content": "你是一个有帮助的 AI 助手，请用中文回答。"}
        ]
    return user_sessions[user_id]


def clear_session(user_id: int):
    """清除用户的对话历史"""
    if user_id in user_sessions:
        del user_sessions[user_id]


# ============================================================
# Bot 启动
# ============================================================

def main():
    print("=" * 50)
    print("Telegram Bot 代码助手")
    print("=" * 50)

    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your-bot-token-here":
        print("\n[错误] TELEGRAM_BOT_TOKEN 未配置")
        print("  1. 在 Telegram 中找 @BotFather 创建 Bot")
        print("  2. 获取 Bot Token")
        print("  3. 在 .env 中添加：TELEGRAM_BOT_TOKEN=你的token")
        print("\n[演示模式] 以下是 Bot 的功能说明：")
        print("  /start  - 开始对话")
        print("  /clear  - 清除对话历史")
        print("  发送消息 - AI 回答你的问题")
        print("  发送代码 - AI 帮你审查代码")
        return

    # TODO: 安装依赖后取消注释
    #
    # app = Application.builder().token(TELEGRAM_TOKEN).build()
    #
    # # 注册处理器
    # app.add_handler(CommandHandler("start", handle_start))
    # app.add_handler(CommandHandler("clear", handle_clear))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    #
    # print("Bot 已启动，等待消息...")
    # app.run_polling()

    print("\n[待实现] 请先安装: pip install python-telegram-bot")


if __name__ == "__main__":
    main()
