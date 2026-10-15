"""Run with: python3 -I skills/dl-timetable/scripts/test_dl_timetable.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dl_timetable import weekly_pattern  # noqa: E402


def session(date, time, name, status="active"):
    return {"date": date, "startTime": time, "name": name, "duration": 45, "locations": ["Studio"], "status": status}


# Two full Thursdays (padded to 20 sessions each) plus a sparse far-future Thursday.
padding = [session(d, "09:00", f"Filler {i}") for d in ("2026-10-15", "2026-10-22") for i in range(19)]
sessions = padding + [
    session("2026-10-15", "18:30", "CYCLONE"),
    session("2026-10-22", "18:30", "CYCLONE"),
    session("2026-10-15", "18:45", "CYCLONE", status="cancelled"),
    session("2026-10-22", "20:00", "CYCLONE On Screen - Virtual"),
    session("2026-12-24", "18:30", "CYCLONE"),
    session("2026-10-15", "18:30", "Pilates"),
]

full_days, slots = weekly_pattern(sessions, "cyclone", ["Thu"], "18:00", "23:59")

assert full_days == ["2026-10-15", "2026-10-22"], full_days
weekly = slots[("Thu", "18:30", "CYCLONE", 45, "Studio")]
assert weekly["dates"] == ["2026-10-15", "2026-10-22"], weekly
cancelled = slots[("Thu", "18:45", "CYCLONE", 45, "Studio")]
assert cancelled["dates"] == [] and cancelled["cancelled"] == ["2026-10-15"], cancelled
one_off = slots[("Thu", "20:00", "CYCLONE On Screen - Virtual", 45, "Studio")]
assert one_off["dates"] == ["2026-10-22"], one_off
assert not any("Pilates" in key for key in slots)
print("ok")
