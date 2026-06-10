# 第一阶段：基础与手写 Agent（第1-4周）

## 目标

从零手写，理解 LLM API、Function Calling 和 ReAct 模式。

## 任务列表

- [x] `01_hello_agent.py` — 第一次 API 调用，理解 token 用量和 system prompt
- [x] `02_chat_loop.py` — 多轮对话、SSE 流式输出、对话历史保存
- [x] `03_function_call.py` — 通过 Function Calling 实现工具调用
- [ ] `04_react_agent.py` — ReAct 循环：推理 → 行动 → 观察 → 重复
- [ ] `05_file_assistant.py` — 综合项目：一个能读写文件的 Agent

## 运行方式

```bash
# 1. 安装依赖（在项目根目录执行）
pip install openai python-dotenv

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY

# 3. 运行
python phase1/01_hello_agent.py
python phase1/02_chat_loop.py
```

---

# 知识手册：LLM API 基础（01-02）

> 涵盖 Phase 1 前两个脚本中涉及的所有 API 知识点，可作为日常开发速查手册。

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

### AI 的"记忆"原理

LLM 本身**没有记忆**，每次 API 调用都是独立的。之所以能"记住"上下文，是因为我们把完整历史每次都发给 API：

```python
# 第3轮对话时，实际发给 API 的内容：
messages = [
    {"role": "system", "content": "你是一个助手"},        # 每次都带
    {"role": "user", "content": "我叫小明"},              # 第1轮 ← 每次都带
    {"role": "assistant", "content": "你好小明！"},       # 第1轮 ← 每次都带
    {"role": "user", "content": "我喜欢Python"},          # 第2轮 ← 每次都带
    {"role": "assistant", "content": "Python很好！"},     # 第2轮 ← 每次都带
    {"role": "user", "content": "我叫什么？"},            # 第3轮（当前问题）
]
# AI 看到完整历史，所以能回答"你叫小明"
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

历史越长 → token 消耗越多 → 成本越高 → 响应越慢。所以需要截断策略。

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

### 常用方法

```python
from openai import OpenAI

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
    model="text-embedding-ada-002",
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

---

# 知识手册：Function Calling 与工具调用（03）

## 12. Function Calling 完整流程

### 核心概念

Function Calling 让 LLM 可以**结构化地请求调用外部工具**，而不是只输出纯文本。

```
用户提问 → LLM 判断需要工具 → 返回 tool_calls（结构化请求）
    → 你的代码执行工具 → 把结果回传给 LLM → LLM 生成最终回复
```

### 完整流程图

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│  用户    │───▶│  LLM    │───▶│ 你的代码  │───▶│  LLM     │
│ "几点了" │    │ 判断需要 │    │ 执行工具  │    │ 生成回复  │
│         │    │ 调用工具 │    │          │    │          │
└─────────┘    └─────────┘    └──────────┘    └──────────┘
                    │                               │
                    ▼                               ▼
              tool_calls                      "现在是下午3点"
              [{name: "get_time"}]
```

### 第一步：定义工具函数

```python
def get_current_time():
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_numbers(a: int, b: int):
    """计算两个数字的和"""
    return a + b

# 工具名称 → 函数的映射（用于执行时查找）
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "add_numbers": add_numbers,
}
```

### 第二步：定义工具的 JSON Schema

这是告诉 LLM "你有什么工具可以用"：

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",       # 工具名称（对应函数名）
            "description": "获取当前的日期和时间",  # 描述（LLM 用来判断何时调用）
            "parameters": {
                "type": "object",
                "properties": {},              # 无参数
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
                "required": ["a", "b"],        # 必填参数
            },
        },
    },
]
```

### 第三步：调用 API 并处理 tool_calls

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,           # ← 传入工具定义
)

message = response.choices[0].message

# 检查 LLM 是否要调用工具
if message.tool_calls:
    # LLM 请求调用工具
    for tool_call in message.tool_calls:
        print(f"工具名: {tool_call.function.name}")
        print(f"参数: {tool_call.function.arguments}")
        print(f"调用ID: {tool_call.id}")
```

### tool_calls 返回值结构

```
message.tool_calls: list[ToolCall]
└── ToolCall
    ├── id: str              # 唯一调用 ID（回传结果时必须带上）
    │   例: "call_abc123"
    │
    ├── type: str            # 固定 "function"
    │
    └── function: Function
        ├── name: str        # 工具名称
        │   例: "add_numbers"
        │
        └── arguments: str   # 参数（JSON 字符串，需要 parse）
            例: '{"a": 10, "b": 20}'
```

### 第四步：执行工具并回传结果

```python
# 1. 把 assistant 消息（含 tool_calls）加入历史
messages.append(message)

# 2. 逐个执行工具
for tool_call in message.tool_calls:
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)  # 解析 JSON 字符串

    # 执行函数
    result = TOOL_FUNCTIONS[func_name](**func_args)

    # 3. 把结果以 "tool" 角色回传
    messages.append({
        "role": "tool",                      # ← 必须是 "tool"
        "tool_call_id": tool_call.id,        # ← 必须匹配对应的调用 ID
        "content": str(result),              # ← 结果必须是字符串
    })

# 4. 再次调用 API，让 LLM 根据工具结果生成回复
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,
)
reply = response.choices[0].message.content
```

### tool_choice 参数

控制 LLM 是否使用工具：

```python
# 让 LLM 自己决定（默认）
client.chat.completions.create(tools=tools, tool_choice="auto")

# 强制使用工具（必须调用至少一个）
client.chat.completions.create(tools=tools, tool_choice="required")

# 强制不使用工具
client.chat.completions.create(tools=tools, tool_choice="none")

# 强制使用某个特定工具
client.chat.completions.create(
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_current_time"}}
)
```

---

# 知识手册：工具递进调用与 Agent 编排（04）

> 这是 AI Agent 开发中**最核心**的知识点。

## 13. 递进调用：第一个工具的结果如何喂给第二个工具？

### 问题的本质

```
用户："帮我查一下 config.json 有多少行，然后算 行数 * 3 等于多少"

理想流程：
  步骤1：read_file("config.json") → 得到文件内容
  步骤2：count_lines(文件内容)    → 得到 42 行
  步骤3：calculate("42 * 3")      → 得到 126
  步骤4：回复用户 "config.json 有 42 行，乘以 3 等于 126"
```

**关键问题**：步骤2 依赖步骤1 的结果，步骤3 依赖步骤2 的结果。这怎么做？

### 答案：你不需要手动编排！LLM 自己会决定调用链

这正是 **ReAct 循环**解决的核心问题。你的代码只需要做一件事：

```
while 模型还在请求工具:
    执行工具 → 把结果回传 → 让模型决定下一步
```

模型看到上一步的结果后，会**自己决定**下一步该调用什么工具、传什么参数。

### 实际执行过程详解

以 "查 config.json 行数，算行数 * 3" 为例：

```
═══════════════════════════════════════════════════════
第1轮 API 调用
═══════════════════════════════════════════════════════
发给 LLM 的 messages:
  [system] 你是一个助手，可以使用工具
  [user]   查 config.json 行数，算行数 * 3

LLM 返回:
  tool_calls: [{name: "read_file", args: {"path": "config.json"}}]

═══════════════════════════════════════════════════════
你的代码执行工具
═══════════════════════════════════════════════════════
read_file("config.json") → "server:\n  port: 8080\n  host: localhost\n..."

把结果回传到 messages:
  [tool] tool_call_id=call_1, content="server:\n  port: 8080\n..."

═══════════════════════════════════════════════════════
第2轮 API 调用（完整历史再次发给 LLM）
═══════════════════════════════════════════════════════
发给 LLM 的 messages:
  [system]    你是一个助手，可以使用工具
  [user]      查 config.json 行数，算行数 * 3
  [assistant] tool_calls: [read_file("config.json")]
  [tool]      "server:\n  port: 8080\n  host: localhost\n..."  ← 第1步结果

LLM 看到了文件内容，自己数出行数，返回:
  tool_calls: [{name: "calculate", args: {"expression": "3 * 3"}}]
              ↑ LLM 判断文件有 3 行，请求计算 3*3

═══════════════════════════════════════════════════════
你的代码执行工具
═══════════════════════════════════════════════════════
calculate("3 * 3") → "9"

把结果回传到 messages:
  [tool] tool_call_id=call_2, content="9"

═══════════════════════════════════════════════════════
第3轮 API 调用
═══════════════════════════════════════════════════════
发给 LLM 的 messages:
  [system]    你是一个助手
  [user]      查 config.json 行数，算行数 * 3
  [assistant] tool_calls: [read_file(...)]
  [tool]      "server:\n  port: 8080\n..."
  [assistant] tool_calls: [calculate("3 * 3")]
  [tool]      "9"                                                ← 第2步结果

LLM 看到所有步骤的结果，不再请求工具，直接回复:
  content: "config.json 有 3 行，3 × 3 = 9"
```

### 核心代码：ReAct 循环

```python
def run_agent(user_query: str, tools: list, tool_functions: dict, max_steps: int = 10):
    """
    ReAct Agent 核心循环

    关键：你不需要编排工具调用顺序！
    LLM 看到每步结果后，自己决定下一步做什么。
    你只需要：执行工具 → 回传结果 → 让 LLM 继续。
    """
    messages = [
        {"role": "system", "content": "你是一个智能助手，可以使用工具辅助回答。"},
        {"role": "user", "content": user_query},
    ]

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=tools,
        )
        message = response.choices[0].message

        # ★ 终止条件：LLM 不再请求工具 → 任务完成
        if not message.tool_calls:
            return message.content

        # 把 assistant 消息（含 tool_calls 请求）加入历史
        messages.append(message)

        # 执行每个工具调用，把结果回传
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            result = tool_functions[func_name](**func_args)

            # ★ 关键：结果以 "tool" 角色回传，LLM 下一步能看到
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "达到最大步数限制"
```

## 14. 工具调用的三种编排模式

### 模式一：顺序调用（Sequential）

最常见的模式，工具之间有依赖关系，前一个的输出是后一个的输入。

```
read_file → count_lines → calculate
     ↓            ↓            ↓
  文件内容      行数 42      结果 126
```

**实现方式**：就是 ReAct 循环，LLM 自动编排。

```python
# 你不需要写任何编排代码！
# LLM 看到 read_file 的结果后，自己决定调用 count_lines
# 看到 count_lines 的结果后，自己决定调用 calculate
# 这就是 ReAct 循环的核心价值
```

### 模式二：并行调用（Parallel）

多个工具之间没有依赖，可以同时调用。LLM 会在**一次返回中请求多个工具**。

```
用户："分别查 config.json 和 main.py 的行数"

LLM 一次返回两个 tool_calls:
  tool_calls: [
    {name: "read_file", args: {"path": "config.json"}},  ← 无依赖
    {name: "read_file", args: {"path": "main.py"}},      ← 无依赖
  ]
```

**实现方式**：

```python
for tool_call in message.tool_calls:
    # 所有 tool_calls 在同一次循环中执行
    result = execute_tool(tool_call)
    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

# 然后一次性把两个结果都回传给 LLM
```

```
并行执行示意：
  read_file("config.json") ──→ "3行"  ─┐
  read_file("main.py")     ──→ "150行" ─┤
                                        ▼
                              LLM 看到两个结果
                              生成回复："config.json 有3行，main.py 有150行"
```

### 模式三：条件分支（Conditional）

LLM 根据上一步的结果，选择不同的下一步工具。

```
用户："检查服务状态，如果有问题就重启"

步骤1: check_status() → "error: port 8080 in use"
步骤2: LLM 看到错误 → restart_service()     ← 因为出错才走这条路
步骤3: LLM 看到成功 → 回复用户
```

**实现方式**：还是 ReAct 循环，LLM 自己判断条件。

```python
# 你不需要写 if/else！
# LLM 看到 check_status 返回了错误信息
# 它会自己判断"需要重启"，然后请求 restart_service
# 如果 check_status 返回 "running"，LLM 会直接回复"服务正常"
```

## 15. 市面上主流产品的工具调用方式

### 方式一：纯 ReAct 循环（大多数产品使用）

**代表产品**：OpenAI Codex、ChatGPT、Claude、Cursor、GitHub Copilot

```
用户输入 → LLM → tool_calls? → 执行 → 回传 → LLM → tool_calls? → ... → 最终回复
              ↑                                                        │
              └────────────────── while 循环 ──────────────────────────┘
```

**优点**：
- 实现简单（一个 while 循环就够）
- LLM 自己编排，不需要你写逻辑
- 灵活，能处理各种任务组合

**缺点**：
- 依赖 LLM 的推理能力（弱模型可能编排不好）
- 不可控（LLM 可能走弯路、多调用不必要的工具）
- 调试困难（不确定 LLM 下一步会做什么）

**你项目中的 04_react_agent.py 就是这种方式。**

### 方式二：Plan-and-Execute（先规划后执行）

**代表产品**：LangGraph Agent、AutoGPT、部分企业级 Agent

```
用户输入 → Planner（LLM 制定步骤列表）→ Executor（逐步执行）→ Reviewer（检查结果）→ 回复
```

```python
# 步骤1：让 LLM 制定计划
plan_response = client.chat.completions.create(
    messages=[{"role": "user", "content": f"把以下任务分解为步骤：{task}"}]
)
steps = parse_steps(plan_response)  # ["读取文件", "统计行数", "计算结果"]

# 步骤2：逐步执行（每步可以调用工具）
results = []
for step in steps:
    result = execute_step(step, tools, previous_results=results)
    results.append(result)

# 步骤3：汇总结果
final = summarize(results)
```

**优点**：
- 可控性强（你知道 LLM 打算做什么）
- 可以人工介入（执行前审核计划）
- 适合复杂多步任务

**缺点**：
- 多一次 API 调用（规划本身消耗 token）
- 计划可能不准确（执行中可能需要调整）

### 方式三：固定工作流（Workflow / Pipeline）

**代表产品**：部分企业应用、特定场景 Bot

```
用户输入 → 步骤A（固定） → 步骤B（固定） → 步骤C（固定） → 回复
```

```python
# 步骤固定，不依赖 LLM 编排
def fixed_workflow(user_input):
    # 步骤1：总是先搜索
    search_results = search_knowledge_base(user_input)

    # 步骤2：总是用搜索结果生成回答
    answer = generate_answer(user_input, search_results)

    # 步骤3：总是做安全检查
    safe_answer = safety_check(answer)

    return safe_answer
```

**优点**：完全可控、可预测
**缺点**：不灵活、只适合固定场景

### 方式四：混合模式（主流产品的实际做法）

**代表产品**：Cursor、Windsurf、Devin、Qoder 等 AI 编程助手

实际产品中，通常是多种方式混合：

```
┌─────────────────────────────────────────────────────┐
│                    混合架构                           │
│                                                     │
│  外层：Plan-and-Execute（高层任务分解）                │
│  ├── 子任务1：ReAct 循环（灵活执行）                  │
│  ├── 子任务2：固定工作流（如代码格式化）               │
│  └── 子任务3：ReAct 循环 + 人工确认（修改文件前）      │
│                                                     │
│  底层：统一工具执行层                                 │
│  ├── 工具注册表（所有可用工具）                       │
│  ├── 权限控制（哪些工具需要用户确认）                 │
│  └── 结果缓存（避免重复调用相同工具）                 │
└─────────────────────────────────────────────────────┘
```

以 Cursor 为例：
```
用户："帮我修复这个 bug"

1. [Plan] LLM 分析 bug，制定修复计划
   → "需要：读取报错文件 → 分析原因 → 修改代码 → 运行测试"

2. [ReAct] 读取文件（自动执行）
   → read_file("app.py") → 文件内容

3. [ReAct] 分析原因（LLM 根据文件内容判断）
   → "第 42 行有类型错误"

4. [ReAct + 人工确认] 修改代码
   → edit_file("app.py", line=42, new_code="...")
   → ⚠️ 弹出确认框："是否修改第42行？"
   → 用户确认 → 执行修改

5. [固定工作流] 运行测试
   → run_command("pytest") → 测试结果

6. [ReAct] 如果测试失败，回到步骤3重新分析
```

## 16. 递进调用的关键设计模式

### 模式一：工具结果作为下一步参数

```python
# LLM 自动编排的过程：
#
# 第1步: LLM 请求 search_code("login")
#        → 结果: "login 函数在 auth.py 第 15 行"
#
# 第2步: LLM 看到结果，请求 read_file("auth.py", start=15, end=30)
#        → 结果: "def login(user, password): ..."
#
# 第3步: LLM 看到代码，请求 edit_file("auth.py", line=15, ...)
#        → 结果: "修改成功"
```

### 模式二：累积上下文

每一步的结果都累积在 messages 中，LLM 能看到所有历史：

```python
# messages 的增长过程：
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "修复 login 函数的 bug"},

    # 第1步
    {"role": "assistant", "content": None, "tool_calls": [search_code(...)]},
    {"role": "tool", "content": "login 在 auth.py:15"},

    # 第2步（LLM 能看到第1步的结果）
    {"role": "assistant", "content": None, "tool_calls": [read_file(...)]},
    {"role": "tool", "content": "def login(user, pw):\n    ..."},

    # 第3步（LLM 能看到第1、2步的所有结果）
    {"role": "assistant", "content": None, "tool_calls": [edit_file(...)]},
    {"role": "tool", "content": "修改成功"},

    # 最终（LLM 综合所有步骤结果生成回复）
    {"role": "assistant", "content": "已修复 login 函数的类型检查 bug..."},
]
```

### 模式三：错误恢复

LLM 看到工具报错后，可以尝试其他方式：

```
步骤1: read_file("config.yaml")  → "错误：文件不存在"
步骤2: LLM 看到错误 → search_file("config")  → "找到: config.json"
步骤3: LLM 换了文件 → read_file("config.json") → 成功
```

### 模式四：结果验证

LLM 执行操作后验证结果：

```
步骤1: write_file("test.py", "print('hello')")  → "写入成功"
步骤2: run_command("python test.py")             → "hello"
步骤3: LLM 验证输出正确 → 回复用户
```

## 17. 实际开发中的注意事项

### 上下文膨胀问题

每步工具结果都会加入 messages，导致上下文快速膨胀：

```
一个文件内容  ≈ 2000-10000 tokens
一次搜索结果  ≈ 3000-8000 tokens
一次命令输出  ≈ 1000-5000 tokens
10步操作后    ≈ 30000-50000 tokens
```

**解决方案**：

```python
# 1. 截断工具结果（只保留关键部分）
def truncate_result(result: str, max_length: int = 2000) -> str:
    if len(result) > max_length:
        return result[:max_length] + f"\n... (已截断，共 {len(result)} 字符)"
    return result

# 2. 压缩历史（把早期工具结果替换为摘要）
def compress_old_tool_results(messages: list) -> list:
    for msg in messages:
        if msg["role"] == "tool" and len(msg["content"]) > 500:
            msg["content"] = f"[之前获取了结果，长度 {len(msg['content'])} 字符]"
    return messages

# 3. 限制最大步数
MAX_STEPS = 15  # 防止无限循环
```

### 工具结果的格式

工具返回的 content 必须是字符串。复杂数据需要序列化：

```python
def search_files(query: str) -> str:
    results = [{"file": "a.py", "line": 10}, {"file": "b.py", "line": 20}]
    return json.dumps(results, ensure_ascii=False)  # 序列化为 JSON 字符串

def read_file(path: str) -> str:
    content = Path(path).read_text()
    # 大文件截断
    if len(content) > 5000:
        return content[:5000] + f"\n...(截断，共{len(content)}字符)"
    return content
```

### 工具描述的写法影响 LLM 调用准确率

```python
# ❌ 差的描述：LLM 不确定何时调用
{"name": "read", "description": "读取"}

# ✅ 好的描述：LLM 清楚知道何时调用、传什么参数
{
    "name": "read_file",
    "description": "读取指定路径的文件内容。参数 path 为文件路径（相对于项目根目录）。如果文件不存在会返回错误信息。返回文件的全部内容（大文件会被截断）。",
}
```

### 工具粒度设计

```python
# ❌ 太粗（一个工具做太多事）
{"name": "manage_file", "description": "管理文件（读/写/删除/移动）"}

# ✅ 适中（每个工具做一件事）
{"name": "read_file", "description": "读取文件内容"}
{"name": "write_file", "description": "写入文件内容"}
{"name": "delete_file", "description": "删除文件"}
{"name": "list_files", "description": "列出目录内容"}

# ❌ 太细（参数太多，LLM 容易传错）
{"name": "search", "description": "搜索", "parameters": {15个参数}}

# ✅ 好的粒度
{"name": "search_code", "description": "按关键词搜索代码", "parameters": {"query": "搜索词"}}
{"name": "search_files", "description": "按文件名模式搜索", "parameters": {"pattern": "glob模式"}}
```

## 18. 总结：工具调用方式对比

| 方式 | 实现复杂度 | 灵活性 | 可控性 | 适用场景 |
|------|-----------|--------|--------|---------|
| 纯 ReAct 循环 | 低 | 高 | 低 | 通用 Agent、简单任务 |
| Plan-and-Execute | 中 | 高 | 中 | 复杂多步任务 |
| 固定工作流 | 低 | 低 | 高 | 特定场景、企业应用 |
| 混合模式 | 高 | 高 | 高 | 生产级产品 |

**学习建议**：先掌握纯 ReAct（你现在的 04_react_agent.py），理解"LLM 自己编排工具调用链"的核心原理。到 Phase 3 学 LangGraph 时，再学习 Plan-and-Execute 和混合模式。
