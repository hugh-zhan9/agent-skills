#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = ZoneInfo("Asia/Shanghai")
DEFAULT_INBOX_DIR = (
    Path.home()
    / "Library"
    / "Mobile Documents"
    / "iCloud~md~obsidian"
    / "Documents"
    / "inbox"
    / "posts"
)
STATE_PATH = Path(__file__).resolve().parent.parent / "state.json"


@dataclass
class PublishResult:
    file_path: Path
    commit_message: str
    from_inbox: bool


def is_valid_repo(repo_path: Path) -> bool:
    repo_path = repo_path.expanduser().resolve()
    return (repo_path / "hugo.toml").is_file() and (repo_path / "content" / "posts").is_dir()


def make_path_hint(target: Path, cwd: Path) -> tuple[str, str]:
    target = target.expanduser().resolve()
    cwd = cwd.expanduser().resolve()
    relative_to_cwd = Path(os.path.relpath(target, cwd)).as_posix()
    return "cwd_relative", relative_to_cwd


def resolve_path_hint(hint_type: str, hint_value: str, cwd: Path) -> Path | None:
    cwd = cwd.expanduser().resolve()
    if hint_type == "cwd_relative":
        return (cwd / hint_value).resolve()
    return None


def load_cached_repo(state_path: Path, cwd: Path) -> Path | None:
    if not state_path.is_file():
        return None
    data = json.loads(state_path.read_text(encoding="utf-8"))
    hint_type = data.get("repo_hint_type")
    hint_value = data.get("repo_path_hint")
    target_relative = data.get("target_relative_path")
    if not hint_type or not hint_value or target_relative != "content/posts":
        return None
    candidate = resolve_path_hint(hint_type, hint_value, cwd)
    if candidate and is_valid_repo(candidate):
        return candidate
    return None


def write_repo_cache(repo_path: Path, state_path: Path, cwd: Path) -> None:
    repo_path = repo_path.expanduser().resolve()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    hint_type, hint_value = make_path_hint(repo_path, cwd)
    state_path.write_text(
        json.dumps(
            {
                "repo_hint_type": hint_type,
                "repo_path_hint": hint_value,
                "target_relative_path": "content/posts",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def find_repo_from_existing_posts(search_start: Path) -> Path | None:
    search_start = search_start.expanduser().resolve()
    for candidate in [search_start, *search_start.parents]:
        if candidate.name == "posts" and candidate.parent.name == "content":
            repo_path = candidate.parent.parent
            if is_valid_repo(repo_path):
                return repo_path
        direct = candidate / "content" / "posts"
        if direct.is_dir():
            if is_valid_repo(candidate):
                return candidate
    for posts_dir in search_start.rglob("posts"):
        if posts_dir.parent.name != "content":
            continue
        repo_path = posts_dir.parent.parent
        if is_valid_repo(repo_path):
            return repo_path
    return None


def find_or_create_repo_from_hugh_note(search_start: Path) -> Path | None:
    search_start = search_start.expanduser().resolve()
    for candidate in [search_start, *search_start.parents]:
        if candidate.name == "hugh-note" and (candidate / "hugo.toml").is_file():
            (candidate / "content" / "posts").mkdir(parents=True, exist_ok=True)
            if is_valid_repo(candidate):
                return candidate
    for repo_path in search_start.rglob("hugh-note"):
        if not repo_path.is_dir():
            continue
        if not (repo_path / "hugo.toml").is_file():
            continue
        (repo_path / "content" / "posts").mkdir(parents=True, exist_ok=True)
        if is_valid_repo(repo_path):
            return repo_path
    return None


def resolve_repo_path(search_start: Path, state_path: Path = STATE_PATH) -> Path:
    cwd = Path.cwd().resolve()
    cached = load_cached_repo(state_path, cwd)
    if cached:
        return cached
    repo_path = find_repo_from_existing_posts(search_start)
    if repo_path is None:
        repo_path = find_or_create_repo_from_hugh_note(search_start)
    if repo_path is None:
        raise FileNotFoundError("未找到可用的 hugh-note 博客目录，且无法定位 content/posts")
    write_repo_cache(repo_path, state_path, cwd)
    return repo_path


def normalize_payload(payload: str) -> str:
    text = payload.strip()
    if text.startswith("发布博客"):
        text = text[len("发布博客") :].strip()
    if text.startswith(":") or text.startswith("："):
        text = text[1:].strip()
    if not text:
        raise ValueError("发布内容不能为空")
    return text


def is_likely_file_name(text: str) -> bool:
    # Heuristic: multi-line or very long payload should be treated as article content.
    if "\n" in text or "\r" in text:
        return False
    if len(text) > 120:
        return False
    return True


def resolve_source_file(payload: str, inbox_dir: Path) -> Path | None:
    inbox_dir = inbox_dir.expanduser().resolve()
    if not inbox_dir.is_dir():
        return None
    name = normalize_payload(payload)
    if not is_likely_file_name(name):
        return None
    candidates = [name]
    if not name.endswith(".md"):
        candidates.append(f"{name}.md")
    for candidate in candidates:
        file_path = inbox_dir / candidate
        try:
            matched = file_path.is_file()
        except OSError:
            matched = False
        if matched:
            return file_path.resolve()
    return None


def extract_title_and_body(content: str) -> tuple[str, str]:
    text = content.strip()
    if not text:
        raise ValueError("发布内容不能为空")

    # Prefer explicit title markers for predictable publishing.
    patterns = [
        re.compile(r"^\s*(标题|名称)\s*[:：]\s*(.+?)\s*$", re.MULTILINE),
        re.compile(r"^\s*(标题|名称)\s+(.+?)\s*$", re.MULTILINE),
        re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE),
    ]

    title = ""
    body = text
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            title = match.group(2 if pattern.pattern.startswith("^\\s*(标题|名称)") else 1).strip()
            start, end = match.span()
            body = (text[:start] + text[end:]).strip()
            break

    if not title:
        raise ValueError("未检测到标题，请补充“标题：xxx”或“名称：xxx”后再发布")

    if not body:
        raise ValueError("正文不能为空，请在标题之外补充文章内容")

    return title, body


def build_markdown_from_text(content: str, now: datetime, description_override: str, tags: list[str] = None) -> tuple[str, str]:
    title, body = extract_title_and_body(content)
    description = description_override.strip()
    if not description:
        raise ValueError("缺少文章摘要，请先提供一句总结内容后再发布")
    if len(description) > 120:
        description = description[:120].strip()
    description = description.replace('"', '\\"')
    title = title.replace('"', '\\"')
    
    if not tags:
        tags = ["杂记"]
    tags_str = ", ".join(tags)

    offset = now.strftime("%z")
    offset = f"{offset[:3]}:{offset[3:]}"
    front_matter = (
        "---\n"
        f'title: "{title}"\n'
        "draft: false\n"
        f"date: {now:%Y-%m-%dT%H:%M:%S}{offset}\n"
        f'description: "{description}"\n'
        f"tags: [{tags_str}]\n"
        "---\n\n"
    )
    return f"{front_matter}{body}\n", now.strftime("%Y-%m-%d-%H%M%S.md")


def has_yaml_front_matter(text: str) -> bool:
    stripped = text.lstrip()
    if not stripped.startswith("---\n"):
        return False
    return stripped.find("\n---\n", 4) != -1


def build_markdown_with_front_matter(title: str, body: str, now: datetime, description_override: str, tags: list[str] = None) -> str:
    description = description_override.strip()
    if not description:
        raise ValueError("缺少文章摘要，请先提供一句总结内容后再发布")
    if len(description) > 120:
        description = description[:120].strip()

    title = title.strip().replace('"', '\\"')
    description = description.replace('"', '\\"')
    body = body.strip()
    if not body:
        raise ValueError("正文不能为空，请补充文章内容")

    if not tags:
        tags = ["杂记"]
    tags_str = ", ".join(tags)

    offset = now.strftime("%z")
    offset = f"{offset[:3]}:{offset[3:]}"
    return (
        "---\n"
        f'title: "{title}"\n'
        "draft: false\n"
        f"date: {now:%Y-%m-%dT%H:%M:%S}{offset}\n"
        f'description: "{description}"\n'
        f"tags: [{tags_str}]\n"
        "---\n\n"
        f"{body}\n"
    )


def update_front_matter_tags(text: str, tags: list[str]) -> str:
    if not tags:
        return text
    tags_str = ", ".join(f'"{t}"' if " " in t else t for t in tags)
    # Simple regex to replace tags: [...]
    pattern = re.compile(r"^tags:\s*\[.*\]$", re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(f"tags: [{tags_str}]", text)
    # If not found, try to insert after date or title
    return text


def publish_post(
    repo_path: Path,
    payload: str,
    now: datetime,
    inbox_dir: Path = DEFAULT_INBOX_DIR,
    description_override: str = "",
    title_override: str = "",
    tags: list[str] = None,
) -> PublishResult:
    repo_path = repo_path.expanduser().resolve()
    posts_dir = repo_path / "content" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    source_file = resolve_source_file(payload, inbox_dir)

    if source_file:
        file_name = source_file.name
        target = (posts_dir / file_name).resolve()
        source_text = source_file.read_text(encoding="utf-8")
        if has_yaml_front_matter(source_text):
            if tags:
                output_text = update_front_matter_tags(source_text, tags)
            else:
                output_text = source_text
        else:
            resolved_title = title_override.strip() or source_file.stem
            output_text = build_markdown_with_front_matter(
                title=resolved_title,
                body=source_text,
                now=now,
                description_override=description_override,
                tags=tags,
            )
        target.write_text(output_text, encoding="utf-8")
        return PublishResult(
            file_path=target,
            commit_message=f"发布博客：{file_name}",
            from_inbox=True,
        )

    text = normalize_payload(payload)
    markdown, file_name = build_markdown_from_text(text, now, description_override=description_override, tags=tags)
    target = (posts_dir / file_name).resolve()
    target.write_text(markdown, encoding="utf-8")
    return PublishResult(
        file_path=target,
        commit_message=f"发布博客：{file_name}",
        from_inbox=False,
    )


def run_git(repo_path: Path, args: list[str]) -> None:
    repo_path = repo_path.expanduser().resolve()
    subprocess.run(["git", "-C", str(repo_path), *args], check=True)


def commit_and_push(repo_path: Path, file_path: Path, commit_message: str, push: bool) -> None:
    repo_path = repo_path.expanduser().resolve()
    file_path = file_path.expanduser().resolve()
    relative_path = file_path.relative_to(repo_path)
    run_git(repo_path, ["add", str(relative_path)])
    run_git(repo_path, ["commit", "-m", commit_message, "--", str(relative_path)])
    if push:
        branch = subprocess.run(
            ["git", "-C", str(repo_path), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not branch:
            raise RuntimeError("无法识别当前分支，无法执行 push")
        run_git(repo_path, ["push", "origin", branch])


def resolve_now(value: str | None) -> datetime:
    if value:
        now = datetime.fromisoformat(value)
        if now.tzinfo is None:
            return now.replace(tzinfo=DEFAULT_TIMEZONE)
        return now
    return datetime.now(DEFAULT_TIMEZONE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="发布博客文章到 content/posts，并可选执行 git 提交推送。")
    parser.add_argument("payload", help="文件名或正文内容")
    parser.add_argument("--repo", help="显式指定博客仓库路径")
    parser.add_argument("--search-start", default=".", help="未显式指定仓库时，用于发现博客目录的起点")
    parser.add_argument("--state-path", default=str(STATE_PATH), help="缓存文件路径")
    parser.add_argument("--inbox-dir", default=str(DEFAULT_INBOX_DIR), help="Obsidian 收件箱 posts 目录")
    parser.add_argument("--description", default="", help="文章摘要（一句话），用于 front matter description")
    parser.add_argument("--tags", action="append", help="文章标签，支持指定多个")
    parser.add_argument("--title", default="", help="文章标题（inbox 文件缺少 front matter 时可显式指定）")
    parser.add_argument("--now", help="指定时间，格式为 ISO 8601，主要用于测试")
    parser.add_argument("--git", action="store_true", help="写入后执行 git add/commit")
    parser.add_argument("--push", action="store_true", help="与 --git 一起使用，提交后推送到 origin 当前分支")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = resolve_now(args.now)
    state_path = Path(args.state_path).expanduser().resolve()
    if args.repo:
        repo_path = Path(args.repo).expanduser().resolve()
        if not is_valid_repo(repo_path):
            raise FileNotFoundError(f"指定仓库不可用: {repo_path}")
        write_repo_cache(repo_path, state_path, Path.cwd())
    else:
        repo_path = resolve_repo_path(Path(args.search_start), state_path=state_path)

    result = publish_post(
        repo_path,
        args.payload,
        now,
        inbox_dir=Path(args.inbox_dir),
        description_override=args.description,
        title_override=args.title,
        tags=args.tags,
    )

    if args.push and not args.git:
        raise ValueError("--push 必须与 --git 一起使用")

    if args.git:
        commit_and_push(repo_path, result.file_path, result.commit_message, push=args.push)

    print(f"已写入: {result.file_path}")
    print(f"提交信息: {result.commit_message}")
    print(f"来源: {'inbox 文件' if result.from_inbox else '直接文本'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
