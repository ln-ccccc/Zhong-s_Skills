# -*- coding: utf-8 -*-
"""OCR 存在但执行失败 → 同样降级 git-fallback(降级路径不因 OCR 半死而中断)"""
import unittest
from unittest import mock

from _helpers import load_preflight, make_repo


class TestOcrFailureFallback(unittest.TestCase):
    def test_ocr_nonzero_exit_falls_back(self):
        pf = load_preflight()
        repo = make_repo()
        with mock.patch("shutil.which", return_value="C:/fake/ocr.exe"), \
             mock.patch.object(pf, "run", return_value=(1, "", "boom")):
            r = pf.preflight(repo)
        self.assertEqual(r["mode"], "git-fallback")
        self.assertTrue(any("退出码 1" in n for n in r["notes"]))

    def test_ocr_bad_json_still_delegates_output(self):
        pf = load_preflight()
        repo = make_repo()
        with mock.patch("shutil.which", return_value="C:/fake/ocr.exe"), \
             mock.patch.object(pf, "run", return_value=(0, "not json", "")):
            r = pf.preflight(repo)
        self.assertEqual(r["mode"], "ocr-delegate")
        self.assertIn("ocr_output_raw", r)


if __name__ == "__main__":
    unittest.main()
