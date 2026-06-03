#!/usr/bin/env python3
"""Generate HAB monitoring plots for Tomales Bay bioluminescence analysis.

Produces three figures saved to plots/:
  bodega_hab.png       — Bodega Marine Lab CalHABMAP weekly species counts + SST
  cencoos_buoy.png     — CeNCOOS/UC Davis hourly SST and chlorophyll (2019–2021)
  habmap_buoy.png      — CalHABMAP Tomales Bay mid-channel buoy weekly species counts
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PLOT_DIR = Path(__file__).parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

# Kayaking trips
TRIP1 = pd.Timestamp("2022-09-23")  # Sep 2022 — no bioluminescence seen
TRIP2 = pd.Timestamp("2023-10-06")  # Oct 2023 — bioluminescence seen

TRIP_LINES = [
    Line2D([0], [0], color="tomato",  lw=1.5, ls="--", label="Sep 2022 trip"),
    Line2D([0], [0], color="darkred", lw=2,             label="Oct 2023 trip"),
]

# Seasonal background shading
SEASONS = [
    ((3,  5),  "#a8d5a2"),  # spring — green
    ((6,  8),  "#ffe08a"),  # summer — yellow
    ((9,  11), "#f4b97a"),  # fall   — orange
    ((12, 2),  "#aac4e0"),  # winter — blue
]

DPI  = 150
FONT = 12

W_CENCOOS = 7.0   # 2.5 years, 2 panels
W_HABMAP  = 9.0   # 5 years,   4 panels
W_BODEGA  = 11.0  # 6+ years,  7 panels

plt.rcParams.update({
    "font.size":        FONT,
    "axes.titlesize":   FONT,
    "axes.labelsize":   FONT,
    "xtick.labelsize":  9,
    "ytick.labelsize":  FONT - 1,
})


# ── Shared helpers ────────────────────────────────────────────────────────────

def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / name, skiprows=[1])
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_localize(None)
    return df.set_index("time").sort_index()


def add_seasons(ax, t0, t1) -> None:
    for year in range(t0.year - 1, t1.year + 2):
        for (m_start, m_end), color in SEASONS:
            if m_start <= m_end:
                s = pd.Timestamp(year, m_start, 1)
                e = pd.Timestamp(year, m_end, 1) + pd.offsets.MonthEnd(1)
            else:
                s = pd.Timestamp(year, m_start, 1)
                e = pd.Timestamp(year + 1, m_end, 1) + pd.offsets.MonthEnd(1)
            if e < t0 or s > t1:
                continue
            ax.axvspan(max(s, t0), min(e, t1), alpha=0.25, color=color, zorder=0, lw=0)


def add_trips(ax, t0, t1) -> None:
    if t0 <= TRIP1 <= t1:
        ax.axvline(TRIP1, color="tomato",  lw=1.5, ls="--", zorder=5)
    if t0 <= TRIP2 <= t1:
        ax.axvline(TRIP2, color="darkred", lw=2,             zorder=5)


def quarterly_axis(ax) -> None:
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    def fmt(x, pos):
        dt = mdates.num2date(x)
        return dt.strftime("%Y") if dt.month == 1 else dt.strftime("%b")

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90, ha="center")


def style_panel(ax, title, color, t0, t1, ylabel, linthresh=None) -> None:
    add_seasons(ax, t0, t1)
    add_trips(ax, t0, t1)
    ax.set_title(title, fontsize=FONT, loc="left", color=color, fontweight="bold", pad=2)
    ax.set_ylabel(ylabel, labelpad=2)
    ax.set_xlim(t0, t1)
    if linthresh is not None:
        ax.set_yscale("symlog", linthresh=linthresh)
    ax.set_ylim(bottom=0)


# ── Plot 1: Bodega Marine Lab ─────────────────────────────────────────────────

def plot_bodega() -> None:
    df = load_csv("bodega_hab.csv")
    species = [
        "Lingulodinium_polyedra",
        "Akashiwo_sanguinea",
        "Alexandrium_spp",
        "Dinophysis_spp",
        "Pseudo_nitzschia_delicatissima_group",
        "Pseudo_nitzschia_seriata_group",
    ]
    for c in species:
        df[c] = df[c].replace(0, np.nan)

    t0, t1 = df.index.min(), df.index.max()

    panels = [
        ("Lingulodinium_polyedra",               "Lingulodinium polyedra",            "#1565C0", 1),
        ("Akashiwo_sanguinea",                   "Akashiwo sanguinea",                "#C62828", 10),
        ("Alexandrium_spp",                      "Alexandrium spp.",                  "#EF6C00", 10),
        ("Dinophysis_spp",                       "Dinophysis spp.",                   "#6A1B9A", 10),
        ("Pseudo_nitzschia_delicatissima_group", "Pseudo-nitzschia delicatissima grp","#2E7D32", 100),
        ("Pseudo_nitzschia_seriata_group",       "Pseudo-nitzschia seriata grp",      "#66BB6A", 100),
        ("Temp",                                 "Sea surface temperature",            "#B71C1C", None),
    ]

    fig, axes = plt.subplots(len(panels), 1, figsize=(W_BODEGA, 17.0), sharex=True)
    fig.suptitle(
        "Bodega Marine Lab — HAB Monitoring (CalHABMAP)\nweekly samples",
        fontsize=FONT, fontweight="bold",
    )

    for i, (ax, (col, label, color, linthresh)) in enumerate(zip(axes, panels)):
        style_panel(ax, label, color, t0, t1,
                    ylabel="cells/L" if linthresh else "°C",
                    linthresh=linthresh)
        ax.plot(df.index, df[col], "o-", color=color, ms=3, lw=1)
        if i == 0:
            ax.legend(handles=TRIP_LINES, fontsize=FONT - 2, loc="upper right", handlelength=1.5)

    quarterly_axis(axes[-1])
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = PLOT_DIR / "bodega_hab.png"
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


# ── Plot 2: CeNCOOS hourly buoy ───────────────────────────────────────────────

def plot_cencoos() -> None:
    df = load_csv("tomales_buoy.csv")
    daily = df.resample("D").median()
    chl = df["mass_concentration_of_chlorophyll_in_sea_water"].resample("D").median().clip(upper=50)
    t0, t1 = daily.index.min(), daily.index.max()

    fig, axes = plt.subplots(2, 1, figsize=(W_CENCOOS, 7.5), sharex=True)
    fig.suptitle(
        "CeNCOOS / UC Davis Tomales Bay Buoy\nsouth of Hog Island · hourly→daily median",
        fontsize=FONT, fontweight="bold",
    )

    for ax in axes:
        add_seasons(ax, t0, t1)
        ax.set_xlim(t0, t1)

    axes[0].plot(daily.index, daily["sea_water_temperature"], color="#C62828", lw=1)
    style_panel(axes[0], "Sea surface temperature", "#C62828", t0, t1, ylabel="°C")

    axes[1].fill_between(chl.index, chl, alpha=0.6, color="#2E7D32")
    style_panel(axes[1], "Chlorophyll (daily median, clipped at 50 µg/L)", "#2E7D32", t0, t1, ylabel="µg/L")

    quarterly_axis(axes[-1])
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = PLOT_DIR / "cencoos_buoy.png"
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


# ── Plot 3: CalHABMAP Tomales Bay mid-channel buoy ───────────────────────────

def plot_habmap() -> None:
    df = load_csv("tomales_habmap.csv")
    t0, t1 = df.index.min(), df.index.max()

    panels = [
        ("Lingulodinium_polyedra", "Lingulodinium polyedra", "#1565C0", 1),
        ("Akashiwo_sanguinea",     "Akashiwo sanguinea",     "#C62828", 10),
        ("Alexandrium_spp",        "Alexandrium spp.",        "#EF6C00", 10),
        ("Dinophysis_spp",         "Dinophysis spp.",         "#6A1B9A", 10),
    ]

    fig, axes = plt.subplots(len(panels), 1, figsize=(W_HABMAP, 10.5), sharex=True)
    fig.suptitle(
        "CalHABMAP Tomales Bay Mid-Channel Buoy\nweekly samples",
        fontsize=FONT, fontweight="bold",
    )

    for i, (ax, (col, label, color, linthresh)) in enumerate(zip(axes, panels)):
        style_panel(ax, label, color, t0, t1, ylabel="cells/L", linthresh=linthresh)
        ax.plot(df.index, df[col].fillna(0), "o-", color=color, ms=4, lw=1)
        if i == 0:
            ax.legend(handles=TRIP_LINES, fontsize=FONT - 2, loc="upper right", handlelength=1.5)

    quarterly_axis(axes[-1])
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = PLOT_DIR / "habmap_buoy.png"
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    plot_bodega()
    plot_cencoos()
    plot_habmap()
    print("\nAll plots saved to plots/")
