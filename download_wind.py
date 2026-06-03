#!/usr/bin/env python3
"""Download NDBC wind data for Tomales Bay area analysis.

Two stations are downloaded:
  PRYC1  — NOAA Point Reyes C-MAN coastal station (37.996°N 122.977°W)
            ~10 miles south of Tomales Bay on the outer Point Reyes coast.
            Direct hourly measurements, top-quality source. Wind anemometer
            stopped reporting after 2019; 2020+ files are present but have
            WSPD=99.0 (missing) throughout.

  46013  — NDBC Bodega Bay offshore buoy (38.235°N 123.317°W)
            ~25 miles west-northwest of Tomales Bay in the open Pacific.
            Reads ~30% higher than PRYC1 due to exposed offshore position.
            Pre-2017: hourly observations; 2017+: 10-minute observations.
            2021 has reduced coverage due to a buoy outage.

Stations investigated but not usable:
  46214  — Point Reyes waverider buoy — wave data only, no wind sensor
  KCAINVER2/KCAINVER14 — WU PWS stations in Inverness — offline, no archived data
  KCAOLEMA3  — WU PWS station in Olema — offline, no archived data
  KCAPOINT29/KCAPOINT5 — WU PWS stations at Point Reyes Station — offline, no data
  WRCC PRCA  — Pt. Reyes RCA field (38.094°N 122.950°W) — RAWS station with data
               2006–present, but historical access (>30 days) requires paid access;
               contact wrcc@dri.edu / 775-674-7010
  KDVO (Gnoss Field/Novato) — nearest ASOS airport, 15 miles SE — inland valley
               microclimate, reads ~half of coastal values; not representative
  NCEI ISD   — no stations in ISD history file for Inverness, Olema, or
               Point Reyes Station town
"""

import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "wind"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://www.ndbc.noaa.gov/data/historical/stdmet"


def fetch(station: str, year: int) -> None:
    fname = f"{station}h{year}.txt.gz"
    dest = DATA_DIR / fname
    if dest.exists():
        print(f"  {fname}: already present ({dest.stat().st_size // 1024} KB)")
        return
    url = f"{BASE}/{fname}"
    print(f"  {fname}: downloading …", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"{dest.stat().st_size // 1024} KB")
    except Exception as e:
        print(f"FAILED ({e})")
        dest.unlink(missing_ok=True)


print("PRYC1 (2010–2019, coastal Point Reyes):")
for yr in range(2010, 2020):
    fetch("pryc1", yr)

print("\n46013 (2010–2024, Bodega Bay offshore buoy):")
for yr in range(2010, 2025):
    fetch("46013", yr)

print("\nDone. Data saved to data/wind/")
