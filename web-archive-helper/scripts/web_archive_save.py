#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


CONFIG_PATH = Path(os.environ.get("WEB_ARCHIVE_HELPER_STATE", str(Path.cwd() / ".web_archive_helper_state.json")))
SKILL_ARCHIVE_SCRIPT = Path(__file__).resolve().parent / "save_webpage_markdown.py"


def load_state():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    CONFIG_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_archive_script():
    if SKILL_ARCHIVE_SCRIPT.exists():
        return SKILL_ARCHIVE_SCRIPT
    raise FileNotFoundError(f"未找到技能内置脚本: {SKILL_ARCHIVE_SCRIPT}")


def choose_output_dir(user_dir):
    if user_dir:
        return str(Path(user_dir).expanduser()), True
    state = load_state()
    default_dir = state.get("default_output_dir", "").strip()
    if default_dir:
        return default_dir, False
    return "", False


def main():
    parser = argparse.ArgumentParser(description="保存网页为 Markdown，并记住默认保存目录")
    parser.add_argument("url", help="网页 URL")
    parser.add_argument("--dir", default="", help="输出目录；不传则使用已记忆的默认目录")
    parser.add_argument("--set-default-dir", action="store_true", help="将 --dir 保存为默认目录")
    parser.add_argument("--name", default="", help="可选文件名")
    parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数")
    parser.add_argument("--render-mode", choices=["auto", "static", "browser"], default="auto")
    args = parser.parse_args()

    output_dir, from_user_dir = choose_output_dir(args.dir)
    if not output_dir:
        print("NEED_DEFAULT_DIR: 首次使用请提供 --dir 目录（例如 --dir docs/web-archive）", file=sys.stderr)
        return 2

    state = load_state()
    has_default = bool(state.get("default_output_dir", "").strip())
    if (from_user_dir and not has_default) or (args.set_default_dir and args.dir):
        # 第一次显式提供目录时自动记忆；后续仅在 --set-default-dir 时更新默认目录。
        state = load_state()
        state["default_output_dir"] = output_dir
        save_state(state)

    script = resolve_archive_script()
    cmd = [
        sys.executable,
        str(script),
        args.url,
        "-o",
        output_dir,
        "--timeout",
        str(args.timeout),
        "--render-mode",
        args.render_mode,
    ]
    if args.name:
        cmd.extend(["--name", args.name])

    proc = subprocess.run(cmd, text=True)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
