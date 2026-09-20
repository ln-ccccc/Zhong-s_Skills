---
name: mine-imagery-gehi
description: 批量获取谷歌地球矿山/任意区域影像(最新一期或多期历史),按 KML 多边形逐块下载 GeoTIFF。当任务涉及:批量下载谷歌卫星影像、查询某区域影像拍摄日期、GEHistoricalImagery、Google Earth 历史影像、GEP/SASPlanet 手工截图的自动化替代、矿山遥感数据集制作时使用。Batch-download Google Earth imagery per KML polygon (timeline date lookup + z18 download + GeoTIFF) with GEHistoricalImagery CLI.
---

# 矿山谷歌影像批量获取(GEHistoricalImagery 管线)

按矢量多边形(矿山图斑)批量获取谷歌地球影像:每块区域先查档案里有哪些拍摄日期,再按选定日期下载为带地理参考的 GeoTIFF。全程命令行,不需要打开 Google Earth Pro 或 SASPlanet 的 GUI。

## 原理:为什么是 GEHistoricalImagery

GEP/SASPlanet 手工流(开 GUI → 定位 → 调时间轴 → 截图/导出)无法批量化,且两者的本地缓存互不相通:

- GEP 7.17 影像缓存在 `AppData\LocalLow\Google\GoogleEarth\Cache\unified_cache_leveldb_leveldb2`,LevelDB 专有格式,外部工具读不了;
- SASPlanet 缓存 `cache_sqlite\sat\` 虽是 SQLite,但实测只有 z3–z7 低倍瓦片;其 ini 里的 `GECache=` 是 GEP 5/6 时代的遗留机制,对 GEP 7.x 无效。

**GEHistoricalImagery**(Mbucari/GEHistoricalImagery,单 exe + 自带精简 gdal 目录)直接走谷歌时间轴协议:

- `availability`:按 bbox 查该区域档案中所有 `image_date` 及覆盖范围(GeoJSON);
- `download --date`:按指定日期下载 bbox 影像,直接输出 EPSG:4326 GeoTIFF。

这就是 GEP 时间轴的网络后端,产出与 GEP 中看到的一致。

## 环境准备

- Windows + Python 3.10+(实测 3.14,无 GDAL/rasterio,用 `tifffile + imagecodecs + pillow + numpy`);
- GEHistoricalImagery 解压到固定目录,记下 `GEHistoricalImagery.exe` 与其 `gdal\` 目录路径;
- 谷歌端点(`kh.google.com` 等)国内多数网络可直连;不通时设置 `HTTPS_PROXY`(如 Clash `127.0.0.1:7890`);
- 该版本已知坑:`--co` 参数静默失败(输出无损压缩参数不生效),**勿用**,压缩由本管线重写时统一处理。

调用前设置环境变量(见 `scripts/gehi_utils.py`):

```
GEHistoricalImagery_Cache = <瓦片缓存目录>
GDAL_DATA = PROJ_LIB = GEOTIFF_CSV = <gehi>\gdal
```

## 标准管线(7 步)

```
KML/矢量 → ①解析多边形(fid+bbox) → ②bbox 外扩缓冲 → ③availability 查日期
        → ④覆盖率栅格化 → ⑤选日期规则 → ⑥z18 下载 + 2×盒滤波降采样
        → ⑦tifffile 写 GeoTIFF + manifest 清单
```

1. **解析**:从 KML 提取每块的 ID(如属性字段 `FID_1`)和经纬度 bbox。ElementTree 命名空间无关解析(`kml:` 前缀 / MultiGeometry / CDATA / 内环均天然支持);带几何但 FID 为空或重复时**直接拒绝**——下游 manifest 与文件名都以 FID 为键,重复会静默覆盖。→ `scripts/parse_kml_polygons.py`
2. **缓冲**:bbox 向四周外扩(矿山图斑惯例 250m),保证图斑边界完整、留判读背景。
3. **查日期**:availability 按 bbox 查询,`--zoom 17`(与交付 GSD 同级),失败重试 3 次、退避 3/8/13s。
4. **覆盖率**:每期日期的 coverage 面片画到 160×160 栅格上算覆盖率(PIL polygon 填充,MultiPolygon 需拆环)。
5. **选日期**:
   - 最新一期场景:`coverage ≥ 0.999` 的日期里取最晚;无完整覆盖则取最晚日期并在清单标记 incomplete;
   - 多期历史场景:每窗口(如 2012–2016 / 2017–2020 / 2021–2025)独立执行同一规则;
   - 天气敏感场景追加:生长季(4–10 月)优先;增强白亮指标 `white + 2*bright < 0.055` 才接受(雪、厚云、雾会误报矿坑裸岩,须拼图目检确认后换期)。
6. **下载**:按选定日期 `-z 18` 下载(原生约 0.6m/px)→ **georef 门(fail-closed)**:源 GeoTIFF 无 geotag 或实际范围偏离请求 bbox 超 4 像素容差,直接判失败(空间无效的影像宁可不要)→ 裁偶数边 → 2×盒滤波降采样——比直接 z17 下载清晰度明显更好(老影像 +32%,新影像视觉无损)。z17 直接下载有谷歌瓦片重采样损耗。
7. **写出**:tifffile 写 RGB GeoTIFF(deflate 无损),手工嵌入 GeoTIFF 标签(免 GDAL):
   - `33550` ModelPixelScale = (xres, yres, 0),其中 **xres=(east-west)/width、yres=(north-south)/height**,由请求 bbox 与实际输出尺寸推导——交付栅格精确铺满请求 bbox,多时相叠加/变化检测无系统性偏移;勿写死单一 GSD 常量(随源尺寸漂移)
   - `33922` ModelTiepoint = (0,0,0, west, north, 0)
   - `34735` GeoKeyDirectory = GTModelTypeGeoKey=2(地理坐标)、GTRasterTypeGeoKey=1、GeographicTypeGeoKey=4326、GeogAngularUnitsGeoKey=9102
   - 同步写 `manifest.csv`:fid / image_date / coverage / status / 属地信息;失败/缺失可 `--retry` 增量补跑(OK 前缀状态跳过)。

## 关键参数(实测定版)

| 参数 | 值 | 说明 |
|---|---|---|
| 交付 GSD | **bbox 推导**:`xres=(east-west)/width, yres=(north-south)/height` | 交付栅格精确铺满请求 bbox;`360/2^25 ≈ 1.0729e-05` deg/px(GEP L18 ≈ z17,赤道 1.19 m/px)仅为名义参考值,非权威输出分辨率 |
| 下载 zoom | 18 | + 2×盒滤波降采样,规避 z17 重采样损耗 |
| availability zoom | 17 | 与交付 GSD 同级;查询上限默认当天(动态,无硬编码年份) |
| 缓冲 | 250m | dlat=250/110574; dlon=250/(111320·cos lat) |
| 完整覆盖阈值 | 0.999 | 栅格近似覆盖率 |
| 命名 | `{FID}_{YYYYMM}.tif` | YYYYMM 取 image_date 前 7 位去连字符,**6 位**,勿用 8 位 |

## 疑难杂症(实战坑)

- **availability 返回空(rc=0、无输出)**:先试不同 zoom(16/17/18)排除参数问题;再以同中心、3km 级大窗探邻域日期;最后直接 `download --date <邻域日期>` 验证内容(std>8 即真实影像)。若 2019→2026 各日期内容逐像素相同,说明该点谷歌档案只有一个版本,按时间轴上出现过的日期命名并在清单标注 `metadata_missing`。
- **"最新一期"不是统一日期**:山区档案更新稀疏,滇西 565 矿实测 2022-11 占 342 幅、2023-10 占 71 幅、2025-10 占 49 幅,其余散布 2014-04 至 2026-02——文件名里的年月必须来自实际 image_date,不能统一 stamp。
- **日期位数**:repick 类脚本曾两次把文件名写成 8 位日期,统一 `date.replace('-','')[:6]`;比较年月时警惕 int/string 混用。
- **并发重跑**:后台重跑前先停旧进程,否则并发写同名文件互相截断。
- **拼图目检**:glob 字典序会把 "100" 排在 "10" 后,联系表必须按数字序排列;清理文件时零填充前缀与数字等值比较("01" ≠ "1")会误删。
- **质量规律**(供验收参考):Laplacian 方差 2021 后质变(中位 ~1000),2024–2025 最好(1400+),2018 前多在 200–600——是年代源分辨率上限,与 GEP 同期一致,非管线问题。

## 脚本

| 文件 | 用途 |
|---|---|
| `scripts/gehi_utils.py` | 环境变量、重试调用、缓冲 bbox、覆盖率、日期挑选、z18 下载降采样、GeoTIFF 写出 |
| `scripts/parse_kml_polygons.py` | KML → JSON(按属性字段取 FID) |
| `scripts/batch_latest.py` | 最新一期批量(565 矿实测 28 min) |
| `scripts/batch_3periods.py` | 三窗口历史分期批量(50 矿×3 期实测 25 min) |

使用:改脚本顶部 CONFIG 区(工具路径、输出目录、KML/JSON 输入),`python batch_latest.py` 即可;中断后 `python batch_latest.py --retry` 只补失败/缺失。回归测试:`python -m unittest discover -s tests -p "test_*.py"`(离线可跑,覆盖 retry 选择/选期规则/KML 解析/地理配准门)。管线已验证两组交付:江西 50 矿×3 期(150 幅)、云南 565 矿最新一期(565 幅,零缺失)。
