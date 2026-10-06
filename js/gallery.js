/**
 * Gallery: a regular grid (2 columns on phones, 3 on tablets, 4 on desktop;
 * never a sideways carousel) + accessible
 * lightbox (native <dialog>). Landscape photos (`wide: true`) span two
 * columns. When the number of portrait photos is odd, the first one is shown
 * larger (two columns wide) so every row is complete.
 * Photo order = order of `gallery` in js/config.js.
 * The lightbox shows the photo and a counter only (no visible caption); the
 * `alt` text stays on the image for screen readers.
 * Keyboard: ←/→ to navigate, Esc to close. Touch: swipe left/right.
 */
(function (AWL) {
  "use strict";
  const { $, h, picture } = AWL;

  const SIZES = {
    tile: "(min-width: 1024px) 320px, (min-width: 768px) 30vw, calc(50vw - 30px)",
    big: "(min-width: 1024px) 660px, (min-width: 768px) 62vw, calc(100vw - 48px)",
  };

  function initGallery(images) {
    const grid = $("#gallery-grid");
    const dialog = $("#lightbox");
    if (!grid || !images || !images.length) return;

    const portraits = images.filter((img) => !img.wide).length;
    let featureDone = portraits % 2 === 0; // only needed when the count is odd
    images.forEach((img, i) => {
      let variant = "tile";
      if (img.wide) variant = "wide";
      else if (!featureDone) {
        variant = "feature";
        featureDone = true;
      }
      const btn = h(
        "button",
        {
          type: "button",
          class: "gallery__btn",
          "aria-label": `Perbesar foto ${i + 1} dari ${images.length}: ${img.alt}`,
          onclick: () => open(i),
        },
        picture(img, { sizes: variant === "tile" ? SIZES.tile : SIZES.big, position: img.position || "50% 40%" }),
        h("span", { class: "gallery__zoom", "aria-hidden": "true" })
      );
      grid.append(h("li", { class: `gallery__item gallery__item--${variant}`, "data-reveal": "tile" }, btn));
    });

    let current = 0;

    if (!dialog || typeof dialog.showModal !== "function") {
      // Very old browsers: no lightbox; images stay in the grid.
      grid.querySelectorAll(".gallery__btn").forEach((b) => (b.disabled = true));
      return;
    }

    const stage = $(".lightbox__stage", dialog);
    const idx = $("#lb-index", dialog);
    const total = $("#lb-total", dialog);
    let opener = null;

    total.textContent = String(images.length).padStart(2, "0");

    const preload = (i) => {
      const img = images[(i + images.length) % images.length];
      const w = img.widths[img.widths.length - 1];
      const im = new Image();
      im.decoding = "async";
      im.src = `${img.src}-${w}.webp`;
    };

    function show(i) {
      current = (i + images.length) % images.length;
      const img = images[current];
      const pic = picture(img, { sizes: "100vw", loading: "eager", className: "lightbox__pic", position: "50% 50%" });
      stage.replaceChildren(pic);
      idx.textContent = String(current + 1).padStart(2, "0");
      preload(current + 1);
      preload(current - 1);
    }

    function open(i) {
      opener = document.activeElement;
      show(i);
      dialog.showModal();
      document.documentElement.classList.add("is-lightbox");
    }

    function close() {
      dialog.close();
    }

    dialog.addEventListener("close", () => {
      document.documentElement.classList.remove("is-lightbox");
      stage.replaceChildren();
      if (opener && opener.focus) opener.focus({ preventScroll: true });
    });

    $(".lightbox__close", dialog).addEventListener("click", close);
    $(".lightbox__nav--prev", dialog).addEventListener("click", () => show(current - 1));
    $(".lightbox__nav--next", dialog).addEventListener("click", () => show(current + 1));

    dialog.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") show(current + 1);
      else if (e.key === "ArrowLeft") show(current - 1);
    });

    // Click on the dark backdrop (outside the photo) closes
    dialog.addEventListener("click", (e) => {
      if (e.target === dialog || e.target === stage) close();
    });

    // Swipe
    let startX = 0;
    let startY = 0;
    let tracking = false;
    stage.addEventListener("pointerdown", (e) => {
      tracking = true;
      startX = e.clientX;
      startY = e.clientY;
    });
    stage.addEventListener("pointerup", (e) => {
      if (!tracking) return;
      tracking = false;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.2) show(current + (dx < 0 ? 1 : -1));
    });
    stage.addEventListener("pointercancel", () => (tracking = false));
  }

  Object.assign(AWL, { initGallery });
})(window.AWL = window.AWL || {});
