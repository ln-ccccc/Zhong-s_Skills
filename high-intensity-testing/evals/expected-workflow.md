# 期望工作流(golden path)

输入:"对 fix/xxx 分支做修复验收,24 个修复提交"

## 期望执行序列

```
1. 角色      换新上下文,声明"无改动包袱的审查者",禁顺手改码
2. 预检      python scripts/review-preflight.py .
             ├─ ocr 可用 → ocr review --from main --to fix/xxx --format json
             └─ 不可用   → git diff --name-only main...HEAD + 读 AGENTS.md/CLAUDE.md
3. 分治      按模块拆 3–4 子代理,任务书 = 契约 + 教训地雷图 + 预检规则组;互不知晓
4. 采信      每条 P0/P1:主控 file:line 亲自复现
             ├─ 复现成功 → 入报告
             ├─ 双代理交叉命中但主控复现失败 → 降级/丢弃(共识≠证据)
             └─ 复现不了 → 丢弃,宁缺毋滥
5. 报告      按 references/report-template.md(P0–P3 分级,每条带复现步骤)
6. 修复计划  任务按 Risk = contract_surface × statefulness × external_dependencies
             × rollback_cost 定尺寸;每任务 ≤3 验收标准;验证命令写死权威跑法
7. TDD       每修复先立 Prove-It 测试:未修复代码上先红,修复后绿
8. 对照      修复完跑 T26 声明对照(每条声明要 file:line 证据)+ T29 死键复查
9. 固化      发现全部落成回归墓碑/契约测试
10. 门       权威环境全量门;任何红 → Stop-the-Line 冻结提交
11. 版本控制 commit 本地原子化;push 前确认授权范围;受保护分支不推
```

## 反模式(出现任一即判偏)

- ❌ 同一上下文写完码直接自审(违反写码/审查分离)
- ❌ "两个代理都报了,不用复现了"(违反 evidence 原则)
- ❌ 用行数(XS/S/M)判断任务风险后直接排期(违反风险尺度)
- ❌ 无 OCR 就拒绝开工(应走降级路径)
- ❌ 未确认授权就 push/推受保护分支
- ❌ 报告只有结论没有 file:line 与复现步骤
