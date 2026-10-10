# 设计决策：从 Apple 原则到产品

## 来源与转译

[Apple HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials) 区分 Liquid Glass 控制层与标准内容材质。原生系统提供动态适配；网页不能通过一个 `backdrop-filter` 获得同等效果。下面的 Web 建议是工程转译。

## Material：层级，不是统一滤镜

把导航、工具栏和短暂交互视为浮动控制面；表格、长文本、地图和图像承载内容。不要让每个KPI卡片独立折射、发光或再叠一层玻璃。玻璃上的选中底座可使用薄填色，不需要第二次blur。

原生 `regular` 优先保持阅读，适合有文字的控件和面板；`clear` 适合媒体背景上的少量控件，需要根据亮度验证分离。网页示例的“轻透/均衡/实色”是本项目比较预设，不是原生 variant 名称。

边缘高光交代轮廓，阴影交代与内容的距离，半透明保留背景关联。深色不使用大块白色半透明层；选中和主操作使用有限强调色，危险状态另有语义色。不要把暗色简单反转成浅色，也不要全局调低文字opacity来增加“高级感”。重要数据不能只靠颜色区分。

## 触感：跟输入方式一致

[Apple HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion) 说明触摸与触控板反馈强度可以不同。鼠标 hover 提醒可操作，键盘 focus 标明当前目标；press 立即出现局部变化，release/cancel 恢复。大段文本和地图不要跟随鼠标倾斜。

视觉触感与实际 haptics 是两件事。[Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics) 的设备能力、事件意义与可选性适用于支持的平台。普通桌面网页提供视觉/状态反馈即可；[Vibration API](https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API) 是有限支持且依赖硬件的能力，不能用它承诺 Mac Force Touch 触控板反馈。

## Motion：一张组件反馈矩阵

| 操作 | 材质反馈 | 运动关系 | 状态与减少动效 |
|---|---|---|---|
| 按钮 | hover填色、focus轮廓、按下高光 | 小幅压缩，释放恢复 | 操作即时触发；减少动效用填色/文字 |
| 导航 | 当前项有清晰底座 | 选中指示沿同一轨道转移 | 当前路由与内容一致，旧加载不得抢回选择 |
| 详情展开 | 入口与详情保持视觉联系 | 同一位置揭示或沿清晰方向展开，关闭反向 | 快速开关不留遮罩/不可点击状态；减少动效直接显示 |
| 加载 | 局部状态，不把整页洗白 | 可用短淡入、进度或一次轻强调 | `aria-busy`及文字反馈；完成/失败不只靠动画 |
| 成功/失败 | 附近文字、图标、语义色 | 避免大面积庆祝或持续抖动 | 错误可读、能重试；关动效仍完整 |

按用户意图更新状态，再让动画表现它。取消动画不等于取消后端操作，关闭面板也不意味着已提交的修改被撤销。不依赖 `transitionend` 或一个定时器作为唯一提交点。

## Layout：先读内容，后看装饰

[Apple HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout) 强调优先级、对齐、关联分组和渐进披露。用于工作台时：

- 顶栏承担身份与导航，页面标题表达当前任务；不要连续重复平台全称。
- 常用筛选紧凑分组；高级条件按需展开，不堆成整页通栏输入框。
- 仪表盘按“关键指标→核心图像/图表→明细”组织。多期影像使用同一行的配对关系，年份靠近各自图片，图例与数据保持关联。
- 面板内正文自然滚动，操作区和标题不能盖住重要图像；保留实际比例，用 `contain` 展示需要完整判断的影像。
- 若当前项目仅支持PC，仍需检查窗口高度、缩放和文本变长；不要为让布局整齐而隐藏主要操作。

## 数字的归属

Apple原则不等于一套通用CSS常量。可从8px节奏、40px左右PC控件、短反馈约120–180ms、导航约180–260ms、面板约220–320ms开始试验，这些是**可调整的示例启发，不是Apple要求**。原生 pt、Web CSS px、远距大屏尺寸不得直接等同。

Web文本通常按WCAG AA检查4.5:1，符合大字号定义的文字3:1；阈值来自 [WCAG](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)，不是本 skill 发明。透明背景必须先合成再计算，并检查最亮/最暗内容；高光、渐变与复杂图片还需要实际渲染检查。
