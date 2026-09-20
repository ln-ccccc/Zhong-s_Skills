# -*- coding: utf-8 -*-
"""无 OCR 时降级 git-fallback"""
import unittest
from unittest import mock

from _helpers import load_preflight, make_repo


class TestOcrMissing(unittest.TestCase):
    def test_falls_back_to_git_when_ocr_absent(self):
        pf = load_preflight()
        repo = make_repo()
        with mock.patch("shutil.which", return_value=None):
            r = pf.preflight(repo)
        self.assertEqual(r["mode"], "git-fallback")
        self.assertTrue(any("降级" in n for n in r["notes"]))


if __name__ == "__main__":
    unittest.main()
