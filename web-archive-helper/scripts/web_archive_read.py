#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse


CONFIG_PATH = Path(os.environ.get("WEB_ARCHIVE_HELPER_STATE", str(Path.cwd() / ".web_archive_helper_state.json")))


def load_state():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize_url(raw):
    parsed = urlparse(raw.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    if not path:
        path = "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{scheme}://{netloc}{path}{query}"


def choose_search_dir(user_dir):
    if user_dir:
        return Path(user_dir).expanduser()
    state = load_state()
    default_dir = state.get("default_output_dir", "").strip()
    if default_dir:
        return Path(default_dir).expanduser()
    return None


def find_by_url(search_dir: Path, target_url: str):
    target_norm = normalize_url(target_url)
    found = []
    for path in search_dir.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        source_line = None
        for line in text.splitlines():
            if line.startswith("- 来源: "):
                source_line = line[len("- 来源: ") :].strip()
                break
        if not source_line:
            continue
        if normalize_url(source_line) == target_norm:
            found.append(path)
    return sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)


def main():
    parser = argparse.ArgumentParser(description="根据 URL 查找已归档的 Markdown 文件")
    parser.add_argument("url", help="原始网页 URL")
    parser.add_argument("--dir", default="", help="检索目录；不传则使用已记忆默认目录")
    parser.add_argument("--print", action="store_true", help="输出命中的文件前 80 行")
    args = parser.parse_args()

    search_dir = choose_search_dir(args.dir)
    if search_dir is None:
        print("NEED_DEFAULT_DIR: 未配置默认目录，请先保存一次并提供 --dir")
        return 2
    if not search_dir.exists():
        print(f"目录不存在: {search_dir}")
        return 1

    matches = find_by_url(search_dir, args.url)
    if not matches:
        print("NOT_FOUND: 未找到该 URL 对应的归档文件")
        return 3

    latest = matches[0]
    print(f"FOUND: {latest}")
    if args.print:
        lines = latest.read_text(encoding="utf-8", errors="ignore").splitlines()
        preview = "\n".join(lines[:80])
        print("-----")
        print(preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
