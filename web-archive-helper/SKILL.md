---
name: web-archive-helper
description: 保存网页为可长期阅读的 Markdown 归档，并支持按原 URL 快速找回。遇到“保存 URL”“归档 URL”“稍后读 URL”“回看 URL”这类请求时使用。首次使用会询问默认保存目录，之后自动复用该目录。
---

# Web Archive Helper

## Overview
使用两个脚本完成网页归档与回读：
- `scripts/web_archive_save.py`：保存 URL 到 Markdown。
- `scripts/web_archive_read.py`：按 URL 查找并读取已保存文档。

## Workflow
1. 识别用户意图：
- 如果用户表达“保存/归档 URL”，执行保存脚本。
- 如果用户表达“稍后读/回看 URL”，执行读取脚本。

默认交互约定：
- `保存`：只保存，不展示文档预览内容。
- `稍后读`：只在用户明确提出读取时，才输出归档内容预览。
- 当执行 `稍后读` 且未命中归档时，只返回未找到结果，不自动触发保存。

2. 首次使用处理默认目录：
- 先执行保存脚本（不带 `--dir`）尝试读取默认目录。
- 若返回 `NEED_DEFAULT_DIR`，必须询问用户“默认保存目录”。
- 用户给出目录后，重新执行保存脚本并加 `--dir <目录>`（首次会自动记住为默认目录）。

3. 后续使用：
- 不再询问目录，直接使用已保存默认目录。
- 用户显式给了新目录时，本次按用户目录执行；如需更新默认目录，再附加 `--set-default-dir`。

## Commands
保存：
```bash
python3 /Users/zhangyukun/.codex/skills/web-archive-helper/scripts/web_archive_save.py "<url>"
```

首次设置默认目录：
```bash
python3 /Users/zhangyukun/.codex/skills/web-archive-helper/scripts/web_archive_save.py "<url>" --dir "<目录>"
```

稍后读（查找最新归档）：
```bash
python3 /Users/zhangyukun/.codex/skills/web-archive-helper/scripts/web_archive_read.py "<url>"
```

稍后读并打印预览：
```bash
python3 /Users/zhangyukun/.codex/skills/web-archive-helper/scripts/web_archive_read.py "<url>" --print
```

## Behavior Notes
- 保存脚本仅调用 skill 内置归档脚本：`scripts/save_webpage_markdown.py`（与 `web_archive_save.py` 同目录）。
- 不再依赖当前项目仓库中的 `scripts/save_webpage_markdown.py`。
- 默认目录配置存放在：`$WEB_ARCHIVE_HELPER_STATE`（若未设置，默认当前工作目录 `.web_archive_helper_state.json`）。
- 导出的 Markdown 头部 `AI速读` 必须为 1-2 句正文总结，优先陈述核心结论，避免直接复用“什么是…？”这类问题式标题。
