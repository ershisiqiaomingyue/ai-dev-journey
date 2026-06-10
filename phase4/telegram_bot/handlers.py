# phase4/telegram_bot/handlers.py
#
# 功能：Telegram 消息处理器
# 学习要点：
#   - 异步处理消息
#   - 流式回复（分段发送长回复）
#   - 错误处理

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# --- 加载配置 ---
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)
model = os.getenv("LLM_MODEL", "deepseek-v4-flash")


# TODO: 安装依赖后取消注释
# from telegram import Update
# from telegram.ext import ContextTypes


# ============================================================
# 消息处理器
# ============================================================

# TODO: 取消注释并实现
#
# async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """处理 /start 命令"""
#     await update.message.reply_text(
#         "你好！我是代码助手 Bot。\n\n"
#         "功能：\n"
#         "- 问我编程问题\n"
#         "- 发送代码让我帮你审查\n"
#         "- 使用 /clear 清除对话历史"
#     )
#
#
# async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """处理 /clear 命令 —— 清除对话历史"""
#     from .bot import clear_session
#     clear_session(update.effective_user.id)
#     await update.message.reply_text("对话历史已清除。")
#
#
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """处理普通消息 —— 调用 LLM 回答"""
#     from .bot import get_session
#
#     user_id = update.effective_user.id
#     messages = get_session(user_id)
#     user_text = update.message.text
#
#     messages.append({"role": "user", "content": user_text})
#
#     # 显示"正在输入"
#     await update.message.reply_chat_action("typing")
#
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=messages,
#         )
#         reply = response.choices[0].message.content
#         messages.append({"role": "assistant", "content": reply})
#
#         # Telegram 消息长度限制 4096 字符
#         if len(reply) > 4000:
#             for i in range(0, len(reply), 4000):
#                 await update.message.reply_text(reply[i:i+4000])
#         else:
#             await update.message.reply_text(reply)
#
#     except Exception as e:
#         await update.message.reply_text(f"[错误] 处理失败：{e}")


# ============================================================
# 占位函数（未安装依赖时）
# ============================================================

def handle_start():
    """占位：/start 命令处理"""
    pass

def handle_clear():
    """占位：/clear 命令处理"""
    pass

def handle_message():
    """占位：消息处理"""
    pass
