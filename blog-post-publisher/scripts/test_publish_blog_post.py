import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("publish_blog_post.py")


def load_module():
    spec = importlib.util.spec_from_file_location("publish_blog_post", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载发布脚本")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BlogPostPublisherTest(unittest.TestCase):
    def test_resolve_repo_from_existing_posts_and_write_cache(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "workspace" / "hugh-note"
            posts_dir = repo / "content" / "posts"
            posts_dir.mkdir(parents=True)
            (repo / "hugo.toml").write_text("baseURL = 'https://example.com/'\n", encoding="utf-8")
            state_path = tmp / "state.json"

            resolved = module.resolve_repo_path(repo / "content", state_path=state_path)

            self.assertEqual(resolved, repo.resolve())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["repo_hint_type"], "cwd_relative")
            self.assertFalse(Path(state["repo_path_hint"]).is_absolute())
            self.assertEqual(state["target_relative_path"], "content/posts")

    def test_resolve_repo_from_hugh_note_and_create_posts(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            workspace = tmp / "workspace"
            repo = workspace / "hugh-note"
            repo.mkdir(parents=True)
            (repo / "hugo.toml").write_text("baseURL = 'https://example.com/'\n", encoding="utf-8")
            state_path = tmp / "state.json"

            resolved = module.resolve_repo_path(workspace, state_path=state_path)

            self.assertEqual(resolved, repo.resolve())
            self.assertTrue((repo / "content" / "posts").is_dir())

    def test_publish_from_inbox_file(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            posts_dir = repo / "content" / "posts"
            posts_dir.mkdir(parents=True)
            inbox_dir = tmp / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "inbox" / "posts"
            inbox_dir.mkdir(parents=True)
            source = inbox_dir / "测试文章.md"
            source.write_text(
                "---\n"
                'title: "已有标题"\n'
                "draft: false\n"
                "date: 2026-01-01T10:00:00+08:00\n"
                'description: "已有摘要"\n'
                "tags: [杂记]\n"
                "---\n\n"
                "这是来自 inbox 的正文。\n",
                encoding="utf-8",
            )
            now = datetime.fromisoformat("2026-03-24T20:00:00+08:00")

            result = module.publish_post(
                repo_path=repo,
                payload="测试文章",
                now=now,
                inbox_dir=inbox_dir,
            )

            self.assertTrue(result.from_inbox)
            self.assertEqual(result.file_path, (posts_dir / "测试文章.md").resolve())
            self.assertIn('title: "已有标题"', result.file_path.read_text(encoding="utf-8"))
            self.assertEqual(result.commit_message, "发布博客：测试文章.md")

    def test_publish_from_inbox_file_without_front_matter_wraps_template(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            posts_dir = repo / "content" / "posts"
            posts_dir.mkdir(parents=True)
            inbox_dir = tmp / "inbox" / "posts"
            inbox_dir.mkdir(parents=True)
            source = inbox_dir / "无头文件.md"
            source.write_text("这是来自 inbox 的正文。\n", encoding="utf-8")
            now = datetime.fromisoformat("2026-03-24T20:00:00+08:00")

            result = module.publish_post(
                repo_path=repo,
                payload="无头文件",
                now=now,
                inbox_dir=inbox_dir,
                description_override="文章记录了最近一段时间的情绪片段与生活感受。",
            )

            self.assertTrue(result.from_inbox)
            content = result.file_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            self.assertIn('title: "无头文件"', content)
            self.assertIn('description: "文章记录了最近一段时间的情绪片段与生活感受。"', content)
            self.assertIn("这是来自 inbox 的正文。", content)

    def test_publish_from_plain_text_creates_new_post(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            posts_dir = repo / "content" / "posts"
            posts_dir.mkdir(parents=True)
            now = datetime.fromisoformat("2026-03-24T20:15:30+08:00")

            result = module.publish_post(
                repo_path=repo,
                payload="发布博客 标题：测试标题\n这是直接输入的正文",
                now=now,
                inbox_dir=tmp / "not-exists",
                description_override="文章介绍了直接输入正文的核心观点与背景。",
            )

            self.assertFalse(result.from_inbox)
            self.assertEqual(result.file_path.name, "2026-03-24-201530.md")
            content = result.file_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            self.assertIn('title: "测试标题"', content)
            self.assertIn("draft: false", content)
            self.assertIn("date: 2026-03-24T20:15:30+08:00", content)
            self.assertIn('description: "文章介绍了直接输入正文的核心观点与背景。"', content)
            self.assertIn("tags: [杂记]", content)
            self.assertIn("这是直接输入的正文", content)
            self.assertEqual(result.commit_message, "发布博客：2026-03-24-201530.md")

    def test_plain_text_without_title_raises_error(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            (repo / "content" / "posts").mkdir(parents=True)

            with self.assertRaisesRegex(ValueError, "未检测到标题"):
                module.publish_post(
                    repo_path=repo,
                    payload="发布博客 这是没有标题的正文",
                    now=datetime.fromisoformat("2026-03-24T20:20:20+08:00"),
                    inbox_dir=tmp / "not-exists",
                    description_override="这是一句摘要。",
                )

    def test_plain_text_without_description_raises_error(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            (repo / "content" / "posts").mkdir(parents=True)

            with self.assertRaisesRegex(ValueError, "缺少文章摘要"):
                module.publish_post(
                    repo_path=repo,
                    payload="发布博客 标题：测试标题\n这里是正文",
                    now=datetime.fromisoformat("2026-03-24T20:20:20+08:00"),
                    inbox_dir=tmp / "not-exists",
                )

    def test_long_multiline_payload_with_title_is_treated_as_text_not_filename(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            (repo / "content" / "posts").mkdir(parents=True)
            inbox_dir = tmp / "inbox" / "posts"
            inbox_dir.mkdir(parents=True)
            now = datetime.fromisoformat("2026-03-24T20:20:20+08:00")

            payload = "发布博客 标题：长文测试\n" + ("很长的正文" * 80) + "\n第二行内容"
            result = module.publish_post(
                repo_path=repo,
                payload=payload,
                now=now,
                inbox_dir=inbox_dir,
                description_override="文章系统梳理了长文场景下的发布策略与关键细节。",
            )

            self.assertFalse(result.from_inbox)
            self.assertTrue(result.file_path.is_file())
            content = result.file_path.read_text(encoding="utf-8")
            self.assertIn('title: "长文测试"', content)
            self.assertIn("第二行内容", content)
            self.assertIn('description: "文章系统梳理了长文场景下的发布策略与关键细节。"', content)

    def test_description_is_from_summary_override(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "hugh-note"
            (repo / "content" / "posts").mkdir(parents=True)
            now = datetime.fromisoformat("2026-03-24T20:33:33+08:00")

            payload = (
                "发布博客 标题：描述测试\n"
                "随着 Codex、Claude Code 等 AI 编程工具的普及，我们似乎进入了动动嘴皮子就能写代码的时代。"
                "然而，项目复杂后依旧需要工程化纪律。"
            )
            result = module.publish_post(
                repo_path=repo,
                payload=payload,
                now=now,
                inbox_dir=tmp / "not-exists",
                description_override="文章讨论了 AI 编程工具普及后为何仍需工程化纪律与流程约束。",
            )
            content = result.file_path.read_text(encoding="utf-8")
            self.assertIn(
                'description: "文章讨论了 AI 编程工具普及后为何仍需工程化纪律与流程约束。"',
                content,
            )

    def test_commit_and_push_only_target_file(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            remote_repo = tmp / "remote.git"
            work_repo = tmp / "work"
            inbox_dir = tmp / "inbox" / "posts"

            subprocess.run(["git", "init", "--bare", str(remote_repo)], check=True, capture_output=True)
            subprocess.run(["git", "init", str(work_repo)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(work_repo), "config", "user.name", "Codex Test"], check=True)
            subprocess.run(["git", "-C", str(work_repo), "config", "user.email", "codex@example.com"], check=True)
            subprocess.run(["git", "-C", str(work_repo), "branch", "-M", "main"], check=True)
            subprocess.run(["git", "-C", str(work_repo), "remote", "add", "origin", str(remote_repo)], check=True)
            (work_repo / "content" / "posts").mkdir(parents=True)
            inbox_dir.mkdir(parents=True)
            (inbox_dir / "发布测试.md").write_text("测试推送\n", encoding="utf-8")

            result = module.publish_post(
                repo_path=work_repo,
                payload="发布测试",
                now=datetime.fromisoformat("2026-03-24T21:00:00+08:00"),
                inbox_dir=inbox_dir,
                description_override="文章用于验证发布流程在提交与推送阶段的完整性。",
            )
            module.commit_and_push(work_repo, result.file_path, result.commit_message, push=True)

            log = subprocess.run(
                ["git", "-C", str(work_repo), "log", "--oneline", "-1"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("发布博客：发布测试.md", log)

            remote_heads = subprocess.run(
                ["git", "--git-dir", str(remote_repo), "branch", "--list"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("main", remote_heads)


if __name__ == "__main__":
    unittest.main()
