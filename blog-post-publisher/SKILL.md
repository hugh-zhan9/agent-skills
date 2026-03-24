---
name: blog-post-publisher
description: 快速发布博客文章到 hugh-note 的 content/posts，并自动提交推送。仅当用户明确要执行“发布博客 + 文件名”或“发布博客 + 正文内容”时使用，支持优先从 Obsidian inbox/posts 读取文件，不存在时按 posts 规范自动创建新文章。
---

# Blog Post Publisher

仅在用户明确发布博客时使用这个技能。不要把普通讨论、润色请求误当成发布命令。

## 触发规则

- 用户消息以 `发布博客` 开头时触发。
- 取 `发布博客` 后面的文本作为 `payload`。
- `payload` 不能为空。

## 发布规则

- 优先把 `payload` 当作文件名处理，去 inbox 目录查找源文件：
  - 默认 inbox 目录：`$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/inbox/posts`
  - 先查同名，再查自动补 `.md` 的同名文件
- 如果找到源文件：
  - 把文件内容写入博客仓库的 `content/posts/<文件名>.md`
  - 如果文件缺少 YAML front matter，则必须先根据正文自动提炼 1-3 个标签。
  - 使用提交信息：`发布博客：<文件名>.md`
- 如果没找到源文件：
  - 把 `payload` 当作正文
  - 正文中必须包含标题信息，支持：
    - `标题：你的标题`
    - `名称：你的标题`
    - Markdown 一级标题 `# 你的标题`
  - 如果未检测到标题，必须先询问用户提供标题，不要直接发布
  - 必须先根据整篇正文生成一句摘要，再写入 `description`；不要直接截取首行
  - **必须根据正文内容自动提炼 1-3 个核心关键词作为标签，若文章中已有明确标签则优先使用。**
  - 在 `content/posts` 新建 `YYYY-MM-DD-HHMMSS.md`
  - 文件格式必须遵循现有 posts 风格：
    - `---` YAML front matter
    - 字段：`title`、`draft`、`date`、`description`、`tags`
    - `draft: false`
    - `description` 需要根据正文自动提炼为一句摘要
    - `tags` 为提炼出的关键词列表
  - 使用提交信息：`发布博客：<新文件名>.md`

## 仓库定位与缓存

- 不要把仓库绝对路径写死在 skill 中。
- 优先读取 skill 根目录的 `state.json` 缓存。
- 缓存使用相对路径提示，不保存绝对路径。
- 每次命中缓存前必须校验：
  - 仓库根目录存在 `hugo.toml`
  - 目标目录存在 `content/posts`
- 缓存失效时按顺序重试：
  1. 在搜索起点附近查找现有 `content/posts`，并向上确认 `hugo.toml`
  2. 若未找到，则查找名为 `hugh-note` 且包含 `hugo.toml` 的目录，并创建 `content/posts`
- 发现成功后写回 `state.json`。

## Git 流程

- 写入完成后执行（注意 `--description` 必填，`--tags` 为提炼出的关键词）：

```bash
python3 "$HOME/.codex/skills/blog-post-publisher/scripts/publish_blog_post.py" "发布博客 xxx" --description "一句话摘要" --tags "标签1" --tags "标签2" --git --push
```

- 仅提交当前发布产生的目标文件，不要把仓库其他改动一起提交。
- push 到 `origin` 当前分支。

## 资源

- `scripts/publish_blog_post.py`：发布实现，支持文件名发布和正文直发。
- `scripts/test_publish_blog_post.py`：覆盖仓库发现、缓存、格式生成、commit/push 的回归测试。
