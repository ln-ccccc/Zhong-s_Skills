import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

// 只验收虚构阅读产品，不连接账户、邮件或真实收藏数据。
const { values } = parseArgs({ options: {
  headed: { type: 'boolean', default: false }, browser: { type: 'string' },
  out: { type: 'string', default: './artifacts/reader' }
} });
const skillDir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(values.out);
await mkdir(output, { recursive: true });
const report = { date: new Date().toISOString(), headed: values.headed, platform: process.platform,
  checks: [], errors: [], limitations: ['仅桌面浏览器模拟窄视口，未验证手机硬件、Safari或读屏。',
    '收藏和保存为内存模拟；未验证服务端、浏览器历史导航或邮件发送。',
    '放大使用CSS zoom:2，另测390×844窄视口；不能覆盖原生浏览器缩放的一切行为。'] };
let browser, page, currentCheck = '浏览器启动';
async function check(name, run) {
  currentCheck = name; await run(); report.checks.push({ name, passed: true }); console.log(`PASS ${name}`);
}
const state = () => page.evaluate(() => window.readerState);
const screenshot = name => page.screenshot({ path: resolve(output, `${name}.png`), fullPage: true });
async function click(selector) { await page.locator(selector).click(); }
async function noOverflow() {
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), '出现水平溢出');
}
async function solidNotice() {
  assert.equal(await page.locator('#notice').evaluate(el => getComputedStyle(el).backdropFilter), 'none');
  assert.match(await page.locator('#notice').evaluate(el => getComputedStyle(el).backgroundColor), /^rgb\(/);
}
try {
  const modulePath = process.env.PLAYWRIGHT_MODULE_PATH;
  const module = modulePath ? await import(pathToFileURL(resolve(modulePath)).href) : await import('playwright');
  browser = await (module.chromium ?? module.default.chromium).launch({ headless: !values.headed,
    ...(values.browser ? { executablePath: resolve(values.browser) } : {}) });
  report.browser = browser.version();
  const context = await browser.newContext({ viewport: { width: 1100, height: 900 } });
  await context.route(/^https?:/, route => { report.errors.push(`意外外部请求：${route.request().url()}`); return route.abort(); });
  page = await context.newPage();
  page.on('pageerror', error => report.errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
  await page.goto(pathToFileURL(resolve(skillDir, 'assets/reader/index.html')).href);
  await check('初始收藏、唯一ID与自包含', async () => {
    assert.deepEqual((await state()).saved, ['a1', 'a2', 'a3']);
    assert.equal(await page.locator('.entry').count(), 3);
    assert.equal(await page.evaluate(() => {
      const ids = [...document.querySelectorAll('[id]')].map(el => el.id); return ids.length === new Set(ids).size;
    }), true);
    await screenshot('reader-desktop');
  });
  await check('窄视口布局与阅读入口命中区域', async () => {
    await page.setViewportSize({ width: 390, height: 844 }); await noOverflow();
    const heights = await page.locator('[data-read]').evaluateAll(buttons => buttons.map(b => b.getBoundingClientRect().height));
    // 44 CSS px是本演示的触摸舒适目标，不是Apple所有平台的统一规范。
    assert.ok(heights.every(height => height >= 44), `阅读按钮过窄：${heights.join(', ')}`);
    await screenshot('reader-mobile'); await page.setViewportSize({ width: 1100, height: 900 });
  });
  await check('搜索范围、空态与阅读返回上下文', async () => {
    await page.locator('#search').fill('林岸');
    assert.equal(await page.locator('.entry').count(), 1);
    await click('[data-filter="all"]'); assert.equal(await page.locator('.entry').count(), 2);
    await click('[data-read="a4"]'); assert.equal((await state()).current, 'a4');
    assert.equal(await page.locator('#library').isVisible(), false);
    await click('#back'); assert.equal((await state()).query, '林岸'); assert.equal((await state()).filter, 'all');
    assert.equal(await page.evaluate(() => document.activeElement.dataset.read), 'a4');
    await page.locator('#search').fill('不存在的文章'); assert.equal(await page.locator('.entry').count(), 0);
    await click('#empty-action'); assert.equal((await state()).query, '');
    await click('[data-filter="saved"]');
  });
  await check('连续移除、逐次撤销与空收藏恢复', async () => {
    await click('[data-delete="a1"]'); await click('[data-delete="a2"]');
    assert.deepEqual((await state()).saved, ['a3']);
    await click('#undo'); await click('#undo');
    assert.deepEqual((await state()).saved, ['a1', 'a2', 'a3']);
    for (const id of ['a1', 'a2', 'a3']) await click(`[data-delete="${id}"]`);
    assert.equal(await page.locator('.entry').count(), 0);
    assert.match(await page.locator('.empty').innerText(), /收藏夹暂时空了/);
    for (let i = 0; i < 3; i++) await click('#undo');
    assert.deepEqual((await state()).saved, ['a1', 'a2', 'a3']);
    await click('#notice-close');
  });
  await check('连续24次阅读切换与真实收藏反馈', async () => {
    for (let i = 0; i < 24; i++) { await click(`[data-read="a${i % 3 + 1}"]`); await click('#back'); }
    assert.equal((await state()).current, null); assert.equal(await page.locator('#reader').isVisible(), false);
    await click('[data-read="a1"]');
    await click('#reader-save'); assert.equal((await state()).saved.includes('a1'), false);
    await click('#undo'); assert.equal((await state()).saved.includes('a1'), true);
    await click('#notice-close'); await screenshot('reader-article');
    await click('#back');
  });
  await check('模态键盘范围、Esc回焦与取消草稿', async () => {
    await click('#settings-open'); assert.equal(await page.evaluate(() => document.activeElement.id), 'email');
    for (let i = 0; i < 12; i++) {
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.querySelector('#settings-dialog').contains(document.activeElement)
        || document.activeElement === document.body), true);
    }
    // 原生dialog允许键盘走到浏览器工具栏，此时activeElement为body；背景页面控件仍不可聚焦。
    await page.locator('#email').focus();
    await page.evaluate(() => document.querySelector('#theme').focus());
    assert.equal(await page.evaluate(() => document.activeElement.id), 'email');
    await page.locator('#email').fill('draft@example.com');
    await page.keyboard.press('Escape');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'settings-open');
    assert.equal((await state()).settings.email, 'reader@example.com');
    await click('#settings-open'); assert.equal(await page.locator('#email').inputValue(), 'reader@example.com');
    await click('#settings-cancel');
  });
  await check('错误位置与输入保留、保存期间按钮禁用与完成状态', async () => {
    await click('#settings-open'); await page.locator('#email').fill('invalid'); await click('#save-settings');
    assert.equal(await page.locator('#email').getAttribute('aria-invalid'), 'true');
    assert.equal(await page.locator('#email').inputValue(), 'invalid');
    assert.match(await page.locator('#email-error').innerText(), /邮箱格式不完整/);
    assert.equal((await state()).saving, false); await screenshot('reader-form-error');
    await page.locator('#email').fill('valid@example.com'); await page.locator('#text-size').selectOption('large');
    await page.locator('#reduce-motion').check(); await page.locator('#solid-material').check();
    await click('#save-settings');
    assert.equal(await page.locator('#settings-form').getAttribute('aria-busy'), 'true');
    assert.equal(await page.locator('#save-settings').isDisabled(), true);
    await page.waitForFunction(() => !window.readerState.saving);
    assert.equal((await state()).settings.email, 'valid@example.com');
    assert.equal((await state()).settings.size, 'large');
    assert.equal(await page.locator('#settings-dialog').isVisible(), false);
    await solidNotice(); await click('#notice-close');
  });
  await check('更大正文、动态偏好与独立深色主题', async () => {
    await click('[data-read="a2"]');
    assert.ok(await page.locator('.prose').evaluate(el => parseFloat(getComputedStyle(el).fontSize)) > 21);
    assert.equal(await page.locator('#reading-content').evaluate(el => getComputedStyle(el).animationName), 'none');
    await click('#theme'); assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
    await screenshot('reader-dark');
    await click('#settings-open'); await page.locator('#reduce-motion').uncheck(); await page.locator('#solid-material').uncheck();
    await click('#save-settings'); await page.waitForFunction(() => !window.readerState.saving);
    await page.emulateMedia({ reducedMotion: 'reduce' });
    assert.equal(await page.locator('#reading-content').evaluate(el => getComputedStyle(el).animationName), 'none');
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    const cdp = await context.newCDPSession(page);
    await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-transparency', value: 'reduce' }] });
    assert.equal(await page.evaluate(() => matchMedia('(prefers-reduced-transparency:reduce)').matches), true);
    await solidNotice(); await cdp.send('Emulation.setEmulatedMedia', { features: [] }); await cdp.detach();
    await click('#notice-close');
  });
  await check('文本放大与窄视口设置、阅读排版', async () => {
    await page.setViewportSize({ width: 390, height: 844 }); await noOverflow(); await screenshot('reader-mobile-article');
    await click('#settings-open'); await noOverflow(); await screenshot('reader-mobile-settings');
    const box = await page.locator('#settings-dialog').boundingBox(); assert.ok(box.x >= 0 && box.x + box.width <= 391);
    await click('#settings-cancel'); await click('#back');
    await page.setViewportSize({ width: 1100, height: 900 });
    await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
    await noOverflow(); await screenshot('reader-zoom-200');
    await page.evaluate(() => { document.documentElement.style.zoom = ''; });
  });
  assert.deepEqual(report.errors, []); report.passed = true;
} catch (error) {
  report.passed = false; report.failedCheck = currentCheck; report.failure = error.stack;
  console.error(error.stack); process.exitCode = 1;
  if (page) await screenshot('failure').catch(() => {});
} finally {
  await writeFile(resolve(output, 'report.json'), JSON.stringify(report, null, 2));
  await browser?.close(); console.log(`报告：${resolve(output, 'report.json')}`);
}
