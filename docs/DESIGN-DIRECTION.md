# Design Direction — *Taman Pagi*

**Resepsi Pernikahan Alghifari & Laeli · Day 1 · Selasa, 20 Oktober 2026**

> "Sebuah perjalanan sederhana, dari pertemuan yang tak direncanakan hingga janji yang kami
> ikrarkan." — from the couple's own story intro

Day 1 is a reception that runs from morning into the evening at a resort in Cisarua, Bogor.
The cover, header, story and closing photographs chosen for it are daylight garden scenes: a
wooden bench under tall trees, cosmos flowers, a stone bridge, ferns. The invitation is built
around that light: **taman pagi**, a morning garden. The colours are the couple's own palette
(white, sage, olive, nude): white paper carries the information, and a deep forest green marks
the quiet, important bands. Thin drawn sprigs and a few falling leaves are the only ornament.

Day 2 (21 Oktober) has its own invitation and its own direction. Both share the same content
system (`js/config.js`), RSVP backend code and guest-link format, so maintenance stays the same.

---

## 1. Principles

1. **Daylight first.** Most of the page is white paper (`#FBFAF6`) with soft grain. Dark
   forest bands are reserved for the countdown, the gift and the colophon.
2. **Photography leads.** Full-bleed photos on phones; on desktop the header and closing
   photos sit in a garden arch so the type has a calm field beside them.
3. **Readable names.** Names are set in Marcellus, a classical roman with flared strokes. No
   script lettering: it gets hard to read at phone sizes and looks templated.
4. **Botany as line art.** One original sprig and one branch (inline SVG symbols `#i-sprig`,
   `#i-branch`) are drawn stroke by stroke as they appear, and reused at different scales.
5. **Lively, never in the way.** More motion than a print invitation (leaves, letter reveals,
   a ticket that lands), but nothing blocks reading, and all of it switches off for
   `prefers-reduced-motion`.

## 2. Typography

| Role | Font | Notes |
|---|---|---|
| Display: names, titles, numerals, verse, ticket day | **Marcellus** (400) | Engraved-roman feel with gentle flares; elegant without script. Ink on paper, cream on forest. |
| UI, body, labels, forms, bank numbers | **Manrope** (variable 200–800) | Modern grotesque. Uppercase labels at 600–800, tracked 0.14–0.4em. Bank numbers use tabular lining figures. |

Two files, self-hosted as WOFF2 in `assets/fonts/` (latin subset, ~38 KB together, both
preloaded), `font-display: swap`, with fallbacks (Cormorant Garamond / Palatino / Georgia for
display, Segoe UI / system-ui for text). When `index.html` is opened straight from a folder
(`file://`), browsers block font files, so the page loads `css/fonts-local.css` (the same fonts
embedded as base64) instead. The live site never loads that file.

## 3. Colour

The couple's palette (white, sage, olive, nude) plus a deep forest for dark bands. Ratios are
the ones noted in `css/main.css`; the forest/nude pairings are computed the same way.

| Token | Hex | Use · contrast |
|---|---|---|
| `--c-paper` | `#FBFAF6` | Main white: page, cover sheet, inputs |
| `--c-white` | `#FFFFFF` | Cards: event ticket, RSVP card, wishes |
| `--c-sage-soft` | `#EEECE3` | Sage tint for alternate sections (couple, RSVP, wishes) and the verse card |
| `--c-mist` | `#F3F2F2` | Softened palette white `#E5E3E6`: Our Story band |
| `--c-sage` | `#C5C0AD` | Palette sage: perforation, quote mark, image placeholders. Never text |
| `--c-olive` | `#6A6B4B` | Palette olive: accent text, eyebrows, sprigs, focus ring (5.3:1 on paper) |
| `--c-olive-ink` | `#55573A` | Olive for small text on sage tints (6.3:1) |
| `--c-nude` | `#D1BEB0` | Palette nude: ring bars, "&" disc, ticket stamp, eyebrows on forest (7.2:1 on forest) |
| `--c-forest` | `#2F3322` | Dark bands, solid buttons, ticket stub, chip ink |
| `--c-ink` | `#262820` | Text (14.3:1 on paper) |
| `--c-ink-soft` | `#5B5D4E` | Secondary text (6.4:1) |
| `--c-on-dark` | `#F4F2EA` | Text on forest (11.6:1) |
| `--c-on-dark-soft` | `#C9C7B6` | Secondary text on forest (7.6:1) |
| `--c-error` | `#9B2C1F` | Form errors |

Bank cards use an olive gradient (`#75775A` → olive → `#43462E`). There `--c-on-dark` and
white reach about 4.9:1 on olive (less toward the lighter corner), while nude and
`--c-on-dark-soft` fall to roughly 3–3.5:1, too low for small text. `tests/a11y.py` samples
the real pixels behind text on gradients, so it catches this.

## 4. Layout

**Phones (primary, < 768px)**

- **Opening cover:** the cover photo fills the top (at least a third of the screen) and a
  white paper sheet with rounded top corners rises from the bottom, holding *Resepsi
  Pernikahan*, the names, `20 · 10 · 2026`, *Kepada Yth. Bapak/Ibu/Saudara/i*, the guest name
  in a sage pill (`.cover__guestname`), *Buka Undangan* and the spelling note.
- **Header:** full-bleed photo, darkened at the top for the names and fading into paper at the
  bottom; names letter by letter, then the date. *Gulir* cue at the bottom.
- **Navigation:** a sticky chip bar at the top (*Mempelai · Acara · Cerita · Galeri · RSVP ·
  Hadiah*) with a forest "ink" pill that slides to the active section. All six fit on a 360px
  phone, so there is nothing to swipe. No hamburger menu, no bottom bar.
- **Sections:** salam + QS. Ar-Rum : 21 in a sage verse card · couple portraits (4:5) in offset
  hairline frames with drawn sprigs, an "&" disc between them · countdown on a forest band ·
  the event as an entrance **ticket** (date stub, perforation with side notches, round date
  stamp, *Lihat Lokasi* / *Simpan Tanggal*) · Our Story as a vertical **timeline** with leaf
  nodes on a rail that fills while scrolling · gallery grid · RSVP card + wishes · gift
  (*Lihat Rekening* opens olive bank cards with a chip and a moving sheen) · closing photo,
  full-bleed and fading into paper, then the farewell, families and a forest colophon with the
  "A & L" monogram.
- Gutters `clamp(1.5rem, 6.4vw, 2.5rem)` plus safe-area insets; text measure 33–42rem;
  section padding `clamp(5rem, 20vw, 7.5rem)`.
- **≤ 359px:** tighter chips, the two RSVP choices stack, smaller ticket stamp.

**Tablet (≥ 768px):** the cover keeps the stacked composition with a taller photo. Portraits
sit side by side with the "&" between them. The ticket turns horizontal (stub left,
perforation running down). The story rail moves to the centre and chapters alternate left and
right. Gallery 3 columns. Bank cards in two columns; families in two columns.

**Desktop (≥ 1024px):** the cover splits into photo left / paper sheet right (also used for
phones held in landscape). The header becomes names on a forest field beside the photo in a
**garden arch** (round top, hairline outline offset 14px). Gallery 4 columns. The closing photo
sits in an arch beside the farewell text. From 1280px portraits and countdown rings grow.

**Gallery rule:** a regular grid, never a carousel or sideways swipe (the owner's explicit
requirement). 2 columns on phones, 3 on tablets, 4 on desktop. When the number of portrait
photos is odd, the first portrait becomes the **feature** (full row on phones, 2×2 from
tablet), so rows stay complete; a `wide: true` landscape photo spans two columns.

## 5. Motion

| Moment | Motion |
|---|---|
| Cover appears | Photo settles from 1.14 → 1 over 9s; the sheet rises; the branch on the sheet draws itself; names rise letter by letter (45 ms apart); the rest fades up in a stagger; the envelope icon on *Buka Undangan* nudges now and then |
| *Buka Undangan* | The text fades while the photo lifts away and the sheet drops (1.25s curtain easing); on the side-by-side cover they split left and right |
| Header | Photo settles 1.12 → 1; kicker, letter-by-letter names and date follow; on desktop the arch photo unveils from the bottom (clip-path) |
| Leaves | Leaves fall and sway over the cover photo (7), the header (6) and the closing (5); positions are deterministic, no randomness |
| Scroll reveals | Default fade-up 26px, plus variants: `image` (clip-path reveal from the bottom + zoom settle), `pop` (spring scale: countdown units, "&" disc, timeline nodes), `rise` (verse, RSVP card), `tile` (gallery), `card` (bank cards tilt up from `rotateX`), `ticket` (rises with a slight turn, then the date stamp lands), `draw` (SVG stroke sprigs). `data-stagger` delays siblings |
| Portraits | Offset frame slides out to ±12px; side sprig draws over 3s |
| Countdown | Progress rings show the share of each unit left (days on a 30-day dial); changed digits drop in |
| Our Story | The rail fills with scroll progress |
| Parallax | Header photo (0.14) and closing photo (0.1) drift with scroll |
| Chip nav | Ink pill slides and resizes to the active chip; a soft shadow once it sticks |
| Buttons, gift | Fill sweeps in from the left on hover; the panel opens by animating its height; a sheen crosses each bank card every 6s |
| Music | Dashed disc spins and equaliser bars move while playing; a ring pulses if autoplay was blocked |
| RSVP / wishes | Circle and check mark draw on success; a new wish slides in with a brief highlight |

Movement uses `transform`, `opacity`, `clip-path` and SVG `stroke-dashoffset`; the scroll
effects (timeline, parallax) share one requestAnimationFrame-throttled loop (`js/motion.js`).
**`prefers-reduced-motion: reduce`** turns every animation and transition off: no leaves, no
parallax, content and names appear immediately, sprigs are fully drawn, the timeline is full,
and the cover opens instantly.

## 6. Accessibility

- Skip link (*Lewati ke isi undangan*), `main`, labelled `nav` (*Navigasi undangan*), one
  `h1`, no heading jumps.
- The cover is a modal `role="dialog"` labelled by the names; the invitation behind it is
  `inert` and scroll is locked until it opens. Focus then moves to the header names.
- Letter-split names: the letters are `aria-hidden`, the heading keeps
  `aria-label="Alghifari dan Laeli"`.
- Active chip has `aria-current`; the countdown is `role="timer"`; the gift toggle uses
  `aria-expanded`/`aria-controls` and the closed panel is `inert`.
- Touch targets ≥ 44px; inputs 16px (no iOS zoom); visible focus (olive outline on light,
  nude on dark); labelled fields with inline errors; lightbox is a native `<dialog>` with
  ←/→/Esc and focus return.
- Decorative SVG is `aria-hidden`; every photo has Indonesian alt text; the gallery buttons
  say *Perbesar foto 3 dari 8: …*.

## 7. Personalization

- `?to=` accepts **either** a free-text name (`?to=Pujo+%26+Partner`) **or** a guest slug
  from the optional `GUESTS` list (`?to=fauzan-wafi` → "Fauzan Wafi & Partner").
- An unknown slug is title-cased gracefully; names are capped at 60 characters. No parameter
  shows *Tamu Undangan*.
- The name appears on the cover nameplate, is pre-filled in the RSVP form, and the slug is
  stored with each RSVP.
- Everything is rendered with `textContent` (never `innerHTML`), so `?to=<script>` is shown
  as plain text.

## 8. Why this fits Day 1

A morning-to-evening reception at a garden resort, photographs full of leaves, cosmos and
soft white clothes: a white, sage and olive page with drawn sprigs belongs to those images. It feels fresh and celebratory for a reception, stays easy to read on a phone,
and is clearly a sibling of, not a copy of, the Day 2 invitation.
