# -*- coding: utf-8 -*-
"""KML -> mines.json: 提取每块的 FID 与 bbox(供批处理脚本使用)

用法: 改下方 SRC/DST 与 FID_FIELD, 然后 python parse_kml_polygons.py
适配 KML 属性表格式(<SchemaData><SimpleData name="...">), 即 QGIS/ogr2ogr 导出的常见格式。
"""
import json
import os
import re

SRC = "input.kml"          # 输入 KML
DST = "mines.json"         # 输出 JSON
FID_FIELD = "FID_1"        # 命名用的 ID 字段名
EXTRA_FIELDS = ["SHI", "XIAN"]   # 需要带进清单的属地等属性, 不需要就留 []

s = open(SRC, encoding="utf-8").read()
pms = re.findall(r"<Placemark>(.*?)</Placemark>", s, re.S)
mines = []
for p in pms:
    def field(name):
        m = re.search(rf'<SimpleData name="{name}">(.*?)</SimpleData>', p)
        return m.group(1).strip() if m else ""
    lons, lats = [], []
    for c in re.findall(r"<coordinates>(.*?)</coordinates>", p, re.S):
        for pair in c.split():
            lon, lat = pair.split(",")[:2]
            lons.append(float(lon))
            lats.append(float(lat))
    mines.append({"fid": field(FID_FIELD),
                  "bbox": [min(lons), min(lats), max(lons), max(lats)],
                  **{f.lower(): field(f) for f in EXTRA_FIELDS}})

with open(DST, "w", encoding="utf-8") as f:
    json.dump(mines, f, ensure_ascii=False, indent=1)
print(f"parsed {len(mines)} -> {DST}")
