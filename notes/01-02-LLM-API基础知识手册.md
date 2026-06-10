# LLM API 基础知识手册

> 本文档涵盖 Phase 1（01-02）中涉及的所有 API 知识点，可作为日常开发速查手册。

---

## 目录

1. [OpenAI 兼容协议概述](#1-openai-兼容协议概述)
2. [API 鉴权与客户端初始化](#2-api-鉴权与客户端初始化)
3. [chat.completions.create() 详解](#3-chatcompletionscreate-详解)
4. [返回值结构详解](#4-返回值结构详解)
5. [messages 数组详解](#5-messages-数组详解)
6. [SSE 流式输出](#6-sse-流式输出)
7. [查询可用模型列表](#7-查询可用模型列表)
8. [Token 与成本](#8-token-与成本)
9. [常用参数速查表](#9-常用参数速查表)
10. [常见错误与处理](#10-常见错误与处理)
11. [Python SDK 常用 API 速查](#11-python-sdk-常用-api-速查)

---

## 1. OpenAI 兼容协议概述

### 什么是 OpenAI 兼容协议？

OpenAI 定义了一套 RESTful API 标准，很多 LLM 服务商都实现了这套标准，这样你只需要学会一套 SDK，就能切换不同的模型提供商。

### 兼容的服务商

| 服务商 | Base URL | 说明 |
|--------|----------|------|
| OpenAI | `https://api.openai.com/v1` | 官方，最贵 |
| 阿里云百炼（DashScope） | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 国内推荐 |
| DeepSeek | `https://api.deepseek.com/v1` | 国内推荐 |
| 智谱 AI | `https://open.bigmodel.cn/api/paas/v4` | GLM 系列 |
| Moonshot | `https://api.moonshot.cn/v1` | Kimi |
| Ollama（本地） | `http://localhost:11434/v1` | 本地部署 |

### 核心 API 端点

```
POST /chat/completions    # 对话补全（最常用）
GET  /models              # 查询可用模型列表
POST /embeddings          # 文本向量化（Phase 2 用）
```

---

## 2. API 鉴权与客户端初始化

### 基本用法

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxx",           # 你的 API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 服务商地址
)
```

### 带超时的初始化

```python
client = OpenAI(
    api_key="sk-xxxxxxxx",
    base_url="https://...",
    timeout=30.0,        # 请求超时（秒）
    max_retries=2,       # 自动重试次数
)
```

### 环境变量方式（推荐）

```python
import os
from openai import OpenAI

# 从环境变量读取（更安全）
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)
```

---

## 3. chat.completions.create() 详解

这是最核心的 API 调用，所有对话功能都基于它。

### 完整参数列表

```python
response = client.chat.completions.create(
    model="deepseek-v4-flash",    # 必填：模型名称
    messages=[...],               # 必填：对话消息列表
    stream=False,                 # 是否流式输出（默认 False）
    temperature=0.7,              # 温度（0-2），越高越随机
    top_p=1.0,                    # 核采样（0-1）
    max_tokens=1024,              # 最大输出 token 数
    n=1,                          # 生成几个候选回复
    stop=None,                    # 停止词（遇到就停止生成）
    presence_penalty=0.0,         # 存在惩罚（-2 到 2）
    frequency_penalty=0.0,        # 频率惩罚（-2 到 2）
    tools=None,                   # 工具定义列表（Function Calling）
    tool_choice=None,             # 工具选择策略
    timeout=30,                   # 超时（秒）
)
```

### 参数详解

#### temperature（温度）

控制输出的随机性。

| 值 | 效果 | 适用场景 |
|----|------|---------|
| 0 | 几乎确定性，每次输出相同 | 代码生成、翻译、格式化 |
| 0.3 | 较确定，略有变化 | 问答、分析 |
| 0.7 | 平衡（默认） | 一般对话 |
| 1.0 | 较随机 | 创意写作 |
| 1.5-2.0 | 非常随机 | 头脑风暴（可能产生胡言乱语） |

#### max_tokens

限制模型输出的最大 token 数（不包含输入）。

```python
# 短回复
response = client.chat.completions.create(
    model="...", messages=messages, max_tokens=100,
)

# 长回复
response = client.chat.completions.create(
    model="...", messages=messages, max_tokens=4096,
)
```

注意：如果输出被 max_tokens 截断，`finish_reason` 会是 `"length"` 而非 `"stop"`。

#### stop（停止词）

```python
response = client.chat.completions.create(
    model="...", messages=messages,
    stop=["\n\n", "用户："],  # 遇到这些字符串就停止生成
)
```

#### presence_penalty / frequency_penalty

- `presence_penalty`：鼓励模型谈论新话题（正值 = 更多新话题）
- `frequency_penalty`：减少重复用词（正值 = 更少重复）

---

## 4. 返回值结构详解

### 非流式返回（stream=False）

```python
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "你好"}],
)
```

返回的 `response` 对象结构：

```
ChatCompletion
├── id: str                     # 请求唯一 ID
│   例: "chatcmpl-abc123"
│
├── object: str                 # 固定值 "chat.completion"
│
├── created: int                # 创建时间（Unix 时间戳）
│   例: 1717987200
│
├── model: str                  # 实际使用的模型
│   例: "deepseek-v4-flash"
│
├── choices: list[Choice]       # 回复列表（通常只有1个）
│   └── Choice
│       ├── index: int          # 候选编号（0, 1, 2...）
│       │
│       ├── message: Message    # ← 最重要的字段
│       │   ├── role: str       # 固定为 "assistant"
│       │   ├── content: str    # ← 模型的回复文本
│       │   └── tool_calls: list[ToolCall] | None  # 工具调用请求
│       │
│       ├── finish_reason: str  # 停止原因
│       │   ├── "stop"          # 正常结束
│       │   ├── "length"        # 达到 max_tokens 限制
│       │   ├── "tool_calls"    # 模型请求调用工具
│       │   └── "content_filter"# 内容被安全过滤
│       │
│       └── logprobs: None      # 对数概率（高级功能，一般不用）
│
├── usage: CompletionUsage      # ← Token 用量统计
│   ├── prompt_tokens: int      # 输入 token 数（你发给 API 的）
│   ├── completion_tokens: int  # 输出 token 数（模型生成的）
│   └── total_tokens: int       # 总计（输入 + 输出）
│
└── system_fingerprint: str     # 系统指纹（用于可复现性）
```

### 代码示例：提取返回值

```python
# 获取回复文本
reply = response.choices[0].message.content

# 获取 token 用量
input_tokens = response.usage.prompt_tokens
output_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens

# 获取停止原因
reason = response.choices[0].finish_reason
if reason == "stop":
    print("正常结束")
elif reason == "length":
    print("输出被截断，考虑增大 max_tokens")
elif reason == "tool_calls":
    print("模型请求调用工具")

# 获取请求 ID（用于调试和日志）
request_id = response.id
```

### 流式返回（stream=True）

流式模式下，返回的不是 `ChatCompletion`，而是一个**迭代器**：

```python
stream = client.chat.completions.create(
    model="...", messages=messages, stream=True,
)

for chunk in stream:
    # 每个 chunk 的结构：
    # chunk.choices[0].delta.content  ← 本次新增的一小段文本
    # chunk.choices[0].finish_reason  ← 最后一个 chunk 才有值
    pass
```

详见 [第6节 SSE 流式输出](#6-sse-流式输出)。

---

## 5. messages 数组详解

### 消息角色

| 角色 | 说明 | 示例 |
|------|------|------|
| `system` | 系统指令，定义 AI 的行为方式 | "你是一个翻译助手" |
| `user` | 用户输入 | "帮我翻译这句话" |
| `assistant` | AI 之前的回复 | "好的，翻译如下..." |
| `tool` | 工具执行结果 | "当前时间: 2024-01-01" |

### 消息格式

```python
messages = [
    # 系统消息（通常放在最前面，只需一条）
    {
        "role": "system",
        "content": "你是一个有帮助的 AI 助手，请用中文回答。"
    },

    # 用户消息
    {
        "role": "user",
        "content": "你好"
    },

    # 助手消息（AI 的回复，用于构建对话历史）
    {
        "role": "assistant",
        "content": "你好！有什么可以帮你的？"
    },

    # 工具结果（Function Calling 时使用）
    {
        "role": "tool",
        "tool_call_id": "call_abc123",  # 对应 tool_call 的 ID
        "content": "2024-01-01 12:00:00"
    },
]
```

### 对话历史管理

```python
# 完整历史（AI 能"记住"所有内容）
messages = [system, user1, assistant1, user2, assistant2, user3]

# 截断历史（只保留最近 2 轮）
messages = [system] + messages[-4:]  # -4 = 最近 2 轮 × 2 条/轮

# 清空历史（AI 失忆，从头开始）
messages = [system]
```

---

## 6. SSE 流式输出

### 什么是 SSE？

**SSE（Server-Sent Events）** 是一种 HTTP 长连接技术，服务器可以持续向客户端推送数据。

在 LLM 场景中：
- 非流式：等模型生成完所有内容，一次性返回 → 用户等很久才看到回复
- 流式：模型每生成几个字就立即推送 → 用户看到"打字机"效果

### Python SDK 中的流式调用

```python
stream = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "讲个笑话"}],
    stream=True,  # ← 关键参数
)
```

### 逐块处理

```python
full_reply = ""

for chunk in stream:
    # chunk.choices[0].delta 包含本次新增的内容
    delta = chunk.choices[0].delta

    if delta.content:
        # 打印新增内容（不换行）
        print(delta.content, end="", flush=True)
        full_reply += delta.content

    # 最后一个 chunk 会有 finish_reason
    if chunk.choices[0].finish_reason:
        reason = chunk.choices[0].finish_reason
        # reason 可能是 "stop", "length", "tool_calls"

print()  # 最后换行
print(f"完整回复: {full_reply}")
```

### 流式 vs 非流式对比

| 特性 | 非流式 (stream=False) | 流式 (stream=True) |
|------|---------------------|-------------------|
| 返回类型 | `ChatCompletion` 对象 | `Stream[ChatCompletionChunk]` 迭代器 |
| 响应速度 | 等全部生成完才返回 | 立即开始返回 |
| 用户体验 | 等待时间长 | 打字机效果，体验好 |
| Token 统计 | `response.usage` 直接可用 | 最后一个 chunk 或需手动累计 |
| 适用场景 | 后端处理、不需要展示过程 | 面向用户的聊天界面 |

### 手动累计 Token（流式模式）

流式模式下 `usage` 可能不直接可用，需要手动估算：

```python
full_reply = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        full_reply += chunk.choices[0].delta.content

# 粗略估算：1 个中文字 ≈ 1.5 tokens，1 个英文单词 ≈ 1 token
estimated_output_tokens = len(full_reply) * 0.7  # 中文粗略估算
```

---

## 7. 查询可用模型列表

### 基本用法

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 查询所有可用模型
models = client.models.list()

for model in models.data:
    print(f"  {model.id}")
```

### 返回值结构

```
ModelList
├── object: "list"
└── data: list[Model]
    └── Model
        ├── id: str          # 模型名称（用于 API 调用的 model 参数）
        │   例: "qwen-turbo", "deepseek-v4-flash"
        ├── object: "model"
        ├── created: int     # 创建时间
        └── owned_by: str    # 模型所有者
```

### 实用工具函数

```python
def list_available_models():
    """列出当前 API 支持的所有模型"""
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        model_ids.sort()

        print(f"可用模型（共 {len(model_ids)} 个）：")
        for mid in model_ids:
            print(f"  - {mid}")

        return model_ids

    except Exception as e:
        print(f"查询失败：{e}")
        return []


def check_model_available(model_name: str) -> bool:
    """检查某个模型是否可用"""
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        return model_name in model_ids
    except:
        return False
```

### 注意

- 不是所有服务商都实现了 `/models` 端点
- 有些代理服务可能返回空列表或不支持此 API
- 建议以服务商文档为准，`models.list()` 作为辅助验证

---

## 8. Token 与成本

### 什么是 Token？

Token 是 LLM 处理文本的基本单位。文本会被分词器（Tokenizer）切割成 token。

| 文本类型 | 粗略换算 |
|---------|---------|
| 英文 | 1 token ≈ 0.75 个单词 ≈ 4 个字符 |
| 中文 | 1 token ≈ 0.5-1.5 个汉字 |
| 代码 | 视语言而定，通常比自然语言更费 token |

### Token 计数

```python
# 方法1：从 API 返回值获取（最准确）
usage = response.usage
print(f"输入: {usage.prompt_tokens}, 输出: {usage.completion_tokens}")

# 方法2：使用 tiktoken 库本地估算（OpenAI 模型适用）
import tiktoken
encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens = encoder.encode("你好世界 Hello World")
print(f"Token 数: {len(tokens)}")
```

### 成本计算

```python
def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    估算 API 调用成本（美元）

    注意：价格会变动，请以服务商官网为准
    """
    # 每百万 token 的价格（美元）—— 示例价格
    PRICES = {
        "gpt-3.5-turbo":     {"input": 0.50, "output": 1.50},
        "gpt-4":             {"input": 30.0, "output": 60.0},
        "deepseek-chat":     {"input": 0.14, "output": 0.28},
        "deepseek-v4-flash": {"input": 0.00, "output": 0.00},  # 免费
        "qwen-turbo":        {"input": 0.30, "output": 0.60},
    }

    price = PRICES.get(model, {"input": 1.0, "output": 2.0})

    input_cost = (input_tokens / 1_000_000) * price["input"]
    output_cost = (output_tokens / 1_000_000) * price["output"]

    return input_cost + output_cost
```

### Token 优化技巧

1. **精简 system prompt** — 不需要长篇大论，简洁即可
2. **截断对话历史** — 只保留最近 N 轮
3. **避免重复发送** — 相同内容可以缓存
4. **选择合适的 max_tokens** — 不需要长回复时设小一点

---

## 9. 常用参数速查表

### create() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | str | 必填 | 模型名称 |
| `messages` | list | 必填 | 对话消息列表 |
| `stream` | bool | False | 是否流式输出 |
| `temperature` | float | 1.0 | 温度（0-2） |
| `top_p` | float | 1.0 | 核采样概率 |
| `max_tokens` | int | 模型默认 | 最大输出 token 数 |
| `n` | int | 1 | 生成几个候选 |
| `stop` | str/list | None | 停止词 |
| `presence_penalty` | float | 0 | 存在惩罚（-2~2） |
| `frequency_penalty` | float | 0 | 频率惩罚（-2~2） |
| `tools` | list | None | 工具定义列表 |
| `tool_choice` | str/dict | None | 工具选择策略 |
| `timeout` | float | 600 | 超时秒数 |

### response 属性

| 属性 | 说明 |
|------|------|
| `response.choices[0].message.content` | 模型回复文本 |
| `response.choices[0].message.role` | 固定 "assistant" |
| `response.choices[0].message.tool_calls` | 工具调用请求列表 |
| `response.choices[0].finish_reason` | 停止原因 |
| `response.usage.prompt_tokens` | 输入 token 数 |
| `response.usage.completion_tokens` | 输出 token 数 |
| `response.usage.total_tokens` | 总 token 数 |
| `response.id` | 请求 ID |
| `response.model` | 实际使用的模型 |

---

## 10. 常见错误与处理

### 错误类型

```python
from openai import (
    AuthenticationError,   # 401: API Key 无效
    RateLimitError,        # 429: 请求过于频繁
    BadRequestError,       # 400: 请求参数错误
    NotFoundError,         # 404: 模型不存在
    APITimeoutError,       # 超时
    APIConnectionError,    # 网络连接失败
    InternalServerError,   # 500: 服务器内部错误
)
```

### 完整错误处理模板

```python
from openai import OpenAI, AuthenticationError, RateLimitError, BadRequestError, APITimeoutError, APIConnectionError

def safe_chat(messages: list) -> str:
    """带完整错误处理的 API 调用"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    except AuthenticationError:
        print("[401] 认证失败：API Key 无效或已过期")
        print("  请检查 .env 中的 LLM_API_KEY")

    except RateLimitError:
        print("[429] 请求限流：调用太频繁或余额不足")
        print("  请稍后重试，或检查账户余额")

    except BadRequestError as e:
        print(f"[400] 请求错误：{e}")
        print("  检查 messages 格式、model 名称、参数范围")

    except APITimeoutError:
        print("[超时] 请求超时，请检查网络连接或增大 timeout")

    except APIConnectionError as e:
        print(f"[连接] 无法连接到 API 服务器：{e}")
        print("  检查 base_url 是否正确，网络是否通畅")

    except Exception as e:
        print(f"[未知] 发生错误：{e}")

    return ""
```

### 常见错误场景

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `AuthenticationError` | API Key 无效 | 检查 Key 是否正确 |
| `RateLimitError` | 频率超限 / 余额不足 | 等待 / 充值 |
| `BadRequestError` | messages 格式错误 | 检查 role 和内容 |
| `NotFoundError` | 模型名称不对 | 用 `models.list()` 查询 |
| `APITimeoutError` | 网络慢或模型大 | 增大 timeout |
| `finish_reason="length"` | 输出被截断 | 增大 max_tokens |

---

## 11. Python SDK 常用 API 速查

### 安装

```bash
pip install openai python-dotenv
```

### 导入

```python
from openai import OpenAI
```

### 常用方法

```python
# 创建客户端
client = OpenAI(api_key="...", base_url="...")

# 对话补全（非流式）
response = client.chat.completions.create(model="...", messages=[...])

# 对话补全（流式）
stream = client.chat.completions.create(model="...", messages=[...], stream=True)

# 查询模型列表
models = client.models.list()

# 文本向量化（Phase 2 用）
response = client.embeddings.create(model="...", input="你好")
```

### embeddings API（Phase 2 预览）

```python
# 单条文本向量化
response = client.embeddings.create(
    model="text-embedding-ada-002",  # 或其他 Embedding 模型
    input="这是一段文本",
)

embedding = response.data[0].embedding  # 高维向量（如 1536 维）
print(f"向量维度: {len(embedding)}")

# 批量向量化
response = client.embeddings.create(
    model="text-embedding-ada-002",
    input=["文本1", "文本2", "文本3"],
)

for item in response.data:
    print(f"文本 {item.index}: 向量维度 {len(item.embedding)}")
```
