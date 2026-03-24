import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("publish_crazy_talk.py")


def load_module():
    spec = importlib.util.spec_from_file_location("publish_crazy_talk", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载发布脚本")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CrazyTalkPublisherTest(unittest.TestCase):
    def test_resolve_repo_from_existing_crazy_talk_and_write_cache(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "workspace" / "hugh-note"
            crazy_talk = repo / "content" / "crazy-talk"
            crazy_talk.mkdir(parents=True)
            (repo / "hugo.toml").write_text("baseURL = 'https://example.com/'\n", encoding="utf-8")
            state_path = tmp / "state.json"

            resolved = module.resolve_repo_path(
                repo / "content",
                state_path=state_path,
            )

            self.assertEqual(resolved, repo.resolve())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["repo_hint_type"], "cwd_relative")
            self.assertFalse(Path(state["repo_path_hint"]).is_absolute())
            self.assertEqual(state["target_relative_path"], "content/crazy-talk")

    def test_resolve_repo_from_hugh_note_and_create_crazy_talk(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            workspace = tmp / "workspace"
            repo = workspace / "hugh-note"
            (repo / "content").mkdir(parents=True)
            (repo / "hugo.toml").write_text("baseURL = 'https://example.com/'\n", encoding="utf-8")
            state_path = tmp / "state.json"

            resolved = module.resolve_repo_path(
                workspace,
                state_path=state_path,
            )

            self.assertEqual(resolved, repo.resolve())
            self.assertTrue((repo / "content" / "crazy-talk").is_dir())

    def test_resolve_repo_prefers_valid_cache_without_search(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = Path.cwd()
            tmp = Path(tmpdir)
            repo = tmp / "workspace" / "hugh-note"
            (repo / "content" / "crazy-talk").mkdir(parents=True)
            (repo / "hugo.toml").write_text("baseURL = 'https://example.com/'\n", encoding="utf-8")
            state_path = tmp / "state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "repo_hint_type": "cwd_relative",
                        "repo_path_hint": "hugh-note",
                        "target_relative_path": "content/crazy-talk",
                    }
                ),
                encoding="utf-8",
            )

            os.chdir(repo.parent)
            try:
                resolved = module.resolve_repo_path(
                    tmp / "another-place",
                    state_path=state_path,
                )
            finally:
                os.chdir(old_cwd)

            self.assertEqual(resolved, repo.resolve())

    def test_create_daily_file_with_timestamp(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "content" / "crazy-talk").mkdir(parents=True)
            now = datetime.fromisoformat("2026-03-24T10:32:00+08:00")

            result = module.upsert_crazy_talk(repo, "测试一下效果", now)

            self.assertTrue(result.created)
            self.assertEqual(result.commit_message, "新增 2026-03-24 疯言疯语")
            target = (repo / "content" / "crazy-talk" / "2026-03-24.md").resolve()
            self.assertEqual(result.file_path, target)
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                """---
title: "2026-03-24"
draft: false
date: 2026-03-24T00:00:00+08:00
description: "疯言疯语。"
tags: [疯言疯语]
---

### 10:32

测试一下效果
""",
            )

    def test_append_entry_with_two_blank_lines_between_blocks(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            target_dir = repo / "content" / "crazy-talk"
            target_dir.mkdir(parents=True)
            target = target_dir / "2026-03-24.md"
            target.write_text(
                """---
title: "2026-03-24"
draft: false
date: 2026-03-24T00:00:00+08:00
description: "疯言疯语。"
tags: [疯言疯语]
---

### 10:32

第一条
""",
                encoding="utf-8",
            )

            now = datetime.fromisoformat("2026-03-24T14:08:00+08:00")
            result = module.upsert_crazy_talk(repo, "第二条", now)

            self.assertFalse(result.created)
            self.assertEqual(result.commit_message, "更新 2026-03-24 疯言疯语")
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                """---
title: "2026-03-24"
draft: false
date: 2026-03-24T00:00:00+08:00
description: "疯言疯语。"
tags: [疯言疯语]
---

### 10:32

第一条


### 14:08

第二条
""",
            )

    def test_commit_and_push_only_target_file(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            remote_repo = tmp / "remote.git"
            work_repo = tmp / "work"

            subprocess.run(["git", "init", "--bare", str(remote_repo)], check=True, capture_output=True)
            subprocess.run(["git", "init", str(work_repo)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(work_repo), "config", "user.name", "Codex Test"], check=True)
            subprocess.run(["git", "-C", str(work_repo), "config", "user.email", "codex@example.com"], check=True)
            subprocess.run(["git", "-C", str(work_repo), "branch", "-M", "main"], check=True)
            subprocess.run(["git", "-C", str(work_repo), "remote", "add", "origin", str(remote_repo)], check=True)

            result = module.upsert_crazy_talk(
                work_repo,
                "测试发布流程",
                datetime.fromisoformat("2026-03-24T21:45:00+08:00"),
            )
            module.commit_and_push(work_repo, result.file_path, result.commit_message, push=True)

            log = subprocess.run(
                ["git", "-C", str(work_repo), "log", "--oneline", "-1"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("新增 2026-03-24 疯言疯语", log)

            remote_heads = subprocess.run(
                ["git", "--git-dir", str(remote_repo), "branch", "--list"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("main", remote_heads)


if __name__ == "__main__":
    unittest.main()
