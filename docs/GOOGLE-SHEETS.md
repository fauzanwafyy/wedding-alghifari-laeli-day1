# RSVP backend: Google Sheets + Apps Script

The website is static (GitHub Pages), so RSVPs are stored in a **Google Sheet** through a
small **Google Apps Script Web App** (`google-apps-script/Code.gs`).

```
Guest's browser ──POST /exec {event:"day1"}──▶ Apps Script (Code.gs) ──new row──▶ tab "RSVP Day 1"
                ◀─GET ?action=wishes&event=day1── name + message only ◀──────────┘
```

Nothing secret is ever placed in the website: the Web App URL only accepts RSVPs and
returns public wishes.

## Day 1 setup: shared with Day 2, separate tab

Both invitations use **one spreadsheet and one Apps Script deployment** (the one made for the
Day 2 invitation). Each invitation has its own tab, picked by `rsvp.event` in `js/config.js`:

| Invitation | `rsvp.event` | Tab | Header colours |
|---|---|---|---|
| Day 2 (Akad + Resepsi, 21 Oct) | *(not sent)* | **RSVP** (the original tab) | black / cream |
| Day 1 (Resepsi, 20 Oct) | `"day1"` | **RSVP Day 1** | olive / white |

The tabs live in `EVENTS` at the top of `Code.gs`. A request without `event` goes to the Day 2
tab, so the live Day 2 site keeps working without any change. Guest lists, duplicate checks,
spam limits and the wish walls are all kept per tab: Day 1 guests never see Day 2 wishes.

| Item | Value |
|---|---|
| Google account (owner) | the account that owns the Day 2 RSVP sheet (not written here, since this repo is public) |
| Spreadsheet | **RSVP - Undangan Alghifari & Laeli** (the Day 2 one) |
| Apps Script project | the one *bound* to that spreadsheet (Ekstensi → Apps Script), `@OnlyCurrentDoc` |
| Deployment | the existing Web app · **Jalankan sebagai: Saya** · **Yang memiliki akses: Siapa saja** |
| Web App URL | same URL as Day 2, already in `js/config.js` → `rsvp.apiUrl` |

**Safety net.** Before sending anything, the Day 1 site asks the script whether it knows the
`day1` tab (`?action=ping` must list it under `events`). While the live script is still the
older single-tab version, the form shows *"Formulir RSVP sedang disiapkan"*, the wishes show
*"sedang disiapkan"*, and nothing is written, so a Day 1 RSVP can never land in the Day 2 tab.

The sheet itself is private (only the owner can open it). The Web App runs as the owner,
so guests can submit without access to the sheet.
Google's menus are shown in English with the Indonesian label in brackets.

---

## 1. Put the new script in the existing spreadsheet (one time)

1. Open the Day 2 spreadsheet **RSVP - Undangan Alghifari & Laeli**.
2. **Extensions → Apps Script** (*Ekstensi → Apps Script*).
3. Select everything in the editor and delete it. Open `google-apps-script/Code.gs` from this
   repository, copy **everything**, paste it in, then click **Save** (💾).
4. In the toolbar function dropdown choose **`setup`** → **Run**. It creates and formats the
   **RSVP Day 1** tab and re-formats **RSVP**. Existing RSVPs are kept.
   If Google asks for permission again: **Review permissions** → your account → **Advanced** →
   **Go to RSVP… (unsafe)** → **Allow** (your own script; the warning appears for every
   personal script).
5. **Deploy → Manage deployments** (*Terapkan → Kelola deployment*) → ✏️ (edit) →
   **Version: New version** (*Versi: Versi baru*) → **Deploy** (*Terapkan*).
   Do **not** use *New deployment*: that makes a new URL and Day 2 would stop receiving RSVPs.

**Check:** open `<Web App URL>?action=ping`. The answer must contain
`"events":["day2","day1"]`. Once it does, the Day 1 form works straight away (no change to
the website needed).

Both tabs have the same columns:

| Column | Content | Public? |
|---|---|---|
| A · Timestamp | Time received (Asia/Jakarta) | No |
| B · Invitation Slug | From the guest link, e.g. `pujo-partner`, or `umum` | No |
| C · Guest Name | Full name typed by the guest | **Yes** (with the wish) |
| D · Attendance | `Hadir` / `Tidak Hadir` | No |
| E · Guest Count | Number of people (0 if not attending) | No |
| F · Wedding Message | The wish | **Yes** |
| G · Submission ID | Random ID used to prevent duplicates | No |
| H · Show on Website | ☑ = wish visible. Untick to hide a wish | No |

## 2. Test it

1. Open the Day 1 invitation with `?to=qa-test`, submit an RSVP with a message.
2. A new row appears in the **RSVP Day 1** tab (not in **RSVP**) within a second or two.
3. The wish appears under **Doa & Ucapan** on Day 1 only.
4. Run **`removeTestRows`** in the editor: it deletes rows whose Invitation Slug is `selftest`
   or `qa-test` in every tab, never real RSVPs.

## Adding another invitation later

Add a line to `EVENTS` in `Code.gs` (key, tab name, header colours), paste, **Save**, run
**`setup`**, deploy a **New version**, then set that key as `rsvp.event` on the new site.

## Starting from scratch (only if the shared spreadsheet is ever lost)

Create a sheet at <https://sheets.new>, open **Extensions → Apps Script** from inside it, paste
`Code.gs`, **Save**, run **`setup`** (creates both tabs), then **Deploy → New deployment → ⚙ Web
app**, *Execute as: Me*, *Who has access: Anyone*. Put the new `/exec` URL into `rsvp.apiUrl`
on **both** sites (Day 2 and Day 1).

---

## Updating the script later

Edits to `Code.gs` only go live after a new version is deployed:

**Deploy → Manage deployments → ✏️ (edit) → Version: New version → Deploy.**
(*Terapkan → Kelola deployment → ✏️ → Versi: Versi baru → Terapkan.*)

Editing the existing deployment this way **keeps the same URL**, so the website needs no change.
(Creating a *New deployment* instead would produce a new URL that you'd have to paste into
`js/config.js`.)

## Moderating wishes

Untick **Show on Website** (column H) on any row. The wish disappears from the site within
~30 seconds. You can also edit the text in column F, or delete the row.

## Reading the RSVPs

- Filter column D for `Hadir` and use `=SUM(E:E)` for the head count.
- **File → Download → .xlsx / .csv** for the vendor.

## Behaviour & safety built in

| Concern | How it's handled |
|---|---|
| Validation | Name 2–80 chars, attendance required, guest count 1–5 (0 if not attending), message ≤ 500. Same rules in browser and server. |
| HTML / script injection | Tags and control characters stripped server-side; the website renders text only (never HTML). |
| Spreadsheet formula injection | Values starting with `= + - @` are stored with a leading `'`. |
| Double taps / retries | Each attempt carries a random `submissionId`; repeats are answered `duplicate` and **not** stored. Identical re-sends within 10 minutes are also ignored. |
| Spam | Hidden honeypot field + max 6 submissions per name/invitation per 10 minutes. |
| Concurrency | `LockService` serialises writes, so no rows are lost when many guests submit at once. |
| Privacy | `?action=wishes` returns only `name` + `message` (+ an opaque id) from the requested invitation's tab. Attendance, counts, timestamps and slugs never leave the sheet. |
| Load | Public wishes cached for 20 s per tab, so polling stays cheap. |
| Unknown invitation | An `event` that isn't in `EVENTS` is rejected; no tab is created. |
| Row placement | New RSVPs go into the first empty row under the data (judged by column A), not via `appendRow`. Checkboxes are added per row. A checkbox column pre-filled down the sheet fills empty rows with FALSE, which made `appendRow` write at row 1001+. `setup` now clears those leftovers. |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Form says *"sedang disiapkan"* | `rsvp.apiUrl` in `js/config.js` is empty or doesn't end in `/exec`, **or** the live script is still the old single-tab version: `?action=ping` doesn't list `day1`. Do step 1 above (paste, Save, `setup`, New version). |
| `?action=ping` asks you to sign in | Deployment access isn't **Anyone**. Edit the deployment. |
| Error *"Maaf, terjadi kendala pada server"* | Open Apps Script → **Executions** to see the error. Usually the `setup` authorisation wasn't completed. |
| Changes to Code.gs have no effect | Deploy a **New version** of the existing deployment (see above). |
| Wishes don't update | Wait ~30 s (cache + polling). Check column H is ticked. |
| New rows appear far below (row 1000+) | Someone filled column H with checkboxes for the whole sheet. Run **`setup`** once: it removes checkboxes/FALSE from empty rows. Existing rows are kept. |
| Need to delete test submissions | Use Invitation Slug `qa-test` for tests, then run **`removeTestRows`** (cleans every tab). |
| A Day 1 RSVP is in the **RSVP** tab | Cannot happen with this site version (see *Safety net*). If you see one, it came from the Day 2 site. |
