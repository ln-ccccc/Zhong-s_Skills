# 后端、BFF 与持久化闭环

读取实际入口、消费者、鉴权、状态机与存储所有者，再选测试；不要给项目凭空补 RBAC、审批或任务状态。

## 测试清单

| 场景 | 断言与副作用 |
| --- | --- |
| 成功/无数据 | HTTP、envelope、字段含义、空结果与错误明确区分 |
| 输入错误 | 类型、范围、文件格式、容量/坐标限制；不部分写入 |
| 会话失效/归属错误 | 实际客户端得到契约内错误，不绕过 BFF；拒绝后资源不变 |
| 重复操作/版本冲突 | 不重复发布；409 不覆盖现有版本，重读旧/新版本证实 |
| 依赖失败 | 数据库异常、文件读写失败、上游 5xx/断流/超时，检查服务仍健康、可重试 |
| 取消/重开 | 只验证项目已有取消语义；终态不被旧轮询覆盖 |

临时 SQLite 适合领域回归，但事务锁、隔离级别与并发一致性必须在目标数据库独立验证。只读概览不应加载模型；固定数据测量请求数与耗时，有依据再建议优化。

## 几条容易漏的跨层断言

- **文件登记 → 加工 → 后续消费**：用带 CRS、NoData 的小合成栅格，记录实际 storage key；逐步读取加工产物，核对 CRS、NoData、transform、尺寸、波段和来源。通过一次服务函数不能替代注册 API 到 worker 的传递。
- **任务**：创建 → queued/running → 实际终态 → 输出重读。记录执行的是真实 worker、合成 runner 或模型；不要为了验收启动未授权 GPU/远程成本。
- **数据库 + 文件**：失败注入后同时检查记录和文件。数据库 rollback 不自动撤销文件移动；用临时目录验证补偿/恢复。
- **导出/快照**：生成 → 下载 → 解包/解析 → 对照来源版本 → 导入/重读。配置快照不等于完整数据备份。不要将正常输出擅自清洗成导入器能接受的内容。
- **BFF**：上游错误状态、JSON body、下载头、cookie 是否透传；流在发出 headers 后失败、慢流间隔超过 timeout、客户端取消时上游是否释放。断流测试用独立子进程，检查退出码和后续健康请求，避免杀死 GUI 使用的服务。

认证重读注意 cookie 上下文：Playwright `page.request`/`context.request` 与浏览器共享 cookie，独立 `request.newContext()` 不共享。API 对照不能因未登录误报持久化丢失。[API testing](https://playwright.dev/docs/api-testing)

收集 HTTP response 状态和应用 envelope 错误；HTTP 404/503 属于完成的请求，不会触发 `requestfailed`。[Request](https://playwright.dev/docs/api/class-request)、[Network](https://playwright.dev/docs/network)

故障注入只在测试边界发生，失败后撤掉注入并验证恢复。未知请求不能默认返回成功；fixture 未覆盖的 API 应暴露为未覆盖项。
