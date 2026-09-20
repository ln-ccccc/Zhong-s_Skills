# -*- coding: utf-8 -*-
"""地理配准测试: bbox 推导 GSD / 下载范围 QA / GeoTIFF 标签回写 / max_date 动态化"""
import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from gehi_utils import (default_max_date, gsd_from_bbox, read_geotags,
                        write_geotiff, z18_bounds_ok)
import numpy as np

BBOX = (100.0, 30.0, 100.1, 30.1)   # 宽 0.1°, 高 0.1°


class TestGsdFromBbox(unittest.TestCase):
    def test_exact_span(self):
        gsd = gsd_from_bbox(BBOX, width=100, height=50)
        self.assertAlmostEqual(gsd[0] * 100, 0.1)
        self.assertAlmostEqual(gsd[1] * 50, 0.1)

    def test_not_square_when_dims_differ(self):
        gsd = gsd_from_bbox(BBOX, width=100, height=200)
        self.assertAlmostEqual(gsd[0], 0.001)
        self.assertAlmostEqual(gsd[1], 0.0005)


class TestZ18BoundsOk(unittest.TestCase):
    # z18 栅格恰与 bbox 对齐: NW=(100,30.1), 尺寸 1000x1000, 每像素 0.0001°
    PS = (0.0001, 0.0001)
    TP = (0.0, 0.0, 0.0, 100.0, 30.1, 0.0)

    def test_aligned_passes(self):
        self.assertTrue(z18_bounds_ok(BBOX, 1000, 1000, self.PS, self.TP))

    def test_small_offset_within_tolerance_passes(self):
        tp_shift = (0.0, 0.0, 0.0, 100.0 + 0.0002, 30.1 - 0.0002, 0.0)  # 偏 2 px
        self.assertTrue(z18_bounds_ok(BBOX, 1000, 1000, self.PS, tp_shift, tol_px=4))

    def test_large_offset_fails(self):
        tp_shift = (0.0, 0.0, 0.0, 100.0 + 0.001, 30.1, 0.0)  # 偏 10 px
        self.assertFalse(z18_bounds_ok(BBOX, 1000, 1000, self.PS, tp_shift, tol_px=4))

    def test_wrong_size_fails(self):
        # tiepoint 对齐但栅格只有一半大小 → 实际范围只有 bbox 一半
        self.assertFalse(z18_bounds_ok(BBOX, 500, 500, self.PS, self.TP))


class TestGeoTiffRoundtrip(unittest.TestCase):
    def test_write_and_read_tags(self):
        arr = np.zeros((4, 6, 3), dtype=np.uint8)
        gsd = gsd_from_bbox(BBOX, width=6, height=4)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.tif")
            write_geotiff(arr, path, gsd=gsd, corner_lonlat=(BBOX[0], BBOX[3]))
            ps, tp = read_geotags(path)
        self.assertAlmostEqual(ps[0], gsd[0])
        self.assertAlmostEqual(ps[1], gsd[1])
        self.assertAlmostEqual(tp[3], 100.0)   # west
        self.assertAlmostEqual(tp[4], 30.1)    # north

    def test_scalar_gsd_accepted(self):
        arr = np.zeros((2, 2, 3), dtype=np.uint8)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.tif")
            write_geotiff(arr, path, gsd=0.001, corner_lonlat=(100.0, 30.0))
            ps, _ = read_geotags(path)
        self.assertAlmostEqual(ps[0], 0.001)
        self.assertAlmostEqual(ps[1], 0.001)

    def test_bounds_of_written_tif_match_bbox(self):
        # QA 终检: 由标签反推的范围 == 请求 bbox(交付栅格精确铺满)
        arr = np.zeros((4, 6, 3), dtype=np.uint8)
        gsd = gsd_from_bbox(BBOX, width=6, height=4)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.tif")
            write_geotiff(arr, path, gsd=gsd, corner_lonlat=(BBOX[0], BBOX[3]))
            ps, tp = read_geotags(path)
        self.assertAlmostEqual(tp[3], BBOX[0])
        self.assertAlmostEqual(tp[4], BBOX[3])
        self.assertAlmostEqual(tp[3] + ps[0] * 6, BBOX[2])
        self.assertAlmostEqual(tp[4] - ps[1] * 4, BBOX[1])


class TestDynamicMaxDate(unittest.TestCase):
    def test_default_max_date_is_today(self):
        self.assertEqual(default_max_date(), date.today().strftime("%Y/%m/%d"))


if __name__ == "__main__":
    unittest.main()
