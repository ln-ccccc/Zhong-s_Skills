---
name: apple-interface-design
description: Use when designing or reviewing Apple-inspired interfaces or applying Apple HIG principles across products, including information architecture, typography, color, icons, navigation, input, feedback, accessibility, adaptive layouts, motion, and Liquid Glass.
---

# Apple 界面设计：从通用思想到交互细节

从人的目标出发，组织内容、行为和反馈，再选择视觉表达。适用于不同领域的 Web、移动与桌面原生界面；保留产品品牌。Apple 当前的 [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) 以 Purpose、Agency、Responsibility、Familiarity、Flexibility、Simplicity、Craft、Delight 指导取舍；它们没有唯一组合公式。

**Material 与 Motion 配套，Layout 服务信息层级；可读、可控和可恢复贯穿全程。** Liquid Glass 是其中一种表达，Web 材质是转译而非原生光学效果。

## 先确定边界

识别平台、主要任务、输入方式、窗口尺寸及显示环境。沿用用户选择与现有组件，不因本 skill 强制主题、移动端、框架更换或全站重构。已有授权内继续；skill 不授权部署、推送或操作设备。

## 核心决策

| 维度 | 应用原则 |
|---|---|
| 目标与信息架构 | 明确核心任务，突出最重要内容与下一步。减少摩擦，保留必要解释；不要把简洁理解成删除标签或隐藏操作。 |
| Typography | 用语义文字层级、字号/字重/行距表达重要性；支持文本放大与本地化，不固定全站同一字号。 |
| Color与Icons | 色彩表达一致含义，主题分别设计。图标统一视觉重量与语义，陌生或关键动作配文字；状态不只靠颜色。 |
| 导航与搜索 | 区分到哪里与做什么；保留位置和返回上下文，导航选型随内容层级与可用空间变化，搜索注明范围。 |
| 输入与反馈 | 少填、好填、能纠错；标签常驻，错误说明位置与修正方式，失败保留输入。按钮、加载、成功、失败、空态和离线有明确反馈。 |
| 控制权与模态 | 只在需要专注或决策时打断；普通详情保持非模态。可撤销操作给恢复路径，破坏性操作说明后果，权限请求贴近用途。 |
| Material | 玻璃主要在导航、工具栏等控制层；表格、图表和正文保持内容层。避免玻璃叠玻璃，不模糊真实影像来制造氛围。大面板增加可读性，小控件可更轻。 |
| 触感 | 静止克制，hover 提示可操作，focus 清晰，按下立即反馈，释放恢复，disabled 明确。PC 使用轻微压缩和明暗反馈；实际硬件触觉取决于平台API，不声称CSS能驱动触控板。 |
| Motion | 动作解释来源、去向和状态。覆盖按钮、导航、面板展开/收起、加载/成功/失败。保持对象连续性，允许打断；业务状态不依赖动画结束。 |
| Layout | 按重要性排列，靠对齐与留白分组；标题不重复，筛选不过度铺满横条。渐进披露次要参数，图像不拉伸，重要内容不被固定控件遮挡。 |
| 可读性 | 明暗主题分别调材质；暗色避免大面积白幕。文本对比和状态标签优先，减少动态效果时保留操作反馈；减少透明度/高对比/不支持blur时可退为实色。 |
| 可访问性与适配 | 视觉、听觉、运动、认知差异从设计开始考虑。键盘、读屏与触摸均有语义路径；适配输入方式、窗口、文本和语言方向，保持核心任务连续。 |

原生优先系统组件；Web采用语义HTML与可验证降级。区分官方原则、WCAG门槛和经验参数，不编造统一时长/字号/blur，不把某行业页面结构变成通用模板。

按任务读取：[视觉与内容基础](references/foundations.md)、[交互与平台决策](references/interaction-and-platforms.md)、[材质/动效/布局](references/principles.md)、[精选案例取舍](references/case-studies.md)、[来源](references/sources.md)。

## 落地与验收

按本次涉及的组件、已支持主题和目标平台执行；局部按钮调整不要求新增导航、主题、token体系或设置。以下连续切换与材质比较用于涉及这些功能的任务，不是所有小改动的固定门槛。

1. 先看现有页面、内容和调用链，写出核心任务、信息层级、导航/行为关系与关键状态。对 Web 实现读 [web-patterns.md](references/web-patterns.md)。
2. 优先复用现有语义 token 管材质、文字、间距与动作，保留现有业务数据和路由。优先调整实际拥挤或遮挡处。
3. **真实操作关键任务**：阅读/搜索/输入/保存/撤销等按范围验证。涉及导航和异步时，连续快切≥20次、加载中切换、重复刷新、反复展开关闭，最后一次意图与内容一致；按钮缩放不等于操作成功。
4. 按目标平台检查支持的外观、背景、窗口、输入与文字放大：Web含200%缩放，原生含Dynamic Type或对应辅助功能设置。检查减少动态效果、减少透明度及实色降级。模态检查困焦/回焦；普通详情面板不困焦。验收细节见 [validation.md](references/validation.md)。
5. 同机比较候选材质：先淘汰功能、可读性和可达性失败，再选层级与开销合适的方案。截图检查渲染，连续操作检查动效；记录卡顿测量方法和未测平台，不凭截图承诺性能。

## 可运行资源

- [演示](assets/demo/index.html)：虚构PC仪表盘是验证材质/动作的一个案例，不限定skill的行业或平台；原生机制请勿照抄CSS。双主题与三种 Web 材质预设供对比，选型结论见 [评估记录](evals/results.md)。
- [阅读收藏示例](assets/reader/index.html)：另一种品牌与内容节奏，验证搜索、阅读返回、移除/撤销、表单纠错和模态；桌面与窄视口采用不同布局。
- 进入实际安装的skill目录，`npm ci` 后运行 `npm run test:browser` 与 `npm run test:reader`；浏览器与 headed 选项见 [validation.md](references/validation.md)。不自动安装、发布或更改真实项目。
- [触发与压力样例](evals/cases.jsonl)、[行为评分](evals/rubric.md)：用于独立评估，不把措辞匹配当效果验证。
