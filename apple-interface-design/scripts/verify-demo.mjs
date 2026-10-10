import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';
import { contrastOnExtremes } from './contrast.mjs';

// 此脚本只验收本skill演示；不能代替真实应用的网络、权限或数据测试。
const { values } = parseArgs({ options: {
  headed: { type: 'boolean', default: false },
  browser: { type: 'string' }, demo: { type: 'string' },
  out: { type: 'string', default: './artifacts/browser' }
} });
const skillDir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(values.out);
const evidence = { date: new Date().toISOString(), headed: values.headed,
  platform: process.platform, viewport: { width: 1440, height: 900 },
  checks: [], materials: [], errors: [], limitations: [
    'rAF间隔是同机页面采样，不是GPU帧时间或生产60fps保证。',
    '黑白底色合成检查不包含渐变、混合模式及任意真实影像。',
    '无blur使用演示的强制降级入口；未模拟一个真正不支持blur的浏览器。',
    '数据读取为模拟；未覆盖Safari、生产网络、投影/LED实机。'
  ] };
await mkdir(output, { recursive: true });
let browser, page, currentCheck = '浏览器启动';

async function check(name, run) {
  currentCheck = name;
  await run();
  evidence.checks.push({ name, passed: true });
  console.log(`PASS ${name}`);
}
async function bounded(promise, timeoutMs, label) {
  let timer;
  try {
    return await Promise.race([promise, new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(`${label}超时；请保持浏览器前台且不要最小化`)), timeoutMs);
    })]);
  } finally { clearTimeout(timer); }
}
async function noMapOverlap() {
  const overlap = await page.evaluate(() => {
    const legend = document.querySelector('.map-legend').getBoundingClientRect();
    const credit = document.querySelector('.map-credit').getBoundingClientRect();
    return Math.min(legend.right, credit.right) > Math.max(legend.left, credit.left)
      && Math.min(legend.bottom, credit.bottom) > Math.max(legend.top, credit.top);
  });
  assert.equal(overlap, false, '地图图例与署名发生遮挡；检查缩放后的内部布局');
}
function rgb(text) {
  const match = /^rgba?\(([^)]+)\)$/.exec(text);
  assert.ok(match, `颜色未解析为sRGB: ${text}`);
  return match[1].split(/[ ,/]+/).map(Number);
}
async function settled(view) {
  await page.waitForFunction(view => window.demoState.phase === 'success'
    && window.demoState.committedView === view
    && document.querySelector('#view-content').dataset.view === view, view);
}
async function snapshot(name) {
  await page.screenshot({ path: resolve(output, `${name}.png`), fullPage: true });
}
async function glassStyle() {
  return page.locator('.topbar').evaluate(el => {
    const style = getComputedStyle(el);
    return { filter: style.backdropFilter, background: style.backgroundColor };
  });
}
async function solid() {
  const style = await glassStyle();
  assert.equal(style.filter, 'none');
  assert.equal(rgb(style.background)[3] ?? 1, 1);
}
async function noMotion() {
  const durations = await page.locator('.nav-indicator').evaluate(el => ({
    transition: getComputedStyle(el).transitionDuration,
    animations: document.getAnimations().filter(a => a.playState === 'running').length
  }));
  assert.equal(durations.transition, '0s');
  assert.equal(durations.animations, 0);
}

try {
  const modulePath = process.env.PLAYWRIGHT_MODULE_PATH;
  const playwright = modulePath
    ? await import(pathToFileURL(resolve(modulePath)).href) : await import('playwright');
  const chromium = playwright.chromium ?? playwright.default?.chromium;
  assert.ok(chromium, '未找到Playwright Chromium入口；请检查PLAYWRIGHT_MODULE_PATH或执行npm ci');
  browser = await chromium.launch({ headless: !values.headed,
    ...(values.browser ? { executablePath: resolve(values.browser) } : {}) });
  evidence.browser = browser.version();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  page = await context.newPage();
  page.setDefaultTimeout(8000);
  page.on('pageerror', error => evidence.errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') evidence.errors.push(message.text());
  });
  await page.route(/^https?:/, route => {
    evidence.errors.push('自包含演示请求了外部网络资源');
    return route.abort();
  });
  await page.goto(pathToFileURL(values.demo ? resolve(values.demo)
    : resolve(skillDir, 'assets/demo/index.html')).href);
  await settled('overview');

  await check('ID唯一，初始内容完整且没有外部请求', async () => {
    const duplicates = await page.evaluate(() => {
      const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
      return ids.filter((id, i) => ids.indexOf(id) !== i);
    });
    assert.deepEqual(duplicates, []);
    assert.equal(await page.locator('tbody tr').count(), 3);
  });
  await check('真实刷新触发busy并完成；重复刷新保留最后一次结果', async () => {
    const before = await page.evaluate(() => window.demoState.requestId);
    await page.locator('#refresh').click();
    assert.equal(await page.locator('#view-content').getAttribute('aria-busy'), 'true');
    assert.equal(await page.locator('#status').getAttribute('data-phase'), 'loading');
    await page.locator('#refresh').click();
    await page.locator('#refresh').click();
    await settled('overview');
    assert.equal(await page.evaluate(() => window.demoState.requestId), before + 3);
    assert.equal(await page.locator('#view-content').getAttribute('aria-busy'), 'false');
  });
  await check('连续26次快切，加载期间可切换且旧请求不回写', async () => {
    const views = ['imagery', 'reports', 'overview'];
    for (let i = 0; i < 26; i++) await page.locator(`nav [data-view="${views[i % 3]}"]`).click();
    await settled('reports');
    assert.equal(await page.locator('nav [aria-current="page"]').getAttribute('data-view'), 'reports');
    assert.equal(await page.locator('.report').count(), 1);
    await page.waitForFunction(() => document.querySelector('.nav-indicator')
      .getBoundingClientRect().left === document.querySelector('nav [aria-current="page"]')
      .getBoundingClientRect().left);
  });
  await check('失败有可读原因，重试恢复正确视图', async () => {
    await page.locator('#fail-next').check();
    await page.locator('#refresh').click();
    await page.waitForFunction(() => window.demoState.phase === 'error');
    assert.equal(await page.locator('#view-content').getAttribute('aria-busy'), 'false');
    assert.match(await page.locator('#status-text').innerText(), /失败/);
    await snapshot('error-retry');
    await page.locator('#retry').click();
    await settled('reports');
  });
  await check('详情反复开关、Esc回焦；隐藏面板不参与Tab序列', async () => {
    for (let i = 0; i < 5; i++) {
      await page.locator('#detail-toggle').click();
      assert.equal(await page.locator('#detail-toggle').getAttribute('aria-expanded'), 'true');
      await page.locator('#detail-close').focus();
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => document.querySelector('#detail').hidden);
      assert.equal(await page.locator('#detail-toggle').getAttribute('aria-expanded'), 'false');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'detail-toggle');
    }
    for (let i = 0; i < 14; i++) {
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.querySelector('#detail')
        .contains(document.activeElement)), false);
    }
    await page.locator('#detail-toggle').focus();
    await page.keyboard.press('Shift+Tab');
    const focus = await page.evaluate(() => ({
      id: document.activeElement.id, outline: getComputedStyle(document.activeElement).outlineWidth
    }));
    assert.equal(focus.id, 'refresh');
    assert.ok(parseFloat(focus.outline) >= 2);
  });
  await check('12次面板运动中断后，最后一次展开/收起意图一致', async () => {
    for (let i = 0; i < 12; i++) await page.locator('#detail-toggle').click();
    await page.locator('#detail-toggle').click();
    await page.waitForFunction(() => window.demoState.detailOpen
      && !document.querySelector('#detail').hidden
      && document.querySelector('#detail').getAnimations().every(a => a.playState !== 'running'));
    assert.equal(await page.locator('#detail').evaluate(el => el.inert), false);
    assert.equal(await page.locator('#detail-toggle').getAttribute('aria-expanded'), 'true');
    await snapshot('detail-open');
    await page.locator('#detail-close').click();
    await page.waitForFunction(() => document.querySelector('#detail').hidden);
  });
  await check('按钮按下有视觉反馈，释放恢复', async () => {
    const button = page.locator('#theme');
    await button.hover();
    await page.mouse.down();
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#theme')).transform !== 'none');
    await snapshot('button-pressed');
    await page.mouse.up();
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#theme')).transform === 'none');
    await button.click(); // 回到初始浅色，按下释放已触发一次主题切换。
  });
  await check('运行时系统/手动减少动态效果保留业务状态', async () => {
    await page.locator('#refresh').click();
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await noMotion();
    await settled('reports');
    await page.locator('#detail-toggle').click();
    await noMotion();
    await page.locator('#detail-close').click();
    await page.waitForFunction(() => document.querySelector('#detail').hidden);
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.locator('#reduce-motion').check();
    await noMotion();
    await page.locator('#reduce-motion').uncheck();
  });
  await check('系统减少透明度/增强对比、手动实色及强制降级', async () => {
    const cdp = await context.newCDPSession(page);
    for (const feature of ['prefers-reduced-transparency', 'prefers-contrast']) {
      const value = feature === 'prefers-contrast' ? 'more' : 'reduce';
      await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: feature, value }] });
      assert.equal(await page.evaluate(query => matchMedia(query).matches, `(${feature}: ${value})`), true);
      await solid();
    }
    await cdp.send('Emulation.setEmulatedMedia', { features: [] });
    await page.locator('#reduce-transparency').check();
    await solid();
    await page.locator('#reduce-transparency').uncheck();
    await page.evaluate(() => document.documentElement.dataset.noBlur = 'true');
    await solid();
    await page.locator('nav [data-view="overview"]').click();
    await settled('overview');
    await page.evaluate(() => delete document.documentElement.dataset.noBlur);
  });
  await check('系统强制颜色模式仍有焦点、选中和业务内容', async () => {
    await page.emulateMedia({ forcedColors: 'active' });
    assert.equal(await page.evaluate(() => matchMedia('(forced-colors: active)').matches), true);
    await page.locator('#detail-toggle').focus();
    await page.keyboard.press('Shift+Tab');
    assert.ok(await page.locator('#refresh').evaluate(el => parseFloat(getComputedStyle(el).outlineWidth) >= 2));
    assert.equal(await page.locator('nav [aria-current="page"]').count(), 1);
    assert.equal(await page.locator('tbody tr').count(), 3);
    await snapshot('forced-colors');
    await page.emulateMedia({ forcedColors: 'none' });
  });
  await check('两期年份与影像关联，SVG保持统一缩放比例', async () => {
    await page.locator('nav [data-view="imagery"]').click();
    await settled('imagery');
    assert.equal(await page.locator('.compare svg').count(), 2);
    const dates = await page.locator('.compare .tag').allTextContents();
    assert.deepEqual(dates, ['2026.09.08', '2026.10.08']);
    const scales = await page.locator('.compare svg').evaluateAll(images => images.map(image => {
      const matrix = image.getScreenCTM();
      return Math.abs(matrix.a - matrix.d);
    }));
    assert.ok(scales.every(difference => difference < 0.001));
    await snapshot('imagery-pair');
    await page.locator('nav [data-view="overview"]').click();
    await settled('overview');
  });

  for (const theme of ['light', 'dark']) {
    if (await page.locator('html').getAttribute('data-theme') !== theme) await page.locator('#theme').click();
    for (const preset of ['light', 'balanced', 'solid']) {
      await page.locator('#material').selectOption(preset);
      const style = await glassStyle();
      const colors = await page.locator('.topbar').evaluate(el => ({
        ink: getComputedStyle(el).color,
        muted: getComputedStyle(el.querySelector('.environment')).color
      }));
      const primary = contrastOnExtremes(rgb(colors.ink), rgb(style.background));
      const secondary = contrastOnExtremes(rgb(colors.muted), rgb(style.background));
      evidence.materials.push({ theme, preset, ...style,
        textMinimum: primary.minimum, secondaryMinimum: secondary.minimum });
      await snapshot(`${theme}-${preset}`);
      if (preset === 'balanced' || preset === 'solid') {
        assert.ok(primary.minimum >= 4.5 && secondary.minimum >= 4.5,
          `${theme}/${preset}文字在黑白极端背景合成后未达4.5:1`);
      }
    }
  }
  evidence.checks.push({ name: '双主题三种材质截图；均衡/实色保守文本对比≥4.5:1', passed: true });

  await page.locator('#material').selectOption('balanced');
  await check('1440/1920窗口、200% CSS缩放及720×450等效视口无裁切/图例遮挡', async () => {
    for (const viewport of [{ width: 1440, height: 900 }, { width: 1920, height: 1080 }]) {
      await page.setViewportSize(viewport);
      await page.evaluate(() => document.documentElement.style.zoom = '1');
      await snapshot(`layout-${viewport.width}`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      await noMapOverlap();
    }
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.evaluate(() => document.documentElement.style.zoom = '2');
    await snapshot('zoom-200');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await noMapOverlap();
    await page.locator('#refresh').click();
    await settled('overview');
    await page.locator('#detail-toggle').click();
    await page.locator('#detail-close').click();
    await page.waitForFunction(() => document.querySelector('#detail').hidden);
    await page.evaluate(() => document.documentElement.style.zoom = '1');
    await page.setViewportSize({ width: 720, height: 450 });
    await noMapOverlap();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await snapshot('reflow-720');
    await page.locator('#refresh').click();
    await settled('overview');
    await page.setViewportSize({ width: 1440, height: 900 });
  });

  evidence.frames = [];
  currentCheck = '连续操作期间的有界rAF采样';
  for (const preset of ['light', 'balanced', 'solid']) {
    await page.locator('#material').selectOption(preset);
    await page.bringToFront();
    await page.evaluate(() => {
      window.frameSample = new Promise(resolve => {
        const intervals = []; let last, first;
        function frame(now) {
          first ??= now;
          if (last !== undefined) intervals.push(now - last);
          last = now;
          if (now - first >= 2200) resolve(intervals); else requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
      });
    });
    for (const view of ['imagery', 'reports', 'overview']) await page.locator(`nav [data-view="${view}"]`).click();
    await settled('overview');
    await page.locator('#detail-toggle').click();
    await page.locator('#detail-close').click();
    await page.waitForFunction(() => document.querySelector('#detail').hidden);
    const frames = await bounded(page.evaluate(() => window.frameSample), 12000, 'rAF采样');
    const sorted = [...frames].sort((a, b) => a - b);
    evidence.frames.push({ preset, samples: frames.length, durationMs: frames.reduce((a, b) => a + b, 0),
      p95Ms: sorted[Math.ceil(sorted.length * .95) - 1],
      maxMs: sorted.at(-1), over50Ms: frames.filter(ms => ms > 50).length });
  }
  evidence.checks.push({ name: '三材质连续操作期间rAF采样（测量，不作为固定帧率承诺）', passed: true });
  assert.deepEqual(evidence.errors, []);
  evidence.passed = true;
} catch (error) {
  evidence.passed = false;
  evidence.failure = error.message;
  evidence.failedCheck = currentCheck;
  evidence.stack = error.stack;
  console.error(`FAIL ${error.message}\n位置: ${error.stack}\n下一步: 检查输出截图与report.json中的最后通过步骤。`);
  if (page && !page.isClosed()) await snapshot('failure').catch(() => {});
  process.exitCode = 1;
} finally {
  await writeFile(resolve(output, 'report.json'), JSON.stringify(evidence, null, 2) + '\n');
  await browser?.close();
}
