# 证据清单与可选校验助手

人类报告包含：基线与当前修改归属、实际测试环境/数据、逐功能状态/保真度、发现与复现、截图查看记录、实际命令/退出码、未测项和风险。没有规定项目必须改用某个报告格式。

需要机器检查时，把 JSON 清单放在证据目录中，所有文件路径相对该目录。`scripts/check-evidence.py` 无网络、无外部依赖、只读输入；Python >=3.9。它检查文件存在与声明矛盾，不读取截图内容、执行测试或修改报告。

一个真实保存、重读并查看页面的记录示例（文件需由实际运行产生）：

```json
{
  "version": 1,
  "all_passed": true,
  "checks": [
    {
      "id": "vector-save",
      "layer": "gui",
      "status": "passed",
      "fidelity": "real",
      "stateful": true,
      "visual": true,
      "evidence": ["save-response.json", "readback.json", "saved-page.png"],
      "readback_evidence": ["readback.json"],
      "visual_review": [{"file": "saved-page.png", "verdict": "passed", "notes": "已打开；版本及类别一致，提交控件未被遮挡。"}]
    }
  ],
  "claims": [{"text": "该合成成果保存并重开一致", "check_ids": ["vector-save"], "requires_real": true}]
}
```

`layer`: unit/api/integration/gui/performance。`status`: passed/failed/blocked/skipped。`fidelity`: real/fixture/simulated，以该项实际验证的边界为准；real 并不表示真实客户数据或生产数据库。fixture 通过仍有价值，但不能支持 `requires_real: true` 的声明。

`evidence` 为执行项的实际文件列表。passed + stateful 要有 readback_evidence；passed + visual 要有打开截图的 visual_review/file/verdict/notes。已知 bug 写 `status: failed`、`failures: [...]` 及复现文件；阻塞/跳过可以无运行文件。未声明 `visual` 不意味着视觉通过。

引用整份自动测试 JSON 支持一项汇总结论时，先实际读取其 fatal/defects/knownBugs/errors、失败断言和跳过项，不只搬运 checks 标签。可声明 `"source_results": [{"file": "run-results.json", "failure_fields": ["fatal", "defects", "errors"]}]`，助手会读取这些显式顶层字段，发现非空失败时拒绝该项 passed。按真实结果格式选择字段，不把有意注入的预期 HTTP 错误当失败；单个已完成阶段可另存它自己的证据，不能引用全程失败的结果支持全程成功。

source_results、visual 和 stateful 都需人工准确标注；漏标不会自动从任意附件推断。助手不审查业务正文、认识保存语义或证明截图判断；不要把清单校验当第二次产品测试。

退出码：0 = 清单一致（可以含诚实记录的失败）；1 = 状态/证据矛盾；2 = 文件或 JSON 读取失败。**0 不是产品通过**。助手不能验证日志真伪、比较像素或证明功能清单完整；人工验收仍需要读证据。

公开交付不要附认证 cookie、私有文件或真实 token；合成数据也标明来源。源码路径和完整 trace 仅按用户指定分享范围交付。
