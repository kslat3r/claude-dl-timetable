# claude-dl-timetable

David Lloyd class timetables for [Claude Code](https://code.claude.com), packaged as an installable plugin.

The davidlloyd.co.uk timetable page is rendered client-side, so a plain fetch returns nothing. The app backend (`mobile-app-back.davidlloyd.co.uk`) is open and returns every session for the next couple of months. This skill wraps it.

## The skill

**`dl-timetable`** - pulls the timetable for any set of clubs, filters to a class name, day range and time window, and prints one row per weekly slot with its studio and whether it is weekly, a one-off, or cancelled. The SKILL.md carries the rules for turning that into a calendar: travel thresholds, alternating live/virtual slots, the data window, and a headless Chrome recipe for showing the user what the website displays.

```
python3 -I skills/dl-timetable/scripts/dl_timetable.py --clubs cheam,purley,kidbrooke --match cyclone --days Mon,Tue,Wed,Thu,Fri --after 18:30
```

## Install

```
/plugin marketplace add kslat3r/claude-dl-timetable
/plugin install dl-timetable@claude-dl-timetable
```

## Test

```
python3 -I skills/dl-timetable/scripts/test_dl_timetable.py
```

## Layout

```
.claude-plugin/        plugin and marketplace manifests
skills/dl-timetable/
  SKILL.md             when to use it, how to read the output, calendar rules
  scripts/
    dl_timetable.py    the fetch and weekly-pattern tool
    test_dl_timetable.py
```
