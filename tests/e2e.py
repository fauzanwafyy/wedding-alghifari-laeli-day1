"""
End-to-end tests: real browser (Playwright/Chromium) + the Apps Script emulator.

    node tests/gas-emulator.mjs 8787 &            # backend emulator
    python3 tests/e2e.py                          # serves a test copy of the site itself

The test copy points rsvp.apiUrl at a fake script.google.com URL; requests to it
are routed to the emulator, so the real frontend code talks to the real Code.gs logic.
"""
import asyncio
import functools
import http.server
import json
import os
import re
import shutil
import sys
import threading
import urllib.request

from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = "/tmp/claude-0/site-test"
SITE_PORT = 8091
EMU = "http://127.0.0.1:8787"
FAKE_API = "https://script.google.com/macros/s/TEST_DEPLOYMENT/exec"
# Day 1 shares the Day 2 spreadsheet; its RSVPs live in their own tab.
DAY1_TAB = "/__sheet?name=RSVP%20Day%201"
DAY2_TAB = "/__sheet?name=RSVP"
SHOTS = "/tmp/claude-0/e2e"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))


def emu(path):
    with urllib.request.urlopen(EMU + path) as r:
        return json.loads(r.read() or b"{}")


def prepare_site():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    shutil.copytree(ROOT, TEST_DIR, ignore=shutil.ignore_patterns(".git", "tests", "node_modules"))
    cfg = os.path.join(TEST_DIR, "js", "config.js")
    s = open(cfg, encoding="utf8").read()
    s, n = re.subn(r'apiUrl:\s*"[^"]*"', f'apiUrl: "{FAKE_API}"', s, count=1)
    assert n == 1, "rsvp.apiUrl not found in config.js"
    open(cfg, "w", encoding="utf8").write(s)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    handler = functools.partial(Quiet, directory=TEST_DIR)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", SITE_PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


async def route_api(route):
    req = route.request
    tail = req.url[len(FAKE_API):]
    try:
        resp = await route.fetch(url=EMU + "/exec" + tail)
        await route.fulfill(response=resp)
    except Exception:
        # The page/context was closed while a background request (wishes polling)
        # was in flight. Nothing to assert on; ignore.
        pass


async def new_page(browser, query="", w=390, h=844, reduced=False, perms=None):
    ctx = await browser.new_context(viewport={"width": w, "height": h}, is_mobile=w < 768, has_touch=w < 768,
                                    reduced_motion="reduce" if reduced else "no-preference",
                                    permissions=perms or [])
    page = await ctx.new_page()
    page.errors = []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.on("console", lambda m: page.errors.append(m.text) if m.type == "error" else None)
    await page.route(FAKE_API + "*", route_api)
    await page.route(FAKE_API, route_api)
    return ctx, page


async def open_invitation(page, query=""):
    await page.goto(f"http://127.0.0.1:{SITE_PORT}/{query}", wait_until="domcontentloaded")
    await page.wait_for_selector("#cover.is-ready")
    await page.click("#open-invitation")
    await page.wait_for_function("document.documentElement.classList.contains('is-open')")


async def main():
    os.makedirs(SHOTS, exist_ok=True)
    srv = prepare_site()
    emu("/__reset")
    async with async_playwright() as p:
        b = await p.chromium.launch()

        # ---------- Guest personalisation ----------
        cases = [
            ("", "Tamu Undangan"),
            ("?to=Pujo", "Pujo"),
            ("?to=Pujo+%26+Partner", "Pujo & Partner"),
            ("?to=fauzan-wafi", "Fauzan Wafi & Partner"),
            ("?to=budi-santoso", "Budi Santoso"),
            ("?to=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E", "<img src=x onerror=alert(1)>"),
        ]
        for q, expected in cases:
            ctx, page = await new_page(b)
            dialogs = []
            page.on("dialog", lambda d: (dialogs.append(d.message), asyncio.ensure_future(d.dismiss())))
            await page.goto(f"http://127.0.0.1:{SITE_PORT}/{q}")
            await page.wait_for_selector("#cover.is-ready")
            txt = await page.text_content(".cover__guestname span")
            check(f"guest {q or '(none)'} → '{expected}'", txt == expected, txt)
            if "img" in q:
                imgs = await page.evaluate("document.querySelectorAll('.cover__guestname img').length")
                check("XSS payload rendered as text (no element, no alert)", imgs == 0 and not dialogs)
            await ctx.close()

        long_name = "Bapak Haji Muhammad Abdurrahman Wahid Al-Fatih Kusumanegara beserta Keluarga Besar"
        ctx, page = await new_page(b, w=360, h=780)
        await page.goto(f"http://127.0.0.1:{SITE_PORT}/?to={urllib.request.quote(long_name)}")
        await page.wait_for_selector("#cover.is-ready")
        await page.wait_for_timeout(1500)
        txt = await page.text_content(".cover__guestname span")
        overflow = await page.evaluate("document.querySelector('.cover__content').scrollWidth - document.querySelector('.cover__content').clientWidth")
        check("long guest name truncated with ellipsis", txt.endswith("…") and len(txt) <= 61, txt)
        check("long guest name causes no horizontal overflow (360px)", overflow <= 0, str(overflow))
        await page.screenshot(path=f"{SHOTS}/long-name-360.png")
        await ctx.close()

        # ---------- Opening, scroll lock, music ----------
        ctx, page = await new_page(b, "?to=Pujo")
        await page.goto(f"http://127.0.0.1:{SITE_PORT}/?to=Pujo")
        await page.wait_for_selector("#cover.is-ready")
        locked = await page.evaluate("getComputedStyle(document.body).overflow")
        check("scroll locked while cover is shown", locked == "hidden", locked)
        check("main is inert behind the cover", await page.evaluate("document.getElementById('main').inert"))
        check("music not started before interaction", await page.evaluate("document.getElementById('bg-music').paused"))
        await page.click("#open-invitation")
        await page.wait_for_function("document.documentElement.classList.contains('is-open')")
        await page.wait_for_timeout(1500)
        check("cover hidden after opening", await page.evaluate("document.getElementById('cover').hidden"))
        check("scroll unlocked after opening", await page.evaluate("getComputedStyle(document.body).overflow") != "hidden")
        await page.mouse.wheel(0, 1200)
        await page.wait_for_timeout(600)
        check("page actually scrolls after opening", await page.evaluate("window.scrollY") > 300)
        state = await page.get_attribute("#music-toggle", "data-state")
        check("music starts after Open click (playing or blocked handled)", state in ("playing", "blocked", "loading"), state)
        await page.click("#music-toggle")
        check("music toggle pauses", await page.get_attribute("#music-toggle", "data-state") == "paused")
        check("music aria-pressed false when paused", await page.get_attribute("#music-toggle", "aria-pressed") == "false")
        await page.click("#music-toggle")
        await page.wait_for_timeout(300)
        check("music toggle resumes", await page.get_attribute("#music-toggle", "data-state") in ("playing", "loading"))
        check("no console errors (normal flow)", not page.errors, "; ".join(page.errors))
        await ctx.close()

        # music unavailable
        ctx, page = await new_page(b)
        await page.route("**/wedding-song.mp3", lambda r: r.fulfill(status=404, body="nope"))
        await open_invitation(page)
        await page.wait_for_timeout(800)
        check("missing music file → toggle shows 'unavailable'", await page.get_attribute("#music-toggle", "data-state") == "unavailable")
        await ctx.close()

        # reduced motion
        ctx, page = await new_page(b, reduced=True)
        await page.goto(f"http://127.0.0.1:{SITE_PORT}/")
        await page.wait_for_selector("#cover.is-ready")
        await page.click("#open-invitation")
        await page.wait_for_timeout(100)
        check("reduced motion: opens instantly", await page.evaluate("document.getElementById('cover').hidden"))
        op = await page.evaluate("getComputedStyle(document.querySelector('#story [data-reveal]')).opacity")
        check("reduced motion: reveal content visible without animation", op == "1", op)
        await ctx.close()

        # ---------- Countdown ----------
        for when, expect in [
            ("2026-10-19T09:00:00+07:00", "counting:01:00:00:00"),
            ("2026-10-20T08:59:58+07:00", "counting:00:00:00:02"),
            ("2026-10-20T09:00:00+07:00", "today"),
            ("2026-10-20T20:59:00+07:00", "today"),
            ("2026-10-20T21:00:01+07:00", "after"),
        ]:
            ctx, page = await new_page(b)
            await page.clock.set_fixed_time(when)
            await page.goto(f"http://127.0.0.1:{SITE_PORT}/")
            await page.wait_for_selector("#cover.is-ready")
            state = await page.get_attribute("#countdown", "data-state")
            if expect.startswith("counting"):
                nums = await page.eval_on_selector_all(".timer__num", "els => els.map(e => e.textContent).join(':')")
                got = f"{state}:{nums}"
            else:
                got = state
                title = await page.text_content(".timer-done__title")
                check(f"countdown {expect} message shown", bool(title) and await page.is_visible(".timer-done") is not None, title)
            check(f"countdown at {when} → {expect}", got == expect, got)
            await ctx.close()

        # visitor in another timezone sees the same countdown
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, timezone_id="America/New_York")
        page = await ctx.new_page()
        await page.clock.set_fixed_time("2026-10-19T09:00:00+07:00")
        await page.goto(f"http://127.0.0.1:{SITE_PORT}/")
        await page.wait_for_selector("#cover.is-ready")
        nums = await page.eval_on_selector_all(".timer__num", "els => els.map(e => e.textContent).join(':')")
        check("countdown is timezone-independent (New York visitor)", nums == "01:00:00:00", nums)
        await ctx.close()

        # ---------- Links: maps + calendar ----------
        ctx, page = await new_page(b)
        await open_invitation(page)
        maps = await page.eval_on_selector_all("a[href^='https://goo.gl/maps']", "els => els.map(a => [a.href, a.target, a.rel])")
        check("all venue links open Google Maps in a new tab",
              maps and all(h == "https://goo.gl/maps/DwpyJcmFjXAfgyxz6" and t == "_blank" and "noopener" in r for h, t, r in maps), str(maps))
        cal = await page.get_attribute("#calendar-link", "href")
        check("calendar URL: Google Calendar template", cal.startswith("https://calendar.google.com/calendar/render?action=TEMPLATE"), cal[:80])
        check("calendar URL: Resepsi 20 Okt 09.00–21.00 WIB", "dates=20261020T020000Z%2F20261020T140000Z" in cal, cal)
        check("calendar URL: title/location/ctz", "Resepsi+Pernikahan+Alghifari" in cal and "Le+Villa+Resort+and+Conference" in cal and "Lembah+Nyiur" in cal and "ctz=Asia%2FJakarta" in cal, cal)
        check("calendar details 'Resepsi: 09.00 WIB – 21.00 WIB'", "Resepsi%3A+09.00+WIB+%E2%80%93+21.00+WIB" in cal, cal)
        check("calendar opens in new tab", await page.get_attribute("#calendar-link", "target") == "_blank")

        # ---------- Content corrections ----------
        titles = await page.eval_on_selector_all(".ticket__title", "els => els.map(e => e.textContent)")
        check("one event ticket: Resepsi", titles == ["Resepsi"], str(titles))
        facts = await page.eval_on_selector_all(".ticket__facts li", "els => els.map(e => e.textContent.replace(/\\s+/g, ' ').trim())")
        check("ticket date Selasa, 20 Oktober 2026", facts and facts[0] == "Selasa, 20 Oktober 2026", str(facts))
        check("ticket time 09.00 – 21.00 WIB", len(facts) > 1 and facts[1] == "09.00 – 21.00 WIB", str(facts))
        check("ticket venue + full address", len(facts) > 2 and "Le Villa Resort and Conference" in facts[2] and "Jl. Lembah Nyiur No.46, Kopo, Kec. Cisarua, Kabupaten Bogor, Jawa Barat 16750" in facts[2], str(facts))
        stamp = await page.text_content(".ticket__stamp")
        check("ticket stamp shows the date", stamp == "20 Okt2026", stamp)
        ev_cals = await page.eval_on_selector_all(".ticket__actions a[href*='calendar.google.com']", "els => els.map(a => a.href)")
        check("ticket has its own calendar link", len(ev_cals) == 1, str(len(ev_cals)))
        if ev_cals:
            check("ticket calendar entry 09.00–21.00 WIB", "dates=20261020T020000Z%2F20261020T140000Z" in ev_cals[0] and "text=Resepsi" in ev_cals[0], ev_cals[0])
        tags = await page.eval_on_selector_all(".person__tag", "els => els.map(e => e.textContent.trim())")
        check("person tags", tags == ["Mempelai Pria", "Mempelai Wanita"], str(tags))
        body = await page.evaluate("document.body.innerText")
        check("no Akad Nikah on the Day 1 page", "Akad" not in body)
        chips = await page.eval_on_selector_all(".chip", "els => els.map(e => e.textContent)")
        check("nav chips", chips == ["Mempelai", "Acara", "Cerita", "Galeri", "RSVP", "Hadiah"], str(chips))
        cover_src = await page.evaluate("[...document.querySelectorAll('[data-slot=cover] img')].map(i => i.currentSrc || i.src).join(' ')")
        check("cover uses cover/cover-*", "/cover/cover-" in cover_src, cover_src[:120])
        names = await page.evaluate("[document.getElementById('cover-title').getAttribute('aria-label'), document.getElementById('hero-title').getAttribute('aria-label')]")
        check("split names keep an accessible label", names == ["Alghifari dan Laeli", "Alghifari dan Laeli"], str(names))
        fonts = await page.evaluate("[...new Set([...document.querySelectorAll('.hero__names, .cover__names, .closing__names')].map(e => getComputedStyle(e).fontFamily.split(',')[0].replace(/\"/g, '')))]")
        check("couple names use Marcellus (no script font)", fonts == ["Marcellus"], str(fonts))

        # ---------- Verse ----------
        v = await page.evaluate("""() => { const sec = document.querySelector('#verse'), r = sec.getBoundingClientRect();
          return { cx: Math.round(r.left + r.width / 2 - innerWidth / 2), align: getComputedStyle(sec).textAlign, src: document.querySelector('.verse__src').textContent }; }""")
        check("verse card centred with QS. Ar-Rum : 21", abs(v["cx"]) <= 1 and v["align"] == "center" and v["src"] == "QS. Ar-Rum : 21", str(v))

        # ---------- Gift ----------
        await ctx.close()
        ctx, page = await new_page(b, perms=["clipboard-read", "clipboard-write"])
        await open_invitation(page)
        await page.locator("#gift").scroll_into_view_if_needed()
        check("gift panel collapsed initially", await page.get_attribute("#gift-toggle", "aria-expanded") == "false")
        await page.click("#gift-toggle")
        await page.wait_for_timeout(800)
        check("gift panel opens (aria-expanded)", await page.get_attribute("#gift-toggle", "aria-expanded") == "true")
        n = await page.locator(".account").count()
        check("two bank accounts rendered", n == 2, str(n))
        groups = await page.eval_on_selector_all(".account__number", "els => els.map(e => [...e.querySelectorAll('.account__group')].map(g => g.textContent).join(' '))")
        check("groom account BCA 7361529751 shown as 736 152 9751", groups and groups[0] == "736 152 9751", str(groups))
        check("bride account BCA 7361504589 shown as 736 150 4589", len(groups) > 1 and groups[1] == "736 150 4589", str(groups))
        raw_text = await page.eval_on_selector_all(".account__number", "els => els.map(e => e.textContent)")
        check("number text has no spaces (manual select-copy gives raw digits)", raw_text == ["7361529751", "7361504589"], str(raw_text))
        # layout widths (cards may still be mid-entrance, which tilts their boxes)
        widths = await page.eval_on_selector_all(".account__digit", "els => [...new Set(els.map(e => getComputedStyle(e).width))]")
        check("all account digits have equal width (tabular)", len(widths) == 1, str(widths))
        style = await page.eval_on_selector(".account__number", "e => { const s = getComputedStyle(e); return [s.fontFamily.split(',')[0], s.fontWeight, s.fontVariantNumeric, s.color]; }")
        check("account number style: Manrope 600, lining+tabular, white", style[0].strip('\"') == "Manrope" and style[1] == "600" and "lining-nums" in style[2] and "tabular-nums" in style[2] and style[3] == "rgb(255, 255, 255)", str(style))
        holders = await page.eval_on_selector_all(".account__holder", "els => els.map(e => e.textContent.replace('a.n. ', '').trim())")
        check("account holders", holders == ["MOH AGIL ALGHIFARI", "LAELI LUSPITA SARI"], str(holders))
        expected = await page.evaluate("WEDDING_CONFIG.gift.accounts.map(a => a.accountNumber)")
        check("config account numbers are 7361529751 / 7361504589", expected == ["7361529751", "7361504589"], str(expected))
        for i, want in enumerate(expected):
            await page.evaluate("navigator.clipboard.writeText('')")
            await page.click(f".account__copy >> nth={i}")
            await page.wait_for_timeout(300)
            clip = await page.evaluate("navigator.clipboard.readText()")
            check(f"copy button {i + 1} copies exactly {want} (no spaces)", clip == want and not any(c.isspace() for c in clip), repr(clip))
        check("copy shows toast", "disalin" in (await page.text_content("#toast")) and await page.evaluate("document.getElementById('toast').classList.contains('is-visible')"))
        await page.screenshot(path=f"{SHOTS}/gift-open.png")
        await ctx.close()

        # ---------- Gallery lightbox ----------
        ctx, page = await new_page(b)
        await open_invitation(page)
        await page.locator("#gallery").scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        items = await page.locator(".gallery__btn").count()
        check("gallery renders 8 photos", items == 8, str(items))
        seq = await page.evaluate("[...document.querySelectorAll('#gallery-grid > li')].map(li => li.className.replace('gallery__item gallery__item--', '')[0]).join('')")
        check("gallery: feature + 6 tiles + landscape", seq == "fttttttw", seq)
        geo = await page.evaluate("""() => { const g = document.querySelector('#gallery-grid'), s = getComputedStyle(g), sec = document.querySelector('#gallery').getBoundingClientRect();
          const first = g.getBoundingClientRect(), last = first; // the grid box (tiles may still be scaling in)
          return { gap: [s.columnGap, s.rowGap], cols: s.gridTemplateColumns.split(' ').length, firstLeft: Math.round(first.left - sec.left), rightGap: Math.round(sec.right - last.right),
                   scroll: g.scrollWidth - g.clientWidth, ox: s.overflowX, dims: [...g.querySelectorAll('img')].every(i => i.getAttribute('width') && i.getAttribute('height')) }; }""")
        check("gallery is a normal 2-column grid on phones (no sideways swipe)", geo["cols"] == 2 and geo["scroll"] <= 0 and geo["ox"] == "visible", str(geo))
        check("gallery gaps equal, symmetric gutters (390px)", geo["gap"][0] == geo["gap"][1] and abs(geo["firstLeft"] - geo["rightGap"]) <= 1 and 24 <= geo["firstLeft"] <= 26, str(geo))
        check("gallery images keep width/height (no layout shift)", geo["dims"])
        await page.click(".gallery__btn[aria-label^='Perbesar foto 3 dari']")
        await page.wait_for_timeout(500)
        check("lightbox opens", await page.evaluate("document.getElementById('lightbox').open"))
        check("lightbox counter 03", await page.text_content("#lb-index") == "03")
        lb = await page.evaluate("""() => { const d = document.getElementById('lightbox'), bar = d.querySelector('.lightbox__bar');
          const img = d.querySelector('.lightbox__stage img');
          return { caption: !!d.querySelector('#lb-caption, .lightbox__caption'), barKids: [...bar.children].map(c => c.className).join(','), count: d.querySelector('.lightbox__count').textContent.replace(/\\s+/g, ' ').trim(), alt: img && img.alt }; }""")
        check("lightbox shows no photo caption (counter only)", not lb["caption"] and lb["barKids"] == "lightbox__count", str(lb))
        check("lightbox image keeps its alt text for screen readers", bool(lb["alt"]), str(lb))
        await page.keyboard.press("ArrowRight")
        check("ArrowRight → 04", await page.text_content("#lb-index") == "04")
        await page.click(".lightbox__nav--prev")
        check("prev button → 03", await page.text_content("#lb-index") == "03")
        await page.screenshot(path=f"{SHOTS}/lightbox.png")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(300)
        check("Escape closes lightbox", not await page.evaluate("document.getElementById('lightbox').open"))
        focused = await page.evaluate("document.activeElement.classList.contains('gallery__btn')")
        check("focus returns to the opening thumbnail", focused)
        await page.locator("#gallery").scroll_into_view_if_needed()
        await page.evaluate("window.scrollBy(0, 200)")
        await page.wait_for_timeout(600)
        active = await page.evaluate("document.querySelector('.chip.is-active')?.dataset.nav")
        check("nav chip highlights current section (gallery)", active == "gallery", str(active))
        await ctx.close()

        # missing image → graceful placeholder
        ctx, page = await new_page(b)
        await page.route(re.compile(r".*/gallery-03-.*"), lambda r: r.fulfill(status=404, body=""))
        await open_invitation(page)
        await page.locator("#gallery").scroll_into_view_if_needed()
        await page.wait_for_timeout(1200)
        broken = await page.locator(".gallery__grid .pic.is-broken").count()
        check("missing image shows placeholder with description", broken == 1, str(broken))
        await ctx.close()

        # ---------- Wishes ----------
        emu("/__reset")
        ctx, page = await new_page(b)
        await open_invitation(page)
        await page.locator("#wishes").scroll_into_view_if_needed()
        await page.wait_for_selector("#wishes-state[data-kind='empty']", timeout=8000)
        check("wishes: empty state", True)
        await page.screenshot(path=f"{SHOTS}/wishes-empty.png")
        await ctx.close()

        emu("/__seed?n=12&event=day1")
        ctx, page = await new_page(b)
        await open_invitation(page)
        await page.locator("#wishes").scroll_into_view_if_needed()
        await page.wait_for_selector(".wish", timeout=8000)
        shown = await page.locator(".wish").count()
        check("wishes: first page shows 8", shown == 8, str(shown))
        more = await page.text_content("#wishes-more")
        check("wishes: 'show more (4)'", "(4)" in more, more)
        await page.click("#wishes-more")
        check("wishes: show more reveals all 12", await page.locator(".wish").count() == 12)
        html = await page.inner_html("#wishes-list")
        check("wishes: no attendance / count / timestamp exposed", "Hadir" not in html and "seed" not in html.lower().replace("selamat", ""))
        check("wishes count label", "12 ucapan" in (await page.text_content("#wishes-count")))
        await ctx.close()

        # wishes error state
        ctx, page = await new_page(b)
        await page.unroute(FAKE_API + "*")
        await page.route(FAKE_API + "*", lambda r: r.abort())
        await open_invitation(page)
        await page.locator("#wishes").scroll_into_view_if_needed()
        await page.wait_for_selector("#wishes-state[data-kind='error']", timeout=8000)
        check("wishes: error state with retry button", await page.locator("#wishes-state button").count() == 1)
        await ctx.close()

        # ---------- RSVP ----------
        emu("/__reset")
        ctx, page = await new_page(b)
        await open_invitation(page)
        await page.locator("#rsvp").scroll_into_view_if_needed()
        await page.click("#rsvp-submit")
        err_name = await page.text_content("#rsvp-guestName-error")
        err_att = await page.text_content("#rsvp-attendance-error")
        check("RSVP validation: name required", "nama" in err_name.lower(), err_name)
        check("RSVP validation: attendance required", "kehadiran" in err_att.lower(), err_att)
        check("RSVP validation: focus moves to first invalid field", await page.evaluate("document.activeElement.id") == "rsvp-name")
        check("RSVP validation: nothing sent", len(emu(DAY1_TAB)) <= 1)
        await page.screenshot(path=f"{SHOTS}/rsvp-validation.png", full_page=False)

        await page.fill("#rsvp-name", "Pujo Santoso")
        await page.click("label.choice__opt:has(input[value=attending])")
        check("guest count shown when attending", await page.is_visible("#guest-count-field"))
        await page.click("[data-step='1']")
        await page.click("[data-step='1']")
        await page.fill("#rsvp-message", "Barakallahu lakuma, semoga sakinah mawaddah warahmah.\nSelamat!")
        await page.click("#rsvp-submit")
        await page.wait_for_selector("#rsvp-success:not([hidden])", timeout=8000)
        check("RSVP success panel shown", True)
        rows = emu(DAY1_TAB)
        check("RSVP creates exactly one new sheet row", len(rows) == 2, str(len(rows)))
        if len(rows) == 2:
            r = rows[1]
            check("row: slug / name / attendance / count / message", r[1] == "umum" and r[2] == "Pujo Santoso" and r[3] == "Hadir" and r[4] == 3 and r[5].startswith("Barakallahu"), str(r))
        await page.wait_for_timeout(500)
        first = await page.text_content(".wish .wish__name")
        check("new wish appears in Wedding Wishes immediately", first == "Pujo Santoso", first)
        await page.screenshot(path=f"{SHOTS}/rsvp-success.png")

        # duplicate: send again with same content
        await page.click("#rsvp-again")
        await page.fill("#rsvp-name", "Pujo Santoso")
        await page.click("label.choice__opt:has(input[value=attending])")
        await page.fill("#rsvp-count", "3")
        await page.fill("#rsvp-message", "Barakallahu lakuma, semoga sakinah mawaddah warahmah.\nSelamat!")
        await page.click("#rsvp-submit")
        await page.wait_for_selector("#rsvp-success:not([hidden])", timeout=8000)
        txt = await page.text_content("#rsvp-success-text")
        check("duplicate submission recognised, no new row", "sebelumnya" in txt and len(emu(DAY1_TAB)) == 2, txt)
        keys = await page.evaluate("Object.keys(localStorage)")
        check("RSVP memory uses the Day 1 key (separate from Day 2)", "awl-day1:rsvp" in keys and "awl:rsvp" not in keys, str(keys))
        await ctx.close()

        # network failure then retry (same submissionId → one row)
        emu("/__reset")
        ctx, page = await new_page(b, "?to=Ade+%26+Partner")
        await open_invitation(page, "?to=Ade+%26+Partner")
        await page.locator("#rsvp").scroll_into_view_if_needed()
        check("RSVP name pre-filled from guest link", await page.input_value("#rsvp-name") == "Ade")
        await page.click("label.choice__opt:has(input[value=not_attending])")
        check("guest count hidden when not attending", not await page.is_visible("#guest-count-field"))
        await page.fill("#rsvp-message", "Mohon maaf belum bisa hadir. Selamat!")
        await page.unroute(FAKE_API + "*")
        await page.unroute(FAKE_API)
        fail_mode = {"on": True}

        async def flaky(route):
            if fail_mode["on"] and route.request.method == "POST":
                # Let the request reach the server but drop the response (worst case)
                await route.fetch(url=EMU + "/exec")
                await route.abort()
            else:
                await route_api(route)
        await page.route(FAKE_API + "*", flaky)
        await page.route(FAKE_API, flaky)
        await page.click("#rsvp-submit")
        await page.wait_for_selector("#rsvp-status:not([hidden])")
        st = await page.text_content("#rsvp-status")
        check("network failure → friendly error, form kept", "Koneksi" in st and await page.input_value("#rsvp-message") != "", st)
        check("button re-enabled after failure", await page.is_enabled("#rsvp-submit"))
        fail_mode["on"] = False
        await page.click("#rsvp-submit")
        await page.wait_for_selector("#rsvp-success:not([hidden])", timeout=8000)
        rows = emu(DAY1_TAB)
        check("retry after lost response does NOT duplicate the row", len(rows) == 2, str(len(rows)))
        check("row: not attending → count 0, slug from link", rows[-1][3] == "Tidak Hadir" and rows[-1][4] == 0 and rows[-1][1] == "ade-partner", str(rows[-1]))
        await ctx.close()

        # server 500 / rejected / slow
        for mode, expect in [("fail500", "kendala"), ("reject", "Simulasi")]:
            emu(f"/__mode?m={mode}")
            ctx, page = await new_page(b)
            await open_invitation(page)
            await page.locator("#rsvp").scroll_into_view_if_needed()
            await page.fill("#rsvp-name", "Tes Server")
            await page.click("label.choice__opt:has(input[value=not_attending])")
            await page.click("#rsvp-submit")
            await page.wait_for_selector("#rsvp-status:not([hidden])", timeout=8000)
            st = await page.text_content("#rsvp-status")
            check(f"Apps Script failure ({mode}) → error message", expect in st, st)
            await ctx.close()

        emu("/__mode?m=slow")
        ctx, page = await new_page(b)
        await open_invitation(page)
        await page.locator("#rsvp").scroll_into_view_if_needed()
        await page.fill("#rsvp-name", "Tes Lambat")
        await page.click("label.choice__opt:has(input[value=not_attending])")
        await page.click("#rsvp-submit")
        await page.wait_for_timeout(600)
        busy = await page.get_attribute("#rsvp-submit", "aria-busy")
        label = await page.text_content("#rsvp-submit .btn__label")
        check("slow network → loading state (busy + 'Mengirim…')", busy == "true" and "Mengirim" in label, f"{busy} {label}")
        check("double submit blocked while sending", await page.is_disabled("#rsvp-submit"))
        await page.screenshot(path=f"{SHOTS}/rsvp-loading.png")
        await page.wait_for_selector("#rsvp-success:not([hidden])", timeout=12000)
        check("slow network eventually succeeds", True)
        emu("/__mode?m=normal")
        await ctx.close()

        # Day 1 rows land in their own tab; the Day 2 tab is never touched
        tabs = emu("/__sheets")
        check("shared spreadsheet: Day 1 writes only to 'RSVP Day 1'", "RSVP Day 1" in tabs and "RSVP" not in tabs, str(tabs))

        # live script not updated yet (no `event` support) → nothing is filed in the Day 2 tab
        emu("/__reset")
        emu("/__seed?n=2")  # Day 2 wishes already in the old script
        emu("/__mode?m=legacy")
        ctx, page = await new_page(b)
        await open_invitation(page)
        await page.locator("#wishes").scroll_into_view_if_needed()
        await page.wait_for_selector("#wishes-state[data-kind='offline']", timeout=8000)
        check("old script: Day 2 wishes are not shown on Day 1", await page.locator(".wish").count() == 0)
        await page.locator("#rsvp").scroll_into_view_if_needed()
        await page.fill("#rsvp-name", "Tes Skrip Lama")
        await page.click("label.choice__opt:has(input[value=not_attending])")
        await page.click("#rsvp-submit")
        await page.wait_for_selector("#rsvp-status:not([hidden])", timeout=8000)
        st = await page.text_content("#rsvp-status")
        check("old script: RSVP says 'sedang disiapkan'", "disiapkan" in st, st)
        check("old script: nothing written to the Day 2 tab", len(emu(DAY2_TAB)) == 3 and len(emu(DAY1_TAB)) == 0, f"{len(emu(DAY2_TAB))} {len(emu(DAY1_TAB))}")
        emu("/__mode?m=normal")
        await ctx.close()

        # ---------- responsive overflow sweep ----------
        for w, h in [(360, 780), (390, 844), (430, 932), (768, 1024), (1024, 768), (1440, 900)]:
            ctx, page = await new_page(b, "?to=Pujo+%26+Partner", w=w, h=h)
            await open_invitation(page, "?to=Pujo+%26+Partner")
            await page.click("#gift-toggle")
            ov = await page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(f"no horizontal overflow at {w}px", ov <= 0, str(ov))
            nav = await page.evaluate("(() => { const t = document.querySelector('.chips__track'); return [t.scrollWidth - t.clientWidth, [...t.querySelectorAll('.chip')].every(c => { const r = c.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth; })]; })()")
            check(f"all six nav chips visible without swiping at {w}px", nav[0] <= 0 and nav[1], str(nav))
            small = await page.evaluate("""[...document.querySelectorAll('button, a.btn, .chip, .stepper__btn, .account__copy, .link-arrow')]
                .filter(e => e.offsetParent && !e.closest('.lightbox')).map(e => ({ width: e.offsetWidth, height: e.offsetHeight }))
                .filter(r => r.width && (r.height < 44 || r.width < 44)).length""")
            check(f"touch targets ≥ 44px at {w}px", small == 0, str(small))
            check(f"no console errors at {w}px", not page.errors, "; ".join(page.errors))
            await ctx.close()

        await b.close()
    srv.shutdown()

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    asyncio.run(main())
