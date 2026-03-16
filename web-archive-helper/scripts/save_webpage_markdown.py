#!/usr/bin/env python3
import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from html.parser import HTMLParser

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from markdownify import markdownify as md_convert
except Exception:
    md_convert = None

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_file_name(url: str, override: str) -> str:
    if override.strip():
        return override.strip()
    parsed = urlparse(url)
    host = (parsed.netloc or "web").replace(":", "_")
    path = parsed.path.strip("/") or "index"
    path = re.sub(r"[^a-zA-Z0-9/_-]+", "-", path)
    path = path.replace("/", "_")
    return f"{host}_{path}.md"


def extract_main_html(raw_html: str) -> str:
    def pick_longest(tag: str) -> str:
        pattern = rf"(?is)<{tag}\b[^>]*>.*?</{tag}>"
        matches = re.findall(pattern, raw_html)
        if not matches:
            return ""
        return max(matches, key=len)

    article = pick_longest("article")
    if article:
        return article
    main = pick_longest("main")
    if main:
        return main
    body = pick_longest("body")
    if body:
        return body
    return raw_html


def html_to_markdown_high_fidelity(raw_html: str) -> str:
    if BeautifulSoup is None or md_convert is None:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "canvas"]):
        tag.decompose()

    target = soup.find("article") or soup.find("main") or soup.body or soup
    markdown = md_convert(
        str(target),
        heading_style="ATX",
        bullets="-",
        strip=["nav", "header", "footer", "aside"],
    )
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    return markdown


class MarkdownHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.ignore_stack = []
        self.list_stack = []
        self.link_stack = []
        self.in_pre = False
        self.in_code = False
        self.blocked_tokens = {"nav", "menu", "sidebar", "toc", "breadcrumb"}

    def _append(self, text: str):
        if text:
            self.out.append(text)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_map = {k.lower(): (v or "") for k, v in attrs}
        class_text = f"{attrs_map.get('class', '')} {attrs_map.get('id', '')}".lower()
        class_tokens = {tok for tok in re.split(r"[^a-z0-9]+", class_text) if tok}
        blocked_by_attr = any(token in class_tokens for token in self.blocked_tokens)

        if tag in {"script", "style", "noscript", "svg", "nav", "header", "footer", "aside"} or blocked_by_attr:
            self.ignore_stack.append(tag)
            return
        if self.ignore_stack:
            return

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self._append(f"\n\n{'#' * level} ")
        elif tag in {"p"}:
            self._append("\n\n")
        elif tag == "br":
            self._append("\n")
        elif tag in {"ul"}:
            self.list_stack.append({"type": "ul", "index": 0})
            self._append("\n")
        elif tag in {"ol"}:
            self.list_stack.append({"type": "ol", "index": 0})
            self._append("\n")
        elif tag == "li":
            indent = "  " * max(0, len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1]["type"] == "ol":
                self.list_stack[-1]["index"] += 1
                bullet = f"{self.list_stack[-1]['index']}. "
            else:
                bullet = "- "
            self._append(f"\n{indent}{bullet}")
        elif tag in {"strong", "b"}:
            self._append("**")
        elif tag in {"em", "i"}:
            self._append("*")
        elif tag == "blockquote":
            self._append("\n\n> ")
        elif tag == "pre":
            self.in_pre = True
            self._append("\n\n```text\n")
        elif tag == "code":
            if not self.in_pre:
                self._append("`")
            self.in_code = True
        elif tag == "a":
            href = attrs_map.get("href", "").strip()
            self.link_stack.append(href)
            self._append("[")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.ignore_stack:
            if tag == self.ignore_stack[-1]:
                self.ignore_stack.pop()
            return

        if tag in {"p", "blockquote"}:
            self._append("\n\n")
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self._append("\n")
        elif tag == "li":
            self._append("\n")
        elif tag in {"strong", "b"}:
            self._append("**")
        elif tag in {"em", "i"}:
            self._append("*")
        elif tag == "pre":
            self.in_pre = False
            self._append("\n```\n\n")
        elif tag == "code":
            if not self.in_pre:
                self._append("`")
            self.in_code = False
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else ""
            if href:
                self._append(f"]({href})")
            else:
                self._append("]")

    def handle_data(self, data):
        if self.ignore_stack:
            return
        if not data:
            return
        if self.in_pre:
            self._append(data)
            return
        text = html.unescape(data)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        if text.strip():
            self._append(text)

    def to_markdown(self) -> str:
        text = "".join(self.out)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        return text.strip()


def html_to_markdown(raw_html: str) -> str:
    markdown = html_to_markdown_high_fidelity(raw_html)
    if markdown:
        return markdown

    target = extract_main_html(raw_html)
    parser = MarkdownHTMLParser()
    parser.feed(target)
    parser.close()
    markdown_fallback = parser.to_markdown()
    if markdown_fallback:
        return markdown_fallback
    return html_to_markdown_fallback(target)


def html_to_markdown_fallback(raw_html: str) -> str:
    text = raw_html
    text = re.sub(r"(?is)<script\b[^>]*>.*?</script>", "", text)
    text = re.sub(r"(?is)<style\b[^>]*>.*?</style>", "", text)
    text = re.sub(r"(?is)<nav\b[^>]*>.*?</nav>", "", text)
    text = re.sub(r"(?is)<header\b[^>]*>.*?</header>", "", text)
    text = re.sub(r"(?is)<footer\b[^>]*>.*?</footer>", "", text)
    text = re.sub(r"(?is)<aside\b[^>]*>.*?</aside>", "", text)

    def replace_link(match):
        href = match.group(1) or ""
        body = re.sub(r"(?is)<[^>]+>", "", match.group(2) or "").strip()
        if not body:
            body = href
        if not href:
            return body
        return f"[{body}]({href})"

    text = re.sub(r'(?is)<a\b[^>]*href=["\']?([^"\' >]+)[^>]*>(.*?)</a>', replace_link, text)
    text = re.sub(r"(?is)<h1\b[^>]*>(.*?)</h1>", lambda m: f"\n\n# {strip_tags(m.group(1))}\n\n", text)
    text = re.sub(r"(?is)<h2\b[^>]*>(.*?)</h2>", lambda m: f"\n\n## {strip_tags(m.group(1))}\n\n", text)
    text = re.sub(r"(?is)<h3\b[^>]*>(.*?)</h3>", lambda m: f"\n\n### {strip_tags(m.group(1))}\n\n", text)
    text = re.sub(r"(?is)<h4\b[^>]*>(.*?)</h4>", lambda m: f"\n\n#### {strip_tags(m.group(1))}\n\n", text)
    text = re.sub(r"(?is)<h5\b[^>]*>(.*?)</h5>", lambda m: f"\n\n##### {strip_tags(m.group(1))}\n\n", text)
    text = re.sub(r"(?is)<h6\b[^>]*>(.*?)</h6>", lambda m: f"\n\n###### {strip_tags(m.group(1))}\n\n", text)
    text = re.sub(r"(?is)<li\b[^>]*>", "\n- ", text)
    text = re.sub(r"(?is)</(p|div|section|article|main|ul|ol|li|blockquote|pre|table|tr|h1|h2|h3|h4|h5|h6)>", "\n", text)
    text = re.sub(r"(?is)<br\\s*/?>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_tags(raw: str) -> str:
    clean = re.sub(r"(?is)<[^>]+>", "", raw)
    return clean_text(clean)


def extract_page_title(raw_html: str, markdown_text: str, url: str) -> str:
    patterns = [
        r'(?is)<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
        r'(?is)<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']',
        r'(?is)<meta[^>]+name=["\']twitter:title["\'][^>]+content=["\'](.*?)["\']',
        r'(?is)<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']twitter:title["\']',
        r"(?is)<title[^>]*>(.*?)</title>",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_html)
        if match:
            title = clean_text(strip_tags(match.group(1)))
            if title:
                return title

    for line in markdown_text.splitlines():
        value = line.strip()
        if value.startswith("# "):
            title = clean_text(value[2:])
            if title:
                return title

    parsed = urlparse(url)
    fallback = clean_text(parsed.path.strip("/").split("/")[-1].replace("-", " "))
    return fallback or url


def markdown_to_plain_text(markdown_text: str) -> str:
    text = markdown_text
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s*>\s*", "", text)
    text = re.sub(r"(?m)^\s*[-*+]\s*", "", text)
    text = re.sub(r"(?m)^\s*\d+\.\s*", "", text)
    text = re.sub(r"\[![A-Z]+\]", " ", text)
    text = text.replace("[", " ").replace("]", " ")
    text = re.sub(r"\b(Tip|Warning|Info|Note)\b", " ", text, flags=re.IGNORECASE)
    return clean_text(text)


def trim_sentence_safe(text: str, max_len: int = 220) -> str:
    if len(text) <= max_len:
        return text
    window = text[: max_len + 1]
    punctuation = "。！？；.!?;"
    cut = max(window.rfind(p) for p in punctuation)
    if cut > 20:
        return window[: cut + 1].strip()
    return window[:max_len].strip()


def normalize_callouts(markdown_text: str) -> str:
    text = markdown_text
    text = re.sub(
        r"(?m)^(#{1,6}\s[^\n]*?)\s*(Tip|Warning|Info|Note)\s*$",
        lambda m: f"{m.group(1)}\n\n> [!{m.group(2).upper()}]",
        text,
    )
    lines = []
    for raw in text.splitlines():
        value = raw.strip()
        if value in {"Tip", "Warning", "Info", "Note"}:
            lines.append(f"> [!{value.upper()}]")
            continue
        lines.append(raw)
    return "\n".join(lines)


def repair_obvious_broken_links(markdown_text: str) -> str:
    text = markdown_text
    text = re.sub(r"\((ttps://[^)\s]+)\)", r"(h\1)", text)
    text = re.sub(r"\((ttp://[^)\s]+)\)", r"(h\1)", text)
    return text


def summarize(markdown_text: str, title: str = "") -> str:
    if not markdown_text.strip():
        return "归档成功，但正文提取为空，建议稍后重试。"
    plain = markdown_to_plain_text(markdown_text)
    if not plain:
        return "归档成功，但正文提取为空，建议稍后重试。"

    headings = [
        clean_text(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", h))
        for h in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", markdown_text)
    ]
    heading_preview = "、".join(h for h in headings[:4] if h)

    keyword_specs = [
        ("配置与权限设置", r"config|toml|配置|权限|sandbox|approval"),
        ("命令与工作流", r"/status|/approvals|/mcp|命令|工作流|continue|resume"),
        ("MCP 接入与兼容", r"mcp|sse|stdio|server|context7|deepwiki"),
        ("跨平台环境差异", r"windows|wsl|macos|linux|跨平台"),
        ("仓库规范与工具链", r"agents\.md|rg|fd|ast-grep|工具"),
    ]
    aspects = [label for label, pattern in keyword_specs if re.search(pattern, plain, re.IGNORECASE)]
    if not aspects:
        aspects = ["核心实践与操作要点"]

    code_blocks = markdown_text.count("```") // 2
    links = len(re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", markdown_text))
    section_count = len(headings)
    topic = clean_text(title) or (headings[0] if headings else "该文章")

    sentence1 = f"本文围绕《{topic}》系统梳理了{ '、'.join(aspects[:3]) }。"
    detail_fragments = []
    if heading_preview:
        detail_fragments.append(f"内容覆盖了 {heading_preview} 等章节")
    if code_blocks > 0:
        detail_fragments.append(f"并配有约 {code_blocks} 段配置/命令示例")
    if links > 0:
        detail_fragments.append(f"附带 {links} 个参考链接")
    if section_count > 0:
        detail_fragments.append(f"整体结构约 {section_count} 个主题段落")
    sentence2 = "，".join(detail_fragments) + "。"
    summary = f"{sentence1}{sentence2}"
    return trim_sentence_safe(summary, max_len=220)


def fetch_html_static(url: str, timeout: int) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="ignore")


def fetch_html_browser(url: str, timeout: int) -> str:
    if sync_playwright is None:
        raise RuntimeError("browser 渲染不可用：未安装 playwright")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
        content = page.content()
        browser.close()
    return content


def fetch_html(url: str, timeout: int, render_mode: str = "auto") -> str:
    if render_mode == "static":
        return fetch_html_static(url, timeout)
    if render_mode == "browser":
        return fetch_html_browser(url, timeout)

    # auto: 先尝试浏览器渲染，失败后回退静态抓取
    try:
        return fetch_html_browser(url, timeout)
    except Exception:
        return fetch_html_static(url, timeout)


def save_markdown(url: str, output_dir: Path, name: str, timeout: int, render_mode: str = "auto") -> Path:
    html = fetch_html(url, timeout, render_mode=render_mode)
    markdown_body = repair_obvious_broken_links(normalize_callouts(html_to_markdown(html)))
    page_title = extract_page_title(html, markdown_body, url)
    summary = summarize(markdown_body, title=page_title)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = build_file_name(url, name)
    out = output_dir / file_name
    content = "\n".join(
        [
            f"# {page_title}",
            "",
            f"- 来源: {url}",
            f"- 标题: {page_title}",
            f"- 归档日期: {date.today().isoformat()}",
            "",
            "## AI速读",
            summary,
            "",
            "## 正文",
            markdown_body,
            "",
        ]
    )
    out.write_text(content, encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="保存网页为 Markdown")
    parser.add_argument("url", help="网页 URL")
    parser.add_argument("-o", "--output-dir", required=True, help="输出目录")
    parser.add_argument("--name", default="", help="文件名（可选）")
    parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数")
    parser.add_argument("--render-mode", choices=["auto", "static", "browser"], default="auto")
    args = parser.parse_args()

    try:
        saved = save_markdown(
            url=args.url,
            output_dir=Path(args.output_dir).expanduser(),
            name=args.name,
            timeout=args.timeout,
            render_mode=args.render_mode,
        )
    except Exception as err:
        print(f"ERROR: 保存失败: {err}", file=sys.stderr)
        return 1

    print(f"SAVED: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
