# -*- coding: utf-8 -*-
"""工作区模式文件面:staged ∪ unstaged ∪ untracked(与 OCR workspace review 对齐)"""
import os
import unittest
from unittest import mock

from _helpers import git, load_preflight, make_repo, write


class TestWorkspaceTracked(unittest.TestCase):
    def test_modified_tracked_file_found(self):
        pf = load_preflight()
        repo = make_repo()
        write(os.path.join(repo, "a.txt"), "modified\n")
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo)
        self.assertIn("a.txt", r["files"])
        self.assertEqual(r["mode"], "git-fallback")

    def test_staged_file_found(self):
        pf = load_preflight()
        repo = make_repo()
        git(repo, "checkout", "main")
        write(os.path.join(repo, "c.txt"), "staged\n")
        git(repo, "add", ".")
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo)
        self.assertIn("c.txt", r["files"])


class TestWorkspaceUntracked(unittest.TestCase):
    def test_untracked_file_found(self):
        # 回归墓碑:git diff --name-only HEAD 不含 untracked,必须 ls-files --others 补齐
        pf = load_preflight()
        repo = make_repo()
        git(repo, "checkout", "main")
        write(os.path.join(repo, "untracked.txt"), "new\n")
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo)
        self.assertIn("untracked.txt", r["files"])

    def test_clean_tree_empty(self):
        pf = load_preflight()
        repo = make_repo()
        git(repo, "checkout", "main")
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo)
        self.assertEqual(r["files"], [])


if __name__ == "__main__":
    unittest.main()
