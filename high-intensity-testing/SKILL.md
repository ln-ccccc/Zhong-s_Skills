---
name: high-intensity-testing
description: "超高强度代码审查与测试工作流——并行子代理六步审查、修复声明 vs 实现对照、发现固化成测试,附 15 问触发清单与 35 条失效模式原则(T2–T37)。当任务涉及:全面审查、高强度测试、对抗审计、里程碑前质量门、「按上次审查的方式」、修复批次验收、审查报告、回归测试固化、审查一个分支/一批修复的质量时使用。Ultra-high-intensity review & testing workflow: six-step parallel sub-agent review, claim-to-evidence audit, 35 failure-mode principles."
---

# 超高强度审查与测试(high-intensity-testing)

对一个大分支、一批修复或整个系统做"作者查不出自己 bug"级别的对抗性审查与测试。

**前提纪律:写码与审查分离**——至少换对话,明确"无改动包袱的审查者"角色;同一上下文不允许既写码又自审。

## 模式选择

| 模式 | 适用 | 裁剪 |
|---|---|---|
| 全面模式 | 分支合并前 / 里程碑前 / 修复批验收 | 五阶段全流程(references/review-playbook.md) |
| 快速模式 | 时间盒紧的 hotfix | 至少保留 Prove-It 先红后绿 + 权威门两环,裁剪项写进提交信息 |

## 六步审查工作法(核心)

1. **分治**:按模块拆 3–4 个并行子代理,独立上下文 + 详细任务书,互不知晓彼此结论(避免锚定)。
2. **地雷图注入**:任务书 = 项目契约 + 历史教训清单,把教训转成定向指令("已知模式 X,找同类未修实例")。
3. **契约驱动**:接口字段 / payload / 键名 grep 对照;跨层链路生产者→消费者两侧都走到。
4. **git 考古**:`git log -S` 找功能死亡提交,diff 对照旧语义。
5. **抽查验证**:每条 P0/P1 主控亲自 file:line 复现后才采信。**双代理交叉命中只提升置信度与优先级,不替代复现——两个代理不统计独立(同模型/同仓库/同 diff/同提示模式),相关幻觉可能同时发生。P0/P1 = evidence,不是 consensus。**
6. **固化成契约测试**:发现全部落成测试(键集 / 接线 / 超时 / 状态码回归),下一轮清单变短。

## 证据契约

- 每条发现带 `file:line` + 可执行复现步骤;**P0/P1 必须有 executable reproduction**,存疑不写(宁缺毋滥)。
- 分级定义:P0 Blocker / P1 Major / P2 Moderate / P3 Minor,见 [references/severity.md](references/severity.md)。
- 报告格式见 [references/report-template.md](references/report-template.md)。

## 预检:OCR 可用则委托,不可用则降级

```
ocr CLI 可用?
   ├─ yes → ocr delegate preview / ocr review --from <base> --to <branch>
   └─ no  → git diff --name-only + git status
            + 读 AGENTS.md / CLAUDE.md 等仓库规则文件当规则源
```

直接跑 `scripts/review-preflight.py [repo_dir]` 自动探测,输出 JSON(变更面 + 规则文件 + 模式)。规则组(无论来源)注入子代理任务书使用,不替代六步工作法。

## 停止条件(Stop-the-Line)

- 权威门(解释器钉死、与生产一致的运行环境、车辆形态匹配)任何红 → 冻结一切新提交,先归因再继续。
- 子代理报告无法在代码中复现 → 丢弃该条,不改码。
- 抽查命中率过低(多数 P0/P1 复现失败)→ 整轮报告降级为线索清单,重派任务书再来。

## 规划与提交纪律

- 任务按**风险**定尺寸:`Risk = contract_surface × statefulness × external_dependencies × rollback_cost`;行数只作辅助(3 行动到鉴权逻辑也可能是大任务)。每任务 ≤3 条验收标准 + 验证命令写死权威跑法。
- commit 本地随时可打(原子、conventional commits);**push 仅在获得明确授权时执行;受保护分支未经显式许可永不推**——push 是外部副作用,权限级别高于本地写测试。
- 每个修复附带回归墓碑:先在未修复代码上跑红,修复后变绿。

## 参考文件路由

| 需求 | 读 |
|---|---|
| 15 问触发清单 + T2–T37 失效模式原则 | [references/failure-modes.md](references/failure-modes.md) |
| 五阶段全流程 / 预检降级细节 / 修复纪律 / 十步执行单 | [references/review-playbook.md](references/review-playbook.md) |
| P0–P3 定义 / 共识 vs 证据 / 修复声明对照 | [references/severity.md](references/severity.md) |
| 报告输出格式 | [references/report-template.md](references/report-template.md) |
| 预检脚本(OCR 探测 + 降级) | [scripts/review-preflight.py](scripts/review-preflight.py) |

## 边界(何时不触发)

单文件小改、纯样式调整直接自测;无持久状态纯函数用单元层重复执行替代递进验证;触发与不触发的判定样例见 [evals/](evals/)。
