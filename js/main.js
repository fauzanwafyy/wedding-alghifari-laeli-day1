/**
 * Entry point: binds config to the page, runs the opening experience and
 * initialises every section. All wedding data comes from js/config.js.
 */
(function (AWL) {
  "use strict";
  const C = window.WEDDING_CONFIG;
  const GUESTS = window.GUESTS;
  const { $, $$, h, picture, dateParts, formatLongDate, formatTime, prefersReducedMotion } = AWL;
  const { resolveGuest } = AWL;
  const { initCountdown } = AWL;
  const { buildGoogleCalendarUrl, buildEventCalendarUrl } = AWL;
  const { initGallery } = AWL;
  const { initRsvp } = AWL;
  const { initWishes } = AWL;
  const { initGift } = AWL;
  const { createMusic } = AWL;
  const { initReveal, splitLetters, initLeaves, initTimeline, initParallax, initChips, initToTop } = AWL;

  const html = document.documentElement;
  const siteUrl = C.site.url || `${location.origin}${location.pathname.replace(/index\.html$/, "")}`;

  const icon = (id, className = "icon") => {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("class", className);
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `#${id}`);
    svg.append(use);
    return svg;
  };

  /* ------------------------------------------------------------ view model -- */
  function buildModel(guest) {
    const { groom, bride } = C.couple;
    const d = dateParts(C.wedding.date, C.site.locale);
    const parents = (p) => `${p.father.prefix} ${p.father.name} & ${p.mother.prefix} ${p.mother.name}`.replace(/\s+/g, " ").trim();
    const first = C.events[0] || {};
    return {
      "couple.short": `${groom.nickname} & ${bride.nickname}`,
      "groom.nick": groom.nickname,
      "bride.nick": bride.nickname,
      "groom.name": groom.displayName,
      "bride.name": bride.displayName,
      "groom.childOf": groom.childOf,
      "bride.childOf": bride.childOf,
      "groom.parents": parents(groom),
      "bride.parents": parents(bride),
      "groom.initial": groom.initial,
      "bride.initial": bride.initial,
      "date.long": formatLongDate(C.wedding.date, C.site.locale),
      "date.weekday": d.weekday,
      "date.day": d.day,
      "date.month": d.month,
      "date.year": d.year,
      "date.dmy": `${d.day} ${d.month} ${d.year}`,
      "date.monthYear": `${d.month} ${d.year}`,
      "date.dots": `${d.day.padStart(2, "0")} · ${d.monthNum} · ${d.year}`,
      "date.firstTime": `${formatLongDate(C.wedding.date, C.site.locale)} · ${formatTime(first.startTime)} ${C.wedding.timezoneLabel}`,
      "venue.name": C.venue.name,
      "venue.address": C.venue.address,
      "venue.short": C.venue.shortAddress || C.venue.address,
      "guest.name": guest.displayName,
      "family.groom": `${C.copy.familyPrefix}\n${parents(groom)}`,
      "family.bride": `${C.copy.familyPrefix}\n${parents(bride)}`,
      ...Object.fromEntries(
        Object.entries(C.copy).filter(([, v]) => typeof v === "string").map(([k, v]) => [`copy.${k}`, v])
      ),
      "copy.verse.text": C.copy.verse.text,
      "copy.verse.source": C.copy.verse.source,
      "gift.intro": C.gift.intro,
    };
  }

  function bindModel(model) {
    $$("[data-bind]").forEach((el) => {
      const v = model[el.dataset.bind];
      if (typeof v === "string") el.textContent = v;
    });
    $$("[data-hide-empty]").forEach((el) => {
      el.hidden = !model[el.dataset.hideEmpty];
    });
    $$("[data-href='maps']").forEach((a) => {
      a.href = C.venue.mapsUrl;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    });
  }

  /* ------------------------------------------------------------- sections -- */
  function renderCouple() {
    for (const role of ["groom", "bride"]) {
      const p = C.couple[role];
      const slot = $(`[data-image="${role}"]`);
      if (slot && p.photo) {
        slot.replaceChildren(picture(p.photo, { sizes: "(min-width: 1024px) 380px, (min-width: 768px) 40vw, 78vw" }));
      }
      const ig = $(`[data-instagram="${role}"]`);
      if (ig) {
        const handle = (p.instagram || "").replace(/^@/, "").trim();
        ig.hidden = !handle;
        if (handle) {
          ig.href = `https://instagram.com/${encodeURIComponent(handle)}`;
          ig.querySelector("span").textContent = `@${handle}`;
        }
      }
    }
  }

  /** Each event is an entrance "ticket": date stub, time, venue and actions. */
  function renderEvents() {
    const list = $("#event-list");
    if (!list) return;
    const tz = C.wedding.timezoneLabel;
    C.events.forEach((ev) => {
      const d = dateParts(ev.date, C.site.locale);
      const sameVenue = ev.venue === C.venue.name;
      const address = ev.address || (sameVenue ? C.venue.address : "");
      const time = ev.endTime
        ? `${formatTime(ev.startTime)} – ${formatTime(ev.endTime)} ${tz}`
        : `${formatTime(ev.startTime)} ${tz}${ev.endText ? ` – ${ev.endText}` : ""}`;
      list.append(
        h("li", { class: "ticket", "data-reveal": "ticket" },
          h("div", { class: "ticket__stub" },
            h("p", { class: "ticket__weekday", text: d.weekday }),
            h("p", { class: "ticket__day", text: d.day }),
            h("p", { class: "ticket__month", text: `${d.month} ${d.year}` })),
          h("div", { class: "ticket__body" },
            h("p", { class: "ticket__stamp", "aria-hidden": "true" },
              h("span", { text: `${d.day} ${d.month.slice(0, 3)}` }), h("span", { text: d.year })),
            h("h3", { class: "ticket__title", text: ev.title }),
            h("ul", { class: "ticket__facts" },
              h("li", {}, icon("i-calendar"), h("span", { text: formatLongDate(ev.date, C.site.locale) })),
              h("li", {}, icon("i-clock"), h("span", { text: time })),
              h("li", {}, icon("i-pin"), h("span", {},
                h("strong", { text: ev.venue }),
                address ? h("span", { class: "ticket__addr", text: address }) : null))),
            ev.note ? h("p", { class: "ticket__note", text: ev.note }) : null,
            h("div", { class: "ticket__actions" },
              h("a", { class: "btn btn--solid btn--small", href: ev.mapsUrl || C.venue.mapsUrl, target: "_blank", rel: "noopener noreferrer",
                "aria-label": `Lihat lokasi ${ev.title} di Google Maps` }, icon("i-pin"), h("span", { text: "Lihat Lokasi" })),
              h("a", { class: "btn btn--small", href: buildEventCalendarUrl(C, ev, siteUrl), target: "_blank", rel: "noopener noreferrer",
                "aria-label": `Simpan ${ev.title} ke Google Calendar` }, icon("i-calendar"), h("span", { text: "Simpan Tanggal" })))))
      );
    });
  }

  /** Our Story as a vertical timeline; the rail fills as the visitor reads. */
  function renderStory() {
    const list = $("#story-list");
    if (!list) return;
    C.story.forEach((ch, i) => {
      list.append(
        h("li", { class: `moment${i % 2 ? " moment--alt" : ""}` },
          h("span", { class: "moment__node", "aria-hidden": "true", "data-reveal": "pop" }, icon("i-leaf", "moment__leaf")),
          ch.image
            ? h("figure", { class: "moment__figure", "data-reveal": "image" },
                picture(ch.image, { sizes: "(min-width: 1024px) 400px, (min-width: 768px) 42vw, calc(100vw - 7rem)" }))
            : null,
          h("div", { class: "moment__body", "data-reveal": "" },
            h("p", { class: "moment__no", text: `Bab ${ch.number}` }),
            h("h3", { class: "moment__title", text: ch.title }),
            h("div", { class: "moment__text" }, ...ch.paragraphs.map((t) => h("p", { text: t })))))
      );
    });
  }

  /** Cover, header and closing photos, all from C.images. */
  function renderPageImages() {
    const { cover, hero, closing } = C.images;
    const put = (sel, node) => {
      const slot = $(sel);
      if (slot && node) slot.replaceChildren(node);
    };
    put("[data-slot='cover']", picture(cover, { sizes: "(min-width: 1024px) 56vw, 100vw", loading: "eager", priority: true, fade: false, alt: false }));
    const heroPic = picture(hero, { sizes: "(min-width: 1024px) 600px, 100vw", loading: "eager", fade: false, alt: false });
    heroPic.dataset.parallax = "0.14";
    put("[data-slot='hero']", heroPic);
    const closingPic = picture(closing, { sizes: "(min-width: 1024px) 70vw, 100vw" });
    closingPic.dataset.parallax = "0.1";
    put("[data-slot='closing']", closingPic);
    // Desktop crops (wider screens show more of the scene)
    if (window.matchMedia("(min-width: 1024px)").matches) {
      const set = (sel, pos) => pos && $(sel) && ($(sel).style.objectPosition = pos);
      set("[data-slot='cover'] img", cover.positionDesktop);
      set("[data-slot='hero'] img", hero.positionDesktop);
    }
  }

  function renderVerse() {
    const verse = $("#verse");
    if (verse) verse.hidden = !C.copy.verse.enabled;
  }

  /* -------------------------------------------------------- opening cover -- */
  function initCover(music) {
    const cover = $("#cover");
    const main = $("#main");
    const btn = $("#open-invitation");
    const done = () => {
      cover.hidden = true;
      html.classList.remove("is-locked", "is-opening");
      html.classList.add("is-open");
      main.inert = false;
      main.removeAttribute("inert");
      const target = location.hash && document.getElementById(location.hash.slice(1));
      if (target && target !== cover) target.scrollIntoView();
      else $("#hero-title")?.focus({ preventScroll: true });
    };

    // If the inline fallback already opened the page (slow network), just sync state.
    if (!cover || cover.hidden) {
      html.classList.remove("is-locked");
      html.classList.add("is-open");
      main && main.removeAttribute("inert");
      music.start && $("#music-toggle") && ($("#music-toggle").hidden = false);
      return;
    }

    requestAnimationFrame(() => {
      cover.classList.add("is-ready");
      html.classList.add("is-ready");
    });

    let opened = false;
    btn.addEventListener("click", () => {
      if (opened) return;
      opened = true;
      window.__awlOpened = true;
      music.start(); // inside the user gesture, so playback is allowed
      window.scrollTo(0, 0);
      if (prefersReducedMotion()) return done();
      html.classList.add("is-opening");
      cover.classList.add("is-leaving");
      let finished = false;
      const finish = () => {
        if (finished) return;
        finished = true;
        done();
      };
      // The sheet slides down last; its transition ends the opening.
      $(".cover__sheet", cover).addEventListener("transitionend", (e) => e.propertyName === "transform" && finish());
      setTimeout(finish, 2000); // safety net
    });
  }

  /* ----------------------------------------------------------------- boot -- */
  function boot() {
    const guest = resolveGuest(location.search, GUESTS, C.copy.coverDefaultGuest);
    html.dataset.guest = guest.source;
    bindModel(buildModel(guest));
    splitLetters();

    const cal = $("#calendar-link");
    if (cal) cal.href = buildGoogleCalendarUrl(C, siteUrl);

    renderPageImages();
    renderVerse();
    renderCouple();
    renderEvents();
    renderStory();
    initGallery(C.gallery);
    initGift(C.gift);
    initCountdown($("#countdown"), C.wedding, C.copy);
    initWishes();
    initRsvp(guest);

    const music = createMusic(C.music);
    initCover(music);
    initLeaves();
    initReveal();
    initChips();
    initTimeline();
    initParallax();
    initToTop();

    window.__awlReady = true;
  }

  try {
    boot();
  } catch (err) {
    // Never leave the guest stuck behind the cover.
    console.error(err);
    html.classList.remove("is-locked");
    const cover = $("#cover");
    if (cover) cover.classList.add("is-ready");
    $("#main")?.removeAttribute("inert");
    window.__awlReady = false;
  }

})(window.AWL = window.AWL || {});
