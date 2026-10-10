# 内容与视觉基础

这是跨产品的决策清单；具体字号、颜色与密度按人、任务和平台确定，不绑定某个仪表盘布局。

## 目的、层级与品牌

[Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) 与 [Design foundations](https://developer.apple.com/videos/play/wwdc2025/359/) 提供整体方向。先问：人要完成什么、当前最需要知道什么、下一步是什么、怎样返回或恢复？用顺序、分组和强调回答，而不是先选玻璃半径。

让核心内容获得空间，熟悉的动作沿用熟悉含义。简洁可以需要增加一个清楚的标签或解释。保持产品自身的语气和识别度；品牌色不需要铺满每个背景。

## Typography：阅读与信息节奏

依据 [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)：

- 区分标题、正文、辅助信息与数据，不用大量字体或细字重制造层级。文字大小、粗细和颜色协同，放大后相对层级仍清楚。
- 阅读型内容重视行长、行距与连续阅读；表格重视数字对齐、单位、精度。需要比较的数值可用等宽数字，不让数值变化跳动。
- 让文本自然换行，重要说明不任意截断；截断必须有获取完整内容的办法。用真实长标题、多语言和字体放大测试。
- 原生沿用文字样式与Dynamic Type；Web使用语义标题和可缩放字号，遵循浏览器文本/页面缩放。Apple各平台pt建议不能直接当成所有网页的CSS px标准。
- 优先可用系统字体；采用自定义字体时核实支持的语言、字重、载入失败回退与使用范围，不因为模仿Apple而自动下载官方字体。

## Color与外观

依据 [Color](https://developer.apple.com/design/human-interface-guidelines/color)：色彩先承担语义。定义正文、次要文字、表面、边界、交互强调和状态。品牌色可以复用，但交互与装饰不要仅靠相同颜色区分；结合下划线、形状、位置与标签避免歧义。

为支持的外观分别定义色彩关系，不用全局反转。玻璃下的图片影响合成颜色，状态图例还需文字/形状；默认背景对比通过不能证明任意背景都通过。测试亮环境、暗环境、增加对比与实际显示设备。

产品允许的外观与原生材质的自适应是不同层次：原生Liquid Glass相关自定义色应遵循官方的明暗适配要求；Web不必为局部改动额外新增整套主题设置。

## Icons、图片与视觉重量

依据 [Icons](https://developer.apple.com/design/human-interface-guidelines/icons)：图标表达一个明确概念，采用熟悉比喻，保持笔画、细节、视角与相邻文字重量一致。光学对齐比单纯几何居中更有价值。

普通界面图标与应用图标作用不同，不把应用图标的丰富光影套到所有操作符号。关键/陌生动作配文字，可访问名称说明行为；装饰图形不重复读给读屏。原生可采用系统符号，Web选择可用的SVG/图标库并保持同一语义体系。

图片按内容价值选裁剪：展示作品可裁剪，核查证据/比较图应完整保留必要范围。不要让光学扭曲、彩色遮罩或文字覆盖损伤实际内容。

## Writing、包容性与信任

依据 [Writing](https://developer.apple.com/design/human-interface-guidelines/writing) 与 [Inclusion](https://developer.apple.com/design/human-interface-guidelines/inclusion)：动作标签用清楚动词，术语和语气一致；严重错误直说原因和恢复方法，普通成功保持克制。语言随场景调整，避免专业缩写、只对某文化成立的比喻与默认人人有同样能力。

日期、数字、单位与语言方向按地区呈现，给翻译和长文本留空间。权限、收集和智能推断的结果说明用途及可控范围，不以视觉效果制造虚假确定性。设计可提示这些需求，但不替代权限实现、业务事实或专业合规判断。

## Accessibility：设计输入，而非最后打补丁

[Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) 与 [Principles of inclusive app design](https://developer.apple.com/videos/play/wwdc2025/316/) 涵盖视觉、听觉、运动、语音、认知的不同需求。对应检查：

| 需求 | 设计决策 | 验证 |
|---|---|---|
| 看不清/色觉差异 | 放大、足够对比、颜色以外的状态 | 字体变大、灰度/对比、忙碌背景 |
| 看不到 | 有意义的标题、标签、顺序与状态描述 | 可访问树与实际读屏任务 |
| 听不到 | 声音同时有文字/视觉反馈，媒体有字幕路径 | 静音完成任务 |
| 精细操作困难 | 足够命中区域、键盘/可见替代、不依赖单手势 | 键盘、触摸、拖动替代 |
| 易分心/易眩晕 | 短流程、清楚用语、可暂停/减少运动 | 减少动态效果、错误恢复 |

自动化仅覆盖部分属性。没有实际读屏、触觉硬件或辅助输入测试时，明确标注，不能宣称全部无障碍支持完成。
