// 输入RGB为0—255；可选第四项alpha为0—1。仅用于已解析的sRGB示例色。
export function composite(foreground, background) {
  const alpha = foreground[3] ?? 1;
  return foreground.slice(0, 3).map((channel, i) => channel * alpha + background[i] * (1 - alpha));
}

function luminance(rgb) {
  const linear = rgb.slice(0, 3).map(channel => {
    const value = channel / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
}

export function contrastRatio(foreground, background) {
  const a = luminance(foreground);
  const b = luminance(background);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

export function contrastOnExtremes(text, material) {
  const values = [[0, 0, 0], [255, 255, 255]].map(background => {
    const surface = composite(material, background);
    return contrastRatio(composite(text, surface), surface);
  });
  return { black: values[0], white: values[1], minimum: Math.min(...values) };
}
