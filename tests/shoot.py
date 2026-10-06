"""
Visual smoke test: screenshots the cover, the opened page and the full page
(plus the event ticket and the gallery grid) at several viewports, and prints
layout facts, console errors and failed requests.

    python3 tests/shoot.py [base_url] [out_dir] [--widths 390,1440] [--query "?to=Pujo"]

Set PW_CHROMIUM to a Chromium binary if Playwright's own browser isn't installed.
"""
import argparse
import asyncio
import os

from playwright.async_api import async_playwright

VIEWPORTS = {
    360: (360, 780), 390: (390, 844), 430: (430, 932),
    768: (768, 1024), 1024: (1024, 768), 1440: (1440, 900),
}

# Layout facts worth eyeballing after a design change
FACTS = """(() => {
  const grid = document.querySelector('#gallery-grid');
  const track = document.querySelector('.chips__track');
  const cols = grid ? getComputedStyle(grid).gridTemplateColumns.split(' ').length : 0;
  const variants = [...document.querySelectorAll('.gallery__item')].map(li => li.className.match(/--(\\w+)/)[1][0]).join('');
  const chipsFit = track ? track.scrollWidth <= track.clientWidth && [...track.querySelectorAll('.chip')].every(c => { const r = c.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth; }) : false;
  const relation = (a, b) => {
    const x = document.querySelector(a)?.getBoundingClientRect(), y = document.querySelector(b)?.getBoundingClientRect();
    if (!x || !y) return 'missing';
    if (x.right <= y.left + 1 || y.right <= x.left + 1) return 'side by side';
    if (x.bottom <= y.top + 1 || y.bottom <= x.top + 1) return 'stacked';
    return 'overlaid';
  };
  return `gallery ${cols} cols [${variants}] · chips fit: ${chipsFit ? 'yes' : 'NO'} · hero names/photo ${relation('.hero__content', '.hero__media')} · couple ${relation('#groom', '#bride')} · closing ${relation('.closing__figure', '.closing__body')}`;
})()"""


async def shoot(base, out, widths, query, full):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
        for w in widths:
            vw, vh = VIEWPORTS.get(w, (w, 900))
            mobile = w < 768
            ctx = await browser.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=1,
                                            is_mobile=mobile, has_touch=mobile)
            page = await ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") else None)
            page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
            page.on("requestfailed", lambda r: errors.append(f"requestfailed: {r.url} {r.failure}"))
            page.on("response", lambda r: errors.append(f"HTTP {r.status}: {r.url}") if r.status >= 400 else None)
            await page.goto(base + query, wait_until="networkidle")
            await page.wait_for_timeout(2800)  # cover entrance: sheet rises, names letter by letter
            await page.screenshot(path=f"{out}/{w}-cover.png")
            cover_split = await page.evaluate("""(() => { const p = document.querySelector('.cover__photo').getBoundingClientRect(),
                s = document.querySelector('.cover__sheet').getBoundingClientRect();
                return s.left >= p.right - 40 ? 'photo left / sheet right' : 'photo top / sheet below'; })()""")
            guest = await page.text_content(".cover__guestname")
            await page.click("#open-invitation")
            await page.wait_for_timeout(2200)
            await page.screenshot(path=f"{out}/{w}-opened.png")
            if full:
                # Trigger every reveal by scrolling through the page
                height = await page.evaluate("document.documentElement.scrollHeight")
                y = 0
                while y < height:
                    await page.evaluate(f"window.scrollTo(0, {y})")
                    await page.wait_for_timeout(120)
                    y += vh // 2
                    height = await page.evaluate("document.documentElement.scrollHeight")
                await page.wait_for_timeout(1500)
                for sel, name in (("#event-list", "ticket"), ("#gallery-grid", "gallery")):
                    el = page.locator(sel)
                    if await el.count():
                        await el.screenshot(path=f"{out}/{w}-{name}.png")
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(400)
                await page.screenshot(path=f"{out}/{w}-full.png", full_page=True)
            overflow = await page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            print(f"[{w}] horizontal overflow: {overflow}px; page height {await page.evaluate('document.documentElement.scrollHeight')}")
            print(f"[{w}] cover: {cover_split}; guest \"{guest.strip()}\" · {await page.evaluate(FACTS)}")
            for e in errors:
                print(f"[{w}] {e}")
            await ctx.close()
        await browser.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base", nargs="?", default="http://127.0.0.1:8080/")
    ap.add_argument("out", nargs="?", default="/tmp/shots")
    ap.add_argument("--widths", default="390")
    ap.add_argument("--query", default="?to=Pujo+%26+Partner")
    ap.add_argument("--no-full", action="store_true")
    a = ap.parse_args()
    asyncio.run(shoot(a.base, a.out, [int(x) for x in a.widths.split(",")], a.query, not a.no_full))
