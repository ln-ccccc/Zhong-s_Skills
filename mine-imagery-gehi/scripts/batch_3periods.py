# -*- coding: utf-8 -*-
"""每块多边形按时间窗口取多期历史影像 -> {序号}_{YYYYMM}.tif (江西 50 矿×3 期实战版)

窗口规则: 窗口内 coverage>=0.999 的日期优先、取最晚; 无完整覆盖则取窗口内最晚并标记。
用法: parse_kml_polygons.py 生成 mines.json -> 改 CONFIG -> python batch_3periods.py
"""
import csv
import json
import os
import time

from gehi_utils import availability, buffered_bbox, date_coverage, download, pick_in_windows

HERE = os.path.dirname(os.path.abspath(__file__))
MINES_JSON = os.path.join(HERE, "mines.json")
OUT_DIR = os.path.join(HERE, "imagery_periods")
BUFFER_M = 250.0
WINDOWS = [("2012-2016", 20120101, 20161231),
           ("2017-2020", 20170101, 20201231),
           ("2021-2025", 20210101, 20251231)]

os.makedirs(OUT_DIR, exist_ok=True)
for w, _, _ in WINDOWS:
    os.makedirs(os.path.join(OUT_DIR, w), exist_ok=True)
MINES = json.load(open(MINES_JSON, encoding="utf-8"))

log = open(os.path.join(OUT_DIR, "batch.log"), "a", encoding="utf-8")


def P(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    log.write(msg + "\n")
    log.flush()


def main():
    rows, failed = [], []
    t0 = time.time()
    for k, m in enumerate(MINES, 1):
        stem = m.get("rank", f"{k:03d}")          # 有 rank 用 rank, 否则按顺序
        stem = f"{int(stem):03d}" if str(stem).isdigit() else str(stem)
        bbox = buffered_bbox(m["bbox"], BUFFER_M)
        feats = availability(bbox)
        if not feats:
            P(f"[{k}/{len(MINES)}] {stem} availability 失败,跳过")
            failed.append((stem, "availability"))
            continue
        cov = date_coverage(feats.get("features", []), bbox)
        picks = pick_in_windows(cov, WINDOWS)
        for wname, _, _ in WINDOWS:
            date, comp = picks[wname]
            if not date:
                P(f"[{k}/{len(MINES)}] {stem} {wname}: 窗口内无影像")
                failed.append((stem, wname, "无影像"))
                continue
            outpath = os.path.join(OUT_DIR, wname, f"{stem}_{date.replace('-', '')[:6]}.tif")
            if os.path.exists(outpath) and os.path.getsize(outpath) > 10000:
                rows.append([stem, wname, date, comp, "cached"])
                continue
            ok, err = download(bbox, date, outpath)
            P(f"[{k}/{len(MINES)}] {stem} {wname}: {date} complete={comp} {'OK' if ok else 'FAIL ' + err}")
            rows.append([stem, wname, date, comp, "OK" if ok else "FAIL"])
            if not ok:
                failed.append((stem, wname, err))
            time.sleep(0.5)
    with open(os.path.join(OUT_DIR, "manifest.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "period", "image_date", "complete_coverage", "status"])
        w.writerows(rows)
    P(f"完成。用时 {time.time()-t0:.0f}s, 失败 {len(failed)} 项")
    for x in failed:
        P("  FAIL:", x)


if __name__ == "__main__":
    main()
