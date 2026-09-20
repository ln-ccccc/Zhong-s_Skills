# -*- coding: utf-8 -*-
"""选期决策规则测试: complete 优先取最晚 / 无 complete 回退最新并标记 / 窗口过滤"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from gehi_utils import pick_latest, pick_in_windows


class TestPickLatest(unittest.TestCase):
    def test_complete_preferred_even_when_incomplete_is_newer(self):
        cov = {"2024-01-01": 0.999, "2024-06-01": 0.7}
        d, comp = pick_latest(cov)
        self.assertEqual(d, "2024-01-01")
        self.assertTrue(comp)

    def test_no_complete_falls_back_to_latest_with_flag(self):
        cov = {"2023-05-01": 0.8, "2024-06-01": 0.7}
        d, comp = pick_latest(cov)
        self.assertEqual(d, "2024-06-01")
        self.assertFalse(comp)

    def test_empty(self):
        self.assertEqual(pick_latest({}), (None, None))

    def test_boundary_coverage_at_threshold_counts_complete(self):
        d, comp = pick_latest({"2024-01-01": 0.999})
        self.assertEqual(d, "2024-01-01")
        self.assertTrue(comp)


class TestPickInWindows(unittest.TestCase):
    COV = {"2013-06-01": 0.99, "2015-01-01": 0.999,
           "2018-03-01": 0.999, "2022-09-01": 0.5}

    WINDOWS = [("w1", 20120101, 20161231),
               ("w2", 20170101, 20201231),
               ("w3", 20210101, 20251231),
               ("w4", 20230101, 20231231)]

    def test_windows(self):
        res = pick_in_windows(self.COV, self.WINDOWS)
        self.assertEqual(res["w1"], ("2015-01-01", True))    # 窗口内 complete 优先
        self.assertEqual(res["w2"], ("2018-03-01", True))
        self.assertEqual(res["w3"], ("2022-09-01", False))   # 无 complete 回退最新并标记
        self.assertEqual(res["w4"], (None, None))            # 窗口内无影像


if __name__ == "__main__":
    unittest.main()
