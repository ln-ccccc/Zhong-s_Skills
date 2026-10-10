# 官方来源与Web对应能力

核对日期：2026-10-10。仅凝练决策原则，不复制官方设计资源、字体、图标或视频。

| 来源 | 核对内容 |
|---|---|
| [HIG Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) / [WWDC26 Principles of great design](https://developer.apple.com/videos/play/wwdc2026/250/) | Purpose/Agency/Responsibility/Familiarity/Flexibility/Simplicity/Craft/Delight，原则作为取舍工具 |
| [WWDC25 Design foundations](https://developer.apple.com/videos/play/wwdc2025/359/) | 功能与层级、字体、图像、色彩的整体关系 |
| [HIG Typography](https://developer.apple.com/design/human-interface-guidelines/typography) | 可读、文字层级、字重、文字放大、各平台pt差异 |
| [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color) | 语义一致、明暗及增加对比、显示环境与透明材质 |
| [HIG Icons](https://developer.apple.com/design/human-interface-guidelines/icons) | 图标单一概念、熟悉比喻、重量一致与光学对齐 |
| [HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) / [Inclusive app design](https://developer.apple.com/videos/play/wwdc2025/316/) | 多能力、多通道、适配与辅助功能验证 |
| [HIG Writing](https://developer.apple.com/design/human-interface-guidelines/writing) / [Inclusion](https://developer.apple.com/design/human-interface-guidelines/inclusion) | 行为标签、语气、包容性与本地化 |
| [HIG Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars) / [Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars) / [Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields) | 目的地与操作区别、导航状态、层级、空间和搜索范围 |
| [HIG Entering data](https://developer.apple.com/design/human-interface-guidelines/entering-data) / [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons) | 输入成本、错误反馈、操作语义、命中与pressed状态 |
| [HIG Modality](https://developer.apple.com/design/human-interface-guidelines/modality) | 临时专注任务、退出与上下文、适度打断 |
| [HIG Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy) / [Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left) | 用途明确的权限与数据请求、语言方向适配 |
| [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials) | Liquid Glass控制层、标准内容材质、regular/clear选择、可读性 |
| [HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion) | 有目的、短而精确、可中断、输入方式与可选动态效果 |
| [HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout) / [中文入口](https://developer.apple.com/cn/design/human-interface-guidelines/layout) | 层级、对齐、分组、渐进披露、窗口和文字尺寸变化 |
| [WWDC25 Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/) | 光学提示与运动整体设计、交互响应、材质适配；重点1:29/6:00/10:31章节 |
| [WWDC25 Get to know the new design system](https://developer.apple.com/videos/play/wwdc2025/356/) | 新设计系统与导航/内容关系；原生应用参考 |
| [HIG Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics) | 设备依赖、反馈意义、一致性、可选性 |
| [HIG Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback) | 状态反馈贴近任务，视觉以外替代方式 |
| [WCAG 2.2 Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | 常规文本4.5:1、大字号3:1及例外范围 |
| [MDN backdrop-filter](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter) | 浏览器能力、透明底色及降级 |
| [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) | 系统动态效果偏好的检测 |
| [MDN prefers-reduced-transparency](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-transparency) | 媒体查询与支持差异 |
| [MDN Vibration API](https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API) | 有限支持、依赖振动硬件，不能替代原生触控板API |

部分HIG页面需要JavaScript，纯文本抓取的“requires JavaScript”不是正文。本次通过真实浏览器读取Materials/Motion/Layout；[页面核对记录](../evals/source-check.json)保存URL、标题、方法与正文长度，不是逐项归属的证明，具体原则仍以原页面为准。以后来源不可读时不能声称已核对。官方页面持续更新，引用时重新核对；网页中自定义blur、间距、曲线与时长不属于Apple官方固定规范。
