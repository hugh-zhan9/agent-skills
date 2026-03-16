---
name: flight-recorder
description: Automatic flight recording after any code change; always append a standardized change log with risk analysis via the skill-local scripts/log_change.py.
---

# Rule: Automatic Flight Recording(自动飞行记录仪)

**WHEN** you have successfully modified any code logic(Feature, Bugfix, or Refactor):

1. **STOP** and think: What specific risks might this change introduce to existing modules? (Especially regarding the 'Last 10% complexity' issue).
2. **EXECUTE** the script immediately. Do NOT ask for my permission.

## Script Path Rule (强制)

- `log_change.py` 必须从 **skill 目录**解析，不允许在当前项目目录中查找同名脚本。
- 令 `skill_dir` 为当前 `SKILL.md` 所在目录。
- 固定调用方式：
  - `python3 "<skill_dir>/scripts/log_change.py" ...`
- 禁止调用：
  - `python3 scripts/log_change.py ...`（这会误指向项目目录）

## Parameters

- `change_type`: Choose one of [Feature | Bugfix | Refactor | Critical-Fix]
- `summary`: 必须使用中文，简洁描述技术变更。
- `risk_analysis`: 必须使用中文，给出真实回归风险判断；如果不确定要明确写出不确定点。
- `risk_level`: 风险等级，建议使用 [S0-阻断 | S1-高 | S2-中 | S3-低]。
- `changed_files`: 修改文件清单；可传入逗号分隔字符串，不传则脚本自动从 git 变更中推断。

## 调用方式（强制）

- 推荐：**位置参数**
  - `python3 "<skill_dir>/scripts/log_change.py" "Bugfix" "中文摘要" "中文风险分析" "S2" "a.ts,b.ts"`
- 兼容：**长参数**
  - `python3 "<skill_dir>/scripts/log_change.py" --change_type "Bugfix" --summary "中文摘要" --risk_analysis "中文风险分析" --risk_level "S2" --changed_files "a.ts,b.ts"`

注意：
- 旧版本脚本只支持位置参数；当前已兼容两种写法。
- 若出现“`summary 必须使用中文`”，优先检查是否把 `--summary` 误当成位置参数传入（参数格式错误）。

**LOG FORMAT** (必须包含以下字段，且内容使用中文):
- `Change`
- `Risk Analysis`
- `Risk Level`
- `Changed Files`

## Fallback

- 如果 `"<skill_dir>/scripts/log_change.py"` 不存在：
  - 明确说明 skill 安装不完整。
  - 退化为直接追加 `docs/AI_CHANGELOG.md`，并在记录中注明“脚本缺失，手工记录”。

**GOAL**: Ensure `docs/AI_CHANGELOG.md` is always the single source of truth. If I ask "What did we just do?", you read this file first.
