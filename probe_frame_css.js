async function run(args) {
  const out = { ok: true, rules: [], computed: {}, pseudo: {}, structure: [] };

  // Collect CSS rules mentioning frame-related selectors
  const keywords = ["device", "screen", "statusbar", "notch", "bezel", "phone", "frame", "side"];
  try {
    for (const sheet of Array.from(document.styleSheets)) {
      let rules;
      try { rules = sheet.cssRules; } catch (e) { continue; }
      if (!rules) continue;
      for (const rule of Array.from(rules)) {
        const txt = rule.cssText || "";
        const lower = txt.toLowerCase();
        if (keywords.some(k => lower.includes(k))) {
          out.rules.push(txt.slice(0, 600));
        }
      }
    }
  } catch (e) { out.rulesError = String(e); }

  // Computed styles of .device and .screen
  const dev = document.querySelector(".device");
  const scr = document.querySelector(".screen");
  function snap(el) {
    if (!el) return null;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      tag: el.tagName, cls: el.className,
      rect: { x: r.x, y: r.y, w: r.width, h: r.height },
      width: cs.width, height: cs.height, minHeight: cs.minHeight, maxWidth: cs.maxWidth,
      position: cs.position, top: cs.top, left: cs.left, transform: cs.transform,
      margin: cs.margin, padding: cs.padding, border: cs.border, borderRadius: cs.borderRadius,
      background: cs.background.slice(0, 120), boxShadow: cs.boxShadow, overflow: cs.overflow,
      display: cs.display, flex: cs.flex, alignItems: cs.alignItems, justifyContent: cs.justifyContent
    };
  }
  out.computed.device = snap(dev);
  out.computed.screen = snap(scr);

  // Pseudo elements
  function pseudoSnap(el, which) {
    if (!el) return null;
    const cs = getComputedStyle(el, which);
    return {
      content: cs.content, display: cs.display, position: cs.position,
      top: cs.top, left: cs.left, right: cs.right, bottom: cs.bottom,
      width: cs.width, height: cs.height, background: cs.background.slice(0, 120),
      borderRadius: cs.borderRadius, border: cs.border, boxShadow: cs.boxShadow
    };
  }
  out.pseudo.deviceBefore = pseudoSnap(dev, "::before");
  out.pseudo.deviceAfter = pseudoSnap(dev, "::after");

  // Body structure
  out.structure = Array.from(document.body.children).map(c => ({ tag: c.tagName, cls: c.className, id: c.id }));

  // Body computed
  const bcs = getComputedStyle(document.body);
  out.computed.body = { display: bcs.display, alignItems: bcs.alignItems, justifyContent: bcs.justifyContent, background: bcs.background.slice(0,120), padding: bcs.padding, margin: bcs.margin };

  return out;
}
