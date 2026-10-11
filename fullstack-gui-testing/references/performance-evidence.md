# Motion、性能与证据范围

录屏用于看过渡和操作异常；性能测量使用单独无录像/trace/截图编码的样本。不要让并行 build、测试或第二个浏览器争抢资源。记录页签 visible/hidden；页面失焦或节流的样本不能直接与前景样本比较。

记录 OS、浏览器、CPU/GPU、视口、数据规模、构建 SHA、网络和采样范围；首次冷加载与热交互分开。按项目已有目标选择样本数、p95、最大值、失败数与长任务，不凭空给所有项目定统一性能门槛。

分别测量：

- 操作→忙碌/选中反馈；操作→正确结果可用。
- 请求/后台任务完成时间；保存→新版本重读一致。
- rAF 帧间隔及 longtask；浏览器 task/script/layout 时长。
- 文件处理耗时、内存及错误数，必要时目标 GPU/worker 指标。

**rAF 不等于 GPU 实际呈现 FPS；累计 TaskDuration 不等于单次点击延迟**。p95 正常仍可能有最大帧卡顿；一次本机成功也不能证明低性能设备流畅。

比较前后时固定数据和环境，给绝对数和相对变化，明确样本不足。诊断可临时关闭材质或 motion 分别采样，不能把诊断设置当正常版本结果；最终 GUI 验收恢复正常设置，另测减少动态效果。

出现退化先定位脚本、布局、绘制/合成、请求或数据规模。不要通过改变分类/预处理、降分辨率或静默简化正式空间成果使性能变绿。

相关一手资料：[PerformanceObserver](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceObserver)、[requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)、[Playwright reducedMotion](https://playwright.dev/docs/api/class-browser#browser-new-context-option-reduced-motion)。
