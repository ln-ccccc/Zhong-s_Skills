# Zhong-s_Skills

我的 agent 技能库:把实战验证过的工作流整理成可复用的 skill(方法文档 + 通用化脚本)。

## 技能列表

| 技能 | 说明 |
|---|---|
| [mine-imagery-gehi](mine-imagery-gehi/SKILL.md) | 按 KML 多边形批量获取谷歌地球影像(最新一期/多期历史),GEHistoricalImagery 时间轴查询 + z18 下载 + EPSG:4326 GeoTIFF,免 GUI、免 GDAL |
| [high-intensity-testing](high-intensity-testing/SKILL.md) | 超高强度审查与测试工作流:OCR 委托审查起手 + 并行子代理六步工作法 + 修复声明对照 + 发现固化成测试,附 15 问触发清单与 35 条失效模式技巧(T2–T37,覆盖策略/用例/工程/容器镜像/跨 shell 五层) |

## 使用方式

每个技能一个目录,`SKILL.md` 是方法与坑位总结,`scripts/` 是可直接改配置运行的脚本。人类读者按 README 顺序看即可;agent 加载时把技能目录注册为 skill 或直接将 SKILL.md 作为参考文档注入上下文。

## 实战记录

- 江西 50 矿 × 3 期历史影像(150 幅)——分期窗口 + 完整覆盖选期 + 天气/清晰度 QC
- 云南 565 矿最新一期影像(565 幅,28 分钟,零缺失)——`{FID}_{YYYYMM}.tif` 命名交付
- high-intensity-testing 的实战底座:三轮全面审查(2026-09-14/16/19)60+ 发现全数闭环,技巧库 T2–T37 全部来自实测踩坑
