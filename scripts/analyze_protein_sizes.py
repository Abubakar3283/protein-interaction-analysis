#!/usr/bin/env python3
"""Analyze protein sizes from MGI protein info data."""

import gzip
import statistics
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "10090.protein.info.v12.0.txt.gz"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "results" / "size_summary.txt"


def load_protein_sizes(path: Path) -> list[int]:
    """Load protein_size column (index 2) from the gzipped tab-separated file."""
    sizes: list[int] = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            sizes.append(int(fields[2]))
    return sizes


def main() -> None:
    sizes = load_protein_sizes(DATA_FILE)

    min_size = min(sizes)
    max_size = max(sizes)
    mean_size = statistics.mean(sizes)
    median_size = statistics.median(sizes)

    print(f"Protein count : {len(sizes)}")
    print(f"Minimum       : {min_size}")
    print(f"Maximum       : {max_size}")
    print(f"Mean          : {mean_size:.2f}")
    print(f"Median        : {median_size:.2f}")

    summary = (
        f"Total proteins: {len(sizes)}\n"
        f"Min length: {min_size}\n"
        f"Max length: {max_size}\n"
        f"Mean length: {mean_size:.2f}\n"
        f"Median length: {median_size:.2f}\n"
    )
    OUTPUT_FILE.write_text(summary)
    print(f"\nSummary saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
