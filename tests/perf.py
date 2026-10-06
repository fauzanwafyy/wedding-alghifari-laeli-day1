"""
Transfer-size budget: what a phone (390px, DPR 3) and a desktop (1440px, DPR 1)
download before and after opening the invitation, plus LCP and CLS (local server,
so the timings are only a relative indicator).

    python3 tests/perf.py [url]          # default http://127.0.0.1:8080/?to=Pujo

Set PW_CHROMIUM to a Chromium binary if Playwright's own browser isn't installed.
"""
import asyncio
import os
import sys
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/?to=Pujo"
_u = urlsplit(URL)
ORIGIN = f"{_u.scheme}://{_u.netloc}{_u.path.rsplit('/', 1)[0]}/"


async def run(w, h, mobile):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
        ctx = await b.new_context(viewport={"width": w, "height": h}, device_scale_factor=3 if mobile else 1, is_mobile=mobile)
        pg = await ctx.new_page()
        sizes = {}

        async def on_resp(r):
            try:
                body = await r.body()
                sizes[r.url.replace(ORIGIN, "")] = len(body)
            except Exception:
                pass
        pg.on("response", lambda r: asyncio.ensure_future(on_resp(r)))
        await pg.goto(URL, wait_until="networkidle")
        await pg.wait_for_timeout(800)
        before = dict(sizes)
        lcp = await pg.evaluate("""new Promise(res => { new PerformanceObserver(l => { const e = l.getEntries(); res(Math.round(e[e.length-1].startTime)); }).observe({type:'largest-contentful-paint', buffered:true}); setTimeout(()=>res(-1), 2000); })""")
        cls = await pg.evaluate("""new Promise(res => { let v=0; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) v += e.value; }).observe({type:'layout-shift', buffered:true}); setTimeout(()=>res(v), 500); })""")
        await pg.click("#open-invitation")
        await pg.wait_for_timeout(2500)
        after = {k: v for k, v in sizes.items() if k not in before}

        def kb(d):
            return sum(d.values()) / 1024
        fonts = {k: v for k, v in before.items() if k.endswith(".woff2")}
        print(f"\n=== {w}x{h} dpr={'3' if mobile else '1'} ===")
        print(f"Before opening: {len(before)} requests, {kb(before):.0f} KB (fonts {kb(fonts):.0f} KB)  | LCP {lcp} ms (local)  | CLS {cls:.3f}")
        for k, v in sorted(before.items(), key=lambda x: -x[1])[:8]:
            print(f"   {v/1024:7.1f} KB  {k}")
        audio = {k: v for k, v in after.items() if k.endswith(".mp3")}
        print(f"After opening (first screen): +{len(after)} requests, {kb(after) - kb(audio):.0f} KB (+ music {kb(audio):.0f} KB streamed)")
        for k, v in sorted(after.items(), key=lambda x: -x[1])[:5]:
            print(f"   {v/1024:7.1f} KB  {k}")
        await b.close()

asyncio.run(run(390, 844, True))
asyncio.run(run(1440, 900, False))
