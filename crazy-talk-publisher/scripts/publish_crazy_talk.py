#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = ZoneInfo("Asia/Shanghai")
STATE_PATH = Path(__file__).resolve().parent.parent / "state.json"


@dataclass
class PublishResult:
    created: bool
    file_path: Path
    commit_message: str


def is_valid_repo(repo_path: Path) -> bool:
    repo_path = repo_path.expanduser().resolve()
    return (repo_path / "hugo.toml").is_file() and (repo_path / "content" / "crazy-talk").is_dir()


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

    if not hint_type or not hint_value or target_relative != "content/crazy-talk":
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
                "target_relative_path": "content/crazy-talk",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def find_repo_from_existing_crazy_talk(search_start: Path) -> Path | None:
    search_start = search_start.expanduser().resolve()

    for candidate in [search_start, *search_start.parents]:
        if candidate.name == "crazy-talk" and candidate.parent.name == "content":
            repo_path = candidate.parent.parent
            if is_valid_repo(repo_path):
                return repo_path

        direct = candidate / "content" / "crazy-talk"
        if direct.is_dir():
            repo_path = candidate
            if is_valid_repo(repo_path):
                return repo_path

    for crazy_talk_dir in search_start.rglob("crazy-talk"):
        if crazy_talk_dir.parent.name != "content":
            continue
        repo_path = crazy_talk_dir.parent.parent
        if is_valid_repo(repo_path):
            return repo_path
    return None


def find_or_create_repo_from_hugh_note(search_start: Path) -> Path | None:
    search_start = search_start.expanduser().resolve()

    for candidate in [search_start, *search_start.parents]:
        if candidate.name == "hugh-note" and (candidate / "hugo.toml").is_file():
            (candidate / "content" / "crazy-talk").mkdir(parents=True, exist_ok=True)
            if is_valid_repo(candidate):
                return candidate

    for repo_path in search_start.rglob("hugh-note"):
        if not repo_path.is_dir():
            continue
        if not (repo_path / "hugo.toml").is_file():
            continue
        (repo_path / "content" / "crazy-talk").mkdir(parents=True, exist_ok=True)
        if is_valid_repo(repo_path):
            return repo_path
    return None


def resolve_repo_path(search_start: Path, state_path: Path = STATE_PATH) -> Path:
    cwd = Path.cwd().resolve()
    cached = load_cached_repo(state_path, cwd)
    if cached:
        return cached

    repo_path = find_repo_from_existing_crazy_talk(search_start)
    if repo_path is None:
        repo_path = find_or_create_repo_from_hugh_note(search_start)

    if repo_path is None:
        raise FileNotFoundError("未找到可用的 hugh-note 博客目录，且无法定位 content/crazy-talk")

    write_repo_cache(repo_path, state_path, cwd)
    return repo_path


def normalize_content(content: str) -> str:
    normalized = content.strip()
    if not normalized:
        raise ValueError("疯言疯语内容不能为空")
    return normalized


def target_file_path(repo_path: Path, now: datetime) -> Path:
    return repo_path / "content" / "crazy-talk" / f"{now:%Y-%m-%d}.md"


def build_front_matter(now: datetime) -> str:
    offset = now.strftime("%z")
    offset = f"{offset[:3]}:{offset[3:]}"
    return (
        "---\n"
        f'title: "{now:%Y-%m-%d}"\n'
        "draft: false\n"
        f"date: {now:%Y-%m-%d}T00:00:00{offset}\n"
        'description: "疯言疯语。"\n'
        "tags: [疯言疯语]\n"
        "---\n\n"
    )


def build_entry(now: datetime, content: str) -> str:
    return f"### {now:%H:%M}\n\n{normalize_content(content)}\n"


def build_commit_message(created: bool, now: datetime) -> str:
    action = "新增" if created else "更新"
    return f"{action} {now:%Y-%m-%d} 疯言疯语"


def split_existing_content(existing: str) -> tuple[str, str, str]:
    if not existing.startswith("---\n"):
        return "", "", existing.strip("\n")

    closing = existing.find("\n---\n", 4)
    if closing == -1:
        return "", "", existing.strip("\n")

    front_matter_end = closing + len("\n---\n")
    remainder = existing[front_matter_end:]
    stripped_remainder = remainder.lstrip("\n")
    leading_newlines = len(remainder) - len(stripped_remainder)
    body_start = front_matter_end + leading_newlines

    marker = "\n### "
    first_entry = stripped_remainder.find("### ")
    if first_entry == -1:
        return existing[:body_start], stripped_remainder.strip("\n"), ""

    if first_entry != 0:
        first_entry = stripped_remainder.find(marker)
        if first_entry == -1:
            return existing[:body_start], stripped_remainder.strip("\n"), ""
        first_entry += 1

    body_index = body_start + first_entry
    preamble = existing[body_start:body_index].strip("\n")
    entries = existing[body_index:].strip("\n")
    return existing[:body_start], preamble, entries


def compose_existing_content(header: str, preamble: str, entries: list[str]) -> str:
    text = header.rstrip("\n") + "\n\n"
    if preamble:
        text += preamble.strip("\n") + "\n\n\n"
    text += "\n\n\n".join(entry.strip("\n") for entry in entries if entry.strip()) + "\n"
    return text


def upsert_crazy_talk(repo_path: Path, content: str, now: datetime) -> PublishResult:
    repo_path = repo_path.expanduser().resolve()
    target = target_file_path(repo_path, now)
    target.parent.mkdir(parents=True, exist_ok=True)

    entry = build_entry(now, content)
    created = not target.exists()

    if created:
        target.write_text(build_front_matter(now) + entry, encoding="utf-8")
    else:
        existing = target.read_text(encoding="utf-8")
        header, preamble, entries = split_existing_content(existing)
        entry_blocks = [entry.rstrip("\n")]
        if entries:
            entry_blocks.append(entries)
        target.write_text(compose_existing_content(header, preamble, entry_blocks), encoding="utf-8")

    return PublishResult(
        created=created,
        file_path=target,
        commit_message=build_commit_message(created, now),
    )


def run_git(repo_path: Path, args: list[str]) -> None:
    repo_path = repo_path.expanduser().resolve()
    subprocess.run(
        ["git", "-C", str(repo_path), *args],
        check=True,
    )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="创建或追加疯言疯语，并可选执行 git 提交推送。")
    parser.add_argument("content", help="疯言疯语正文")
    parser.add_argument("--repo", help="显式指定博客仓库路径")
    parser.add_argument("--search-start", default=".", help="未显式指定仓库时，用于发现博客目录的起点")
    parser.add_argument("--state-path", default=str(STATE_PATH), help="缓存文件路径")
    parser.add_argument("--now", help="指定时间，格式为 ISO 8601，主要用于测试")
    parser.add_argument("--git", action="store_true", help="写入后执行 git add/commit")
    parser.add_argument("--push", action="store_true", help="与 --git 一起使用，提交后推送到 origin 当前分支")
    return parser.parse_args()


def resolve_now(value: str | None) -> datetime:
    if value:
        now = datetime.fromisoformat(value)
        if now.tzinfo is None:
            return now.replace(tzinfo=DEFAULT_TIMEZONE)
        return now
    return datetime.now(DEFAULT_TIMEZONE)


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

    result = upsert_crazy_talk(repo_path, args.content, now)

    if args.push and not args.git:
        raise ValueError("--push 必须与 --git 一起使用")

    if args.git:
        commit_and_push(repo_path, result.file_path, result.commit_message, push=args.push)

    print(f"已写入: {result.file_path}")
    print(f"提交信息: {result.commit_message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
