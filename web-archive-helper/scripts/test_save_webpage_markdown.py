import importlib.util
import re
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "save_webpage_markdown.py"
SPEC = importlib.util.spec_from_file_location("save_webpage_markdown", SCRIPT_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


class SaveWebpageMarkdownTest(unittest.TestCase):
    def test_summary_is_conceptual_not_raw_excerpt(self):
        markdown = """
## 前言
这并不是一篇零基础指南，需要读者先有一些使用经验。

## 基础配置
本文介绍了 config.toml 的关键参数与权限配置建议。

## 命令
还总结了 /status、/approvals、/mcp 的常见使用方式。
""".strip()
        summary = MOD.summarize(markdown)
        self.assertRegex(summary, r"本文|文章|主要")
        self.assertNotIn("这并不是一篇零基础指南，需要读者先有一些使用经验。", summary)
        self.assertNotIn("## 前言", summary)
        self.assertNotRegex(summary, r"\[[^\]]+\]\([^)]+\)")

    def test_html_to_markdown_keeps_table_and_code_block(self):
        raw_html = """
<html><body><article>
  <h1>测试标题</h1>
  <p>说明段落</p>
  <table>
    <tr><th>键</th><th>值</th></tr>
    <tr><td>model</td><td>gpt-5-codex</td></tr>
  </table>
  <pre><code>model = "gpt-5-codex"</code></pre>
</article></body></html>
""".strip()
        markdown = MOD.html_to_markdown(raw_html)
        self.assertIn("```", markdown)
        self.assertIn('model = "gpt-5-codex"', markdown)
        self.assertRegex(markdown, r"\|.+\|")

    def test_repair_obvious_broken_links(self):
        text = "[config.md](ttps://github.com/openai/codex/blob/main/docs/config.md)"
        repaired = MOD.repair_obvious_broken_links(text)
        self.assertIn("https://github.com/openai/codex/blob/main/docs/config.md", repaired)


if __name__ == "__main__":
    unittest.main()
