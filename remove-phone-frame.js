async function run(args) {
  const NS = "__dePhoneFrame";
  const STYLE_ID = NS + "_style";

  // Cleanup any prior instance so re-execution does not stack effects.
  if (window[NS] && typeof window[NS].destroy === "function") {
    try { window[NS].destroy(); } catch (e) {}
  }

  const css = `
    /* === 移除手机外框 (Remove phone mockup outer frame) === */
    body {
      background: var(--bg) !important;
      padding: 0 !important;
      margin: 0 !important;
      display: block !important;
      min-height: 0 !important;
    }
    .device {
      width: 100vw !important;
      height: 100vh !important;
      max-width: none !important;
      max-height: none !important;
      background: transparent !important;
      border-radius: 0 !important;
      padding: 0 !important;
      box-shadow: none !important;
      position: relative !important;
    }
    .device::after { display: none !important; }   /* 顶部刘海 notch */
    .screen { border-radius: 0 !important; }        /* 屏幕圆角 */
    .statusbar { display: none !important; }        /* 手机状态栏 9:41 */
    .home-ind { display: none !important; }         /* 底部 Home 指示条 */
  `;

  let style = document.getElementById(STYLE_ID);
  if (!style) {
    style = document.createElement("style");
    style.id = STYLE_ID;
    (document.head || document.documentElement).appendChild(style);
  }
  style.textContent = css;

  const controller = {
    id: NS,
    styleId: STYLE_ID,
    destroy() {
      const s = document.getElementById(STYLE_ID);
      if (s) s.remove();
      if (window[NS] === controller) window[NS] = null;
    }
  };
  window[NS] = controller;

  function info(el) {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
      borderRadius: cs.borderRadius, padding: cs.padding, background: cs.background.slice(0, 40)
    };
  }

  const dev = document.querySelector(".device");
  const scr = document.querySelector(".screen");
  const sb = document.querySelector(".statusbar");
  const hover = document.querySelector(".home-ind");
  const notchDisplay = dev ? getComputedStyle(dev, "::after").display : null;
  const sbDisplay = sb ? getComputedStyle(sb).display : null;

  const devW = dev ? dev.getBoundingClientRect().width : -1;
  const ok = !!dev && !!scr &&
    Math.abs(devW - window.innerWidth) < 2 &&
    notchDisplay === "none" &&
    (sbDisplay === "none" || sbDisplay === null);

  return {
    ok,
    summary: ok
      ? "已移除手机外框：深色边框、圆角、阴影、刘海、状态栏与 Home 指示条均已去除，应用内容铺满整个视口。"
      : "脚本已注入，但部分后置条件未满足，请查看 data。",
    changed_count: ok ? 1 : 0,
    data: {
      device: info(dev),
      screen: info(scr),
      notchDisplay,
      statusbarDisplay: sbDisplay,
      homeIndPresent: !!hover,
      viewport: { w: window.innerWidth, h: window.innerHeight }
    },
    warnings: []
  };
}
