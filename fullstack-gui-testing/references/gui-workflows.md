# 连续浏览器与视觉验收

优先使用环境已有浏览器工具；记录工具、浏览器版本和 headed/headless。原工具不可用时，可使用已有独立 Playwright/浏览器；缺少依赖时记录阻塞并继续 API/静态验证，不擅自系统安装。GUI 必须执行用户动作并看到实际结果。

## 选择一条真实任务路径

例如：登录错误 → 成功登录 → 创建项目 → 输入校验 → 保存 → 重读/刷新 → 选择地图 → 点选 → 编辑保存 → 下载 → 退出。按项目功能裁剪，长任务可拆段，但保留会话与数据状态。再走一次关键段检查缓存、重入、重复事件和 loading 计数。

记录项目/结果 ID、当前版本、数据预置方式。真实服务验证与 HTTP fixture 验证分别运行；有意只延迟真实响应时，说明后端仍真实执行，避免误标成纯 mock。

| 操作 | 核对最终状态 |
| --- | --- |
| A→B→C 快速切换/加载中切项目 | 最后意图是 C；标题、列表、数据和保存目标一致；控制释放 |
| 展开→收起→展开/动画未结束再点击 | 终态正确，离场层不吞点击，无多重激活项 |
| 保存中继续编辑/重复保存 | 可编辑则新修改仍保留；禁用则所有会变更内容的入口一致禁用 |
| dirty 时刷新/重新加载/返回 | 按契约确认或保留；不能无提示覆盖/丢弃 |
| 两页面同时编辑 | 冲突提示；原版本及本地未保存内容保留；不自动覆盖 |
| 网络失败→重试→切换→返回 | 提示可见、忙碌状态释放、旧请求不覆盖新上下文 |
| 滚到底/回顶、窄屏、缩放、长名称/空态 | 主动作可达、内容不被固定层盖住、表格/地图滚动范围清楚 |

不要靠 `force:true`、`dispatchEvent()`、直接调用组件函数通过用户操作测试。Playwright 的 actionability 和 auto-wait 减少竞态；优先 role/label 定位和可重试断言。[Auto-waiting](https://playwright.dev/docs/actionability)、[Best practices](https://playwright.dev/docs/best-practices)

短等待可以用于有明确间隔的压力序列或 motion 中间态采样，不能用任意延时替代“已就绪”。长期轮询/地图使 `networkidle` 不一定适合；等可操作控件、对应请求或任务终态，并给有限 timeout。

## 实际看图

截图保存后使用视觉工具打开。至少检查关键内容、失败反馈、忙碌状态、窄屏与重要浮层；按风险选择尺寸，不写固定“几张图即通过”的门槛。

检查文字是否裁切/挤压、对比和图标字形、玻璃透明层是否遮内容、弹窗是否越界、图像比例、地图瓦片及画布是否空白。`toBeVisible()` 单独不足：opacity:0 也可能符合 Playwright 的可见定义。记录 screenshot→URL/步骤/数据/视口→查看结论。

键盘验收覆盖 Tab 顺序、焦点可见、Enter/Escape、弹窗打开/关闭回焦；检查项目已有可访问名称与错误关联。自动 accessibility 检查只能补充，不能替代键盘和视觉操作。

正常 motion 下观察按压、导航、面板及状态过渡，快速反向操作；用 `prefers-reduced-motion: reduce` **实际再操作**，检查行为仍可完成与位移/过渡减少。只看 CSS 属性不能证明按压时优先级或 teleport 浮层都正确。

下载用 `page.waitForEvent('download')` 在点击之前等待，`saveAs()` 在 context 关闭前落盘，解析内容/版本；只出现下载按钮不是通过。[Downloads](https://playwright.dev/docs/downloads)

保存 trace/录像便于回看；trace 含 DOM、请求和源码，认证状态也可含敏感 cookie，交付前检查脱敏，登录过程可在 trace 开始前完成。[Trace viewer](https://playwright.dev/docs/trace-viewer)、[Authentication](https://playwright.dev/docs/auth)

视觉基线要先人工确认，再作为回归参考；环境变化会影响截图，不能盲目更新基线。[Visual comparisons](https://playwright.dev/docs/test-snapshots)
