# 精选案例：学决策，不照搬外观

案例来源与可迁移结论分开。下面的“取舍”是本skill的分析，不是Apple对所有Web产品的命令。官方原生示例未编译运行；我们的独立Web示例才是浏览器验收对象。

## 1. Apple：基础设计课程

[Design foundations from idea to interface](https://developer.apple.com/videos/play/wwdc2025/359/) 讨论层级、字体、图像和色彩如何服务功能；[Principles of great design](https://developer.apple.com/videos/play/wwdc2026/250/) 给出Purpose等八项原则。

**保留**：从任务与人的感受开始，先决定重点和流程，再完善视觉；把精致理解为每个状态、细节和性能都可信。

**舍弃**：用一种皮肤、统一字号或一套像素参数替代设计判断。Apple原则之间需要取舍，并没有保证完美结果的组合公式。

**迁移**：阅读产品重点是连续阅读和返回上下文；购买流程重点是费用、输入与纠错；创作工具重点是编辑对象与撤销；业务工作台重点是比较与操作反馈。以上产品推演是本skill的应用建议。

## 2. Apple Landmarks：内容、导航与平台

[Landmarks: Building an app with Liquid Glass](https://developer.apple.com/documentation/swiftui/landmarks-building-an-app-with-liquid-glass) 展示iPhone、iPad与Mac上的内容探索。案例将导航、工具栏及自定义玻璃效果与主体图片分层，并处理窗口变化。

**保留**：列表与详情关系、主体内容完整性、系统控件的适配、与入口有关联的展开。原生背景扩展可延伸图片到控制层之后，同时保持主体体验。

**舍弃**：把SwiftUI的背景扩展或玻璃动画直接说成CSS blur；把同一平台布局原封不动套给所有设备。

**迁移**：原生优先对应系统组件；Web用适合任务的导航和语义控件，少量控制层玻璃，主体阅读/媒体保持稳定。未经原生运行不能声称复现了Landmarks的光学与触觉能力。

## 3. Codrops / Shader：无限玻璃网格

[作者原创解析](https://tympanus.net/codrops/2026/09/08/building-an-infinite-liquid-glass-grid-with-three-js-webgpu-and-tsl/) / [在线实验](https://infinite-jelly-glass.shader.se/) 演示WebGPU折射、曲面网格及拖动响应；后续更新加入布料运动，文字改为场景内渲染。

**保留**：效果应与交互响应一致；将材质、运动和性能一起比较。阅读作者更新，而不是只看最初“HTML文字可访问”的描述。

**舍弃**：把艺术实验当成所有产品的默认组件；把连续变形的正文放进表单/阅读流程；未经测试就假定渲染文字具备DOM语义、键盘和读屏能力。

**迁移**：作品展示或特定品牌体验可以评估图形方案；一般任务界面先用轻量语义DOM实现与降级。只有内容价值、设备能力和可访问性合同都支持时才增加图形复杂度。

## 本skill的取舍结果

两个自包含案例用于验证思想的迁移，而不是模板化所有产品：

- `assets/demo/index.html`：数据比较、异步导航与非模态详情；三种材质对比后默认均衡。
- `assets/reader/index.html`：连续阅读、文字层级、输入纠错、删除撤销及模态设置；采用阅读产品自己的密度与视觉语气。

复制时提取任务关系、语义状态和组件反馈，不复制虚构业务数据或强制整页结构。效果是否适合由真实操作、可读性、辅助输入与性能共同决定；测试和限制见 [评估记录](../evals/results.md)。
