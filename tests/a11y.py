"""
Lightweight accessibility audit: names, labels, alt text, headings, landmarks,
contrast and keyboard focus. Needs Playwright and Pillow.

    python3 tests/a11y.py [url]          # default http://127.0.0.1:8080/?to=Pujo

Runs at 390px (phone) and 1440px (desktop) with reduced motion. The cover sheet
is audited before opening, the invitation after opening (gift panel expanded).

Contrast: text is measured against the nearest solid background colour. When a
gradient sits in between (forest bands, ticket stub, bank cards), the text is
made transparent and the pixels behind it are sampled from a screenshot; the
lightest/darkest 10% (whichever is closer to the text colour) decides.
Disabled controls are exempt (WCAG 1.4.3). Text over photographs (phone hero,
cover photo, closing photo) is excluded: check it visually with tests/shoot.py.

Set PW_CHROMIUM to a Chromium binary if Playwright's own browser isn't installed.
"""
import asyncio
import io
import json
import os
import sys

from PIL import Image
from playwright.async_api import async_playwright

JS = r"""
(scope) => {
  const issues = [];
  const vis = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length) && getComputedStyle(el).visibility !== 'hidden';
  const name = (el) => (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') && document.getElementById(el.getAttribute('aria-labelledby'))?.textContent || el.textContent || el.getAttribute('title') || '').trim();
  const root = scope === 'cover' ? document.getElementById('cover') : document;
  if (scope !== 'cover') {
    document.querySelectorAll('img').forEach(img => { if (!img.hasAttribute('alt')) issues.push('img without alt: ' + img.src.slice(-60)); });
    document.querySelectorAll('input:not([type=hidden]), textarea, select').forEach(el => {
      if (el.closest('.hp')) return;
      const labelled = el.labels && el.labels.length || el.getAttribute('aria-label') || el.getAttribute('aria-labelledby');
      if (!labelled) issues.push('unlabelled field: ' + (el.name || el.id));
    });
    const hs = [...document.querySelectorAll('main h1, main h2, main h3, main h4')].filter(h => !h.closest('[hidden]'));
    let prev = 0; hs.forEach(h => { const l = +h.tagName[1]; if (prev && l > prev + 1) issues.push(`heading jump h${prev}→h${l}: ${h.textContent.trim().slice(0,40)}`); prev = l; });
    if (document.querySelectorAll('main h1').length !== 1) issues.push('main should have exactly one h1');
    const ids = {}; document.querySelectorAll('[id]').forEach(e => { ids[e.id] = (ids[e.id]||0)+1; }); Object.entries(ids).forEach(([k,v]) => v>1 && issues.push('duplicate id: '+k));
    document.querySelectorAll('[aria-describedby],[aria-controls],[aria-labelledby]').forEach(e => ['aria-describedby','aria-controls','aria-labelledby'].forEach(a => (e.getAttribute(a)||'').split(/\s+/).filter(Boolean).forEach(id => { if (!document.getElementById(id)) issues.push(`${a} → missing #${id}`); })));
  }
  // split headings: letters are aria-hidden, the heading itself must carry the name
  root.querySelectorAll('[data-split]').forEach(h => { if (!h.getAttribute('aria-label')) issues.push('split heading without aria-label: ' + h.id); });
  root.querySelectorAll('button, a[href]').forEach(el => { if (vis(el) && !name(el)) issues.push('control without name: ' + el.outerHTML.slice(0, 90)); });

  // ---- contrast of visible text
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const over = (c, base) => ({ r: c.r*c.a + base.r*(1-c.a), g: c.g*c.a + base.g*(1-c.a), b: c.b*c.a + base.b*(1-c.a), a: 1 });
  const lum = ({r,g,b}) => [r,g,b].map(v => { v/=255; return v<=.03928? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }).reduce((s,v,i)=> s + v*[.2126,.7152,.0722][i], 0);
  const ratioOf = (a, b) => { const L1 = lum(a), L2 = lum(b); return (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05); };
  const PAPER = {r:251,g:250,b:246,a:1};
  // Nearest solid background; `gradient` = a gradient lies between the text and it
  const background = (el) => {
    const active = el.closest('.chip.is-active');
    if (active) { const ink = document.querySelector('.chips__ink'); if (ink) return { base: parse(getComputedStyle(ink).backgroundColor), gradient: false }; }
    const layers = [];
    let gradient = false;
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage.includes('gradient')) gradient = true;
      const c = parse(cs.backgroundColor);
      if (c && c.a > .9) return { base: layers.reduceRight((acc, l) => over(l, acc), c), gradient };
      if (c && c.a > 0) layers.push(c);
    }
    return { base: PAPER, gradient };
  };
  const opacityOf = (el) => { let o = 1; for (let e = el; e && e !== document.body; e = e.parentElement) o *= +getComputedStyle(e).opacity; return o; };
  const low = [], sample = [];
  let checked = 0;
  const sel = scope === 'cover'
    ? '.cover p, .cover span, .cover button, .cover h2'
    : 'main p, main span, main a, main label, main legend, main h1, main h2, main h3, main button, main strong, main figcaption';
  const skip = scope === 'cover' ? '.cover__photo' : (scope === 'desktop' ? '.hero__media, .closing__figure' : '.hero, .closing__figure');
  root.querySelectorAll(sel).forEach(el => {
    if (!vis(el) || ![...el.childNodes].some(n => n.nodeType===3 && n.textContent.trim())) return;
    if (el.closest(skip) || el.closest(':disabled')) return;
    const cs = getComputedStyle(el); const fg0 = parse(cs.color); const op = opacityOf(el);
    if (!fg0 || op === 0) return;
    checked++;
    const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 600; const large = size >= 24 || (size >= 18.66 && bold);
    const need = large ? 3 : 4.5;
    const label = `${size}px ${cs.fontWeight} .${(el.getAttribute('class') || el.tagName).split(' ')[0]} "${el.textContent.trim().slice(0,30)}"`;
    const fg = { ...fg0, a: fg0.a * op };
    const { base, gradient } = background(el);
    if (gradient) {
      el.dataset.a11ySample = String(sample.length);
      sample.push({ i: sample.length, fg, need, label });
      return;
    }
    const ratio = ratioOf(over(fg, base), base);
    if (ratio < need) low.push(`${ratio.toFixed(2)} ${label}`);
  });
  return { issues, low: [...new Set(low)], sample, textChecked: checked,
           landmarks: { main: !!document.querySelector('main'), nav: !!document.querySelector('nav[aria-label]'), skipLink: !!document.querySelector('.skip-link[href="#main"]') } };
}
"""

HIDE_TEXT = "* { color: transparent !important; text-shadow: none !important; caret-color: transparent !important; }"


def lum(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    l1, l2 = lum(a), lum(b)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


async def measure_gradients(pg, samples):
    """Contrast of text over gradients, from the real pixels behind it."""
    if not samples:
        return []
    style = await pg.add_style_tag(content=HIDE_TEXT)
    low = []
    for s in samples:
        loc = pg.locator(f'[data-a11y-sample="{s["i"]}"]')
        try:
            png = await loc.screenshot(animations="disabled", timeout=5000)
        except Exception as e:  # element can't be captured (zero size, detached)
            low.append(f"? {s['label']} (not measured: {str(e)[:60]})")
            continue
        img = Image.open(io.BytesIO(png)).convert("RGB")
        img.thumbnail((200, 200))
        fg = s["fg"]
        ratios = []
        pixels = img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()
        for px in pixels:
            a = fg["a"]
            text = tuple(fg[k] * a + px[i] * (1 - a) for i, k in enumerate("rgb"))
            ratios.append(ratio(text, px))
        ratios.sort()
        worst = ratios[len(ratios) // 10]  # 10th percentile: ignores a few stray pixels
        if worst < s["need"]:
            low.append(f"{worst:.2f} (median {ratios[len(ratios) // 2]:.2f}, sampled) {s['label']}")
    await style.evaluate("el => el.remove()")
    return low


async def audit(browser, url, w, h, tab_stops):
    ctx = await browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce",
                                    is_mobile=w < 768, has_touch=w < 768)
    pg = await ctx.new_page()
    await pg.goto(url)
    await pg.wait_for_selector("#cover.is-ready")
    cover = await pg.evaluate(JS, "cover")
    cover["low"] += await measure_gradients(pg, cover.pop("sample"))
    await pg.click("#open-invitation")
    await pg.wait_for_timeout(500)
    await pg.click("#gift-toggle")
    await pg.mouse.move(0, 0)  # no hover state on the toggle while measuring
    await pg.wait_for_timeout(600)
    page = await pg.evaluate(JS, "desktop" if w >= 1024 else "phone")
    page["low"] += await measure_gradients(pg, page.pop("sample"))
    print(f"\n=== {w}x{h} ===")
    print("cover:", json.dumps(cover, indent=1, ensure_ascii=False))
    print("invitation:", json.dumps(page, indent=1, ensure_ascii=False))
    if tab_stops:
        # keyboard: tab from the top of the page, make sure focus is visible
        await pg.evaluate("window.scrollTo(0, 0); document.querySelector('.skip-link').focus(); document.activeElement.blur()")
        stops = []
        for _ in range(tab_stops):
            await pg.keyboard.press("Tab")
            stops.append(await pg.evaluate("""(() => { const e = document.activeElement; const cs = getComputedStyle(e);
                const ring = cs.outlineStyle !== 'none' ? 'outline' : (cs.boxShadow !== 'none' ? 'box-shadow' : 'NONE');
                return ((e.id && '#' + e.id) || (e.getAttribute('class') || e.tagName).split(' ')[0]) + (e.textContent.trim() ? ' "' + e.textContent.trim().slice(0, 20) + '"' : '') + ' focus=' + ring; })()"""))
        print("tab order:", *stops, sep="\n  ")
    await ctx.close()
    return len(cover["issues"]) + len(cover["low"]) + len(page["issues"]) + len(page["low"])


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/?to=Pujo"
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
        problems = await audit(b, url, 390, 844, 25)
        problems += await audit(b, url, 1440, 900, 0)
        await b.close()
    print(f"\n{problems} finding(s)")
    sys.exit(1 if problems else 0)


asyncio.run(main())
