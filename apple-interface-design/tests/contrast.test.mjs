import assert from 'node:assert/strict';
import test from 'node:test';
import { composite, contrastRatio, contrastOnExtremes } from '../scripts/contrast.mjs';

test('WCAG 黑白基准是21:1，相同颜色是1:1', () => {
  assert.equal(contrastRatio([0, 0, 0], [255, 255, 255]), 21);
  assert.equal(contrastRatio([128, 128, 128], [128, 128, 128]), 1);
});
test('半透明颜色必须先与底图合成，不能直接忽略alpha', () => {
  assert.deepEqual(composite([255, 255, 255, 0.5], [0, 0, 0]), [127.5, 127.5, 127.5]);
  assert.deepEqual(composite([12, 20, 30, 1], [255, 255, 255]), [12, 20, 30]);
});
test('同一玻璃面板在黑白背景上有不同的可读性', () => {
  const result = contrastOnExtremes([255, 255, 255, 1], [0, 0, 0, 0.1]);
  assert.equal(result.black, 21);
  assert.ok(result.white < 1.3);
  assert.equal(result.minimum, result.white);
});
test('文字本身的alpha也参与合成', () => {
  const result = contrastOnExtremes([255, 255, 255, 0.2], [0, 0, 0, 1]);
  assert.ok(result.minimum < 2);
});
