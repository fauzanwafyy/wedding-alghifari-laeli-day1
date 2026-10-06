# Deployment: GitHub Pages

The site is plain HTML/CSS/JS with no build step. GitHub Pages serves the repository as-is.

## 1. Repository

| Setting | Value |
|---|---|
| Name | `fauzanwafyy/wedding-alghifari-laeli-day1` |
| Visibility | **Public** (GitHub Pages is free for public repos; private repos need GitHub Pro) |
| Default branch | `main` |

```bash
git remote add origin https://github.com/fauzanwafyy/wedding-alghifari-laeli-day1.git
git push -u origin main
```

> Everything in a public repo is public, but so is everything on the website itself. No
> secrets live here: the Apps Script URL is designed to be public, and RSVP data stays in your
> Google Sheet.

The Day 2 invitation is a separate repository (`fauzanwafyy/wedding-alghifari-laeli`) and a
separate site. Changes here never affect it.

## 2. Turn on GitHub Pages

1. Repository → **Settings → Pages**.
2. **Build and deployment → Source:** *Deploy from a branch*.
3. **Branch:** `main` · folder `/ (root)` → **Save**.
4. After ~1 minute the site is live at
   `https://fauzanwafyy.github.io/wedding-alghifari-laeli-day1/`

`.nojekyll` in the root tells Pages to serve files as-is (no Jekyll processing).

## 3. Set the public URL in the page head

Social previews (WhatsApp, Instagram, Facebook) need absolute URLs. They are already set to
the Day 1 address:

```
https://fauzanwafyy.github.io/wedding-alghifari-laeli-day1/
```

(`index.html`: `canonical`, `og:url`, `og:image`, `twitter:image`; `js/config.js`: `site.url`.)
If the address ever changes (custom domain, renamed repo), update those 5 places.

The preview image is `assets/images/meta/og-image.jpg` (1200 × 630: the cover photo on the
left, names, date and venue on paper on the right). To refresh a preview WhatsApp has already
cached, share the link with a harmless extra parameter (e.g. `?to=Nama&v=2`). Facebook's
[Sharing Debugger](https://developers.facebook.com/tools/debug/) can force a re-scrape.

### Same origin as Day 2

Day 1 (`…github.io/wedding-alghifari-laeli-day1/`) and Day 2 (`…github.io/wedding-alghifari-laeli/`)
share the origin `https://fauzanwafyy.github.io`, so they share browser storage. Day 1 therefore
uses its own keys: `awl-day1:rsvp` (the guest's last RSVP), `awl-day1:music` (paused or not)
and `awl-day1:generator` (the generator's address, names and template). Keep these names if you copy
code between the two projects, or one invitation will read the other's data.

## 4. Guest links

Every guest uses the same site with a different `?to=`:

```
https://fauzanwafyy.github.io/wedding-alghifari-laeli-day1/?to=Pujo
https://fauzanwafyy.github.io/wedding-alghifari-laeli-day1/?to=Pujo+%26+Partner
https://fauzanwafyy.github.io/wedding-alghifari-laeli-day1/?to=fauzan-wafi    ← slug from GUESTS in config.js
```

These work when opened directly, from WhatsApp, and on any phone, because query strings need
no server routing. As a bonus, `…/wedding-alghifari-laeli-day1/fauzan-wafi` (no `?to=`) is
redirected by `404.html` to `?to=fauzan-wafi`.

Use **`generator.html`** (`…/wedding-alghifari-laeli-day1/generator.html`) to create links and
ready-to-send WhatsApp messages (Resepsi, 20 Oktober 2026, 09.00 – 21.00 WIB) for a whole list
of names. It isn't linked from the invitation and is marked `noindex`. Guests invited to both
days get two links: this one and the Day 2 link.

## 5. Custom domain (optional)

1. Buy a domain, e.g. `alghifarilaeli.com`.
2. DNS at your registrar:
   - Apex domain: four `A` records → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
   - or a subdomain such as `resepsi`: `CNAME` → `fauzanwafyy.github.io`
3. Repository → **Settings → Pages → Custom domain** → enter the domain → Save
   (GitHub adds a `CNAME` file). Tick **Enforce HTTPS** once it's available.
4. Update the 4 URLs in `index.html` (step 3) and `site.url` in `js/config.js`.

A custom domain gives Day 1 its own origin, so its storage is then separate from Day 2 anyway.

## 6. Updating the site

Edit → commit → push to `main`. Pages redeploys automatically in about a minute.
Hard-refresh (or add `?v=2` to the URL) if the browser shows an old version.

## 7. Pre-launch checklist

- [ ] Day 1 RSVP sheet + Apps Script deployed and its `/exec` URL in `js/config.js` →
      `rsvp.apiUrl` (see `GOOGLE-SHEETS.md`); `?action=ping` answers `{"ok":true,…}`
- [x] Live address set in `index.html` (4 places) and `site.url`
- [ ] GitHub Pages turned on for `wedding-alghifari-laeli-day1` (`main`, `/ (root)`)
- [ ] Open a guest link on an iPhone and an Android phone: cover → open → music → RSVP
- [ ] Submit one real-phone test RSVP with Invitation Slug `qa-test`
      (e.g. `…/?to=qa-test`), check it lands in the **Day 1** sheet (not Day 2), then run
      `removeTestRows` in Apps Script
- [ ] Share a link in WhatsApp and check the preview image and title
