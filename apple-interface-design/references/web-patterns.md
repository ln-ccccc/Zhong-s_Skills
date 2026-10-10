# Web 落地：默认轻量，可中断

## 材质层

用 `--surface` 表示内容实色、`--glass` 表示控制层、`--ink/--muted/--accent/--danger` 表示语义色。深浅分别定义alpha和明度；避免对图片/地图/整个内容容器应用blur。网页rim高光与阴影只是光学提示，不宣称实时折射。

默认采用可读实色，浏览器支持时逐步增强；低性能设备或用户选择可回退。示例：

```css
.glass { background: var(--surface); border: 1px solid var(--edge); }
@supports ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass {
    background: var(--glass);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
  }
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more) {
  .glass { background: var(--surface); backdrop-filter: none; -webkit-backdrop-filter: none; }
}
html[data-solid="true"] .glass {
  background: var(--surface); backdrop-filter: none; -webkit-backdrop-filter: none;
}
```

`prefers-reduced-transparency` 支持范围可能变化，不以媒体查询没匹配为用户没有需求。有现成偏好入口时提供“减少透明度/实色材质”；没有入口且超出任务范围时直接采用可读的实色，不强制新增设置。`forced-colors` 时服从系统颜色，避免让自定义高光覆盖焦点。

## 动效与数据解耦

对高频动作优先动画 `transform/opacity`，避免动画blur、大面积shadow、宽高及 `transition: all`。不要让持续cursor光斑、每卡片独立blur或永久 `will-change` 扩大合成开销。媒体/地图第三方画布被缩放或显隐后，按其API必要时通知尺寸变化，并复验。

导航动作允许被后一次动作接管；前一次异步请求不能覆盖新页。读请求可用AbortController取消，仍保留请求序号检查；写请求的取消语义需要后端合同，不能照抄读请求代码。

```js
let requestId = 0;
async function selectView(view) {
  const id = ++requestId;
  setSelected(view); // 同步更新可访问状态，不等动画
  setLoading(view);
  try {
    const data = await load(view);
    if (id !== requestId) return;
    renderData(view, data);
  } catch (error) {
    if (id === requestId) renderError(view, error);
  } finally {
    if (id === requestId) clearLoading(view);
  }
}
```

这是模式示例，`setSelected/load/renderData` 应替换为项目实际函数，不是假设仓库已提供这些API。相关工程要点见 [AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)。

## 减少动态效果

CSS减少位移/弹性，JS动画也读取偏好，并监听运行时变更。切换偏好后立即稳定到当前状态，不回退路由、取消有效业务或丢掉内容。除去弹性后仍有焦点、选中、状态文字；不要只让整个页面“什么反馈都没有”。

不要依赖无限旋转表示唯一加载信息。若减少动态效果时停止spinner，保留“加载中”文字及live状态。不依赖转场结束事件切换页面。

## 面板与焦点

普通详情展开使用 `aria-expanded` / `aria-controls`，关闭后隐藏或 `inert` 未显示内容，焦点若在内部则回到入口；非模态不用困焦。真正模态可用原生 `dialog.showModal()`，仍检查Esc、标题、关闭与回焦。退出过渡不能留下透明但拦截点击的遮罩。

语义button比div更可靠；控件和SVG symbol的ID保持唯一。真实点击“刷新”并观察busy→结果/错误，比静态检查函数名能发现更多问题。

## 可运行示例

`assets/demo/index.html` 是同一业务内容下的三种材质比较，含两套主题、减少动态效果和透明度开关。无外部字体、图片、网络数据；SVG与数值均是演示，不是矿山/遥感实测。演示异步延迟为确定性模拟，生产仍需真实网络与服务错误联调。
