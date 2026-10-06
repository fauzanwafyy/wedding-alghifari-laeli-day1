# Photo Replacement Guide

How to swap any photo on the invitation without breaking the layout, the crops
or the page speed. Everything below uses the **real file names in this project**.

> Short version: make the web versions with `tools/optimize-images.py`, keep the
> same file name (or update the one line in `js/config.js`), adjust `position`
> if a face is cut off, then check the page on a phone.

---

## 1. Where every photo is used (current mapping)

All photo settings live in **`js/config.js`**. Apart from the share preview image
in the `<head>` of `index.html` (last row), the HTML never hard-codes a photo.

| Place on the page | Config key (`js/config.js`) | File base in the repo | Original source file | Widths | Shape |
|---|---|---|---|---|---|
| Opening cover (first screen, before "Buka Undangan"): top of the screen above the paper sheet on phones, left side on desktop | `images.cover` | `assets/images/cover/cover` | `cover/cover.jpg` | 640, 960, 1440 | 2:3 portrait |
| Header after opening: full-bleed behind the names on phones/tablets, in the garden arch on desktop | `images.hero` | `assets/images/cover/hero` | `cover/header.jpg` | 640, 960, 1440 | 2:3 portrait |
| Closing "Terima Kasih": full-bleed on phones/tablets, arch beside the text on desktop | `images.closing` | `assets/images/cover/closing` | `cover/footer.jpg` | 640, 960, 1440 | 2:3 portrait |
| Mempelai Pria portrait | `couple.groom.photo` | `assets/images/groom/groom` | `groom/groom.jpeg` | 480, 800, 1200 | 2:3 portrait (shown 4:5) |
| Mempelai Wanita portrait | `couple.bride.photo` | `assets/images/bride/bride` | `bride/bride.jpeg` | 480, 800, 1200 | 2:3 portrait (shown 4:5) |
| Our Story · 01 Pertemuan | `story[0].image` | `assets/images/story/story-01` | `cover/pertemuan.jpg` | 480, 800, 1200 | 2:3 portrait (shown 4:5) |
| Our Story · 02 Pendekatan | `story[1].image` | `assets/images/story/story-02` | `cover/pendekatan.jpg` | 480, 800, 1200 | 2:3 portrait (shown 4:5) |
| Our Story · 03 Lamaran | `story[2].image` | `assets/images/story/story-03` | `cover/lamaran.jpg` | 480, 800, 1200 | 2:3 portrait (shown 4:5) |
| Our Story · 04 Pernikahan | `story[3].image` | `assets/images/story/story-04` | `cover/pernikahan.jpg` | 480, 800, 1200 | 2:3 portrait (shown 4:5) |
| Gallery photos 1–7 | `gallery[0]` … `gallery[6]` | `assets/images/gallery/gallery-01` … `gallery-07` | `gallery/galeri (1).jpg` … `galeri (7).jpg` | 480, 800, 1600 | 2:3 portrait (photo 1 is the feature, see section 8) |
| Gallery photo 8 (landscape) | `gallery[7]` (`wide: true`) | `assets/images/gallery/gallery-08` | `gallery/galeri (8).jpg` | 800, 1600, 2400 | 3:2 landscape |
| Link preview (WhatsApp / social share) | `<meta property="og:image">` in `index.html` | `assets/images/meta/og-image.jpg` (single file) | made from the cover photo, with the names, date and venue set on the right | 1200 × 630 | 1.91:1 |

Each "file base" exists as an **AVIF and a WebP for every width**, for example
`assets/images/story/story-02-480.avif`, `story-02-480.webp`, `story-02-800.avif`
… `story-02-1200.webp`. The browser picks the smallest one that looks sharp on
the visitor's screen.

The original photos (`cover.jpg`, `header.jpg`, `galeri (1).jpg` …) are **not**
stored in the repository; only the optimized web versions are. Keep the originals
somewhere safe (e.g. Google Drive).

---

## 2. Before you start: what a good replacement photo looks like

- **Orientation.** Use the same shape as the photo you replace (see the table).
  Portrait 2:3 for almost everything; landscape 3:2 only for a `wide` gallery photo.
  Another ratio still works (the page crops it), but more of the photo is cut off.
- **Resolution.** At least **1600 px on the long side** for gallery/story/couple
  photos and **2400 px** for cover, hero and closing. Larger is fine; the tool
  scales it down.
- **Faces.** Keep faces away from the extreme top and bottom 15% of the frame.
  On phones the cover, header and closing are cropped to the screen shape.
- **Cover photo specifically.** On phones the photo only shows in the **top part
  of the screen** (roughly a square, at least a third of the height); the paper
  sheet with the names and "Buka Undangan" covers the rest. The photo is cropped
  hard there, so set `position` to keep the faces in that window (the current
  cover uses `42% 66%`, i.e. the lower-middle of the photo). On desktop the photo
  fills the left side of the screen (`positionDesktop`).
- **Header photo.** On phones the names sit on the top third of the photo (it is
  darkened there), so faces at or below the middle work best.
- **Colour & mood.** Fresh daylight greens and soft whites match the white/sage/
  olive palette. For the cover, header and closing avoid night or very orange
  photos; in the gallery they are fine.
- **File type.** JPG or PNG straight from the photographer is fine. HEIC from an
  iPhone: export as JPG first.

---

## 3. File names (important on GitHub Pages)

- Use **lowercase letters, numbers and hyphens only**: `gallery-12`, `story-02`.
- **No spaces**, no brackets, no `&`, no accents.
  `Foto Prewed (1).JPG` will break; `gallery-12` will not.
- **GitHub Pages is case-sensitive.** `Gallery-12-800.webp` and
  `gallery-12-800.webp` are different files there, even if they look the same on
  Windows/macOS. Always lowercase.
- Don't type the width or extension in `js/config.js`. Write only the base:
  `assets/images/gallery/gallery-12` (the page adds `-800.webp` etc. itself).
- Paths are **relative** (no leading `/`). That keeps them working on
  `https://username.github.io/repo-name/`, on a custom domain, and when
  `index.html` is opened straight from a folder.

---

## 4. Make the web versions (one command)

Requirements once: Python 3 and Pillow (`pip install pillow`).

From the project folder:

```bash
# Cover / hero / closing (portrait, large)
python3 tools/optimize-images.py ~/Downloads/new-cover.jpg assets/images/cover/cover --widths 640 960 1440

# Groom / bride / story (portrait)
python3 tools/optimize-images.py ~/Downloads/new-story.jpg assets/images/story/story-02 --widths 480 800 1200

# Gallery, portrait
python3 tools/optimize-images.py ~/Downloads/new-photo.jpg assets/images/gallery/gallery-05 --widths 480 800 1600

# Gallery, landscape (wide)
python3 tools/optimize-images.py ~/Downloads/new-landscape.jpg assets/images/gallery/gallery-08 --widths 800 1600 2400
```

On Windows, write the path in quotes if it has spaces, e.g.
`"C:\Users\Nama\Downloads\Foto Baru.jpg"`. The *output* name must still have no spaces.

The tool:

- fixes the rotation from the camera,
- writes AVIF + WebP for every width,
- prints the line to paste into `js/config.js`:

```
config values ->  w: 5888, h: 8832, color: '#8da57e'
```

**Use exactly the widths in the table for that slot.** The page asks for those
sizes; a missing width shows as a broken image on some screens.

If you can't run Python, use [squoosh.app](https://squoosh.app) in the browser:
resize to each width, export once as AVIF and once as WebP, and name the files
`<base>-<width>.avif` / `<base>-<width>.webp`. Fill in `w`/`h` with the original
size and pick any mid-tone colour from the photo for `color`.

---

## 5. Update `js/config.js`

Each photo is one small object. Example (Our Story · 02):

```js
image: {
  src: "assets/images/story/story-02",   // file base, no width/extension
  widths: [480, 800, 1200],              // the widths you generated
  w: 5888, h: 8832,                      // ORIGINAL size printed by the tool
  color: "#8da57e",                      // placeholder colour while loading
  position: "62% 40%",                   // which part stays visible when cropped
  alt: "Alghifari dan Laeli tersenyum di tengah rerumputan hijau",
},
```

What each field does:

| Field | Why it matters |
|---|---|
| `src` | The file base. Same name as before = nothing else to change. |
| `widths` | Must match the files that exist, or some screens get a broken image. |
| `w`, `h` | Lets the browser reserve the right space, so the page doesn't jump while loading. Use the original photo's size. |
| `color` | Shown behind the photo while it loads. Use the value the tool prints. |
| `position` | The focal point. See section 6. |
| `positionDesktop` | (cover and hero only) focal point on desktop (≥ 1024px): the cover's left side and the header's garden arch. |
| `alt` | Description for screen readers and when an image fails to load. See section 7. |
| `wide: true` | (gallery only) landscape photo that spans two columns (see section 8). |

If you **reused the exact same file name**, you only need to change `w`, `h`,
`color`, `position` and `alt` when they differ from the old photo.

---

## 6. Keeping faces in the frame (`position`)

Photos are cropped to fit their frame (`object-fit: cover`). `position` says
which point of the photo to keep: `"horizontal% vertical%"`.

- `"50% 50%"`: centre (default).
- `"50% 25%"`: keep the upper part, typical for portraits so heads aren't cut.
- `"50% 70%"`: keep the lower part.
- `"35% 40%"`: keep the left-of-centre area.

Current values to start from:

| Slot | `position` | `positionDesktop` |
|---|---|---|
| Cover (`cover`) | `42% 66%` | `45% 62%` |
| Hero (`hero`) | `58% 50%` | `50% 58%` |
| Closing (`closing`) | `62% 52%` | n/a |
| Groom | `50% 22%` | n/a |
| Bride | `50% 24%` | n/a |
| Story 01–04 | `56% 62%` · `62% 40%` · `50% 64%` · `50% 62%` | n/a |
| Gallery | not set: the gallery uses `50% 40%` unless a line has its own `position` | n/a |

Tip: change the number in steps of 5–10%, save, refresh. Check at phone width
(see section 10). Portraits and story photos are shown at 4:5 and gallery tiles
at 3:4, so a 2:3 photo loses a little at the top and bottom there and `position`
decides which part.

---

## 7. Alt text

Write one short Indonesian sentence describing what is in the photo, the way you
would describe it to someone on the phone:

- Good: `"Alghifari dan Laeli berjalan bergandengan di antara bunga kosmos"`
- Avoid: `"foto 5"`, `"prewedding"`, `"IMG_2041"`, or repeating the same text on every photo.

Alt text is read aloud by screen readers, appears if a photo fails to load, and
is used in the gallery's enlarge buttons ("Perbesar foto 3 dari 8: …"). It is
not shown as visible text: the gallery and its lightbox show photos only (plus
the "03 / 08" counter). The cover and header photos are decoration on the page
(their `alt` is not read out), but keep it filled in: it documents the photo.

---

## 8. Add, remove or reorder gallery photos

The gallery shows `gallery` in `js/config.js` **in array order** as a regular
grid: **2 columns on phones, 3 on tablets (≥ 768px), 4 on desktop (≥ 1024px)**.
There is no carousel and no sideways swiping; that is the owner's explicit
requirement, so keep it a grid. The rule (`js/gallery.js`):

- **tile**: a portrait photo in one cell, cropped to **3:4**.
- **feature**: when the number of portrait photos (lines without `wide: true`)
  is **odd**, the **first** portrait becomes the feature so every row stays
  complete: full row width at **4:5** on phones, a **2 × 2** block on tablet and
  desktop. With an even number of portraits there is no feature.
- **wide** (`wide: true`): a landscape photo that spans **two columns** at **3:2**.

The grid fills gaps automatically (`grid-auto-flow: dense`), so on tablet and
desktop a tile may move up next to the feature.

Current set: 7 portraits (odd) + 1 landscape, so `gallery-01` is the feature,
`gallery-02` … `gallery-07` are tiles and `gallery-08` is wide. Phones: feature
row, three rows of two, landscape row. Desktop: feature 2 × 2 with four tiles
beside it, then two tiles and the landscape photo close the last row.

**Add a photo**

1. Pick the next free name, e.g. `gallery-09`.
2. Generate it (section 4) with `--widths 480 800 1600` (portrait) or
   `--widths 800 1600 2400` (landscape).
3. Add a line in `gallery: [ … ]` where you want it to appear:
   ```js
   { src: "assets/images/gallery/gallery-09", widths: [480, 800, 1600], w: 2944, h: 4416, color: "#5a6b44", alt: "…" },
   ```
   For landscape add `wide: true` and use `widths: [800, 1600, 2400]`.

**Remove a photo**: delete its line from `gallery`. Optionally delete its
files (`gallery-05-480.avif` … `gallery-05-1600.webp`) so the repository stays small.

**Reorder**: move the lines. The numbers in the file names don't have to be in
order; only the array order matters. The first portrait in the list is the one
that becomes the feature, so put the strongest shot first.

Layout tips:

- Adding or removing **one** portrait switches the feature on or off (it only
  exists when the number of portraits is odd).
- Phones always end with complete rows. On tablet and desktop count cells
  (feature = 4, tile = 1, wide = 2): the total must be a multiple of 3 for tablet
  and of 4 for desktop. Now it is 4 + 6 + 2 = 12, which fits both. Otherwise the
  last row ends with an empty space; check it at 768px and 1440px.
- 8–14 photos in total feels curated; much more makes the page long on phones.

The lightbox counter ("03 / 08") updates automatically.

---

## 9. Special files

**Share preview (`assets/images/meta/og-image.jpg`)**: what WhatsApp and social
apps show when the link is shared. The current one is the cover photo (the couple
on the wooden bench) on the left, with *Resepsi Pernikahan*, the names,
*Selasa · 20 Oktober 2026* and the venue on paper on the right. Make a
**1200 × 630 JPG under 300 KB**, keep faces and text away from the outer ~60 px
(some apps crop the edges or show a square thumbnail from the centre), and keep
the same file name. WhatsApp caches previews for a long time; a changed image may
only appear for new chats.

**Favicons** (`meta/favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` 180 × 180):
a sage leaf on forest green, not photos. They don't need changing.

---

## 10. Check before publishing

1. Open the site locally (double-click `index.html`, or run
   `python3 -m http.server 8080` in the project folder and open
   `http://localhost:8080/?to=Pujo`).
2. In Chrome DevTools, device toolbar: check **360, 390 and 430 px** wide, then tablet (768)
   and desktop (1440). `python3 tests/shoot.py http://localhost:8080/ /tmp/shots --widths 390,768,1440`
   saves screenshots of the cover, the full page and the gallery grid.
3. For each replaced photo, check:
   - faces are not cut off and not hidden behind the paper sheet (especially the cover);
   - no broken-image placeholder (a soft coloured box with the alt text means the file is missing or misnamed);
   - the page doesn't jump while the photo loads (if it does, `w`/`h` are wrong).
4. Open the gallery lightbox and swipe through all photos.
5. On GitHub Pages, after pushing, hard-refresh (Ctrl+Shift+R / pull-to-refresh)
   because browsers cache images. Test once on a real phone over mobile data.

---

## 11. Size budget (keeps it fast on mobile data)

| Slot | Target per file (AVIF, largest width) |
|---|---|
| Cover / hero / closing @1440 | ≤ 250 KB (current: 179–231 KB) |
| Groom / bride / story @1200 | ≤ 200 KB (current: 52–220 KB; story-03 and story-04 are slightly over) |
| Gallery @1600 | ≤ 500 KB (current: up to 282 KB). Only the lightbox and large screens load this size; phones show the 480/800 versions in the grid |
| Gallery landscape @2400 | ≤ 500 KB (current: 378 KB) |
| og-image.jpg | ≤ 300 KB (current: 116 KB) |

Detailed foliage and grainy night photos compress less well, which is why
some gallery files are near the limit. If a new file is bigger than its budget,
lower `AVIF_QUALITY` / `WEBP_QUALITY` at the top of `tools/optimize-images.py`
by 5 and run it again.

---

## 12. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Coloured box with text instead of the photo | File name/path doesn't match `src`, or a width is missing | Compare the names letter by letter (case!); make sure every width in `widths` exists as `.avif` and `.webp` |
| Works on the laptop, broken on GitHub Pages | Upper/lower-case difference, or a space in the name | Rename to lowercase, no spaces; push again |
| Face cut off on phones | Focal point | Adjust `position` (section 6) |
| Faces hidden behind the paper sheet on the cover (phones) | Only the top part of the screen shows the photo | Adjust `position`: a higher vertical % shows more of the lower part of the photo, a lower % more of the top |
| Page jumps while loading | Wrong `w`/`h` | Use the original size printed by the tool |
| Old photo still shows | Browser/CDN cache | Hard-refresh; GitHub Pages can take a few minutes to update |
| Photo looks sideways | Camera rotation | Re-run the tool (it auto-rotates), don't rotate by renaming |
