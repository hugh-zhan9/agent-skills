import subprocess
import sys
from datetime import datetime


RISK_LEVEL_HINTS = {
    "S0": "阻断级: 可能导致服务不可用、数据损坏或严重安全问题",
    "S1": "高级: 关键流程失败、主要功能不可用或明显业务回归",
    "S2": "中级: 局部功能异常、可绕过但影响效率",
    "S3": "低级: 轻微行为偏差或日志/可观测性影响",
}


def normalize_risk_level(raw: str) -> str:
    value = (raw or "").strip().upper()
    aliases = {
        "高": "S1",
        "中": "S2",
        "低": "S3",
        "阻断": "S0",
        "CRITICAL": "S0",
        "HIGH": "S1",
        "MEDIUM": "S2",
        "LOW": "S3",
    }
    if value in RISK_LEVEL_HINTS:
        return value
    if value in aliases:
        return aliases[value]
    return "S2"


def parse_changed_files(raw: str):
    value = (raw or "").strip()
    if not value:
        return []
    items = [x.strip() for x in value.split(",")]
    return [x for x in items if x]


def contains_chinese(text: str) -> bool:
    if not text:
        return False
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def detect_changed_files():
    try:
        out = subprocess.check_output([
            "git",
            "status",
            "--porcelain",
        ], text=True)
    except Exception:
        return []

    files = []
    seen = set()
    for line in out.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path and path not in seen:
            seen.add(path)
            files.append(path)
    return files


def build_files_block(files):
    if not files:
        return "- (未检测到变更文件或当前目录非 git 仓库)"
    return "\n".join([f"- `{p}`" for p in files])


def append_log(change_type, summary, risk_analysis, risk_level="S2", changed_files=None):
    normalized_level = normalize_risk_level(risk_level)
    files = changed_files or detect_changed_files()
    files_block = build_files_block(files)

    entry = f"""## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] [{change_type}]
- **Change**: {summary}
- **Risk Analysis**: {risk_analysis}
- **Risk Level**: {normalized_level}（{RISK_LEVEL_HINTS.get(normalized_level, '')}）
- **Changed Files**:
{files_block}
----------------------------------------
"""
    with open("docs/AI_CHANGELOG.md", "a", encoding="utf-8") as f:
        f.write(entry)
    print("✅ [Flight Recorder] Log appended to AI_CHANGELOG.md")


def print_usage():
    print("Usage (位置参数): python log_change.py <type> <summary_zh> <risk_zh> [risk_level] [changed_files]")
    print("Usage (长参数兼容): python log_change.py --change_type <type> --summary <summary_zh> --risk_analysis <risk_zh> [--risk_level <level>] [--changed_files <csv>]")
    print("Risk level: S0/S1/S2/S3 (or 阻断/高/中/低)")
    print("changed_files: 可选，逗号分隔；不传则自动检测 git 变更文件")


def parse_named_args(argv):
    mapping = {}
    i = 1
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--"):
            i += 1
            continue
        key = token[2:]
        if i + 1 >= len(argv):
            mapping[key] = ""
            break
        mapping[key] = argv[i + 1]
        i += 2
    return mapping


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    named_args = parse_named_args(sys.argv)

    if "change_type" in named_args or "summary" in named_args or "risk_analysis" in named_args:
        change_type = named_args.get("change_type", "")
        summary = named_args.get("summary", "")
        risk_analysis = named_args.get("risk_analysis", "")
        risk_level = named_args.get("risk_level", "S2")
        changed_files = parse_changed_files(named_args.get("changed_files", ""))
    else:
        if len(sys.argv) < 4:
            print_usage()
            sys.exit(1)
        change_type = sys.argv[1]
        summary = sys.argv[2]
        risk_analysis = sys.argv[3]
        risk_level = sys.argv[4] if len(sys.argv) >= 5 else "S2"
        changed_files = parse_changed_files(sys.argv[5]) if len(sys.argv) >= 6 else []

    if not contains_chinese(summary):
        print("错误: summary 必须使用中文")
        sys.exit(1)
    if not contains_chinese(risk_analysis):
        print("错误: risk_analysis 必须使用中文")
        sys.exit(1)
    append_log(change_type, summary, risk_analysis, risk_level, changed_files)
