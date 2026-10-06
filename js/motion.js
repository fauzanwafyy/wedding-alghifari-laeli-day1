/**
 * Motion for "Taman Pagi": scroll reveals, letter-by-letter names, drifting
 * leaves, the story timeline that fills as you read, parallax photos, the
 * sticky chip navigation and the back-to-top button.
 *
 * Everything animates transform/opacity (or a CSS variable read by them), and
 * all of it is skipped when the visitor prefers reduced motion.
 */
(function (AWL) {
  "use strict";
  const { $, $$, h, prefersReducedMotion } = AWL;
  const html = document.documentElement;

  /** One rAF-throttled scroll/resize loop shared by every scroll effect. */
  const scrollJobs = [];
  let ticking = false;
  function onScrollFrame(job) {
    scrollJobs.push(job);
    if (scrollJobs.length > 1) return;
    const run = () => {
      ticking = false;
      for (const j of scrollJobs) j();
    };
    const request = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(run);
      }
    };
    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request, { passive: true });
    request();
  }

  /* ------------------------------------------------------------- reveals -- */
  function initReveal() {
    // Children of [data-stagger] appear one after another.
    $$("[data-stagger]").forEach((group) => {
      const step = Number(group.dataset.stagger) || 110;
      [...group.querySelectorAll("[data-reveal]")].forEach((el, i) => el.style.setProperty("--reveal-delay", `${Math.min(i, 7) * step}ms`));
    });
    const items = $$("[data-reveal]");
    if (!("IntersectionObserver" in window) || prefersReducedMotion()) {
      items.forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );
    items.forEach((el) => io.observe(el));
    // Elements added later (wishes, RSVP states) can opt in too.
    AWL.observeReveal = (el) => io.observe(el);
  }

  /* ------------------------------------------------------ split headings -- */
  /**
   * Wraps every letter of [data-split] headings in a span so they can rise one
   * by one. Screen readers get the original text via aria-label.
   */
  function splitLetters() {
    $$("[data-split]").forEach((heading) => {
      const names = [...heading.querySelectorAll("[data-bind]")].map((el) => el.textContent.trim());
      heading.setAttribute("aria-label", names.join(" dan "));
      let i = 0;
      heading.querySelectorAll("[data-bind], .amp").forEach((part) => {
        const text = part.textContent;
        part.textContent = "";
        part.setAttribute("aria-hidden", "true");
        for (const ch of text) {
          const s = h("span", { class: "char", text: ch });
          s.style.setProperty("--i", String(i++));
          part.append(s);
        }
      });
      heading.querySelectorAll(".visually-hidden").forEach((el) => el.remove());
    });
  }

  /* -------------------------------------------------------------- leaves -- */
  /** Fills each [data-leaves="n"] box with n slowly falling, swaying leaves. */
  function initLeaves() {
    if (prefersReducedMotion()) return;
    const NS = "http://www.w3.org/2000/svg";
    $$("[data-leaves]").forEach((box) => {
      const n = Number(box.dataset.leaves) || 5;
      for (let i = 0; i < n; i++) {
        const leaf = h("span", { class: "leaf" });
        // Deterministic spread (no Math.random) so layout is stable between visits
        const x = (i * 37 + 11) % 100;
        leaf.style.setProperty("--x", `${x}%`);
        leaf.style.setProperty("--dur", `${13 + ((i * 5) % 9)}s`);
        leaf.style.setProperty("--delay", `${-((i * 3.7) % 13)}s`);
        leaf.style.setProperty("--size", `${12 + ((i * 7) % 12)}px`);
        leaf.style.setProperty("--sway", `${18 + ((i * 11) % 26)}px`);
        leaf.style.setProperty("--spin", `${i % 2 ? -1 : 1}`);
        const svg = document.createElementNS(NS, "svg");
        const use = document.createElementNS(NS, "use");
        use.setAttribute("href", "#i-leaf");
        svg.append(use);
        leaf.append(svg);
        box.append(leaf);
      }
    });
  }

  /* ---------------------------------------------------- story timeline -- */
  function initTimeline() {
    const timeline = $(".timeline");
    if (!timeline) return;
    if (prefersReducedMotion()) return timeline.style.setProperty("--progress", "1");
    onScrollFrame(() => {
      const r = timeline.getBoundingClientRect();
      const vh = window.innerHeight;
      // 0 when the top of the list reaches 70% of the screen, 1 when its end does
      const p = Math.min(1, Math.max(0, (vh * 0.7 - r.top) / Math.max(1, r.height)));
      timeline.style.setProperty("--progress", p.toFixed(3));
    });
  }

  /* ------------------------------------------------------------ parallax -- */
  function initParallax() {
    if (prefersReducedMotion()) return;
    const layers = $$("[data-parallax]");
    if (!layers.length) return;
    onScrollFrame(() => {
      const vh = window.innerHeight;
      for (const el of layers) {
        const box = el.parentElement.getBoundingClientRect();
        if (box.bottom < -50 || box.top > vh + 50) continue;
        const speed = Number(el.dataset.parallax) || 0.12;
        const centre = box.top + box.height / 2 - vh / 2;
        el.style.transform = `translate3d(0, ${(-centre * speed).toFixed(1)}px, 0)`;
      }
    });
  }

  /* ----------------------------------------------------------------- nav -- */
  function initChips() {
    const nav = $("#chips");
    if (!nav) return;
    const links = $$(".chip", nav);
    const ink = $(".chips__ink", nav);
    const track = $(".chips__track", nav);
    const byKey = new Map(links.map((a) => [a.dataset.nav, a]));
    let activeKey = "";

    const moveInk = (a) => {
      if (!ink) return;
      if (!a) {
        ink.style.opacity = "0";
        return;
      }
      ink.style.opacity = "1";
      ink.style.width = `${a.offsetWidth}px`;
      ink.style.transform = `translateX(${a.offsetLeft}px)`;
    };
    const setActive = (key) => {
      if (key === activeKey) return;
      activeKey = key;
      let current = null;
      links.forEach((a) => {
        const on = a.dataset.nav === key;
        a.classList.toggle("is-active", on);
        if (on) {
          a.setAttribute("aria-current", "true");
          current = a;
        } else a.removeAttribute("aria-current");
      });
      moveInk(current);
      // Keep the active chip visible on narrow screens
      if (current && track.scrollWidth > track.clientWidth) {
        track.scrollTo({ left: current.offsetLeft - (track.clientWidth - current.offsetWidth) / 2, behavior: prefersReducedMotion() ? "auto" : "smooth" });
      }
    };
    window.addEventListener("resize", () => moveInk(byKey.get(activeKey)), { passive: true });

    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          for (const e of entries) {
            if (e.isIntersecting) {
              const key = e.target.dataset.nav;
              setActive(byKey.has(key) ? key : "");
            }
          }
        },
        { rootMargin: "-45% 0px -50% 0px" }
      );
      $$("main section[data-nav]").forEach((s) => io.observe(s));
    }

    // "Stuck" shadow once the bar sticks to the top
    const sentinel = h("span", { class: "chips__sentinel", "aria-hidden": "true" });
    nav.before(sentinel);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => nav.classList.toggle("is-stuck", !e.isIntersecting && e.boundingClientRect.top < 0)).observe(sentinel);
    }

    // Hide floating buttons while typing (mobile keyboards)
    document.addEventListener("focusin", (e) => {
      if (e.target.matches("input, textarea, select")) html.classList.add("is-typing");
    });
    document.addEventListener("focusout", () => html.classList.remove("is-typing"));
  }

  function initToTop() {
    const btn = $("#to-top");
    const hero = $("#home");
    if (!btn || !hero || !("IntersectionObserver" in window)) return;
    new IntersectionObserver(([e]) => html.classList.toggle("is-past-hero", !e.isIntersecting)).observe(hero);
  }

  Object.assign(AWL, { initReveal, splitLetters, initLeaves, initTimeline, initParallax, initChips, initToTop });
})(window.AWL = window.AWL || {});
