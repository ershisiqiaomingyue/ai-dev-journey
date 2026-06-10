# AI Dev Journey — 从 Android 工程师到 AI Agent 开发者

## 阶段路线

| 阶段  | 主题 | 关键产物 |
|------|------|---------|
| [Phase 1](./phase1/)  | 基础与手写 Agent | `file_agent.py` —— 能调用工具的 ReAct 循环 |
| [Phase 2](./phase2/)  | RAG 与检索 | `code_qa_agent.py` —— 回答中型代码库的结构问题 |
| [Phase 3](./phase3/)  | 框架与复杂任务 | `auto_fix_agent.py` —— 运行测试 → 读日志 → 自动修复 |
| [Phase 4](./phase4/)  | 成本优化 & 副业项目 | Telegram Bot + 知识库 RAG + 作品集 |

> 📋 详细任务清单（按节奏推进，无固定日期）：[`tasks/AI Agent 转型全任务清单.md`](./tasks/AI%20Agent%20转型全任务清单.md)

## 快速上手

```bash
# 1. 克隆 & 安装
git clone https://github.com/ershisiqiaomingyue/ai-dev-journey.git
cd ai-dev-journey
pip install -e ".[phase2,phase3,phase4]"

# 2. 配置 API Key
# 编辑 .env，填入 LLM_API_KEY 和 LLM_BASE_URL
# 推荐：DeepSeek / 阿里云百炼（OpenAI 兼容协议，免费额度够用）

# 3. 跑第一个 Agent
python phase1/01_hello_agent.py
```

## 每个 phase 在干嘛

### Phase 1 — 基础与手写 Agent
目标：跑通 API，手写一个能调用工具的简单 ReAct Agent。
- 学会 OpenAI 兼容协议、Function Calling、ReAct 循环
- 不用任何框架，**纯手写**理解每一行
- 里程碑：`file_agent.py`（200 行内的文件操作助手）

→ 详细：[phase1/README.md](./phase1/README.md)（含 API 速查手册）

### Phase 2 — RAG 与检索
目标：让 Agent 能读取你的代码项目，回答问题。
- Chroma / LanceDB 向量库、文本切块、rerank
- 把 phase1 的能力升级为"问我的代码"
- 里程碑：`code_qa_agent.py`，命令行 `ask "哪里定义了 User 类"`

### Phase 3 — 框架与复杂任务
目标：用 LangGraph 构建能完成多步任务的 Agent。
- StateGraph、Node、Edge 状态管理
- Plan-and-Execute 模式：先让模型分解任务，再逐步执行
- 多 Agent 协作（Coder + Reviewer）
- 里程碑：`auto_fix_agent.py` —— 集成 Shell、能跑测试、读错误日志、自动修复

### Phase 4 — 成本优化 & 副业级项目
目标：低成本、稳定运行，交付可展示的完整项目。
- 前缀缓存（Prefix Caching）—— 节省 50%+ token
- 模型路由：简单问题用便宜模型，复杂问题用强模型
- 可靠性工程：重试、步数限制、人工接管
- **副业项目**：
  - Telegram / Discord 代码助手 Bot
  - 垂直领域知识库 RAG Agent（基于 Android Framework 笔记）
- 作品集整理 + 简历更新 + 投出 20 份简历/10 份副业 proposal

## 设计原则

1. **手写优先于框架** —— phase1-2 不用任何 Agent 框架，理解底层后再上 LangGraph
2. **里程碑驱动** —— 每个 phase 都有一个"能跑 + 能演示"的项目，不是无止境的学习
3. **成本意识** —— 从 phase1 就开始统计 token 用量，phase4 专门优化
4. **作品即简历** —— phase4 的三个项目就是求职/接单的筹码

## 可选扩展

- 本地模型（Llama.cpp 替换 DeepSeek API）
- 用 Rust 重写 Agent 核心循环（性能极客路线）
- Multi-Agent 框架（AutoGen / CrewAI）
- 写一篇技术博客，把这个项目讲给别人听

## 📚 参考项目（学习借鉴来源）

不是从零造轮子，而是站在巨人肩膀上：

| 项目 | 借鉴的核心思想 | 落地到 |
|---|---|---|
| [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) | 工具调用自愈、Append-Only 缓存、Checkpoint、成本仪表盘 | Phase 1/2/3/4 |
| [Claude Code](https://claude.com/product/claude-code) | Plan 模式 + 审批门、人工介入 interrupt/resume | Phase 3 |
| [Codex CLI](https://github.com/openai/codex) | ripgrep 全文搜索 + 按需 RAG 的混合架构 | Phase 2 |
| LangGraph / LangChain | 状态图、Plan-and-Execute、多 Agent 编排 | Phase 3 |

**学完每个 phase 的对应借鉴点，你就理解了"为什么生产级 Agent 这么设计"**——不是凭空想象，是从真实项目里提炼的最佳实践。

## 进度跟踪

每个 phase 的子目录里都有独立的 `README.md` 记录：
- 当前任务完成度
- 踩过的坑和解决思路
- 下一个任务的计划

## License

MIT
