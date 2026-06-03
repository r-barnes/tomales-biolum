#!/usr/bin/env python3
"""Estimate paddle distances and times between Tomales Bay launch points and campsites.

Launch points
-------------
  Miller Boat Launch    38.2000, -122.9215  (east shore, near Marshall)
  Chicken Ranch Beach   38.1071, -122.8629  (southern end, near Inverness)

Routes computed
---------------
  Miller – direct      : straight-line haversine to each campsite
  Miller – via shore   : cross bay to waypoint (38.189975, -122.934522),
                         then follow west shore to campsite
  CRB – shore          : follow west shore northward from Chicken Ranch Beach

Speed calibration
-----------------
  User's group paddled from Chicken Ranch Beach to Marshall Beach in 2 hours.
  The stated route distance is 5.29 miles → 2.645 mph.

Shore-distance correction
-------------------------
  The campsite coordinates are simplified waypoints; straight-line segments
  between them underestimate the real shoreline distance by ~8.9% (ratio
  computed from the known 5.29-mile CRB→Marshall reference). All shore
  segments are multiplied by SHORE_FACTOR = 1.089 to correct for this.
  Direct (open-water) distances are not corrected.

Output
------
  Prints a Markdown table suitable for pasting into the blog post.
  Also prints a CSV for further analysis.
"""

from math import asin, cos, radians, sin, sqrt

# ── Constants ─────────────────────────────────────────────────────────────────

SPEED_MPH    = 5.29 / 2.0   # calibrated from CRB→Marshall, 2 h
SHORE_FACTOR = 5.29 / 4.86  # correct for simplified waypoints (≈1.089)

MILLER = (38.2000, -122.9215)
CRB    = (38.1071, -122.8629)   # Chicken Ranch Beach / Tomales Bay Resort
WAYPOINT = (38.189975, -122.934522)  # west-shore landing for Miller crossing

# West shore, ordered south → north. Waypoint inserted between Pelican North
# and Wall Beach (it sits at 38.190°N, between them at 38.189° and 38.192°).
WEST_SHORE = [
    ("Chicken Ranch Beach",   38.1071, -122.8629, False),
    ("Kilkenny Beach",        38.1456, -122.9037, False),
    ("Long Cove Beach",       38.1521, -122.9108, False),
    ("Marshall Beach",        38.1631, -122.9155, False),
    ("No Name Beach",         38.1692, -122.9214, False),
    ("Tomales Beach",         38.1739, -122.9236, False),
    ("Elk Fence South Beach", 38.1763, -122.9269, False),
    ("Elk Fence North Beach", 38.1808, -122.9305, False),
    ("Pelican North Beach",   38.1889, -122.9367, False),
    ("_waypoint_",            38.189975, -122.934522, True),   # Miller landing
    ("Wall Beach",            38.1924, -122.9413, False),
    ("White Gulch Beach",     38.1935, -122.9465, False),
    ("Pita Beach",            38.2030, -122.9503, False),
    ("Jacks Beach",           38.2098, -122.9599, True),    # closed Mar 2018
    ("Blue Gum Beach",        38.2264, -122.9770, False),
    ("Avalis Beach",          38.2303, -122.9807, True),    # closed May 2023
    ("Duck Beach",            38.2351, -122.9850, True),    # closed May 2023
]

# Campsites to include in output (excludes the CRB launch and the waypoint itself)
CAMPSITES = [(n, lat, lon, closed) for n, lat, lon, closed in WEST_SHORE
             if not n.startswith("_") and n != "Chicken Ranch Beach"]


# ── Haversine ─────────────────────────────────────────────────────────────────

def hav(p1: tuple, p2: tuple) -> float:
    """Great-circle distance in miles."""
    R = 3958.8
    lat1, lon1 = map(radians, p1)
    lat2, lon2 = map(radians, p2)
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 2 * R * asin(sqrt(a))


# ── Shore-distance lookup ─────────────────────────────────────────────────────

# Cumulative corrected shore distance northward from CRB for every west-shore
# point (including the waypoint).
_cum: list[float] = [0.0]
for i in range(1, len(WEST_SHORE)):
    p_prev = (WEST_SHORE[i-1][1], WEST_SHORE[i-1][2])
    p_curr = (WEST_SHORE[i][1],   WEST_SHORE[i][2])
    _cum.append(_cum[-1] + hav(p_prev, p_curr) * SHORE_FACTOR)

_shore_dist: dict[str, float] = {
    row[0]: _cum[i] for i, row in enumerate(WEST_SHORE)
}

WAYPOINT_SHORE = _shore_dist["_waypoint_"]


def shore_dist_between(name_a: str, name_b: str) -> float:
    return abs(_shore_dist[name_b] - _shore_dist[name_a])


# ── Time formatting ───────────────────────────────────────────────────────────

def fmt_time(hours: float) -> str:
    h = int(hours)
    m = round((hours - h) * 60)
    if m == 60:
        h += 1
        m = 0
    return f"{h}:{m:02d}"


def fmt_row(dist: float) -> str:
    return f"{dist:.1f} mi / {fmt_time(dist / SPEED_MPH)}"


# ── Main ──────────────────────────────────────────────────────────────────────

rows = []
for name, lat, lon, closed in CAMPSITES:
    camp = (lat, lon)
    camp_shore = _shore_dist[name]

    # Route 1: Miller direct (straight-line open water)
    d_direct = hav(MILLER, camp)

    # Route 2: Miller → waypoint (open water) + waypoint → camp (shore)
    d_cross = hav(MILLER, WAYPOINT)
    d_via   = d_cross + abs(camp_shore - WAYPOINT_SHORE)

    # Route 3: CRB along west shore
    d_crb = shore_dist_between("Chicken Ranch Beach", name)

    rows.append((name, closed, d_direct, d_via, d_crb))

# ── Print Markdown table ──────────────────────────────────────────────────────

print("Paddle distances and estimated times (calibrated at 2.65 mph).\n")
print("Shore distances corrected by ×{:.3f} for simplified waypoints.\n".format(SHORE_FACTOR))

header = (
    "| Campsite"
    " | Miller direct"
    " | Miller via shore"
    " | Chicken Ranch Beach"
    " |"
)
sep = "|---|---|---|---|"
print(header)
print(sep)
for name, closed, d_direct, d_via, d_crb in rows:
    tag = " ⚠" if closed else ""
    print(
        f"| {name}{tag}"
        f" | {fmt_row(d_direct)}"
        f" | {fmt_row(d_via)}"
        f" | {fmt_row(d_crb)}"
        f" |"
    )

print()
print("⚠ = closed to camping.")
print(f"Speed: {SPEED_MPH:.3f} mph (calibrated: Chicken Ranch Beach → Marshall Beach = 5.29 mi in 2 h).")
print(f"Miller crossing to waypoint: {hav(MILLER, WAYPOINT):.2f} mi.")

# ── Print CSV ─────────────────────────────────────────────────────────────────

print("\n\nCSV output:\n")
print("campsite,closed,miller_direct_mi,miller_via_mi,crb_mi,"
      "miller_direct_h,miller_via_h,crb_h")
for name, closed, d_direct, d_via, d_crb in rows:
    print(
        f"{name},{int(closed)}"
        f",{d_direct:.2f},{d_via:.2f},{d_crb:.2f}"
        f",{d_direct/SPEED_MPH:.2f},{d_via/SPEED_MPH:.2f},{d_crb/SPEED_MPH:.2f}"
    )
