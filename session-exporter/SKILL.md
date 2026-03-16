---
name: session-exporter
description: Export the full assistant-user conversation to ./docs/session (relative to current working directory) as markdown after any user request to save or export chat history; requires a session id.
---

# Session Exporter

## When to use
Use this skill whenever the user asks to export/save our conversation or chat history.

If the user does not provide a session id, ask them to get it from `/status` and provide it.

## Output requirements
- Save under `./docs/session/` relative to the current working directory (create the folder if missing).
- Format as markdown with the exact pattern:
  ```markdown
  > user message
  assistant message
  
  > user message
  assistant message
  
  ```
- File name: generate a short, descriptive kebab-case name based on your summary of the session.

## Workflow
1. If session id is missing, ask the user to provide it (they can get it via `/status`).
2. Summarize the session in 4–8 words and create a kebab-case filename (e.g. `proxy-setup-and-zsh-fixes.md`).
3. Ensure `./docs/session/` exists under the current working directory.
4. Export the session using `scripts/export_session.py` with `--session-id` and `--output`.

## Script usage
```
python3 scripts/export_session.py --session-id <id> --output <output_path>
```
The script finds the matching session JSONL under `~/.codex/sessions`, formats it, and writes markdown to the given path.
