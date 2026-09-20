# Zhong-s_Skills

我的 agent 技能库:把实战验证过的工作流整理成可复用的 skill(方法文档 + 通用化脚本 + 测试)。

**收录标准**:只收"自己真实踩坑 → 总结成稳定决策规则 → 能验证/能执行"的东西——不做"几百份 system prompt"式仓库。

## 技能列表

| 技能 | 说明 |
|---|---|
| [mine-imagery-gehi](mine-imagery-gehi/SKILL.md) | 按 KML 多边形批量获取谷歌地球影像(最新一期/多期历史),GEHistoricalImagery 时间轴查询 + z18 下载 + EPSG:4326 GeoTIFF,免 GUI、免 GDAL |
| [high-intensity-testing](high-intensity-testing/SKILL.md) | 超高强度审查与测试工作流:并行子代理六步审查 + 修复声明对照 + 发现固化成测试,附 15 问触发清单与 35 条失效模式原则(T2–T37) |

## 目录约定

每个技能一个目录:

```
<skill>/
├── SKILL.md          # 触发条件 + 核心流程 + 路由(主文件保持精简,细节下沉)
├── references/       # 深参考:失效模式、全流程手册、严重度定义、报告模板
├── scripts/          # 可直接运行的辅助脚本(标注依赖与只读性)
├── evals/            # 触发判定样例:should-trigger / should-not-trigger / expected-workflow
└── tests/            # 脚本的回归测试(离线可跑)
```

人类读者按 README 顺序看;agent 加载时把技能目录注册为 skill,或按 SKILL.md 的路由表按需读 references。

## 工程约定

- License:MIT(见 [LICENSE](LICENSE));行为变化见 [CHANGELOG](CHANGELOG.md)。
- skill 内的流程性规则只写原则层;项目级实证与具体命令留在各项目的 playbook。
- 证据原则:P0/P1 = evidence 不是 consensus——共识提升置信度,可执行复现不可豁免。
- 工具依赖全部带降级路径(如 OCR 不可用 → git/规则文件),不做硬依赖。
- push 是外部副作用:commit 本地随时可打,push 需授权,受保护分支不推。

## 实战记录

- 江西 50 矿 × 3 期历史影像(150 幅)——分期窗口 + 完整覆盖选期 + 天气/清晰度 QC
- 云南 565 矿最新一期影像(565 幅,28 分钟,零缺失)——`{FID}_{YYYYMM}.tif` 命名交付
- high-intensity-testing 的实战底座:三轮全面审查(2026-09-14/16/19)60+ 发现全数闭环,技巧库 T2–T37 全部来自实测踩坑
