# -*- coding: utf-8 -*-
"""每块多边形取最新一期谷歌影像 -> {FID}_{YYYYMM}.tif (云南 565 矿实战版)

用法:
  1. parse_kml_polygons.py 生成 mines.json
  2. 改下方 CONFIG
  3. python batch_latest.py           # 全量
     python batch_latest.py --retry   # 只补失败/缺失, manifest 断点续跑
"""
import csv
import json
import os
import sys
import time

from gehi_utils import availability, buffered_bbox, date_coverage, download, pick_latest

HERE = os.path.dirname(os.path.abspath(__file__))
MINES_JSON = os.path.join(HERE, "mines.json")
OUT_DIR = os.path.join(HERE, "imagery_latest")
BUFFER_M = 250.0
FID_FIELDS = ("fid", "shi", "xian")   # 与 mines.json 里的键对应


def select_todo(mines, rows, only_missing):
    """--retry 时只保留『失败/缺失』: status 以 OK 开头(OK/OK_incomplete)视为已成功跳过,
    FAIL_* 与 manifest 里没有的(缺失)重做。全量时返回全部。"""
    if not only_missing:
        return list(mines)
    return [m for m in mines
            if not rows.get(str(m["fid"]), {}).get("status", "").startswith("OK")]


def main(only_missing=False):
    os.chdir(HERE)
    os.makedirs(OUT_DIR, exist_ok=True)
    mines = json.load(open(MINES_JSON, encoding="utf-8"))
    manifest = os.path.join(OUT_DIR, "manifest.csv")
    cols = ["fid", "image_date", "coverage", "status", *FID_FIELDS[1:]]
    rows = {}
    if only_missing and os.path.exists(manifest):
        with open(manifest, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                rows[row["fid"]] = row

    todo = select_todo(mines, rows, only_missing)
    log = open(os.path.join(OUT_DIR, "batch.log"), "a", encoding="utf-8")

    def P(*a):
        msg = " ".join(str(x) for x in a)
        print(msg, flush=True)
        log.write(msg + "\n")
        log.flush()

    def save():
        with open(manifest, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, cols)
            w.writeheader()
            w.writerows(sorted(rows.values(), key=lambda r: int(r["fid"])))

    P(f"=== start {time.strftime('%F %T')} todo={len(todo)}/{len(mines)} ===")
    t0 = time.time()
    nerr = 0
    for k, m in enumerate(todo, 1):
        fid = str(m["fid"])
        bbox = buffered_bbox(m["bbox"], BUFFER_M)
        try:
            feats = availability(bbox)
            if not feats:
                P(f"[{k}/{len(todo)}] fid{fid} availability 失败")
                rows[fid] = dict(fid=fid, image_date="", coverage="", status="FAIL_availability",
                                 **{f: m.get(f, "") for f in FID_FIELDS[1:]})
                nerr += 1
                continue
            cov = date_coverage(feats.get("features", []), bbox)
            date, comp = pick_latest(cov)
            if not date:
                P(f"[{k}/{len(todo)}] fid{fid} 无任何影像")
                rows[fid] = dict(fid=fid, image_date="", coverage="", status="FAIL_no_imagery",
                                 **{f: m.get(f, "") for f in FID_FIELDS[1:]})
                nerr += 1
                continue
            ok, err = download(bbox, date, os.path.join(OUT_DIR, f"{fid}_{date.replace('-', '')[:6]}.tif"))
            status = ("OK" if comp else "OK_incomplete") if ok else "FAIL_download"
            P(f"[{k}/{len(todo)}] fid{fid} {date} cov={cov.get(date, 0):.3f} {'OK' if ok else 'FAIL ' + err}")
            rows[fid] = dict(fid=fid, image_date=date, coverage=f"{cov.get(date, 0):.3f}", status=status,
                             **{f: m.get(f, "") for f in FID_FIELDS[1:]})
            nerr += 0 if ok else 1
        except Exception as e:
            P(f"[{k}/{len(todo)}] fid{fid} EXC {e}")
            rows[fid] = dict(fid=fid, image_date="", coverage="", status="FAIL_exc",
                             **{f: m.get(f, "") for f in FID_FIELDS[1:]})
            nerr += 1
        time.sleep(0.4)
        if k % 20 == 0:
            save()
    save()
    P(f"=== done {time.strftime('%F %T')} 用时 {time.time()-t0:.0f}s 错误 {nerr} ===")


if __name__ == "__main__":
    main(only_missing="--retry" in sys.argv)
