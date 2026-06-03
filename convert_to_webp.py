#!/usr/bin/env python3
"""Convert plots/  PNGs to WebP for use in the blog.

Writes webp/ inside this repo. Copy the resulting files to:
  ~/homepage/site/assets/blog/images/
"""

import subprocess
import sys
from pathlib import Path

PLOTS_DIR = Path(__file__).parent / "plots"
WEBP_DIR  = Path(__file__).parent / "webp"
WEBP_DIR.mkdir(exist_ok=True)

# Map: source PNG → destination WebP filename (blog asset name)
CONVERSIONS = {
    "bodega_hab.png":   "2026-06-03-bodega-hab-monitoring.webp",
    "cencoos_buoy.png": "2026-06-03-tomales-bay-cencoos-buoy.webp",
    "habmap_buoy.png":  "2026-06-03-tomales-bay-habmap-buoy.webp",
}

QUALITY = 88

for src_name, dst_name in CONVERSIONS.items():
    src = PLOTS_DIR / src_name
    dst = WEBP_DIR / dst_name
    if not src.exists():
        print(f"MISSING: {src} — run plot_all.py first", file=sys.stderr)
        continue
    result = subprocess.run(
        ["convert", str(src), "-quality", str(QUALITY), str(dst)],
        capture_output=True,
    )
    size_kb = dst.stat().st_size // 1024
    print(f"{dst_name}: {size_kb} KB")

print(f"\nWebP files written to {WEBP_DIR}/")
print("Copy to blog with:")
print(f"  cp {WEBP_DIR}/*.webp ~/homepage/site/assets/blog/images/")
