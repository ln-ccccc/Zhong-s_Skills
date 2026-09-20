# -*- coding: utf-8 -*-
"""--retry 选择逻辑回归测试:成功跳过、失败/缺失重做(2026-09-20 修复反转 bug 的守卫)"""
import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
bl = importlib.import_module("batch_latest")


class TestSelectTodo(unittest.TestCase):
    MINES = [{"fid": 1}, {"fid": 2}, {"fid": 3}, {"fid": 4}]

    def test_retry_skips_ok_and_retries_fail_and_missing(self):
        rows = {"1": {"status": "OK"},
                "2": {"status": "OK_incomplete"},
                "3": {"status": "FAIL_download"}}
        todo = bl.select_todo(self.MINES, rows, only_missing=True)
        self.assertEqual([m["fid"] for m in todo], [3, 4])

    def test_full_runs_all_even_with_ok_rows(self):
        rows = {"1": {"status": "OK"}}
        todo = bl.select_todo(self.MINES, rows, only_missing=False)
        self.assertEqual(len(todo), 4)

    def test_retry_with_empty_manifest_retries_everything(self):
        todo = bl.select_todo(self.MINES, {}, only_missing=True)
        self.assertEqual(len(todo), 4)

    def test_retry_status_case_sensitive_ok_prefix_only(self):
        rows = {"1": {"status": "ok"}}   # 小写 ok 不算成功(与写入侧大写约定一致)
        todo = bl.select_todo(self.MINES, rows, only_missing=True)
        self.assertEqual([m["fid"] for m in todo], [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
