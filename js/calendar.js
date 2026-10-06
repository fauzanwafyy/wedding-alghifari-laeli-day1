/**
 * "Save the Date": builds Google Calendar event-template URLs from config.
 * No OAuth needed; Google Calendar opens with everything pre-filled.
 *
 * No end time is ever invented: when an event has no `endTime`
 * (e.g. "10.00 WIB – selesai"), the entry ends at the same moment it starts
 * (Google Calendar requires an end value) and the description carries the
 * official wording. Day 1's Resepsi has a real end time (09.00 – 21.00 WIB).
 */
(function (AWL) {
  "use strict";
  const { formatTime, eventMoment } = AWL;

  const toGoogleDate = (iso) =>
    new Date(iso).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, ""); // 20261020T020000Z

  /** "Resepsi: 09.00 WIB – 21.00 WIB" (or "… – selesai" when there is no end time) */
  function eventLine(ev, tz) {
    const end = ev.endTime ? ` – ${formatTime(ev.endTime)} ${tz}` : ev.endText ? ` – ${ev.endText}` : "";
    return `${ev.title}: ${formatTime(ev.startTime)} ${tz}${end}`;
  }

  function eventRange(ev) {
    const start = eventMoment(ev.date, ev.startTime);
    const end = ev.endTime ? eventMoment(ev.date, ev.endTime) : start;
    return `${toGoogleDate(start)}/${toGoogleDate(end)}`;
  }

  function buildCalendarDetails(config, siteUrl, onlyEvent) {
    const { calendar, events, venue, wedding } = config;
    const tz = wedding.timezoneLabel || "WIB";
    const lines = [calendar.description, ""];
    (onlyEvent ? [onlyEvent] : events).forEach((ev) => lines.push(eventLine(ev, tz)));
    lines.push("", venue.name, venue.address, `Google Maps: ${venue.mapsUrl}`);
    if (siteUrl) lines.push("", `Undangan: ${siteUrl}`);
    return lines.join("\n");
  }

  function calendarUrl(params) {
    return `https://calendar.google.com/calendar/render?${new URLSearchParams(params).toString()}`;
  }

  const defaultLocation = ({ calendar, venue }) => calendar.location || `${venue.name}, ${venue.address}`;

  /** Main "Save the Date": the wedding day, starting at the first event. */
  function buildGoogleCalendarUrl(config, siteUrl = "") {
    const { calendar, wedding, events } = config;
    return calendarUrl({
      action: "TEMPLATE",
      text: calendar.title,
      dates: eventRange(events[0]),
      details: buildCalendarDetails(config, siteUrl),
      location: defaultLocation(config),
      ctz: wedding.timezone || "Asia/Jakarta",
    });
  }

  /** One entry per event ticket (Day 1: Resepsi 09.00 – 21.00). */
  function buildEventCalendarUrl(config, ev, siteUrl = "") {
    const { calendar, wedding } = config;
    return calendarUrl({
      action: "TEMPLATE",
      text: `${ev.title}${calendar.eventTitleSuffix || ""}`,
      dates: eventRange(ev),
      details: buildCalendarDetails(config, siteUrl, ev),
      location: ev.venue && ev.address ? `${ev.venue}, ${ev.address}` : defaultLocation(config),
      ctz: ev.timezone || wedding.timezone || "Asia/Jakarta",
    });
  }

  Object.assign(AWL, { buildCalendarDetails, buildGoogleCalendarUrl, buildEventCalendarUrl });
})(window.AWL = window.AWL || {});
