#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$(pwd)}"
cd "$ROOT_DIR"

SOURCE_FILE="AI-CONTEXT.md"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"

# 目标文件名不限制大小写；如果目录中不存在对应文件，则创建默认大写名。
declare -a TARGET_FILES=()
found_agent=0
found_gemini=0
found_claude=0

for entry in *; do
  if [ ! -e "$entry" ] && [ ! -L "$entry" ]; then
    continue
  fi

  lower_name="$(printf '%s' "$entry" | tr '[:upper:]' '[:lower:]')"
  case "$lower_name" in
    agents.md)
      TARGET_FILES+=("$entry")
      found_agent=1
      ;;
    gemini.md)
      TARGET_FILES+=("$entry")
      found_gemini=1
      ;;
    claude.md)
      TARGET_FILES+=("$entry")
      found_claude=1
      ;;
  esac
done

if [ "$found_agent" -eq 0 ]; then
  TARGET_FILES+=("AGENTS.md")
fi
if [ "$found_gemini" -eq 0 ]; then
  TARGET_FILES+=("GEMINI.md")
fi
if [ "$found_claude" -eq 0 ]; then
  TARGET_FILES+=("CLAUDE.md")
fi

if [ ! -f "$SOURCE_FILE" ]; then
  cat > "$SOURCE_FILE" <<'TEMPLATE'
# AI Context

> 这是统一上下文单一事实源文件。
> 请将多终端（agents.md / gemini.md / claude.md）的共同规则维护在此处。
TEMPLATE
fi

for target in "${TARGET_FILES[@]}"; do
  if [ -e "$target" ] || [ -L "$target" ]; then
    mv "$target" "${target}.bak.${TIMESTAMP}"
  fi

  cat > "$target" <<TEMPLATE
# Context Delegation Notice

The file "$SOURCE_FILE" is the master source of truth for project context.
You must read and understand "$SOURCE_FILE" before taking any action.
若与当前文件存在任何冲突，必须以 "$SOURCE_FILE" 为准。

This file is only a compatibility pointer for tools expecting "$target".
Do not maintain independent rules here unless explicitly required.

Generated at: $TIMESTAMP
TEMPLATE
done

echo "[OK] source file ready: $SOURCE_FILE"
for target in "${TARGET_FILES[@]}"; do
  echo "[OK] wrote pointer file: $target"
done
