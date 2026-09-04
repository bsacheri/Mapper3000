# Garage Sale Run — Changelog

This file keeps track of everything that's been changed or added, version by
version, written in plain simple language. The little version number shown
in the bottom-left corner of the app should get bumped by hand every time a
new entry gets added here. **Click on the version stamp in the bottom-left
corner to see this whole changelog inside the app!**

## v1.27 — 2026-09-03

- **Fixed: drag-to-reorder in manual mode now works correctly.** The
  implementation used pointer-event capture on the drag handle. Drag-reorder
  works by calling `insertBefore()` on every `pointermove` to show live visual
  feedback — but `insertBefore` on an already-attached node does an implicit
  remove-then-reinsert, which silently releases any pointer capture set on a
  child of that node (per the Pointer Events spec). After the first move,
  capture was gone, so later `pointerup` only reached the handler if the pointer
  happened to still be physically over the handle's relocated position (usually
  not the case) — making the drag appear stuck forever. Moved all event
  listeners from the handle to `document`, which is never reparented, so
  capture state is irrelevant. The drag now completes reliably.
- **Route lines are now blue** (#2E86FF) instead of red, matching the "You are
  here" marker and nav buttons for visual consistency.

## v1.26 — 2026-09-02

- **Fixed: the local server could freeze the whole page while fetching a
  route.** `server.py` used a plain `HTTPServer`, which can only handle one
  connection at a time — while it was waiting on a slow ORS or MapQuest
  response (anywhere from a couple seconds up to its 30-second timeout), it
  couldn't serve *anything* else, including the map page itself. Switched to
  `ThreadingHTTPServer` (Python's drop-in threaded replacement), confirmed
  with a controlled test: under the old server a page request made mid-fetch
  waited 2.34s behind a simulated 2.5s-slow proxy call; under the new one it
  returned in under a hundredth of a second, completely unaffected.

## v1.25 — 2026-09-01

- **MapQuest added as a second road-routing option.** Settings → Road
  Distances now has a **Service** dropdown: None (straight-line), OpenRouteService,
  or MapQuest. If ORS's quota runs out, switch to MapQuest from that one menu —
  your addresses, algorithm, and everything else stay exactly as they were.
  MapQuest needs its own free API key from developer.mapquest.com. Its free
  tier is a one-time allotment of transactions rather than a daily reset like
  ORS, so it's best used as backup/overflow rather than a full replacement.
- **MapQuest has one general "Bicycle" mode**, not ORS's separate regular/
  e-bike/road/mountain profiles — it's a different service with a coarser set
  of options, not a bug.
- **Draw road paths on map now works with either provider.** The checkbox
  moved out of the OpenRouteService-only panel and applies regardless of
  which service is active.
- **Saved lists now also remember which service and route type were active**
  (not the API keys — those stay device-only, same as before). Restoring an
  older list that predates this leaves your current service choice alone.
- **The request-count meter now works for whichever service is active**,
  labeled by name so it's clear which one's usage it's showing.
- **Existing "use real road distances" and "draw road paths" choices carry
  forward automatically** — this update replaces the on/off checkbox with the
  Service dropdown, but anyone already using OpenRouteService is switched to
  it under the hood rather than reset to "None."

## v1.24 — 2026-08-31

- **Fixed: Avoid highways / Avoid toll roads / Avoid ferries never actually
  did anything.** Checking one of these three boxes updated the checkbox
  itself but silently wrote to the wrong internal setting (a leftover string-
  transform bug turned "avoid-highways" into a setting named "highways"
  instead of "avoidHighways"), so the Google Maps link never picked up the
  avoidance, the choice never survived a page reload, and it was never
  something a saved list could capture. All three now write to the correct
  setting and actually affect the Google Maps link.
- **Saved lists now also remember avoid highways / tolls / ferries.** Restoring
  a list puts all three checkboxes back the way they were when it was saved,
  and the list's summary line says which ones (e.g. “avoids
  highways/ferries”).

## v1.23 — 2026-08-31

- **Fixed: the Ride tab's "Travel mode" wasn't saved with a list.** There are
  two different settings that both ended up labeled similarly: the Settings
  modal's Google Maps travel mode (bicycling/driving/walking/transit), and the
  Ride tab's **Travel mode** dropdown, which is actually the OpenRouteService
  cycling profile (regular bike / e-bike / road bike / mountain bike / walking
  / driving). Saved lists already captured the first one; the second — the
  one visible right on the Ride tab while you're actually planning — was
  never included. It's now part of the same snapshot, and a list's summary
  shows which one it has saved (e.g. “Regular bike — uses trails &
  gravel”), pulled directly from the dropdown's own option text so the two
  can't drift out of sync with each other again.

## v1.22 — 2026-08-31

- **A manually-set location now survives a page reload.** Tapping the map to
  set your location used to be forgotten the moment you refreshed — GPS
  tracking naturally re-fixes on its own, but a tapped pin had nothing bringing
  it back, so you had to re-tap every time. It's now remembered and restored
  automatically, with a note in the location status explaining where it came
  from. GPS positions are never persisted this way, since a live fix goes
  stale the instant you move and re-requesting GPS is the better fix.
- **Manually-set locations are now saved with address lists, too.** If your
  location was set by tapping the map (not GPS) when you save a list, that
  spot is stored alongside it and put back when you restore. A saved list's
  summary now says “saved location” when it's carrying one. Restoring a list
  also updates your remembered location for future reloads.
- **Reset all now also clears the remembered manual location**, matching how
  it already clears the saved manual route order.

## v1.21 — 2026-08-31

- **Fixed: saved lists were missing the number of stops and return-to-start.**
  Saving a list already remembered the travel mode and routing algorithm, but
  silently dropped the "Number of stops" and "Return to starting point"
  settings — restoring a list always put stop count back to whatever it
  happened to be, and always left return-to-start unchecked. Both are now part
  of what gets saved, and each row's summary shows them (e.g. “12 addresses
  · saved 8/31/2026 · bicycling · manual order · 20 stops · round trip”).
  **Note:** lists saved before this fix don't have these two fields recorded,
  so restoring them will leave your current stop count and return-to-start
  setting alone rather than guessing — use Overwrite on an old list to bring
  it up to date.

## v1.20 — 2026-08-31

- **Overwrite a saved list.** Each saved list now has an **Overwrite** button
  that replaces it with whatever is currently loaded, keeping the same name.
  It asks first, and the message tells you how many addresses are about to
  replace how many — so you can back out if you picked the wrong row.
- **Delete is now a trashcan button, and it asks first.** Deleting a saved list
  used to happen instantly on a single click with no way back. It now uses a
  trashcan icon and confirms before removing anything.
- **Saved lists remember the travel mode and routing algorithm.** Saving a list
  stores the Google Maps travel mode and the routing algorithm alongside the
  addresses, and restoring puts both back. Each row shows what it has stored,
  so you can see what a Restore will change before clicking it. If the saved
  algorithm was *Manual order*, your arranged sequence comes back too — it is
  stored as positions rather than internal ids, which is what lets it survive a
  restore. Lists saved before this update simply leave your current settings
  alone.
- **Copy the visible list from the All addresses tab.** A **Copy this list**
  button copies exactly what is on screen, honouring the active filter (all /
  visited / not visited) and sort. Sorting by route order numbers the lines so
  the sequence carries across; the other sorts copy plain addresses.
- **Fixed: confirmation dialogs could open behind other dialogs.** The confirm
  box sat below the Settings, Help, and Saved-lists windows in the stacking
  order, so any confirmation raised from inside one of those would have been
  invisible and unclickable. It now sits above them.

## v1.19 — 2026-08-31

- **Removed the "Optimize for" dropdown.** The choice between shortest distance
  and fastest time barely changed anything in practice — on ordinary
  neighbourhood riding, time is close enough to distance divided by a steady
  speed that both settings produced near-identical stop orders. Routes are once
  again always ordered by shortest distance. The estimated ride time is still
  shown next to the total in the heading; only the choice is gone.

## v1.18 — 2026-08-31

- **The route button now says what it actually does in Manual order mode.**
  It used to keep reading *"Find nearest 5 & route"* even while manual ordering
  was active, which made it look like clicking it would re-sort your stops. It
  never did — in manual mode it only redraws the map line, leg distances,
  heading total, and Google Maps link from the order you arranged. The button
  now reads **"Redraw route (keeps my order)"** so that's obvious, and the
  algorithm hint says the same thing.

## v1.17 — 2026-08-31

- **Fixed: routing choices were forgotten on every page load.** The number of
  stops, the routing algorithm, and the return-to-start tick box were never
  saved, so every reload quietly put them back to 5 stops / nearest-neighbor /
  unticked. This was most visible with the new *Manual order* mode: your
  arranged order was still saved, but the mode itself wasn't, so the drag
  handles vanished after a refresh and the route came back re-optimized. All
  three now persist, and a saved value that no longer matches a real option
  falls back to the default instead of leaving the dropdown stuck.
- **Changing stops or return-to-start now re-routes immediately**, matching how
  the other routing controls already behaved.

## v1.16 — 2026-08-31

- **Manual route ordering.** The routing algorithm dropdown has a new option,
  *Manual order (drag to arrange)*. Pick it and each stop in the route list
  grows a ⠿ handle you can drag to put the stops in whatever order you want.
  Distances, the heading total, the map line, and the Google Maps link all
  update as soon as you let go. It seeds from the last route you built, so the
  natural workflow is to optimize first and then tweak the couple of stops that
  need it.
- **Duplicate a stop with "Save as copy".** Click the ✏️ on any pin, give it a
  new label, then hit *Save as copy* instead of *Save*. You get a second pin at
  the same place. This is for trips where you pass somewhere twice — drop the
  dog at the groomer, hit the mechanic, then swing back for the dog.
  **The copy only helps in Manual order mode**: two stops at the same address
  are zero distance apart, so every optimizer will always put them back to back
  rather than spacing them out. Manual ordering is what lets you separate them.
- **Route recalculations no longer re-hit the API.** The last road-distance
  matrix is now cached, so dragging a stop, toggling return-to-start, or
  switching between distance and time reuses it instead of spending another
  OpenRouteService request. A fresh request is made only when the stops, your
  location, or the cycling profile actually change.
- **Reordering is safe when the stop count is small.** If you arrange ten stops
  and then drop the count to five, rearranging the visible five no longer
  discards the other five — they keep their saved positions and come back when
  you raise the count again.

## v1.15 — 2026-08-31

- **Route total shown in the heading.** Once a route is planned, the "Nearest
  unvisited stops" heading shows the total distance and, when road routing is
  on, the estimated ride time — e.g. *"Nearest unvisited stops — 8.4 mi ·
  47 min"*. With road routing off it shows distance only, labelled
  "straight-line" so you know it's a crow-flies estimate.
- **Optimize for distance or time.** A new dropdown lets you pick whether the
  stop order minimizes total miles or total ride time. This costs no extra API
  calls — the travel times were already coming back in the same request that
  fetches distances, they just weren't being used.
- **Note on how much this actually changes things.** On flat, evenly-paved
  neighborhoods the two settings usually produce near-identical routes, since
  time is roughly distance divided by a constant speed. The difference grows
  when a route mixes surfaces or terrain — a crushed-limestone trail is slower
  per mile than pavement, so the fastest route may not be the shortest one.

## v1.14 — 2026-08-31

- **Cycling type picker moved into the Ride tab.** You no longer have to open
  Settings to change how you're riding. When road routing is on, a "Cycling
  type" dropdown appears right above the route button, with a one-line note
  explaining what each option does. It stays in sync with the same setting in
  the Settings modal — change it in either place and both update.
- **Default profile is now Regular bike, not Driving.** The app is built for
  bike routes, so defaulting to car routing was the wrong out-of-box choice.
- **Added E-bike as a profile option.** Same route preferences as a regular
  bike, but assumes you hold speed on hills (about 15% faster on a typical
  10-mile run).
- **Guidance on which profile to pick.** Only *Regular bike* reliably routes
  onto converted rail-trails and greenways — those are usually crushed
  limestone, and the *Road bike* profile treats unpaved surfaces as off-limits
  and will route around them entirely. *Mountain bike* is tuned for rough
  off-road terrain and tends to prefer streets over smooth trails. Verified
  against the Illinois Prairie Path: Regular used the trail for 80% of the
  route, Road bike used it for 0%.
- **More stop counts.** Added 20, 30, 40, and 49 to the number-of-stops
  dropdown (49 is the ceiling the free OpenRouteService tier allows).

## v1.13 — 2026-08-31

- **OpenRouteService road routing.** A new "Road Distances (OpenRouteService)"
  section in Settings lets you enable real road-distance routing instead of
  straight-line (crow-flies) distances. Paste a free API key from
  openrouteservice.org, pick a routing profile (driving, regular cycling, road
  bike, mountain bike, or walking), and the app fetches an actual road-distance
  matrix before optimizing your stop order. The route list shows "road mi"
  when ORS is active. If ORS is unavailable or the key is missing, the app
  falls back to straight-line distances automatically with a red notice.
- **Draw actual road paths on map (optional).** When ORS is enabled, an extra
  checkbox lets you replace the dashed straight lines with polylines that follow
  real streets. This uses one additional ORS API call per route.
- **All three routing algorithms (nearest-neighbor, optimal, 2-opt) use road
  distances** when ORS is active — the existing Held-Karp and 2-opt code was
  updated to accept a pluggable distance function rather than always using
  haversine.

## v1.12 — 2026-08-05 21:15 UTC

- **Edit pin descriptions with a pencil icon.** When you click on a pin, the
  popup now has a blue pencil icon button (fourth icon in the row) that opens
  an edit dialog. You can change the address text or description, hit Enter or
  click Save, and the change is immediately saved and reflected in the address
  list. Handy for fixing typos, adding notes, or updating what's being sold at
  each location.

## v1.11 — 2026-08-05 21:00 UTC

- **Tablet landscape now uses side-by-side layout instead of stacking.** The
  split (panel-above-map with a resize handle) was applying to all tablets up
  to 1024px wide, regardless of orientation. Tablets in landscape have plenty
  of horizontal room for the normal side-by-side desktop layout, so now they
  use it — panel as a full-height sidebar, map filling the entire remaining
  width and height. Tablets in portrait still get the stacked layout with the
  resizer (since vertical space is tight). Phone portrait (below 600px) always
  stacks. All three orientations now fit their screen properly with nothing
  overflowing or getting squashed.

## v1.10 — 2026-08-05 20:45 UTC

- **Fixed tablets getting the tiny phone-sized header.** The drag-to-resize
  panel/map split intentionally applies to both phones and tablets, but the
  shrunken header text and cramped stat pills meant for narrow phone screens
  were accidentally applying at tablet widths too, making a full-size tablet
  look stuck in "mobile mode." Tablets now keep the normal full-size header
  while still getting the stacked panel-above-map layout and resize handle.

## v1.9 — 2026-08-05 20:15 UTC

- **Pin popup buttons are now icons in a single row.** "Mark visited",
  "Navigate to", and "Remove" used to stack as three text buttons that could
  crowd out the address itself in the small popup bubble. They're now three
  round icon buttons side by side: a checkmark (or an undo arrow once
  visited) for visited status, a paper-plane/compass arrow for navigate, and
  a trash can for remove. Each still has a tooltip on hover/long-press.

- **Fixed "Select box" not working on phones/tablets at all.** It only
  listened for mouse drag events, which touchscreens never fire — so the
  crosshair cursor would appear but dragging did nothing. It now uses
  Pointer Events, which cover mouse, touch, and pen the same way, so drawing
  a selection rectangle with your finger works the same as dragging with a
  mouse. Also swapped the "no pins in that box" alert() popup (unreliable on
  some mobile/PWA setups) for a quick inline message on the button itself.

- **Fixed address-list centering being off on short mobile screens.**
  Selecting an address now waits for the map's pan/zoom to fully settle
  before opening its popup (opening it mid-animation was reading a stale
  view), and the target center is nudged to account for the popup's height
  so the pin-plus-popup lands as a centered group instead of the popup's
  top getting clipped off on a short map viewport.

## v1.8 — 2026-08-05 19:00 UTC

- **Right-click (or long-press on mobile) anywhere on the map to drop a new
  pin.** A small box pops up asking for a description — like a family name
  or what's for sale — and adds it as a pin right where you clicked/pressed.
  No address lookup needed since you're placing it exactly where you want it.

- **Clicking an address in "All addresses" now reliably centers it on the
  map.** Previously the popup that opened above the pin could nudge the map's
  auto-pan and shift the pin away from center, especially on a short mobile
  map view. That auto-pan is now suppressed for this specific action, so the
  pin lands dead-center every time.

- **Drag handle to resize the map on phones and tablets.** Below a certain
  screen width, where the address panel stacks above the map instead of
  beside it, there's now a small grip bar between the two you can drag up or
  down to trade space between them. Your preferred split is remembered for
  next time.

- **"Reset all" moved out of the header and into "Add addresses."** It's now
  at the bottom of the Add Addresses tab under a "Danger zone" heading,
  instead of sitting in the header next to "Hide panel." Clicking it now
  shows a proper confirmation box explaining exactly what will be erased
  (every address, pin, and visited status) before doing anything — the old
  version used a plain browser confirmation popup that silently failed to
  appear in some environments, so the button looked broken.

- **Fixed the header growing an extra row when toggling "Hide/Show panel"
  on phones.** The stats-and-button row could occasionally wrap onto two
  lines depending on the button's exact text width. It's now locked to a
  single row on narrow screens.

## v1.7 — 2026-08-05 17:30 UTC

- **Fixed the map buttons floating in the wrong place on phones.** "Fit all
  pins" and "Select box" were positioned relative to the whole app instead of
  the map itself. On a phone (where the address panel stacks above the map
  instead of beside it) that meant the buttons floated over the *panel*, not
  the map. They now live inside the map's own container, so they always land
  in the map's top-right corner no matter how the layout is arranged.

- **Fixed "Hide panel" only partly hiding the panel on phones.** The old
  collapse trick shifted the panel sideways by a fixed 320 pixels — fine on a
  desktop where the panel really is 320px wide, but on a phone the panel is
  full-width, so 320px of shift left a chunk of it still hanging off the edge
  of the screen, and the panel's vertical space stayed reserved (an empty gap
  above the map) since phones stack panel-then-map instead of side-by-side.
  On phones it now collapses by height instead of by sideways position, so it
  disappears completely and the map actually gets the freed-up room.

- **"Hide panel" is now a single toggle button.** It used to pair with a
  separate floating "☰ Show panel" button that appeared over the map once
  you'd hidden the sidebar. That extra button is gone — the same header
  button now just flips between "Hide panel" and "Show panel" depending on
  the current state.

- **Bigger buttons and confirmation dialogs on phones.** The map toolbar
  buttons and the confirmation pop-ups (like "Remove 3 selected pins?") now
  use larger tap targets and don't overflow the screen width on narrow
  phones — the "Mark visited / Not visited / Remove / Cancel" buttons wrap
  into a neat 2-column grid instead of a cramped single row.

- **New "My location" button on the map.** Once you've tracked your GPS
  location (or tapped the map to set it manually), a new button appears in
  the map's top-right corner next to "Fit all pins" and "Select box". Tap it
  anytime to snap the map back to where you are — handy after you've scrolled
  or zoomed away while planning your route.

## v1.6 — 2026-08-05 15:45 UTC

- **"Try again" button for addresses that failed geocoding.** In the "Add
  addresses" tab, when an address couldn't be auto-located by any of the 3
  lookup services, it now shows a "Try again" button right next to the address.
  Click it to re-attempt geocoding — maybe the service is back online or had a
  temporary hiccup. If it succeeds, the address disappears from the failed list
  and gets added to your map. Super handy for addresses that temporarily failed
  due to network issues or service problems.

- **Click an address to zoom to its approximate location.** For addresses that
  still can't be found, you can now click on the address text itself (it's
  underlined as a hint) to zoom the map to an approximate location — usually
  the city or street the address mentions. This gives you a starting point so
  you can then manually place the pin more accurately instead of dropping it
  blindly on the wrong side of the state. The app extracts the city and state
  from the address and finds that, so you see roughly where to look.

## v1.5 — 2026-08-05 14:20 UTC

- **Progressive Web App (PWA) support for mobile installation.** The app now
  works as a standalone mobile app! On iOS, you can add it to your home screen
  using "Add to Home Screen" from Safari's share menu. On Android, after visiting
  the app in Chrome you'll see an "Install" prompt to add it to your home screen.
  Once installed, it runs full-screen like a native app, includes a custom icon
  and theme color, and even works offline using cached resources. Perfect for
  taking into the field on a phone during your garage sale bike route without
  needing to open a browser.

- **"Remove" option when selecting multiple pins.** When you draw a rectangle
  around a bunch of pins to select them, you now get a "Remove" button along
  with the "Mark as visited" and "Mark as NOT visited" buttons. Click it and
  you'll be asked to confirm before those pins disappear from the map. Great
  for cleaning up pins you changed your mind about after plotting them.

- **Formatted addresses with better readability.** Addresses now display on
  multiple lines: description on top, street address on the second line, and
  city/state/zip on the third line. This makes the address list and pin popups
  way easier to scan and understand at a glance instead of one long comma-
  separated line.

- **Escape key now closes any open modal dialog.** Whether it's a selection
  modal, a confirmation dialog, or the changelog popup, pressing Escape will
  close it immediately. Makes the app feel more responsive and standard.

## v1.4 — 2026-08-05 06:15 UTC

- **Click the version number to see this changelog inside the app.** The
  little version stamp in the bottom-left corner (like "v1.4 · 2026-08-05
  06:15 UTC") is now clickable — click it and a popup appears showing you
  this whole changelog with nice formatting. It's a way to quickly remind
  yourself what changed in each version without having to find the file.

- **"Fit all pins" button on the map.** In the top-right corner of the map
  there's now a button that zooms the map out to show every single pin at
  once, so you can see your whole route. It's the same as when the app is
  first loading addresses and showing you progress — it fits everything in
  the view.

- **Automatic zoom when you add your first batch of addresses.** The first
  time you paste in a bunch of addresses and they get plotted, the map
  automatically zooms out to show all of them instead of zooming in on just
  one. It makes it way easier to get oriented.

- **Draw a rectangle to select multiple pins at once.** There's a new
  "Select box" button on the map (top-right, next to "Fit all pins"). Click
  it, then drag a rectangle around a bunch of pins on the map. When you let
  go, it shows you how many pins you selected and asks whether you want to
  mark them all as visited or all as not-visited. Great for when you get
  home and want to bulk-update a whole section of your route at once without
  clicking each pin individually.

## v1.3 — 2026-08-05 05:30 UTC

- **You can now pick how many stops to find at once: 5, 10, or 15.** Before,
  the app always looked for exactly 5 unvisited garage sales near you. Now
  there's a dropdown menu where you can ask for 5, 10, or 15 instead. It
  still defaults to 5 if you don't touch it.
- **Fixed the "best route" option so it doesn't freeze the app at 10 or 15
  stops.** There are 3 ways the app can decide what order to visit stops in:
  - *Nearest-neighbor*: just always walk to whichever stop is closest right
    now. Fast, but not always the smartest.
  - *2-opt*: does the nearest-neighbor thing first, then double-checks for
    any "X" shaped crossovers in the route and uncrosses them.
  - *Optimal*: tries to find the actual best possible order, guaranteed.

  The "optimal" one used to work by trying literally every possible order of
  stops and picking whichever one was shortest. That's fine when you only
  have 5 stops (there are only 120 different orders to check). But with 10
  stops there are 3.6 *million* orders, and with 15 stops there are over a
  trillion — the browser would basically lock up trying to check them all.
  So it now uses a smarter math trick (called Held-Karp, a well-known
  method for this exact kind of problem) that finds the same perfect answer
  without having to check every single possibility one by one. It's like
  the difference between trying every possible way to solve a maze versus
  remembering which turns already led to a dead end so you never repeat
  them. Now "optimal" solves 15 stops in about 1/25th of a second instead of
  never finishing.
- The "Find nearest 5 & route" button now updates its own text to say
  "Find nearest 10 & route" or "Find nearest 15 & route" depending on what
  you picked, so it's always clear what's about to happen when you click it.

## v1.2 (fixes made after the first release) — 2026-08-05 02:15 UTC

These are bugs that got fixed and new tools that got added, without changing
the version number yet (that happened with v1.3 above).

- **Fixed a crash that happened when sorting or filtering the address list.**
  In the "All addresses" tab there are buttons like "A–Z", "Visited", and
  "Not visited" that are supposed to just re-sort or filter the list. But
  they were accidentally sharing some styling code with the *main* tabs at
  the top of the app (Ride / All addresses / Add addresses). Because of that
  mix-up, clicking "A–Z" made the app think you were trying to switch to a
  whole different tab that doesn't exist, and it crashed trying to find
  something that wasn't there. Fixed by making sure only the *real* top tabs
  respond that way, and the sort/filter buttons just do their own job.

- **Figured out why some real addresses — like the church — were showing up
  as "couldn't find it" even though Google Maps finds them instantly.**
  This one took some digging. Here's what's actually going on:

  The app doesn't have just one way to turn an address into map coordinates
  — it has a backup plan with three tries, one after another:
  1. **US Census Bureau** — a US government service. It's really good at
     finding addresses on roads that are out in small towns or the
     countryside, because it uses official government road maps.
  2. **Nominatim (OpenStreetMap)** — a free, crowd-mapped service, kind of
     like Wikipedia but for maps. Great for a lot of places, but if nobody's
     mapped a particular street in detail, it might not know it.
  3. **Photon** — a third backup that searches a slightly different map
     index, in case the first two both miss.

  The app tries #1 first, and only moves on to #2 and #3 if #1 says it
  can't find the address. The problem was: **the Census service (the first
  and best one) was silently failing every single time**, for a sneaky
  reason. Web browsers have a security rule (called CORS) that blocks a
  webpage from asking a *different* website for data unless that website
  specifically says "yes, it's OK for other pages to ask me things." The
  Census website never says that, so the browser was blocking the request
  before it even got an answer back — even though the Census service
  genuinely *did* have the church's address the whole time! It's like
  calling someone who has the answer, but the phone company blocks your
  call before it even rings. Because Census kept silently failing, the app
  was falling back to Nominatim and Photon for every address — and those
  two just didn't have that particular church.

  The fix: since the phone call itself gets blocked, the trick is to have
  someone *else* make the call *for* you and just hand you the answer. That
  someone is a small helper program (`server.py`) that runs on your own
  computer. Now, instead of your browser trying to call Census directly
  and getting blocked, it asks the helper program on your own computer,
  and the helper program (which isn't a browser, so it doesn't have that
  CORS rule) makes the real call to Census and passes the answer back.
  Same information, just relayed through a middleman who isn't blocked.

  - One thing to know: if an address already failed once and is sitting in
    the "couldn't locate" list, just pasting it in again won't make the app
    try again — it recognizes the address as one it's already seen and
    skips it, even though last time it failed. For now, you have to remove
    it from the list first before re-adding it. (A proper "try again"
    button for this is on the list of future improvements.)

- **Added a double-click launcher (`start_server.bat`) for Windows.** At
  first, double-clicking it just started the helper program with a plain
  black command-prompt window and nothing else happened — no map, nothing.
  Fixed it so now double-clicking it starts the helper program *and*
  automatically opens the map app in your browser a couple seconds later,
  so it actually feels like something happened.

## v1.2 — original baseline features

This is the full list of everything the app already could do before this
round of changes, explained simply:

1. **Paste a list of addresses and it plots them.** You type or paste
   addresses into a text box, one per line, and it turns each one into a
   pin on the map. If you accidentally paste the same address twice, it
   quietly ignores the second copy instead of making a duplicate pin.
2. **Three-way address lookup, so it tries hard before giving up.** As
   explained above: it tries the US Census Bureau first, then Nominatim,
   then Photon, only moving to the next one if the previous one comes up
   empty. Whichever one actually finds the address gets remembered, so you
   can tell later which service was used.
3. **If all three lookups fail, you can drop the pin yourself.** Addresses
   that none of the three services could find show up in a "couldn't
   locate" list with a "Place on map" button. Click it, then tap the map
   wherever that address actually is, and it drops a pin right there. This
   list sticks around even if you close and reopen the app.
4. **You can stop in the middle of adding a big batch of addresses.** If
   you paste in 50 addresses and get impatient, there's a Cancel button.
   It finishes whichever address it's currently checking, then stops —
   keeping everything it already found instead of throwing it all away.
5. **You can watch it work in real time.** While it's looking up a big
   batch of addresses, it shows a progress bar and a running count like
   "12 found, 2 failed so far." The map also periodically zooms out to fit
   all the new pins as they come in, instead of making you wait for the
   very end to see anything.
6. **Tap a pin to mark it visited.** Click on any pin, and a little popup
   shows the address with a "Mark visited" button. Clicking it turns the
   pin from red (haven't been there) to green (already went), and it's
   saved right away so it remembers even if you close the app.
7. **It can track your live location on the map with GPS** — but only
   when the app is opened as a real webpage (like `http://localhost:8000`
   or a hosted `https://` link), not when it's running inside Claude.ai's
   built-in preview window, because that preview isn't allowed to ask for
   GPS permission at all.
8. **If GPS doesn't work, you can just tap the map to say "I'm here."**
   This is the backup for when GPS isn't available or you'd rather not use
   it — tap a button, then tap your real-world location on the map, and
   the app treats that as your current position.
9. **It can suggest the next 5 (or now, 5/10/15) closest sales to bike to.**
   You pick one of three routing styles (explained in the v1.3 section
   above — nearest-neighbor, 2-opt, or optimal), and it draws a dashed line
   on the map connecting the stops in the suggested order. It also builds
   you a ready-to-click Google Maps link with bicycling directions through
   all those stops.
10. **A full list of every address you've added, with sorting and
    filtering.** There's a separate tab that lists every single pin —
    visited or not — with a colored dot showing its status. You can sort
    it by the order you added things or alphabetically, and filter it down
    to just visited or just unvisited. Clicking any address in the list
    jumps the map straight to that pin and pops it open.
11. **You can hide the sidebar to see more map.** A "Hide panel" button
    slides the whole sidebar out of the way so the map takes up the full
    screen, with a small floating button to bring it back.
12. **A "Reset all" button to start completely fresh.** Wipes every saved
    address and visited status, after double-checking with you first since
    it can't be undone.
13. **A little version stamp in the corner.** Shows which version of the
    app you're looking at and when it was last updated, so you can tell at
    a glance whether you're running the latest copy.
