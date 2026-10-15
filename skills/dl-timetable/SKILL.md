---
name: dl-timetable
description: Use when asked about David Lloyd class times or timetables (Cyclone, Blaze, Rhythm, Pilates, any DL class) across one or more clubs, when comparing clubs for a weekly schedule, or when putting David Lloyd classes onto a calendar.
---

# David Lloyd timetable

The davidlloyd.co.uk timetable page is JavaScript-rendered: WebFetch and curl return an empty "Club timetable" shell. Do not scrape it and do not reverse engineer the bundle. The app backend is open and has everything.

## Pull the data

```bash
python3 -I scripts/dl_timetable.py --clubs cheam,purley,kidbrooke --match cyclone
python3 -I scripts/dl_timetable.py --help
```

One row per weekly slot: day, time, duration, club, class name, studio, and whether it is `weekly` (seen on 2+ dates) or `one-off`. `--days`, `--after`, `--before` narrow the output, so run it once for weekdays and once for weekends when the constraints differ. `--json` for machine use.

Endpoints, if you need them directly: `GET https://mobile-app-back.davidlloyd.co.uk/clubs` (siteId by clubName) and `GET /clubs/{siteId}/sessions/timetable` (`sessionsDetails[]` with `date`, `startTime`, `duration`, `name`, `locations`, `status`, `instructorNames`). No auth, no key.

## Reading the output

- The API carries full detail for roughly the next 2.5 weeks, then only a few courses. The script prints the full-data window; anything outside it is ignored. Timetables rotate termly, so a calendar built from this needs a re-run when the term changes.
- `status: cancelled` sessions are hidden on the website. A slot that only ever appears cancelled, or appears once, is not a weekly class. Say so rather than dropping it silently; the user will ask.
- Some slots alternate week to week (live one week, virtual the next; CYCLONE one week, CYCLONE FTP Ride the next). They show as two one-offs at the same day and time. Merge them into one calendar entry and name both.
- Class name variants matter: "CYCLONE", "CYCLONE On Screen - Virtual", "CYCLONE FTP Ride", "CYCLONE Taster". Confirm which the user wants before filtering.

## Building a schedule

1. Agree the constraints first: home and work locations, working hours, which clubs on which days, transport (motorcycle beats Google Maps car times, car on the weekend), earliest acceptable start after work, preferred times, class variants.
2. Travel threshold per club = departure + journey + 10 min to change + the user's contingency. Flag slots inside the contingency as tight rather than dropping them.
3. Present the filtered table in chat and get a yes before writing anything to a calendar.
4. Calendar events: one weekly recurring event per slot (`RRULE:FREQ=WEEKLY;BYDAY=XX`), duration from the timetable, marked free, title `Cyclone Virtual - Purley` style, description carrying class name, studio and travel estimate. Check the target calendar for existing entries first.

## Checking a claim visually

To show the user what the website displays for a given day, headless Chrome renders it:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --user-data-dir=/tmp/dl-chrome --virtual-time-budget=15000 --window-size=1200,9000 \
  --screenshot=/tmp/dl.png "https://www.davidlloyd.co.uk/clubs/<slug>/timetable/"
```

Crop into 1500px tiles with `sips -c 1500 1200 --cropOffset <y> 0` before reading. The page only renders the selected day (today by default); other days need a click, which this does not do.
