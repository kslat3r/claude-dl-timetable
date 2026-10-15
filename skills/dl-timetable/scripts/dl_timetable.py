#!/usr/bin/env python3
"""Pull David Lloyd club timetables and print the weekly pattern for matching classes.

The public website renders its timetable with JavaScript, so fetching the HTML
gives nothing. The app backend is open and returns the full sessions list.
"""
import argparse
import collections
import datetime
import json
import sys
import urllib.request

API = "https://mobile-app-back.davidlloyd.co.uk"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FULL_DAY_MIN_SESSIONS = 20


def fetch(path):
    request = urllib.request.Request(API + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def resolve_clubs(wanted):
    clubs = fetch("/clubs")["clubs"]
    resolved = {}
    for name in wanted:
        hits = [c for c in clubs if name.lower() in c["clubName"].lower()]
        if len(hits) != 1:
            sys.exit(f"club '{name}' matched {len(hits)} clubs: {[c['clubName'] for c in hits]}")
        resolved[hits[0]["clubName"]] = hits[0]["siteId"]
    return resolved


def weekday(date_string):
    return DAYS[datetime.date.fromisoformat(date_string).weekday()]


def weekly_pattern(sessions, match, days, after, before):
    """Group sessions into (day, time, name, duration, studio) slots with their dates.

    Only days that carry a full timetable count towards the window, because the
    API pads later weeks with a handful of courses and nothing else.
    """
    per_day = collections.Counter(s["date"] for s in sessions)
    full_days = sorted(d for d, n in per_day.items() if n >= FULL_DAY_MIN_SESSIONS)
    slots = collections.defaultdict(lambda: {"dates": [], "cancelled": []})
    for s in sessions:
        if match.lower() not in s["name"].lower():
            continue
        if s["date"] not in full_days:
            continue
        day = weekday(s["date"])
        if day not in days or not (after <= s["startTime"] <= before):
            continue
        key = (day, s["startTime"], s["name"], s["duration"], ", ".join(s["locations"]))
        bucket = slots[key]["dates"] if s["status"] == "active" else slots[key]["cancelled"]
        bucket.append(s["date"])
    return full_days, slots


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clubs", required=True, help="comma separated club names, substring match, e.g. cheam,purley,kidbrooke")
    parser.add_argument("--match", default="cyclone", help="case-insensitive substring of the class name (default: cyclone)")
    parser.add_argument("--days", default=",".join(DAYS), help="comma separated days, e.g. Mon,Tue,Wed,Thu,Fri")
    parser.add_argument("--after", default="00:00", help="earliest start time HH:MM, inclusive")
    parser.add_argument("--before", default="23:59", help="latest start time HH:MM, inclusive")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    parser.add_argument("--raw-dir", help="also save each club's raw timetable JSON into this directory")
    args = parser.parse_args()

    days = [d.strip().title() for d in args.days.split(",")]
    rows = []
    windows = {}
    for club_name, site_id in resolve_clubs([c.strip() for c in args.clubs.split(",")]).items():
        sessions = fetch(f"/clubs/{site_id}/sessions/timetable")["sessionsDetails"]
        if args.raw_dir:
            with open(f"{args.raw_dir}/{site_id}.json", "w") as f:
                json.dump(sessions, f)
        full_days, slots = weekly_pattern(sessions, args.match, days, args.after, args.before)
        windows[club_name] = [full_days[0], full_days[-1]] if full_days else None
        for (day, time, name, duration, studio), found in slots.items():
            rows.append({
                "club": club_name, "day": day, "time": time, "duration": duration, "name": name, "studio": studio,
                "active_dates": sorted(found["dates"]), "cancelled_dates": sorted(found["cancelled"]),
                "weekly": len(found["dates"]) >= 2,
                "window": windows[club_name],
            })

    rows.sort(key=lambda r: (DAYS.index(r["day"]), r["time"], r["club"]))
    if args.json:
        json.dump(rows, sys.stdout, indent=1)
        return
    print("weekly (n) = active on n dates (2+) inside the club's full-data window. one-off = active once. Cancelled dates are appended when present.")
    for r in rows:
        status = f"weekly ({len(r['active_dates'])})" if r["weekly"] else f"one-off {r['active_dates']}" if r["active_dates"] else "never active"
        if r["cancelled_dates"]:
            status += f" cancelled:{r['cancelled_dates']}"
        print(f"{r['day']} {r['time']} {r['duration']:>3}min  {r['club']:<18} {r['name']:<32} {r['studio']:<34} {status}")
    print()
    for club_name, window in windows.items():
        print(f"full-data window {club_name}: {window[0]} -> {window[1]}" if window else f"full-data window {club_name}: none")


if __name__ == "__main__":
    main()
