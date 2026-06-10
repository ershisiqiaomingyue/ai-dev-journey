import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 大模型的客户端，封装的方法用来调用api。
# 现在预留使用openAI协议
# todo 配置协议
class AiClient:
    def __init__(self):
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path)

        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")

        if not api_key or api_key == "your-api-key-here":
            print("[错误] LLM_API_KEY 未配置，请编辑 .env 文件")
            sys.exit(1)
        self.model = os.getenv("LLM_MODEL",'qwen3.5-flash')

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def get_model(self):
        return self.model