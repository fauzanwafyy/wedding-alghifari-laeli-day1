# Resepsi Pernikahan Alghifari & Laeli (Day 1)

Digital invitation to the wedding reception of **Moh Agil Alghifari & Laeli Luspitasari**:
**Resepsi** · Selasa, 20 Oktober 2026 · 09.00–21.00 WIB · Le Villa Resort and Conference,
Kopo, Cisarua, Bogor. Hosted by the groom's family.

Site address (GitHub Pages): <https://fauzanwafyy.github.io/wedding-alghifari-laeli-day1/>. The second day
(Rabu, 21 Oktober 2026) has its own invitation (Day 2):
<https://fauzanwafyy.github.io/wedding-alghifari-laeli/>.

A lightweight, mobile-first static site (GitHub Pages) with personalised guest links, live
countdown, Google Maps + Google Calendar, gallery, RSVP and wedding wishes stored in its own
Google Sheet through a Google Apps Script Web App. No framework, no build step.

**Design direction:** *Taman Pagi* (morning garden). See [`docs/DESIGN-DIRECTION.md`](docs/DESIGN-DIRECTION.md).

## Quick start

| I want to… | Read |
|---|---|
| Change names, times, bank details, guests | [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md) |
| Replace, add or remove photos | [`docs/PHOTO-REPLACEMENT-GUIDE.md`](docs/PHOTO-REPLACEMENT-GUIDE.md) |
| RSVP Google Sheet + Apps Script (Day 1's own sheet; setup, moderation, updates) | [`docs/GOOGLE-SHEETS.md`](docs/GOOGLE-SHEETS.md) |
| Publish / update GitHub Pages, custom domain | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |
| Generate personal guest links + WhatsApp text | open `generator.html` on the live site |

All wedding content lives in **`js/config.js`**.

## Guest links

```
https://<site>/?to=Pujo                 → "Pujo"
https://<site>/?to=Pujo+%26+Partner     → "Pujo & Partner"
https://<site>/?to=fauzan-wafi          → "Fauzan Wafi & Partner" (from GUESTS in config.js)
https://<site>/                         → "Tamu Undangan"
```

## Structure

```
├── index.html                 The invitation (static <head> for SEO/social previews)
├── 404.html                   Not-found page + /<slug> → ?to=<slug> redirect
├── generator.html             Guest-link & WhatsApp message generator (noindex)
├── css/
│   ├── main.css               Tokens, typography, components, animations (mobile-first)
│   ├── responsive.css         Small phones, tablet, desktop, landscape phones, reduced motion, print
│   └── fonts-local.css        Embedded fonts, used only when index.html is opened from a folder
├── js/
│   ├── config.js              ★ All editable content + guest list
│   ├── main.js                Boot: binds config to the page, opening cover, event ticket, story
│   ├── motion.js              Scroll reveals, letter-by-letter names, leaves, timeline, parallax, chip nav
│   ├── guest.js               ?to= personalisation (sanitised)
│   ├── countdown.js           Timezone-safe countdown (WIB) with progress rings
│   ├── calendar.js            Google Calendar "Save the Date" URLs (day + per event)
│   ├── api.js                 Apps Script client (no-preflight POST, timeouts)
│   ├── rsvp.js                RSVP form: validation, states, duplicate-safe retries
│   ├── wishes.js              Public wishes: lazy load, polling, pagination
│   ├── gallery.js             Photo grid + accessible lightbox
│   ├── gift.js                Bank cards + copy to clipboard
│   ├── music.js               Background music (starts on "Buka Undangan")
│   └── utils.js               DOM/format/image helpers
├── assets/
│   ├── images/{cover,groom,bride,story,gallery,meta}/   AVIF + WebP, responsive widths
│   ├── fonts/                 Marcellus + Manrope (WOFF2, self-hosted)
│   └── audio/wedding-song.mp3
├── google-apps-script/Code.gs RSVP backend (paste into Apps Script)
├── tools/optimize-images.py   Regenerate responsive images from a new photo
├── tests/                     Apps Script emulator + unit tests, Playwright e2e, a11y, screenshots, perf
└── docs/                      Design direction, deployment, Google Sheets, maintenance, photo guide
```

## Tech notes

- **Performance:** two font files preloaded (~38 KB together), the opening photo preloaded as
  AVIF (~59–187 KB depending on screen density) and the header photo fetched behind the cover so
  it is ready on opening; everything else lazy-loaded. Measured with `tests/perf.py`: about
  640 KB before opening on a 3× phone, 560 KB on a desktop. Music (`preload="none"`, ~740 KB)
  is only fetched after the guest taps *Buka Undangan*. No third-party scripts, no frameworks.
- **Accessibility:** semantic landmarks and headings, labelled form controls with inline
  errors, keyboard-operable lightbox (native `<dialog>`), visible focus, colour tokens chosen
  for WCAG AA (ratios noted in `css/main.css`), `prefers-reduced-motion` support (every
  animation off), `inert` content behind the cover. Check with `tests/a11y.py`.
- **Security:** no secrets in the frontend; all user text rendered with `textContent`;
  server-side validation, sanitisation, formula-injection guard, honeypot, rate limit.
- **Shared origin with Day 2:** both sites live on `fauzanwafyy.github.io`, so Day 1 keeps
  its own browser storage keys (`awl-day1:rsvp`, `awl-day1:music`, `awl-day1:generator`).
- **Browser support:** current Safari (iOS 15+), Chrome, Edge, Firefox, Samsung Internet.

## Credits

Photography: the couple's pre-wedding session. Music: *"Bernaung"* by Feby Putri, used as
background music for this private invitation. Fonts: Marcellus (Astigmatic) and Manrope
(Mikhail Sharanda), both SIL Open Font License.
