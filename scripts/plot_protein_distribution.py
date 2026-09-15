#!/usr/bin/env python3
"""Plot the distribution of mouse protein lengths from STRINGdb protein.info data.

Reads data/10090.protein.info.v12.0.txt.gz (tab-separated, gzipped),
filters out unannotated protein sizes (missing / non-numeric / <= 0),
computes descriptive statistics (count, mean, median, standard deviation,
and quartiles), and generates a high-resolution publication-style
histogram with KDE overlay.

The plot is saved as results/protein_length_distribution.png (300 dpi).
Protein lengths are strongly right-skewed (max 32,000 aa vs. median ~360 aa),
so the x-axis uses a logarithmic scale with log-spaced bins.
The KDE is computed with a Gaussian kernel using Silverman's rule-of-thumb
bandwidth (implemented with numpy; no scipy required).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
INPUT_FILE = DATA_DIR / "10090.protein.info.v12.0.txt.gz"
OUTPUT_FILE = RESULTS_DIR / "protein_length_distribution.png"

# Publication-style figure defaults
PLOT_DPI = 300
FIG_SIZE = (9, 6)
HIST_COLOR = "#4C72B0"
KDE_COLOR = "#C44E52"
N_KDE_GRID = 500


def load_protein_sizes(path: Path) -> np.ndarray:
    """Load protein_size from the gzipped TSV and filter unannotated values.

    Returns a float numpy array of annotated sizes (> 0, numeric).
    """
    df = pd.read_csv(path, sep="\t", compression="gzip")
    sizes = pd.to_numeric(df["protein_size"], errors="coerce")
    sizes = sizes.dropna()
    sizes = sizes[sizes > 0]
    return sizes.to_numpy(dtype=float)


def describe_sizes(sizes: np.ndarray) -> dict[str, float]:
    """Compute descriptive statistics for the protein sizes."""
    n = len(sizes)
    q1, q2, q3 = np.percentile(sizes, [25, 50, 75])
    return {
        "n": float(n),
        "mean": float(np.mean(sizes)),
        "median": float(q2),
        "std": float(np.std(sizes, ddof=1)),
        "q1": float(q1),
        "q3": float(q3),
    }


def gaussian_kde(values: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Gaussian kernel density estimate at grid points.

    Bandwidth is estimated with Silverman's rule of thumb using the more
    robust IQR-based sigma when the data is non-normal.
    """
    n = len(values)
    sigma_std = np.std(values, ddof=1)
    iqr = np.percentile(values, 75) - np.percentile(values, 25)
    sigma = min(sigma_std, iqr / 1.349) if iqr > 0 else sigma_std
    bandwidth = 0.9 * sigma * n ** (-1 / 5)

    diff = grid[:, np.newaxis] - values[np.newaxis, :]
    kernel = np.exp(-0.5 * (diff / bandwidth) ** 2) / (bandwidth * np.sqrt(2.0 * np.pi))
    return kernel.mean(axis=1)


def render_plot(sizes: np.ndarray, stats: dict[str, float]) -> None:
    """Render and save the histogram + KDE figure."""
    log_sizes = np.log10(sizes)
    log_grid = np.linspace(log_sizes.min(), log_sizes.max(), N_KDE_GRID)
    kde_density = gaussian_kde(log_sizes, log_grid)

    bins = np.logspace(log_sizes.min(), log_sizes.max(), 80)

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=PLOT_DPI)

    ax.hist(
        sizes,
        bins=bins,
        density=True,
        alpha=0.6,
        color=HIST_COLOR,
        edgecolor="white",
        linewidth=0.4,
        label="Histogram",
    )
    ax.plot(
        10**log_grid,
        kde_density,
        color=KDE_COLOR,
        linewidth=2.0,
        label="KDE (Silverman)",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Protein length (amino acids)", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)

    ax.grid(True, which="major", linestyle=":", linewidth=0.6, alpha=0.5)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.4, alpha=0.3)
    ax.tick_params(labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    stats_txt = (
        f"n = {int(stats['n']):,}\n"
        f"Mean = {stats['mean']:,.1f} aa\n"
        f"Median = {stats['median']:,.1f} aa\n"
        f"SD = {stats['std']:,.1f} aa\n"
        f"Q1 = {stats['q1']:,.1f} aa  |  Q3 = {stats['q3']:,.1f} aa"
    )
    ax.text(
        0.97,
        0.97,
        stats_txt,
        transform=ax.transAxes,
        fontsize=10,
        ha="right",
        va="top",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "white", "edgecolor": "#888888", "alpha": 0.9},
    )

    ax.legend(loc="upper left", frameon=False, fontsize=11)
    fig.tight_layout()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    sizes = load_protein_sizes(INPUT_FILE)
    if len(sizes) == 0:
        raise SystemExit("No annotated protein sizes found.")

    stats = describe_sizes(sizes)
    render_plot(sizes, stats)

    print(f"Input file      : {INPUT_FILE}")
    print(f"Annotated sizes : {int(stats['n']):,}")
    print(f"Mean            : {stats['mean']:,.1f} aa")
    print(f"Median          : {stats['median']:,.1f} aa")
    print(f"Standard dev.   : {stats['std']:,.1f} aa")
    print(f"Q1 (25%)        : {stats['q1']:,.1f} aa")
    print(f"Q3 (75%)        : {stats['q3']:,.1f} aa")
    print(f"Plot saved to   : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()