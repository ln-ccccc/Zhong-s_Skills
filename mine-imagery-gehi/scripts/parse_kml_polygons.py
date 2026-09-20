# -*- coding: utf-8 -*-
"""KML -> mines.json: 提取每块的 FID 与 bbox(供批处理脚本使用)

用法: 改下方 CONFIG, 然后 python parse_kml_polygons.py
用 ElementTree 解析(命名空间无关), 不依赖正则与第三方库:
适配 QGIS/ogr2ogr 导出格式(<SchemaData><SimpleData name="...">),
namespace 前缀(kml:Placemark)、MultiGeometry、CDATA、内环(hole)均天然支持。
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

SRC = "input.kml"          # 输入 KML
DST = "mines.json"         # 输出 JSON
FID_FIELD = "FID_1"        # 命名用的 ID 字段名
EXTRA_FIELDS = ["SHI", "XIAN"]   # 需要带进清单的属地等属性, 不需要就留 []


def _local(tag):
    """去掉 namespace 前缀: '{http://...}Placemark' -> 'Placemark'"""
    return tag.rsplit("}", 1)[-1]


def validate_fids(mines):
    """FID 数据唯一性守卫:空/重复 FID 直接拒绝。
    下游 rows[fid] 与 {fid}_{YYYYMM}.tif 都以 FID 为键,重复会静默覆盖。"""
    ids = [m["fid"] for m in mines]
    if any(not fid for fid in ids):
        raise ValueError(f"empty FID: {ids.count('')} 个 Placemark 缺少 {FID_FIELD} 字段")
    dups = sorted(f for f, c in Counter(ids).items() if c > 1)
    if dups:
        raise ValueError(f"duplicate FID: {dups}")


def parse_kml_text(text, fid_field=FID_FIELD, extra_fields=None):
    """KML 文本 -> (mines, skipped)。skipped 是无几何坐标的 Placemark fid 列表。
    带几何但 FID 为空/重复时抛 ValueError(数据唯一性守卫)。"""
    if extra_fields is None:
        extra_fields = EXTRA_FIELDS
    root = ET.fromstring(text)
    mines, skipped = [], []
    for pm in root.iter():
        if _local(pm.tag) != "Placemark":
            continue
        fields = {}
        for el in pm.iter():
            if _local(el.tag) == "SimpleData" and el.get("name"):
                fields[el.get("name")] = (el.text or "").strip()
        lons, lats = [], []
        for el in pm.iter():
            if _local(el.tag) != "coordinates":
                continue
            for pair in (el.text or "").split():
                parts = pair.split(",")
                if len(parts) >= 2:
                    lons.append(float(parts[0]))
                    lats.append(float(parts[1]))
        fid = fields.get(fid_field, "")
        if not lons:
            skipped.append(fid)
            continue
        mines.append({"fid": fid,
                      "bbox": [min(lons), min(lats), max(lons), max(lats)],
                      **{f.lower(): fields.get(f, "") for f in extra_fields}})
    validate_fids(mines)
    return mines, skipped


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    mines, skipped = parse_kml_text(text)
    with open(DST, "w", encoding="utf-8") as f:
        json.dump(mines, f, ensure_ascii=False, indent=1)
    print(f"parsed {len(mines)} -> {DST}")
    if skipped:
        print(f"warning: {len(skipped)} 个 Placemark 无几何坐标已跳过: {skipped}")


if __name__ == "__main__":
    main()
