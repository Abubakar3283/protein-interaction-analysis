#!/usr/bin/env python3
"""Identify hub proteins in the STRING v12.0 mouse high-confidence PPI network.

Processes the STRING v12.0 *Mus musculus* interaction network
``data/10090.protein.links.v12.0.txt.gz`` (12,684,354 scored pairwise
edges), then:

1. **Filter** -- keeps only edges with ``combined_score >= 900``
   (STRING's "highest confidence" band), i.e. the same edge set that
   ``scripts/filter_interactions.py`` counts.

2. **Degree** -- for every protein, counts its **unique** interacting
   partners among the high-confidence edges (the node degree of the
   high-confidence sub-network). Proteins with the highest degree are
   the network's hubs.

3. **Annotate** -- each hub is resolved against the STRING → Ensembl
   correspondence table ``results/string_to_ensembl_mapping.tsv``
   (written by ``scripts/map_string_ensembl.py``) to attach the gene
   symbol (``Protein_Name``) and Ensembl gene ID, and against
   ``data/10090.protein.info.v12.0.txt.gz`` for the biological
   annotation (UniProt-derived summary from STRING).

   **Coverage fallback.** The correspondence table stores only the first
   1,000 STRING records (see README §7.2), and the hub proteins fall
   outside that prefix. For hubs missing from the table, the Ensembl gene
   ID is recovered directly from the same GFF3-derived protein → gene
   walk that ``scripts/map_string_ensembl.py`` uses (CDS ``protein_id``
   -> parent transcript -> parent gene), and the gene symbol falls back
   to the STRING ``preferred_name`` -- the exact value the mapping
   table's ``Protein_Name`` column is built from. The annotation
   resolution is therefore complete without modifying any existing file.

4. **Report** -- the Top 20 hubs are written to
   ``results/top20_hub_proteins.tsv`` and the Top 10 are rendered as a
   horizontal bar plot at ``results/top10_hub_proteins.png``; a Markdown
   table of the Top 10 is printed to stdout for the README.

Note on parsing: the ``protein.links`` file is *space*-delimited (unlike
the tab-delimited ``protein.info`` file), but the ID and score fields
contain no whitespace, so simple row splitting handles it in both cases.

Run from the repository root:  python scripts/find_hub_proteins.py
"""

from __future__ import annotations

import gzip
from pathlib import Path
from typing import Iterator, NamedTuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"

LINKS_FILE = DATA_DIR / "10090.protein.links.v12.0.txt.gz"
INFO_FILE = DATA_DIR / "10090.protein.info.v12.0.txt.gz"
GFF3_FILE = DATA_DIR / "genes.gff3.gz"
MAPPING_FILE = RESULTS_DIR / "string_to_ensembl_mapping.tsv"

OUTPUT_HUBS = RESULTS_DIR / "top20_hub_proteins.tsv"
OUTPUT_PLOT = RESULTS_DIR / "top10_hub_proteins.png"

SCORE_THRESHOLD = 900  # STRING 'highest confidence' band
TOP_N = 20  # number of hubs written to the TSV
PLOT_N = 10  # number of hubs rendered in the figure
SAMPLE_N = 10  # rows in the README sample table

STRING_TAXON_PREFIX = "10090."
GENE_PARENT_PREFIX = "gene:"
TRANSCRIPT_ID_PREFIX = "transcript:"
_TRANSCRIPT_FEATURES = {
    "transcript",
    "mRNA",
    "lnc_RNA",
    "pseudogenic_transcript",
    "unconfirmed_transcript",
}

# Publication-style figure defaults
PLOT_DPI = 300
FIG_SIZE = (9, 6)
BAR_COLOR = "#4C72B0"
LABEL_COLOR = "#333333"


class Mapping(NamedTuple):
    """One row of the STRING -> Ensembl correspondence table."""

    ensembl_protein_id: str
    ensembl_gene_id: str
    protein_name: str


class InfoRecord(NamedTuple):
    """Preferred name and biological annotation from the STRING info file."""

    protein_name: str
    annotation: str


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


def read_info_records(info_path: Path) -> dict[str, InfoRecord]:
    """Load STRING protein ID -> (preferred name, annotation) from the info TSV."""
    records: dict[str, InfoRecord] = {}
    with gzip.open(info_path, "rt", encoding="utf-8") as handle:
        next(handle)  # '#string_protein_id preferred_name protein_size annotation'
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 2 or not fields[0]:
                continue
            records[fields[0]] = InfoRecord(
                protein_name=fields[1].strip(),
                annotation=fields[3].strip() if len(fields) >= 4 else "",
            )
    return records


def parse_attributes(attr_field: str) -> dict[str, str]:
    """Parse the GFF3 column-9 attribute string into a dictionary."""
    attrs: dict[str, str] = {}
    for part in attr_field.split(";"):
        if "=" in part:
            key, _, value = part.partition("=")
            attrs[key] = value
    return attrs


def resolve_missing_genes(
    gff3_path: Path, protein_ids: set[str]
) -> dict[str, str]:
    """Resolve Ensembl gene IDs from the GFF3 for the given Ensembl protein IDs.

    Walks the GFF3 feature hierarchy exactly as ``map_string_ensembl.py``
    does: a CDS ``protein_id`` points to its parent transcript, which in
    turn points to its parent gene. Returns ``{ensembl_protein_id: gene_id}``
    for the requested proteins that could be resolved. The transcript →
    gene dictionary must be complete (142,819 transcripts), so one pass
    over the gzipped file covers all requested proteins regardless of order.
    """
    if not protein_ids:
        return {}
    transcript_to_gene: dict[str, str] = {}
    protein_to_transcript: dict[str, str] = {}

    with gzip.open(gff3_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                continue
            feature_type = fields[2]
            attrs = parse_attributes(fields[8])

            if feature_type in _TRANSCRIPT_FEATURES:
                transcript_id = attrs.get("transcript_id")
                if transcript_id is None:
                    raw_id = attrs.get("ID", "")
                    if raw_id.startswith(TRANSCRIPT_ID_PREFIX):
                        transcript_id = raw_id[len(TRANSCRIPT_ID_PREFIX):]
                parent = attrs.get("Parent", "")
                if (
                    transcript_id is not None
                    and parent.startswith(GENE_PARENT_PREFIX)
                ):
                    transcript_to_gene[transcript_id] = parent[len(GENE_PARENT_PREFIX):]

            elif feature_type == "CDS":
                protein_id = attrs.get("protein_id")
                parent = attrs.get("Parent", "")
                if (
                    protein_id in protein_ids
                    and parent.startswith(TRANSCRIPT_ID_PREFIX)
                ):
                    protein_to_transcript[protein_id] = parent[len(TRANSCRIPT_ID_PREFIX):]

    return {
        protein_id: transcript_to_gene[transcript_id]
        for protein_id, transcript_id in protein_to_transcript.items()
        if transcript_id in transcript_to_gene
    }


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


def clean_annotation(annotation: str) -> str:
    """Flatten a TSV field so it can never corrupt the output table."""
    return annotation.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def row_markdown(rows: list[tuple[int, str, str, str, int]]) -> str:
    """Render the top hubs as a GitHub-flavoured Markdown table."""
    header = "| Rank | Gene Symbol | Ensembl Gene ID | STRING Protein ID | Degree |"
    divider = "|---:|---|---|---:|---:|"
    lines = [header, divider]
    for rank, symbol, gene_id, protein_id, degree in rows:
        lines.append(
            f"| {rank} | **{symbol}** | `{gene_id}` | `{protein_id}` | {degree} |"
        )
    return "\n".join(lines)


def render_plot(hubs: list[dict[str, object]]) -> None:
    """Render a horizontal bar plot of the top hubs by degree."""
    # The list is already sorted by degree descending; reverse so the
    # most-connected hub appears at the top of the horizontal chart.
    labels = [str(hub["gene_symbol"]) for hub in reversed(hubs)]
    degrees = [int(hub["degree"]) for hub in reversed(hubs)]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=PLOT_DPI)
    bars = ax.barh(labels, degrees, color=BAR_COLOR, edgecolor="white", linewidth=0.5)

    for bar, value in zip(bars, degrees):
        ax.text(
            bar.get_width() + max(degrees) * 0.01,
            bar.get_y() + bar.get_height() / 2.0,
            f"{value:,}",
            va="center",
            ha="left",
            fontsize=10,
            color=LABEL_COLOR,
        )

    ax.set_xlabel("Degree (unique high-confidence partners)", fontsize=12)
    ax.set_ylabel("Gene symbol", fontsize=12)
    ax.set_title(
        "Top 10 hub proteins in the mouse high-confidence PPI network\n"
        f"(STRING v12.0, combined score \u2265 {SCORE_THRESHOLD})",
        fontsize=13,
    )

    ax.grid(True, axis="x", linestyle=":", linewidth=0.6, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0.15)
    fig.tight_layout()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PLOT, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not LINKS_FILE.exists():
        raise FileNotFoundError(f"Missing input: {LINKS_FILE}")
    if not INFO_FILE.exists():
        raise FileNotFoundError(f"Missing input: {INFO_FILE}")
    if not GFF3_FILE.exists():
        raise FileNotFoundError(f"Missing input: {GFF3_FILE}")
    if not MAPPING_FILE.exists():
        raise FileNotFoundError(f"Missing input: {MAPPING_FILE}")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading correspondence : {MAPPING_FILE.name}")
    mapping = read_mapping(MAPPING_FILE)
    print(f"  mapped proteins      : {len(mapping):,}")

    print(f"Loading INFO records   : {INFO_FILE.name}")
    info = read_info_records(INFO_FILE)
    print(f"  annotated proteins  : {len(info):,}")

    print(f"Streaming links       : {LINKS_FILE.name}")
    total_edges = 0
    high_confidence = 0
    partners: dict[str, set[str]] = {}
    for p1, p2, score in iter_edges(LINKS_FILE):
        total_edges += 1
        if score < SCORE_THRESHOLD:
            continue
        high_confidence += 1
        if p1 == p2:
            continue
        partners.setdefault(p1, set()).add(p2)
        partners.setdefault(p2, set()).add(p1)

    print(f"  total edges          : {total_edges:,}")
    print(
        f"  combined_score >= {SCORE_THRESHOLD} : "
        f"{high_confidence:,} ({100.0 * high_confidence / total_edges:.2f}%)"
    )
    print(f"  proteins in sub-graph: {len(partners):,}")

    if not partners:
        raise RuntimeError("No high-confidence edges were found in the network.")

    # Rank: degree descending; ties broken by STRING protein ID order.
    ranked = sorted(partners.items(), key=lambda item: (-len(item[1]), item[0]))
    top_hubs = ranked[:TOP_N]

    # Resolve Ensembl gene IDs for hubs missing from the mapping table via
    # the same GFF3-derived correspondence the mapping table was built from.
    missing_ids = {
        protein_id[len(STRING_TAXON_PREFIX):]: protein_id
        for protein_id, _ in top_hubs
        if protein_id not in mapping and protein_id.startswith(STRING_TAXON_PREFIX)
    }
    gff3_genes = (
        resolve_missing_genes(GFF3_FILE, set(missing_ids)) if missing_ids else {}
    )

    rows: list[dict[str, object]] = []
    table_resolved = 0
    gff3_resolved = 0
    for rank, (protein_id, partner_set) in enumerate(top_hubs, start=1):
        m = mapping.get(protein_id)
        info_rec = info.get(protein_id)
        if m is not None:
            gene_symbol = m.protein_name
            ensembl_gene_id = m.ensembl_gene_id
            table_resolved += 1
        else:
            ensembl_protein_id = protein_id[len(STRING_TAXON_PREFIX):]
            ensembl_gene_id = gff3_genes.get(ensembl_protein_id, "")
            gene_symbol = info_rec.protein_name if info_rec else protein_id
            if ensembl_gene_id:
                gff3_resolved += 1
        rows.append(
            {
                "rank": rank,
                "protein_id": protein_id,
                "gene_symbol": gene_symbol,
                "ensembl_gene_id": ensembl_gene_id,
                "degree": len(partner_set),
                "annotation": clean_annotation(
                    info_rec.annotation if info_rec else ""
                ),
            }
        )

    print(
        f"  hub annotation       : {table_resolved}/{len(rows)} via mapping table, "
        f"{gff3_resolved}/{len(rows)} via GFF3 fallback"
    )

    with open(OUTPUT_HUBS, "w", encoding="utf-8") as handle:
        handle.write(
            "Rank\tSTRING_Protein_ID\tGene_Symbol\tEnsembl_Gene_ID\t"
            "Degree\tAnnotation\n"
        )
        for row in rows:
            handle.write(
                f"{row['rank']}\t{row['protein_id']}\t{row['gene_symbol']}\t"
                f"{row['ensembl_gene_id']}\t{row['degree']}\t{row['annotation']}\n"
            )
    print(f"Wrote {len(rows):,} hubs -> {OUTPUT_HUBS}")

    render_plot(rows[:PLOT_N])
    print(f"Plot saved to          : {OUTPUT_PLOT}")

    print(f"\n=== Top {SAMPLE_N} hub proteins (for README) ===")
    print(
        row_markdown(
            [
                (
                    int(row["rank"]),
                    str(row["gene_symbol"]),
                    str(row["ensembl_gene_id"]),
                    str(row["protein_id"]),
                    int(row["degree"]),
                )
                for row in rows[:SAMPLE_N]
            ]
        )
    )


if __name__ == "__main__":
    main()