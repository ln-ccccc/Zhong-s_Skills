# -*- coding: utf-8 -*-
"""
GEHistoricalImagery 管线公共工具
用法:批处理脚本 import 本模块;先按你的安装路径改下方 CONFIG。
依赖:tifffile、numpy、pillow(无需 GDAL)
"""
import json
import math
import os
import subprocess
import time
from datetime import date

import numpy as np
import tifffile
from PIL import Image, ImageDraw

# ── CONFIG:按本机实际情况修改 ────────────────────────────────────────────
GEHI_DIR = r"C:\tools\GEHistoricalImagery"        # 解压目录(含 gdal 子目录)
EXE = os.path.join(GEHI_DIR, "GEHistoricalImagery.exe")
CACHE_DIR = os.path.join(GEHI_DIR, "cache")       # 瓦片缓存,可放任意大容量盘
# ────────────────────────────────────────────────────────────────────────

AVAIL_ZOOM = 17        # availability 查询 zoom(与交付 GSD 同级)
DOWNLOAD_ZOOM = 18     # 下载 zoom(原生 ~0.6m/px,下载后 2x 盒滤波降采样)
DEFAULT_MIN_DATE = "2012/01/01"


def make_env():
    return {**os.environ,
            "GEHistoricalImagery_Cache": CACHE_DIR,
            "GDAL_DATA":  os.path.join(GEHI_DIR, "gdal"),
            "PROJ_LIB":   os.path.join(GEHI_DIR, "gdal"),
            "GEOTIFF_CSV": os.path.join(GEHI_DIR, "gdal")}


def run(args, timeout=900):
    return subprocess.run([EXE] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=make_env(), timeout=timeout)


def buffered_bbox(bbox, buffer_m):
    """(lon0, lat0, lon1, lat1) 向四周外扩 buffer_m 米"""
    lon0, lat0, lon1, lat1 = bbox
    dlat = buffer_m / 110574.0
    dlon = buffer_m / (111320.0 * max(0.2, math.cos(math.radians((lat0 + lat1) / 2))))
    return (lon0 - dlon, lat0 - dlat, lon1 + dlon, lat1 + dlat)


def default_max_date():
    """availability 默认查询上限=今天,避免硬编码年份随时间老化"""
    return date.today().strftime("%Y/%m/%d")


def availability(bbox, min_date=DEFAULT_MIN_DATE, max_date=None, zoom=AVAIL_ZOOM, retries=3):
    """bbox -> GeoJSON dict(含各期 image_date 与 coverage 面片);失败返回 None"""
    if max_date is None:
        max_date = default_max_date()
    ll = f"{bbox[1]:.6f},{bbox[0]:.6f}"
    ur = f"{bbox[3]:.6f},{bbox[2]:.6f}"
    for attempt in range(retries):
        r = run(["availability", "--zoom", str(zoom), "--min-date", min_date,
                 "--max-date", max_date, "--lower-left", ll, "--upper-right", ur,
                 "-o", "-", "-q"], timeout=300)
        if r.returncode == 0 and r.stdout.strip().startswith("{"):
            return json.loads(r.stdout)
        time.sleep(3 + attempt * 5)
    return None


def date_coverage(features, bbox, grid=160):
    """每期 image_date 在 bbox 内的覆盖率(栅格近似, 160x160 足够)"""
    by_date = {}
    for f in features:
        d = f["properties"].get("image_date", "")
        by_date.setdefault(d, []).append(f["geometry"]["coordinates"])
    lon0, lat0, lon1, lat1 = bbox

    def to_px(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * grid, (lat1 - lat) / (lat1 - lat0) * grid)

    out = {}
    for d, geoms in by_date.items():
        img = Image.new("1", (grid, grid), 0)
        dr = ImageDraw.Draw(img)
        for mp in geoms:                       # MultiPolygon: list of polygons
            polys = mp if isinstance(mp[0][0][0], list) else [mp]
            for poly in polys:
                dr.polygon([to_px(x, y) for x, y in poly[0]], fill=1)
        out[d] = sum(img.getdata()) / (grid * grid)
    return out


def pick_latest(cov, complete_th=0.999):
    """最新一期: complete 优先取最晚; 无 complete 取最新并返回 complete=False"""
    if not cov:
        return None, None
    complete = {d: c for d, c in cov.items() if c >= complete_th}
    pool, flag = (complete, True) if complete else (cov, False)
    return sorted(pool.keys())[-1], flag


def pick_in_windows(cov, windows, complete_th=0.999):
    """多期历史: windows=[(名称, 起yyyymmdd, 止yyyymmdd), ...] -> {名称: (date, complete)}"""
    res = {}
    for wname, y0, y1 in windows:
        cand = {d: c for d, c in cov.items() if d and y0 <= int(d.replace("-", "")[:8]) <= y1}
        if not cand:
            res[wname] = (None, None)
            continue
        complete = {d: c for d, c in cand.items() if c >= complete_th}
        pool, flag = (complete, True) if complete else (cand, False)
        res[wname] = (sorted(pool.keys())[-1], flag)
    return res


def read_geotags(path):
    """读取 GeoTIFF 的 ModelPixelScale/ModelTiepoint。
    返回 (pixel_scale=(sx,sy), tiepoint=(i,j,k,x,y,z));标签缺失或读不了返回 None。"""
    try:
        with tifffile.TiffFile(path) as t:
            page = t.pages[0]
            ps, tp = page.tags.get(33550), page.tags.get(33922)   # ModelPixelScale/ModelTiepoint
            if ps is None or tp is None:
                return None
            return (tuple(float(v) for v in ps.value[:2]),
                    tuple(float(v) for v in tp.value))
    except Exception:
        return None


def gsd_from_bbox(bbox, width, height):
    """交付栅格精确铺满请求 bbox 的 PixelScale (deg/px)。
    从实际范围推导而非硬编码,避免『下载栅格实际尺寸 × 写死分辨率 ≠ 请求 bbox』的系统性偏移。"""
    return ((bbox[2] - bbox[0]) / width, (bbox[3] - bbox[1]) / height)


def z18_bounds_ok(bbox, width, height, pixel_scale, tiepoint, tol_px=4.0):
    """QA:下载栅格实际范围与请求 bbox 的偏差 ≤ tol_px 个 z18 像素。
    tiepoint=(i,j,k,x,y,z) 的 (x,y) 是栅格 NW 角地理坐标。"""
    sx, sy = pixel_scale
    west, north = tiepoint[3], tiepoint[4]
    east, south = west + sx * width, north - sy * height
    tx, ty = tol_px * sx, tol_px * sy
    return (abs(west - bbox[0]) <= tx and abs(east - bbox[2]) <= tx and
            abs(north - bbox[3]) <= ty and abs(south - bbox[1]) <= ty)


def write_geotiff(arr, path, gsd, corner_lonlat):
    """RGB uint8 数组 -> EPSG:4326 GeoTIFF(deflate), 手工嵌 GeoTIFF 标签, 免 GDAL。
    gsd 可传标量或 (xres, yres);corner_lonlat=(west_lon, north_lat) 为栅格 NW 角。"""
    if corner_lonlat is None:
        raise ValueError("corner_lonlat=(west_lon, north_lat) 必须提供")
    if not isinstance(gsd, (tuple, list)):
        gsd = (gsd, gsd)
    geokey = np.array([1, 1, 0, 4,
                       1024, 0, 1, 2,      # GTModelTypeGeoKey = ModelTypeGeographic
                       1025, 0, 1, 1,      # GTRasterTypeGeoKey = RasterPixelIsArea
                       2048, 0, 1, 4326,   # GeographicTypeGeoKey = WGS84
                       2054, 0, 1, 9102],  # GeogAngularUnitsGeoKey = degree
                      dtype=np.uint16)
    tifffile.imwrite(path, arr, photometric="rgb", compression="deflate",
                     extratags=[(33550, 12, 3, (gsd[0], gsd[1], 0.0), False),                # ModelPixelScale
                                (33922, 12, 6, (0.0, 0.0, 0.0,
                                                corner_lonlat[0], corner_lonlat[1], 0.0), False),  # ModelTiepoint
                                (34735, 3, 20, tuple(geokey), False)])                 # GeoKeyDirectory


def download(bbox, date, outpath, retries=3):
    """按日期下载 bbox 影像: z18 拉取 -> georef QA -> 2x 盒滤波降采样 -> GeoTIFF。
    PixelScale 从请求 bbox 与实际栅格尺寸推导(交付栅格精确铺满 bbox)。
    date 格式 'YYYY-MM-DD' 或 'YYYY/MM/DD'。返回 (ok, err_msg)。"""
    ll = f"{bbox[1]:.6f},{bbox[0]:.6f}"
    ur = f"{bbox[3]:.6f},{bbox[2]:.6f}"
    tmp = outpath + ".z18tmp.tif"
    try:
        for attempt in range(retries):
            r = run(["download", "--date", date.replace("-", "/"), "-z", str(DOWNLOAD_ZOOM),
                     "--lower-left", ll, "--upper-right", ur, "-o", tmp, "-p", "8", "-q"])
            if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 10000:
                a = tifffile.imread(tmp).astype(np.float32)
                H0, W0 = a.shape[:2]
                geo = read_geotags(tmp)
                if geo is not None and not z18_bounds_ok(bbox, W0, H0, *geo):
                    return False, "georef mismatch: 下载栅格范围偏离请求 bbox"
                H, W = H0 - H0 % 2, W0 - W0 % 2
                if H < 2 or W < 2:
                    return False, f"bad size {W}x{H}"
                a2 = a[:H, :W].reshape(H // 2, 2, W // 2, 2, 3).mean(axis=(1, 3)).round().astype(np.uint8)
                write_geotiff(a2, outpath, gsd=gsd_from_bbox(bbox, W // 2, H // 2),
                              corner_lonlat=(bbox[0], bbox[3]))
                return True, ""
            time.sleep(3 + attempt * 5)
        return False, (r.stderr.strip()[-200:] if r.stderr else "download failed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
