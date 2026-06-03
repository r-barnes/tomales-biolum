# Tomales Bay Bioluminescence — Data & Plots

Supporting data and plots for the blog post
[Kayaking Tomales Bay in search of bioluminescence](https://richard.science/blog/2026-06-03-tomales-bay-kayaking.html).

## Data sources

### CalHABMAP — Bodega Marine Lab (`data/bodega_hab.csv`)

- **Source:** [CalHABMAP ERDDAP](https://erddap.sccoos.org/erddap/tabledap/HABs-BodegaMarineLab.html)
- **Coverage:** 2020–present, weekly samples
- **Location:** Bodega Marine Lab pier, Bodega Bay CA (~15 miles south of Tomales Bay)
- **Variables:** *Lingulodinium polyedra*, *Akashiwo sanguinea*, *Alexandrium* spp.,
  *Dinophysis* spp., *Pseudo-nitzschia* (two size classes), sea surface temperature
- **Notes:** Tomales Bay is not a CalHABMAP station; Bodega Bay is the closest site
  in the same coastal upwelling regime.

### CalHABMAP — Tomales Bay mid-channel buoy (`data/tomales_habmap.csv`)

- **Source:** [CalHABMAP ERDDAP](https://erddap.sccoos.org/erddap/tabledap/HABs-TomalesBayMid-ChannelBuoy.html)
- **Coverage:** 2021–present, weekly samples
- **Location:** Mid-channel south of Hog Island, Tomales Bay (near Marshall Beach campsite)
- **Variables:** Same HAB species as Bodega; chlorophyll and temperature columns present
  but not populated in the downloaded data

### CeNCOOS / UC Davis — Tomales Bay buoy (`data/tomales_buoy.csv`)

- **Source:** [CeNCOOS ERDDAP](https://erddap.cencoos.org/erddap/tabledap/tomales-bay-buoy.html)
- **Coverage:** 2019–2021, hourly (buoy decommissioned Oct 2021)
- **Location:** South of Hog Island, Tomales Bay
- **Variables:** Sea surface temperature, chlorophyll, salinity, turbidity

### iNaturalist observations (`data/inat_*.json`)

- **Source:** [iNaturalist API](https://api.inaturalist.org/v1/observations)
- **Radius:** 100 km around Tomales Bay (38.1°N, 122.9°W)
- **Species queried:** *Lingulodinium polyedra*, *Noctiluca scintillans*
- **Result:** 0 *Lingulodinium* observations; 7 *Noctiluca* observations (all from
  San Francisco, none from Tomales Bay)

## Usage

```bash
pip install -r requirements.txt

# Re-download all data (overwrites data/)
python download_data.py

# Regenerate plots (saved to plots/)
python plot_all.py
```

Plots are sized at 750 px wide (5 in × 150 dpi) for 2× retina mobile display.
