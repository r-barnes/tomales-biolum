#!/usr/bin/env python3
"""Download HAB monitoring and buoy data for Tomales Bay bioluminescence analysis."""

import json
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def download(url: str, dest: Path) -> None:
    print(f"Downloading {dest.name} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"  → {dest.stat().st_size // 1024} KB")


# CalHABMAP — Bodega Marine Lab (weekly, 2020–present)
# Closest coastal HAB station to Tomales Bay (~15 miles south, same upwelling regime)
download(
    "https://erddap.sccoos.org/erddap/tabledap/HABs-BodegaMarineLab.csv"
    "?time,Temp,Avg_Chloro,Akashiwo_sanguinea,Alexandrium_spp,Dinophysis_spp"
    ",Lingulodinium_polyedra,Prorocentrum_spp"
    ",Pseudo_nitzschia_delicatissima_group,Pseudo_nitzschia_seriata_group",
    DATA_DIR / "bodega_hab.csv",
)

# CalHABMAP — Tomales Bay mid-channel buoy (weekly, 2021–present)
# Located south of Hog Island, near Marshall Beach campsite
download(
    "https://erddap.sccoos.org/erddap/tabledap/HABs-TomalesBayMid-ChannelBuoy.csv"
    "?time,Temp,Avg_Chloro,Akashiwo_sanguinea,Alexandrium_spp,Dinophysis_spp"
    ",Lingulodinium_polyedra",
    DATA_DIR / "tomales_habmap.csv",
)

# CeNCOOS / UC Davis — Tomales Bay buoy (hourly, 2019–2021)
# High-frequency SST and chlorophyll from the same location
download(
    "https://erddap.cencoos.org/erddap/tabledap/tomales-bay-buoy.csv"
    "?time,sea_water_temperature,mass_concentration_of_chlorophyll_in_sea_water"
    "&sea_water_temperature_qc_agg=1"
    "&mass_concentration_of_chlorophyll_in_sea_water_qc_agg=1",
    DATA_DIR / "tomales_buoy.csv",
)

# iNaturalist — bioluminescent species observations within 100 km of Tomales Bay
for taxon in ["Lingulodinium+polyedra", "Noctiluca+scintillans"]:
    slug = taxon.lower().replace("+", "_")
    url = (
        f"https://api.inaturalist.org/v1/observations"
        f"?taxon_name={taxon}&lat=38.1&lng=-122.9&radius=100&per_page=200"
    )
    dest = DATA_DIR / f"inat_{slug}.json"
    print(f"Downloading {dest.name} ...")
    with urllib.request.urlopen(url) as r:
        data = json.load(r)
    dest.write_text(json.dumps(data, indent=2))
    print(f"  → {data['total_results']} observations")

print("\nDone. All data saved to data/")
