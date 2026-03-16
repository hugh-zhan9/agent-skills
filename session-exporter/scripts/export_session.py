import argparse
import glob
import json
import os
import sys


def should_skip_message(role, text):
    if role != "user":
        return False

    stripped = text.strip()
    if stripped.startswith("# AGENTS.md instructions for "):
        return True
    if stripped.startswith("<skill>") and stripped.endswith("</skill>"):
        return True
    return False


def find_session_file(session_id):
    pattern = os.path.expanduser(f"~/.codex/sessions/**/rollout-*{session_id}.jsonl")
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        return ""
    matches.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return matches[0]


def extract_messages(jsonl_path):
    messages = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("type") != "response_item":
                continue
            payload = data.get("payload", {})
            if payload.get("type") != "message":
                continue
            role = payload.get("role")
            if role not in ("user", "assistant"):
                continue
            content_items = payload.get("content", [])
            parts = []
            for item in content_items:
                item_type = item.get("type")
                if item_type in ("input_text", "output_text"):
                    parts.append(item.get("text", ""))
            text = "\n".join([p for p in parts if p is not None]).strip()
            if text and not should_skip_message(role, text):
                messages.append((role, text))
    return messages


def format_markdown(messages):
    out = []
    for role, text in messages:
        if role == "user":
            out.append(f"> {text}\n")
        else:
            out.append(f"{text}\n")
    out.append("\n")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    jsonl_path = find_session_file(args.session_id)
    if not jsonl_path:
        print(f"Session file not found for id: {args.session_id}")
        sys.exit(1)

    messages = extract_messages(jsonl_path)
    if not messages:
        print(f"No messages found in {jsonl_path}")
        sys.exit(1)

    content = format_markdown(messages)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Session exported to {args.output}")


if __name__ == "__main__":
    main()
