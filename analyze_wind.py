#!/usr/bin/env python3
"""Compute average monthly wind speed by hour of day from NDBC data.

Outputs two tables (2010s and 2020s) for the Tomales Bay kayaking post.
Run download_wind.py first.

Method
------
PRYC1 2010–2019: direct hourly UTC observations (mm=00), converted to Pacific
  time via zoneinfo. Missing values (WSPD ≥ 99.0) excluded. ~235–248 obs per
  month/hour cell.

46013 2020–2024: same processing. Offshore buoy reads higher than PRYC1 due to
  open-ocean exposure. To estimate local coastal conditions, a cell-by-cell
  scaling matrix is derived from the 2010–2019 overlap period where both
  stations were operating (PRYC1 / 46013, 72 cells = 12 months × 6 hours;
  mean ratio 0.77, range 0.53–0.96), then applied to the 2020–2024 46013
  averages. This corrects for exposure differences while preserving diurnal
  and seasonal patterns.

Output units: mph (m/s × 2.237).
"""

import collections
import gzip
import statistics
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DATA_DIR = Path(__file__).parent / "data" / "wind"
pacific = ZoneInfo("America/Los_Angeles")
utc = timezone.utc

TARGET_HOURS = {0, 9, 12, 15, 18, 21}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
HOURS  = [9, 12, 15, 18, 21, 0]
HLABEL = {9: "9 AM", 12: "12 PM", 15: "3 PM", 18: "6 PM", 21: "9 PM", 0: "Midnight"}


def load_station(station: str, years: range) -> dict:
    """Return data[month][hour] = list of wind speeds (m/s)."""
    data: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    for year in years:
        path = DATA_DIR / f"{station}h{year}.txt.gz"
        if not path.exists():
            print(f"  Missing: {path.name}")
            continue
        with gzip.open(path, "rt") as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 7:
                    continue
                yr, mo, dd, hh, mm = (int(parts[i]) for i in range(5))
                if mm != 0:
                    continue  # top-of-hour only
                wspd_raw = parts[6]
                if float(wspd_raw) >= 99.0:
                    continue  # missing
                wspd_ms = float(wspd_raw)
                dt_pac = datetime(yr, mo, dd, hh, 0, tzinfo=utc).astimezone(pacific)
                lh, lmo = dt_pac.hour, dt_pac.month
                if lh not in TARGET_HOURS:
                    continue
                data[lmo][lh].append(wspd_ms)
    return data


def mph(ms: float) -> float:
    return ms * 2.237


def print_table(data: dict, label: str) -> None:
    print(f"\n{label}")
    print("=" * len(label))
    header = f"{'Month':<6}" + "".join(f"{HLABEL[h]:>10}" for h in HOURS)
    print(header)
    print("-" * len(header))
    for mo in range(1, 13):
        row = f"{MONTHS[mo - 1]:<6}"
        for h in HOURS:
            vals = data[mo][h]
            row += f"{mph(statistics.mean(vals)):>10.1f}" if vals else f"{'N/A':>10}"
        print(row)
    # sample count check
    sample = data[6][15]
    print(f"  (n={len(sample)} obs for Jun 3 PM)")


# ── Load data ────────────────────────────────────────────────────────────────

print("Loading PRYC1 (2010–2019) …")
pryc1_10s = load_station("pryc1", range(2010, 2020))

print("Loading 46013 (2010–2024) …")
b46013_10s = load_station("46013", range(2010, 2020))
b46013_20s = load_station("46013", range(2020, 2025))

# ── Scaling matrix: PRYC1 / 46013 for 2010–2019 ─────────────────────────────

scaling: dict = {}
for mo in range(1, 13):
    for h in TARGET_HOURS:
        p = pryc1_10s[mo][h]
        b = b46013_10s[mo][h]
        if p and b:
            scaling[(mo, h)] = statistics.mean(p) / statistics.mean(b)

ratios = list(scaling.values())
print(f"\nScaling matrix: {len(ratios)} cells, "
      f"mean={statistics.mean(ratios):.3f}, "
      f"range={min(ratios):.3f}–{max(ratios):.3f}")

# ── Estimated 2020s: apply scaling to 46013 ──────────────────────────────────

est20s: dict = collections.defaultdict(lambda: collections.defaultdict(list))
for mo in range(1, 13):
    for h in TARGET_HOURS:
        vals = b46013_20s[mo][h]
        r = scaling.get((mo, h))
        if vals and r:
            # Store as a single-element list so the table code works uniformly
            est20s[mo][h] = [statistics.mean(vals) * r]

# ── Print tables ─────────────────────────────────────────────────────────────

print_table(pryc1_10s, "2010–2019: PRYC1, Point Reyes coastal station (mph)")
print_table(est20s,    "2020–2024: 46013 scaled to local conditions (mph)")

print("""
Notes
-----
- PRYC1 (37.996°N 122.977°W): NOAA C-MAN/NOS coastal station on the outer
  Point Reyes Peninsula. Wind anemometer stopped reporting after 2019.
- 46013 (38.235°N 123.317°W): NDBC offshore buoy, Bodega Bay area, open Pacific.
  2020–2024 values scaled to local coastal conditions using cell-by-cell
  PRYC1/46013 ratios from the 2010–2019 overlap period.
""")
