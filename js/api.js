/**
 * Tiny client for the Google Apps Script Web App (see google-apps-script/Code.gs).
 *
 * - POST uses Content-Type text/plain so the browser sends a "simple" request
 *   (no CORS preflight, which Apps Script can't answer). The body is still JSON.
 * - GET returns only public data: { name, message } per wish.
 * - `rsvp.event` picks this invitation's tab in the shared spreadsheet. Before
 *   the first RSVP is sent, the server must confirm it knows that event (an
 *   older script would otherwise file it under the default tab).
 */
(function (AWL) {
  "use strict";
  const WEDDING_CONFIG = window.WEDDING_CONFIG;
  const { fetchWithTimeout } = AWL;

  const { rsvp } = WEDDING_CONFIG;
  const URL_PATTERN = /^https:\/\/script\.google\.com\/(?:a\/macros\/[^/]+|macros)\/s\/[\w-]+\/exec$/;

  const apiUrl = () => (rsvp.apiUrl || "").trim();
  const isApiConfigured = () => URL_PATTERN.test(apiUrl());
  const eventKey = () => (rsvp.event || "").trim();

  class ApiError extends Error {
    constructor(kind, message, detail) {
      super(message);
      this.kind = kind; // "network" | "timeout" | "server" | "rejected" | "config"
      this.detail = detail;
    }
  }

  async function readJson(res) {
    const text = await res.text();
    try {
      return JSON.parse(text);
    } catch {
      throw new ApiError("server", "Respons server tidak valid.", text.slice(0, 200));
    }
  }

  async function call(url, options) {
    if (!isApiConfigured()) throw new ApiError("config", "RSVP belum dikonfigurasi.");
    let res;
    try {
      res = await fetchWithTimeout(url, { cache: "no-store", redirect: "follow", ...options }, rsvp.requestTimeoutMs);
    } catch (err) {
      if (err && err.name === "AbortError") throw new ApiError("timeout", "Permintaan terlalu lama.");
      throw new ApiError("network", "Tidak dapat terhubung ke server.");
    }
    if (!res.ok) throw new ApiError("server", `Server error (${res.status}).`);
    const data = await readJson(res);
    if (!data || data.ok !== true) {
      throw new ApiError("rejected", (data && data.error) || "Permintaan ditolak server.", data);
    }
    return data;
  }

  const notReady = () => new ApiError("config", "RSVP belum dikonfigurasi.");

  function getUrl(action) {
    const u = new URL(apiUrl());
    u.searchParams.set("action", action);
    if (eventKey()) u.searchParams.set("event", eventKey());
    u.searchParams.set("_", String(Date.now())); // defeat intermediary caches
    return u.toString();
  }

  /** Resolves once the server has confirmed it stores this invitation's RSVPs in their own tab. */
  let eventConfirmed = null;
  function confirmEvent() {
    const key = eventKey();
    if (!key) return Promise.resolve();
    if (!eventConfirmed) {
      eventConfirmed = call(getUrl("ping"), { method: "GET" }).then((data) => {
        if (!Array.isArray(data.events) || !data.events.includes(key)) throw notReady();
      });
      eventConfirmed.catch(() => (eventConfirmed = null)); // ask again next time
    }
    return eventConfirmed;
  }

  async function getWishes() {
    if (!isApiConfigured()) throw notReady();
    const data = await call(getUrl("wishes"), { method: "GET" });
    if (eventKey()) {
      // An older script ignores `event` and would return another invitation's wishes.
      if (data.event !== eventKey()) throw notReady();
      eventConfirmed = Promise.resolve();
    }
    return data;
  }

  async function submitRsvp(payload) {
    if (!isApiConfigured()) throw notReady();
    await confirmEvent();
    return call(apiUrl(), {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify({ action: "rsvp", ...(eventKey() ? { event: eventKey() } : {}), ...payload }),
    });
  }

  Object.assign(AWL, { apiUrl, isApiConfigured, ApiError, getWishes, submitRsvp });
})(window.AWL = window.AWL || {});
