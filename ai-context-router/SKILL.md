---
name: ai-context-router
description: Route all context-file updates to a single source file AI-CONTEXT.md. Use when users ask to run /init or to create/modify/sync agent.md, gemini.md, or claude.md (any letter case), so the agent must update AI-CONTEXT.md first, then rewrite those files as explicit pointer notices that require reading and understanding AI-CONTEXT.md.
---

# AI Context Router

执行目标：将多 AI 终端上下文文件统一到单一事实源 `AI-CONTEXT.md`。

## 工作流

1. 识别触发请求：
- 用户提到 `/init`。
- 用户要求创建、修改、同步 `agents.md`、`gemini.md`、`claude.md`。
- 用户描述“多个 AI 上下文不一致”“需要统一提示词文件”。

2. 固定执行顺序：
- 始终先检查 `AI-CONTEXT.md` 是否存在。
- 若不存在则创建 `AI-CONTEXT.md`。
- 所有内容变更都只写入 `AI-CONTEXT.md`。
- 执行技能目录内的脚本 `scripts/sync_ai_context.sh`，并显式传入“目标项目根目录”，重写 `agents/gemini/claude` 的 `.md` 文件为“指向声明文件”。

3. 大小写规则：
- `AI-CONTEXT.md` 必须使用全大写文件名。
- `agents.md`、`gemini.md`、`claude.md` 的文件名匹配不区分大小写（例如 `AGENTS.md`、`Gemini.md` 都会被处理）。

4. 执行命令（禁止在当前项目目录盲目查找 `scripts/`）：
```bash
bash <skill_dir>/scripts/sync_ai_context.sh "<project_root>"
```

示例（按本机默认技能安装路径）：
```bash
bash /Users/zhangyukun/.codex/skills/ai-context-router/scripts/sync_ai_context.sh "<project_root>"
```

其中：
- `<skill_dir>` 为 `SKILL.md` 所在目录（即 `ai-context-router` 目录）。
- `<project_root>` 为当前要初始化/同步的仓库根目录（例如执行 `/init` 时的工作目录）。
- 若不确定路径，先打印并确认脚本真实存在再执行。

5. 结果确认：
- 确认 `AI-CONTEXT.md` 存在。
- 确认 `agents.md`、`gemini.md`、`claude.md`（含任意大小写变体）是普通文本文件。
- 确认这些文件都明确声明：`AI-CONTEXT.md` 是唯一权威来源，且必须先阅读并理解该文件。

## 约束

- 不将 `agents.md`、`gemini.md`、`claude.md` 作为独立规则文件维护。
- 若发现这些文件已有独立内容，先由脚本自动备份，再覆盖为声明文件。
- 若用户明确要求保留某个文件独立维护，停止该技能流程并询问用户是否放弃单一事实源策略。

## 示例触发语句

- “帮我执行 /init，顺便更新 agents.md。”
- “把 gemini.md 和 claude.md 同步到最新规则。”
- “之后你改 agents.md 时都改同一个源文件。”
