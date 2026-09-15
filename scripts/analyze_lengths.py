#!/usr/bin/env python3
"""Analyze protein length statistics from STRINGdb protein.info file.

Reads data/10090.protein.info.v12.0.txt.gz (tab-separated, gzipped),
computes total count, min/max/mean protein size, and reports the
top 5 largest proteins. Results are printed to stdout and saved as
results/protein_length_stats.json.
"""

from __future__ import annotations

import gzip
import json
import statistics
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
INPUT_FILE = DATA_DIR / "10090.protein.info.v12.0.txt.gz"
OUTPUT_FILE = RESULTS_DIR / "protein_length_stats.json"

# Column indices in the tab-separated file (0-based)
COL_PROTEIN_ID = 0
COL_PREFERRED_NAME = 1
COL_PROTEIN_SIZE = 2


def parse_protein_sizes(path: Path) -> list[dict[str, object]]:
    """Parse protein_id, preferred_name, and protein_size from the gzipped TSV."""
    records: list[dict[str, object]] = []
    with gzip.open(path, "rt") as handle:
        header = handle.readline().strip().split("\t")
        size_idx = header.index("protein_size")
        name_idx = header.index("preferred_name")
        id_idx = header.index("#string_protein_id")

        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            fields = line.split("\t")
            if len(fields) <= size_idx:
                continue
            try:
                size = int(fields[size_idx])
            except ValueError:
                continue
            records.append(
                {
                    "protein_id": fields[id_idx],
                    "preferred_name": fields[name_idx] if len(fields) > name_idx else "",
                    "protein_size": size,
                }
            )
    return records


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    records = parse_protein_sizes(INPUT_FILE)
    if not records:
        raise SystemExit("No valid protein records parsed.")

    sizes = [r["protein_size"] for r in records]  # type: ignore[misc]

    total = len(sizes)
    min_len = min(sizes)
    max_len = max(sizes)
    mean_len = statistics.mean(sizes)

    # Top 5 largest proteins
    top5 = sorted(records, key=lambda r: int(r["protein_size"]), reverse=True)[:5]
    top5_clean = [
        {
            "rank": i + 1,
            "protein_id": r["protein_id"],
            "preferred_name": r["preferred_name"],
            "protein_size": r["protein_size"],
        }
        for i, r in enumerate(top5)
    ]

    stats = {
        "total_proteins": total,
        "min_length": min_len,
        "max_length": max_len,
        "mean_length": round(mean_len, 2),
        "top_5_largest": top5_clean,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w") as out:
        json.dump(stats, out, indent=2)
        out.write("\n")

    # Console report
    print(f"Input file      : {INPUT_FILE}")
    print(f"Total proteins  : {total:,}")
    print(f"Min length      : {min_len:,} aa")
    print(f"Max length      : {max_len:,} aa")
    print(f"Mean length     : {mean_len:,.2f} aa")
    print()
    print("Top 5 largest proteins:")
    print(f"{'Rank':<6}{'Protein ID':<28}{'Name':<20}{'Length (aa)':>12}")
    print("-" * 66)
    for r in top5_clean:
        print(
            f"{r['rank']:<6}{r['protein_id']:<28}{r['preferred_name']:<20}{r['protein_size']:>12,}"
        )
    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()