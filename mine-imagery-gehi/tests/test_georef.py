# -*- coding: utf-8 -*-
"""地理配准测试: bbox 推导 GSD / 下载范围 QA / GeoTIFF 标签回写 / max_date 动态化"""
import os
import sys
import tempfile
import unittest
import unittest.mock
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


class TestDownloadGeorefGate(unittest.TestCase):
    """下载 georef 门 fail-closed:缺 geotag / 范围偏离都必须失败,不许带病交付"""

    BBOX = (100.0, 30.0, 100.1, 30.1)

    @staticmethod
    def _fake_run(plant):
        """返回 mock 的 gehi_utils.run:把夹具 tif 写到 -o 指定的 tmp 路径"""
        from types import SimpleNamespace
        import tifffile

        def _run(args, timeout=900):
            tmp = args[args.index("-o") + 1]
            plant(tmp)
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        return _run

    def _aligned_z18(self, tmp, shift=0.0):
        # 1000x1000 px, 0.0001°/px, 精确覆盖 bbox;shift=西移/南移扰动(单位:°)
        # 随机内容保证文件体积过 download 的 >10KB 最小检查
        rng = np.random.default_rng(7)
        arr = rng.integers(0, 255, (1000, 1000, 3), dtype=np.uint8)
        write_geotiff(arr, tmp, gsd=(0.0001, 0.0001),
                      corner_lonlat=(self.BBOX[0] + shift, self.BBOX[3] - shift))

    def _plain_z18(self, tmp):
        import tifffile
        rng = np.random.default_rng(7)
        tifffile.imwrite(tmp, rng.integers(0, 255, (1000, 1000, 3), dtype=np.uint8),
                         photometric="rgb")

    def _download(self, plant):
        import gehi_utils
        out = os.path.join(tempfile.mkdtemp(), "out.tif")
        with unittest.mock.patch.object(gehi_utils, "run", side_effect=self._fake_run(plant)):
            return gehi_utils.download(self.BBOX, "2024-06-01", out)

    def test_aligned_source_passes_and_output_written(self):
        ok, err = self._download(lambda tmp: self._aligned_z18(tmp))
        self.assertTrue(ok, err)

    def test_offset_source_fails(self):
        ok, err = self._download(lambda tmp: self._aligned_z18(tmp, shift=0.05))  # 偏 5 px > 容差 4
        self.assertFalse(ok)
        self.assertIn("georef mismatch", err)

    def test_missing_geotags_fail_closed(self):
        ok, err = self._download(self._plain_z18)
        self.assertFalse(ok)
        self.assertIn("missing source georeference", err)


if __name__ == "__main__":
    unittest.main()
