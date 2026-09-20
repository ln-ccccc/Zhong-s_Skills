# -*- coding: utf-8 -*-
"""区间模式回归墓碑(P1-1):--from/--to 必须在 fallback 里按 merge-base 取 range diff。

原 bug:range 参数只被 OCR 路径消费,fallback 只查工作区——干净工作区时 b.txt
这类已提交变更完全漏掉(files=[])。
"""
import unittest
from unittest import mock

from _helpers import load_preflight, make_repo


class TestRangeDiff(unittest.TestCase):
    def test_range_diff_without_ocr_finds_committed_change(self):
        pf = load_preflight()
        repo = make_repo()   # main: a.txt;feature: +b.txt,工作区干净
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo, from_ref="main", to_ref="feature")
        self.assertEqual(r["mode"], "git-fallback")
        self.assertEqual(r["files"], ["b.txt"])
        self.assertTrue(any("merge-base" in n for n in r["notes"]))
        self.assertTrue(any("b" in c for c in r["recent_commits"]))

    def test_range_mode_same_file_different_content(self):
        pf = load_preflight()
        repo = make_repo()
        with open(f"{repo}/a.txt", "w", encoding="utf-8") as f:
            f.write("changed on feature\n")
        import subprocess
        subprocess.run(["git", "commit", "-am", "edit a"], cwd=repo, check=True, capture_output=True)
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo, from_ref="main", to_ref="feature")
        self.assertIn("a.txt", r["files"])


if __name__ == "__main__":
    unittest.main()
