# Garage Sale Run — Handoff Notes

**File:** `garage-sale-map.html` (single self-contained HTML file — no build step, no dependencies to install)
**Current version:** v1.2 (see `#version-stamp` div for live version/timestamp shown bottom-left of the app)

## What it does

A tool for planning a bike route to garage sales. You paste a list of addresses, it
geocodes and plots them as pins on a map, tracks which ones you've visited, and can
suggest a route to the nearest unvisited ones from your current location.

## Core stack

- **Leaflet.js** (via cdnjs) for the map, tiles from OpenStreetMap
- Vanilla JS, no framework, no build tools — just open the file
- **`window.storage`** (Claude.ai artifact persistence API) for saving state, with a
  `localStorage` fallback for when it's run outside Claude.ai (see Known Constraints below)

## Data model

Each address is an object in the `addresses` array:
```js
{ id, raw, lat, lon, visited: bool, error: bool, source: 'Census'|'OpenStreetMap'|'Photon'|'Manual' }
```
Persisted as JSON under storage key `garage-sale-addresses`.

## Features implemented so far

1. **Paste-and-geocode** — textarea accepts one address per line. Duplicate lines
   (by exact string match, case-insensitive) are skipped automatically.
2. **Three-tier geocoding fallback**, tried in order until one succeeds:
   - US Census Bureau geocoder (`geocoding.geo.census.gov`) — primary, best for US
     addresses since it uses TIGER/Line address-range interpolation (covers streets
     OSM hasn't manually mapped)
   - Nominatim / OpenStreetMap (`nominatim.openstreetmap.org`) — fallback
   - Photon (`photon.komoot.io`) — second fallback, different OSM search index/parser
   - Whichever source succeeds is recorded on the address (`source` field)
3. **Manual placement fallback** — addresses that fail all 3 geocoders show up in a
   "couldn't locate" list with a "Place on map" button; clicking it arms a
   click-to-place mode so the user can drop the pin themselves by tapping the map.
   This list persists across sessions (recomputed from `addresses` on load).
4. **Cancel mid-geocode** — a Cancel button appears during batch processing; checked
   between each address so it stops cleanly and keeps whatever was already geocoded.
5. **Live progress** — shows "X found, Y failed so far" during processing, plus the
   map auto-fits to bounds roughly every 10% of the batch (not just at the end).
6. **Visited tracking** — click a pin's popup → "Mark visited" toggles `visited` and
   flips pin color (red = unvisited, green = visited). Saved immediately.
7. **Geolocation, with a big caveat** — `navigator.geolocation.watchPosition` for a
   live-updating blue dot. **This does not work inside Claude.ai's chat/artifact
   preview** (sandboxed iframe has no geolocation permission delegation — calls fail
   immediately without ever prompting the user). Works fine as a real hosted page
   (GitHub Pages, Netlify, etc.) opened directly in a phone browser.
8. **Manual location fallback** — "Set location by tapping map" button arms a
   click-to-set-location mode, for when GPS isn't available/granted.
9. **Nearest-5 routing with 3 selectable algorithms** (dropdown in the Ride tab):
   - `nearest` — greedy nearest-neighbor chain (fast, default)
   - `optimal` — brute-forces all 120 permutations of the 5 nearest candidates,
     picks the shortest total path (cheap at this size, always at least as good)
   - `twoopt` — nearest-neighbor chain, then 2-opt local search to remove
     crossed/inefficient legs
   - All three use **straight-line (haversine) distance**, not road distance. Real
     bike-road routing (e.g. via BRouter or OSRM's bike profile) was discussed as a
     future addition but not yet built.
   - Draws a dashed polyline on the map and generates a Google Maps bicycling
     directions link (`google.com/maps/dir/?api=1&...&travelmode=bicycling`) with the
     route's waypoints for actual turn-by-turn navigation.
10. **All-addresses list tab** — separate tab listing every plotted address with a
    visited/unvisited color dot. Sortable (order-added / A–Z) and filterable
    (all / visited / not visited). Clicking a row pans+zooms the map to that pin and
    opens its popup (uses a `markerById` lookup map maintained in `renderPins()`).
11. **Collapsible sidebar** — "Hide panel" button slides the sidebar out via a
    negative-margin CSS transition; a floating "☰ Show panel" button brings it back.
    Calls `map.invalidateSize()` after the transition so Leaflet redraws correctly.
12. **Reset all** — clears all stored addresses/visited state after a confirm dialog.
13. **Version/timestamp stamp** — bottom-left corner, manually bumped by hand on each
    file revision (not automated — just a hardcoded string in the HTML, update it
    with each new version you generate).

## UI structure

- Header: title, live stats (total/visited/remaining), Hide-panel + Reset buttons
- Left sidebar, tabbed: **Ride** (location + routing) / **All addresses** (list) /
  **Add addresses** (paste box + geocoding progress + failed-list)
- Main area: the Leaflet map, full height

## Known constraints / things to watch for

- **`window.storage` only exists inside Claude.ai's artifact sandbox.** The file
  detects this (`hasClaudeStorage` check) and falls back to `localStorage` — but
  `localStorage` still requires a real origin (http/https), not `file://`. If opened
  as a downloaded local file, storage AND network fetches (geocoding) both silently
  fail. There's a `#file-warning` banner that detects `location.protocol === 'file:'`
  and explains this to the user.
- **Geolocation requires a secure context** (https, or `localhost`) on most modern
  mobile browsers. A `file://` page or a local-network IP over plain http will not
  get GPS on a phone — only `localhost` (same machine) or real https will.
- **Nominatim has a 1 req/sec rate-limit policy** — the geocode loop paces itself
  with a 250ms delay between addresses as a courtesy since Census (the primary) has
  no such limit; if Census starts failing a lot and it's falling back to Nominatim
  frequently, consider slowing the pace back down.
- The three geocoders occasionally disagree or one may go down temporarily — the
  `source` field on each address records which one actually resolved it, useful for
  debugging accuracy issues.

## Ideas discussed but not yet built

- Real bike-road routing (BRouter or OSRM bike profile) instead of straight-line
  distance for the nearest-5 feature
- Auto-mark-visited by GPS proximity (with undo)
- A third pin state beyond visited/unvisited (e.g. "no one home / skip")
- Bulk actions (mark all in an area visited, hide visited pins from map)

## Deployment notes

This was built and iterated on inside a Claude.ai chat, using the in-chat artifact
preview for quick iteration. That preview cannot grant GPS permission and runs
`window.storage` — neither of which exist in a normal browser tab. For actual field
use (biking around with a phone), the file needs to be hosted somewhere with a real
`https://` address — GitHub Pages and Netlify Drop were both discussed and work with
zero server-side code, since this is a fully static/client-side file.
