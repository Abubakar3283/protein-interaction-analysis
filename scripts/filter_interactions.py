#!/usr/bin/env python3
"""Filter the STRING v12.0 mouse interaction network to its highest-confidence edges.

Processes the STRING v12.0 *Mus musculus* interaction network
``data/10090.protein.links.v12.0.txt.gz`` (12,684,354 scored pairwise
edges), then:

1. **Filter** -- keeps only edges with ``combined_score >= 900``
   (STRING's "highest confidence" band) and reports how many
   high-confidence edges exist across the whole network.

2. **Annotate** -- merges each surviving edge with the STRING → Ensembl
   correspondence table ``results/string_to_ensembl_mapping.tsv``
   (written by ``scripts/map_string_ensembl.py``), looking up *both*
   partners and attaching their gene symbol (``Protein_Name``) and
   Ensembl gene ID. This is an inner join: only interactions whose two
   partners are both resolved to a gene are retained, so every output
   row is fully interpretable.

3. **Rank & write** -- the fully annotated interactions are ranked by
   ``combined_score`` descending (ties broken by protein ID order) and
   the top 1,000 are written to
   ``results/high_confidence_interactions.tsv``.

Outputs:

- ``results/high_confidence_interactions.tsv`` -- top 1,000 rows (header)
- A 5-row Markdown table of the top interactions is printed to stdout
  for inclusion in the README.

Note on parsing: the ``protein.links`` file is *space*-delimited (unlike
the tab-delimited ``protein.info`` file), but the ID and score fields
contain no whitespace, so simple row splitting handles it in both cases.

Run from the repository root:  python scripts/filter_interactions.py
"""

from __future__ import annotations

import gzip
from pathlib import Path
from typing import Iterator, NamedTuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"

LINKS_FILE = DATA_DIR / "10090.protein.links.v12.0.txt.gz"
MAPPING_FILE = RESULTS_DIR / "string_to_ensembl_mapping.tsv"

OUTPUT_INTERACTIONS = RESULTS_DIR / "high_confidence_interactions.tsv"

SCORE_THRESHOLD = 900  # STRING 'highest confidence' band
TOP_N = 1000  # number of interactions to write
SAMPLE_N = 5  # rows in the README sample table


class Mapping(NamedTuple):
    """One row of the STRING -> Ensembl correspondence table."""

    ensembl_protein_id: str
    ensembl_gene_id: str
    protein_name: str


def read_mapping(mapping_path: Path) -> dict[str, Mapping]:
    """Load the correspondence table keyed by STRING protein ID."""
    mapping: dict[str, Mapping] = {}
    with open(mapping_path, "r", encoding="utf-8") as handle:
        next(handle)  # header: STRING_Protein_ID Ensembl_Protein_ID ...
        for line in handle:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            mapping[parts[0]] = Mapping(
                ensembl_protein_id=parts[1],
                ensembl_gene_id=parts[2],
                protein_name=parts[3],
            )
    return mapping


def iter_edges(links_path: Path) -> Iterator[tuple[str, str, int]]:
    """Yield ``(protein1, protein2, combined_score)`` for every data row."""
    with gzip.open(links_path, "rt", encoding="utf-8") as handle:
        next(handle)  # header: protein1 protein2 combined_score
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                score = int(parts[2])
            except ValueError:
                continue
            yield parts[0], parts[1], score


def row_markdown(rows: list[tuple[str, str, int, str, str]]) -> str:
    """Render the top interactions as a GitHub-flavoured Markdown table."""
    header = (
        "| Protein 1 (STRING ID) | Protein 2 (STRING ID) | Combined Score | "
        "Protein 1 Name | Protein 2 Name |"
    )
    divider = "|---|---|---:|---|---|"
    lines = [header, divider]
    for p1, p2, score, name1, name2 in rows:
        lines.append(f"| `{p1}` | `{p2}` | {score} | {name1} | {name2} |")
    return "\n".join(lines)


def main() -> None:
    if not LINKS_FILE.exists():
        raise FileNotFoundError(f"Missing input: {LINKS_FILE}")
    if not MAPPING_FILE.exists():
        raise FileNotFoundError(f"Missing input: {MAPPING_FILE}")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading correspondence: {MAPPING_FILE.name}")
    mapping = read_mapping(MAPPING_FILE)
    print(f"  mapped proteins : {len(mapping):,}")

    print(f"Streaming links : {LINKS_FILE.name}")
    total_edges = 0
    high_confidence = 0
    annotated_edges: list[tuple[str, str, int, str, str, str, str]] = []
    for p1, p2, score in iter_edges(LINKS_FILE):
        total_edges += 1
        if score < SCORE_THRESHOLD:
            continue
        high_confidence += 1
        m1 = mapping.get(p1)
        m2 = mapping.get(p2)
        if m1 is not None and m2 is not None:
            annotated_edges.append(
                (
                    p1,
                    p2,
                    score,
                    m1.protein_name,
                    m2.protein_name,
                    m1.ensembl_gene_id,
                    m2.ensembl_gene_id,
                )
            )

    print(f"  total edges           : {total_edges:,}")
    print(
        f"  combined_score >= {SCORE_THRESHOLD} : "
        f"{high_confidence:,} ({100.0 * high_confidence / total_edges:.2f}%)"
    )
    print(f"  both partners mapped  : {len(annotated_edges):,}")

    if not annotated_edges:
        raise RuntimeError(
            "No high-confidence edges with two mapped partners were found."
        )

    # Rank: combined_score descending; ties broken by ascending protein IDs.
    annotated_edges.sort(key=lambda row: (-row[2], row[0], row[1]))
    top_rows = annotated_edges[:TOP_N]

    with open(OUTPUT_INTERACTIONS, "w", encoding="utf-8") as handle:
        handle.write(
            "Protein1_STRING_ID\tProtein2_STRING_ID\tCombined_Score\t"
            "Protein1_Name\tProtein2_Name\t"
            "Protein1_Ensembl_Gene_ID\tProtein2_Ensembl_Gene_ID\n"
        )
        for p1, p2, score, name1, name2, gene1, gene2 in top_rows:
            handle.write(f"{p1}\t{p2}\t{score}\t{name1}\t{name2}\t{gene1}\t{gene2}\n")
    print(f"Wrote {len(top_rows):,} interactions -> {OUTPUT_INTERACTIONS}")

    print(f"\n=== Top {SAMPLE_N} high-confidence interactions (for README) ===")
    print(row_markdown([row[:5] for row in top_rows[:SAMPLE_N]]))


if __name__ == "__main__":
    main()