async function run(args) {
  const out = { ok: true, rules: [], computed: {} };
  const seen = new Set();
  for (const sheet of Array.from(document.styleSheets)) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    if (!rules) continue;
    for (const rule of Array.from(rules)) {
      const t = rule.cssText || "";
      if (seen.has(t)) continue; seen.add(t);
      out.rules.push(t.slice(0, 500));
    }
  }
  function snap(sel) {
    const el = document.querySelector(sel);
    if (!el) return null;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return { rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
      width: cs.width, maxWidth: cs.maxWidth, height: cs.height, margin: cs.margin, padding: cs.padding,
      display: cs.display, flexDirection: cs.flexDirection, overflow: cs.overflow, gap: cs.gap, position: cs.position };
  }
  [".device", ".screen", ".statusbar", "#view-home", ".topbar", "#feed", ".feed", ".card", "body", "html"].forEach(s => out.computed[s] = snap(s));
  out.totalRules = out.rules.length;
  return out;
}
