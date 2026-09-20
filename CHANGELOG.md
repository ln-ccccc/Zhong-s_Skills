# Changelog

本仓库遵循 [Keep a Changelog](https://keepachangelog.com/) 风格;skill 的行为变化(触发条件、流程、产出物)在此可追踪。

## [Unreleased]

### high-intensity-testing

- **修复 preflight 区间降级(P1)**:`--from/--to` 此前只被 OCR 路径消费,fallback 只查工作区——干净工作区时已提交的分支变更完全漏掉。现在 fallback 按 OCR 同语义取 `merge-base(from,to)..to` 的 range diff(附回归墓碑测试 `test_range_diff_without_ocr_finds_committed_change`)。
- **range 模式统一走委托(P1)**:`ocr delegate preview --from/--to`,不再调 `ocr review`(后者跑 OCR 自带 LLM 管线,违背"OCR 选文件/规则、宿主 agent 做评审"的分工)。
- **工作区文件面补齐 untracked(P1)**:fallback 现为 `git diff HEAD ∪ git diff --cached ∪ git ls-files --others --exclude-standard`,与 OCR workspace review 语义对齐。
- **preflight notes 合并**:降级时保留 OCR 失败原因,不再被 fallback 的 notes 覆盖(测试抓出)。
- **跨运行时泛化**:六步法第 1 步"分治"的本质改为**独立审查遍(pass)**——支持子代理则并行,不支持则顺序多遍(契约→数据流→git 考古→对抗),遍间重置上下文。
- 新增 `evals/cases.jsonl`(可执行触发判定样例 12 条)与 `tests/`(preflight 回归 9 项);新增 CI(`.github/workflows/ci.yml`:双套件单测 + py_compile + evals 格式 + preflight 冒烟 + skills-ref 校验 best-effort)。

### mine-imagery-gehi

- **SKILL.md 与实现对齐(P2)**:GSD 描述改为 bbox 推导(`xres=(east-west)/width, yres=(north-south)/height`),原 `1.0729e-05` 常量降级为名义参考值;补 georef 门(fail-closed)与 KML 守卫描述——修复文档漂移(CHANGELOG/代码/测试已更新而 SKILL.md 未同步,违反自身 T26 原则)。
- **GeoTIFF QA 改 fail-closed(P2)**:源无 geotag 时不再放行,判 `missing source georeference` 失败——"图像能看 ≠ 空间有效",多时相变化检测不容未验证配准。
- **KML FID 唯一性守卫(P2)**:带几何但 FID 为空/重复直接抛错(下游以 FID 为 manifest 键与文件名,重复会静默覆盖);附 `test_empty_fid_rejected` / `test_duplicate_fid_rejected`。
- 测试增至 31 项(新增下载 georef 门三态:对齐通过/偏离失败/缺 geotag 失败)。

## [2026-09-20]

### high-intensity-testing

- 首次发布:五阶段审查测试工作流 + 六步并行子代理审查法。
- **重构**:主 SKILL.md 压缩为路由层(触发/模式/六步/证据契约/停止条件),细节拆分到 `references/`(failure-modes / review-playbook / severity / report-template),新增 `scripts/review-preflight.py` 与 `evals/`。
- **P0 证据原则修正**:删除"双代理交叉命中可免复验"——共识只提升置信度与优先级,P0/P1 仍必须可执行复现(两个代理不统计独立,相关幻觉可能同时发生)。
- **工具层去硬依赖**:OCR(open-code-review)可用则委托,不可用自动降级 git diff + 仓库规则文件。
- **push 权限分级**:commit 本地随时可打;push 仅在授权时执行;受保护分支未经显式许可永不推。
- **任务尺度改为风险模型**:`Risk = contract_surface × statefulness × external_dependencies × rollback_cost`,行数降为辅助指标。
- 失效模式原则 T2–T37(35 条):策略/用例/工程/环境与边界四层,原则层表述;15 问触发清单。

### mine-imagery-gehi

- **修复 `--retry` 反转 bug**:原实现对 OK/OK_incomplete 重做、对 FAIL_*/缺失跳过,与声明完全相反;修正为跳过 OK 前缀、重做失败与缺失(`select_todo`,附回归测试)。
- **KML 解析改用 ElementTree**(命名空间无关):替换正则方案,正确处理 `kml:` 前缀、MultiGeometry、CDATA、内环;空几何 Placemark 跳过并告警。
- **GeoTIFF 配准修正**:PixelScale 从请求 bbox 与实际栅格尺寸推导(交付栅格精确铺满 bbox),替换硬编码 GSD;新增下载范围 QA(实际范围偏离请求 bbox 超容差即判失败),消除多时相叠加/变化检测的系统性偏移风险。
- **max_date 动态化**:availability 默认查询上限改为当天,去除会老化的硬编码年份。
- 新增最小测试套件 `tests/`(26 项:retry 选择/选期决策/KML 解析/地理配准),离线可跑。

### 仓库

- 新增 MIT LICENSE、本 CHANGELOG;README 增补目录结构与收录标准。
