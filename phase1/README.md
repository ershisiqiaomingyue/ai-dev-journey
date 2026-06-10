# 第一阶段：基础与手写 Agent（第1-4周）

## 目标

从零手写，理解 LLM API、Function Calling 和 ReAct 模式。

## 脚本列表

| 文件 | 周次 | 学习要点 |
|------|------|---------|
| `01_hello_agent.py` | W1 | 第一次 API 调用，理解 token 用量和 system prompt |
| `02_chat_loop.py` | W2 | 多轮对话，理解上下文窗口 |
| `03_function_call.py` | W2 | 通过 Function Calling 实现工具调用 |
| `04_react_agent.py` | W3 | ReAct 循环：推理 → 行动 → 观察 → 重复 |
| `05_file_assistant.py` | W4 | 综合项目：一个能读写文件的 Agent |

## 运行方式

```bash
# 1. 安装依赖（在项目根目录执行）
pip install openai python-dotenv

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY

# 3. 运行
python phase1/01_hello_agent.py
```

## 核心概念

- **System prompt（系统提示词）**：每次对话开始时给模型的指令，定义模型的行为方式
- **Token**：LLM 处理文本的基本单位（大约 1 token ≈ 0.75 个英文单词 或 0.5 个汉字）
- **Temperature（温度）**：控制输出的随机性（0 = 确定性，1 = 更有创造性）
- **Function Calling（函数调用）**：模型可以结构化地请求调用外部工具，而非只输出纯文本
