---
name: crazy-talk-publisher
description: 快速创建或追加 hugh-note 博客的“疯言疯语”日记条目，并自动提交推送。仅当用户消息以“疯言疯语：”开头，且目标是把该句内容发布到某个 hugh-note Hugo 博客的 content/crazy-talk 当日日记文件时使用。
---

# Crazy Talk Publisher

仅在用户明确要发布“疯言疯语”内容时使用这个技能。不要把普通讨论、润色请求或示例文本误当成发布命令。

## 触发规则

- 仅当用户消息以 `疯言疯语：` 开头时执行。
- 将 `疯言疯语：` 后面的全部文本视为正文。
- 如果正文为空，停止并告诉用户内容不能为空。

## 目标发现

- 不要把仓库绝对路径写死在 skill 中。
- 优先使用 skill 根目录下的 `state.json` 缓存。
- 缓存只允许保存相对路径提示，不要写绝对路径。
- 每次使用缓存前都要验证：
  - 目标仓库根目录存在 `hugo.toml`
  - 目标目录存在 `content/crazy-talk`
- 缓存失效时，按以下顺序重新发现：
  1. 查找现有的 `content/crazy-talk`，再向上确认 Hugo 根目录有 `hugo.toml`
  2. 如果没有现成的 `content/crazy-talk`，查找名为 `hugh-note` 且包含 `hugo.toml` 的目录，并在其下创建 `content/crazy-talk`
- 发现成功后，把可复用的相对路径提示写回 `state.json`
- 当天文件名固定为 `YYYY-MM-DD.md`

## 写入规则

- 如果当天文件不存在，创建文件并写入标准 front matter：

```md
---
title: "YYYY-MM-DD"
draft: false
date: YYYY-MM-DDT00:00:00+08:00
description: "疯言疯语。"
tags: [疯言疯语]
---
```

- 每条新增内容都写成以下格式：

```md
### HH:MM

正文内容
```

- 如果当天文件已存在，在文件末尾追加新条目。
- 新旧条目之间保留两行空行。
- 不要重写已有 front matter，不要改动旧条目内容。

## Git 流程

- 写入成功后，执行脚本：

```bash
python3 "/Users/zhangyukun/.codex/skills/crazy-talk-publisher/scripts/publish_crazy_talk.py" "正文内容" --git --push
```

- 如有必要，可以显式指定仓库或缓存文件：

```bash
python3 "/Users/zhangyukun/.codex/skills/crazy-talk-publisher/scripts/publish_crazy_talk.py" "正文内容" --repo "/path/to/hugh-note" --state-path "/path/to/state.json" --git --push
```

- 新建当天文件时，提交信息使用：`新增 YYYY-MM-DD 疯言疯语`
- 追加当天文件时，提交信息使用：`更新 YYYY-MM-DD 疯言疯语`
- 仅提交当天被改动的那一个文件，不要把仓库里的其他改动一起提交。
- 推送到 `origin` 的当前分支。

## 执行后反馈

- 简洁告知用户写入的文件路径。
- 说明本次是“新增”还是“更新”。
- 说明已经完成 commit 和 push。

## 资源

### scripts/

- `scripts/publish_crazy_talk.py`：创建或追加当天文件，并执行 `git add`、中文 `commit`、`git push`。
- `scripts/test_publish_crazy_talk.py`：验证创建、追加、发现、缓存与 Git 推送逻辑是否符合约定。
