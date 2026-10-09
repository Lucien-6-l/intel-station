async function run(args) {
  const root = document.querySelector(".device");
  const out = { ok: true, counts: {}, samples: [] };
  if (!root) return { ok: false, error: "no .device" };

  // count all class frequencies within root
  const freq = {};
  root.querySelectorAll("*").forEach(el => {
    const c = el.className;
    if (typeof c === "string" && c.trim()) {
      c.trim().split(/\s+/).forEach(x => { freq[x] = (freq[x] || 0) + 1; });
    }
  });
  const sorted = Object.entries(freq).sort((a,b)=>b[1]-a[1]).slice(0, 40);
  out.counts = Object.fromEntries(sorted);

  // anchor-like repeated items
  const anchors = Array.from(root.querySelectorAll("a")).map(a => ({
    cls: a.className, href: (a.getAttribute("href")||"").slice(0,50), text: (a.textContent||"").trim().slice(0,40)
  })).filter(a => a.href.startsWith("http"));
  out.samples = anchors.slice(0, 5);
  out.anchorCount = anchors.length;

  // try common feed containers
  [".feed", "#feed", ".list", ".news-list", ".cards", "[id*=feed]", "[class*=list]", "[class*=card]"].forEach(s => {
    out.counts["sel:"+s] = root.querySelectorAll(s).length;
  });
  return out;
}
