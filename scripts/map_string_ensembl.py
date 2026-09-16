#!/usr/bin/env python3
"""Map STRING protein IDs to Ensembl protein IDs and Ensembl gene IDs.

Merges two datasets for *Mus musculus* (NCBI taxid 10090):

1. STRING v12.0  -- ``data/10090.protein.info.v12.0.txt.gz``
     Tab-separated; first column is the STRING protein ID
     (``10090.ENSMUSP00000000001``), second column is the preferred
     protein/gene name (e.g. ``Gnai3``).

2. Ensembl GFF3 -- ``data/genes.gff3.gz``
     The gene association is recovered by walking the GFF3 feature
     hierarchy:

        gene  (a.k.a. ``gene:ENSMUSG...``)
          └── transcript / mRNA  -- ``Parent=gene:...``, ``ID=transcript:...``
                └── CDS          -- ``Parent=transcript:...``, ``protein_id=ENSMUSP...``

     i.e.  Ensembl protein ID (CDS ``protein_id``) -> parent transcript
     -> parent gene (``transcript``/``mRNA`` ``Parent=gene:...``).

Outputs:

- ``results/string_to_ensembl_mapping.tsv``     -- top 1000 rows (header)
- ``results/string_to_ensembl_mapping_sample.tsv`` -- first 10 rows (header)
- A Markdown table of the 10-row sample is printed to stdout for the README.

Run from the repository root:  python scripts/map_string_ensembl.py
"""

from __future__ import annotations

import gzip
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"

GFF3_FILE = DATA_DIR / "genes.gff3.gz"
STRING_FILE = DATA_DIR / "10090.protein.info.v12.0.txt.gz"

OUTPUT_MAPPING = RESULTS_DIR / "string_to_ensembl_mapping.tsv"
OUTPUT_SAMPLE = RESULTS_DIR / "string_to_ensembl_mapping_sample.tsv"

TOP_N = 1000  # number of mappings to write to the main output
SAMPLE_N = 10  # number of rows in the README sample table

# Feature types in the GFF3 that carry a gene parent and a transcript ID.
_TRANSCRIPT_FEATURES = {
    "transcript",
    "mRNA",
    "lnc_RNA",
    "pseudogenic_transcript",
    "unconfirmed_transcript",
}

GENE_PARENT_PREFIX = "gene:"
TRANSCRIPT_ID_PREFIX = "transcript:"
STRING_TAXON_PREFIX = "10090."


def parse_attributes(attr_field: str) -> dict[str, str]:
    """Parse the GFF3 column-9 attribute string into a dictionary.

    Attributes are ``key=value`` pairs separated by semicolons
    (e.g. ``ID=CDS:ENSMUSP...;Parent=transcript:ENSMUST...;protein_id=...``).
    """
    attrs: dict[str, str] = {}
    for part in attr_field.split(";"):
        if "=" in part:
            key, _, value = part.partition("=")
            attrs[key] = value
    return attrs


def build_protein_to_gene_map(
    gff3_path: Path,
) -> tuple[dict[str, str], dict[str, str]]:
    """Return (protein->gene, transcript->gene) maps parsed from the GFF3.

    Single pass over the gzipped file:

    * ``transcript``-like features record the transcript ID -> gene ID link
      from their ``transcript_id``/``ID`` and ``Parent=gene:...`` attributes.
    * ``CDS`` features record the protein ID -> transcript ID link from
      their ``protein_id`` and ``Parent=transcript:...`` attributes.

    The protein -> gene map is finalized after the pass by chaining the two.
    """
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
                if protein_id is not None and parent.startswith(TRANSCRIPT_ID_PREFIX):
                    protein_to_transcript[protein_id] = parent[len(TRANSCRIPT_ID_PREFIX):]

    protein_to_gene = {
        protein_id: transcript_to_gene[transcript_id]
        for protein_id, transcript_id in protein_to_transcript.items()
        if transcript_id in transcript_to_gene
    }
    return protein_to_gene, transcript_to_gene


def read_string_records(string_path: Path) -> list[tuple[str, str]]:
    """Read STRING records as (string_protein_id, preferred_name) tuples."""
    records: list[tuple[str, str]] = []
    with gzip.open(string_path, "rt", encoding="utf-8") as handle:
        next(handle)  # skip the '#string_protein_id ...' header line
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 2 or not fields[0]:
                continue
            protein_id = fields[0]
            preferred_name = fields[1].strip()
            records.append((protein_id, preferred_name))
    return records


def ensembl_protein_id(string_protein_id: str) -> str | None:
    """Strip the ``10090.`` taxon prefix from a STRING protein ID."""
    if string_protein_id.startswith(STRING_TAXON_PREFIX):
        return string_protein_id[len(STRING_TAXON_PREFIX):]
    return None


def row_markdown(rows: list[tuple[str, str, str, str]]) -> str:
    """Render the correspondence rows as a GitHub-flavoured Markdown table."""
    header = "| STRING Protein ID | Ensembl Protein ID | Ensembl Gene ID | Protein Name |"
    divider = "|---|---|---|---|"
    lines = [header, divider]
    for string_id, ensembl_id, gene_id, name in rows:
        lines.append(
            f"| `{string_id}` | `{ensembl_id}` | `{gene_id}` | {name} |"
        )
    return "\n".join(lines)


def main() -> None:
    if not GFF3_FILE.exists():
        raise FileNotFoundError(f"Missing input: {GFF3_FILE}")
    if not STRING_FILE.exists():
        raise FileNotFoundError(f"Missing input: {STRING_FILE}")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Parsing GFF3   : {GFF3_FILE.name}")
    protein_to_gene, transcript_to_gene = build_protein_to_gene_map(GFF3_FILE)
    print(
        f"  transcript -> gene : {len(transcript_to_gene):,} transcripts"
    )
    print(
        f"  protein   -> gene : {len(protein_to_gene):,} proteins"
    )

    print(f"Parsing STRING : {STRING_FILE.name}")
    string_records = read_string_records(STRING_FILE)
    print(f"  STRING records    : {len(string_records):,}")

    # Merge the two datasets, preserving STRING file order.
    merged: list[tuple[str, str, str, str]] = []
    matched = 0
    for string_id, preferred_name in string_records:
        ensembl_id = ensembl_protein_id(string_id)
        if ensembl_id is None:
            continue
        gene_id = protein_to_gene.get(ensembl_id)
        if gene_id is None:
            continue
        matched += 1
        merged.append((string_id, ensembl_id, gene_id, preferred_name))

    print(
        f"Matched {matched:,} / {len(string_records):,} "
        f"STRING proteins to an Ensembl gene"
    )

    if not merged:
        raise RuntimeError("No STRING-to-Ensembl mappings were produced.")

    # -- main output: TOP_N mappings ---------------------------------------
    top_rows = merged[:TOP_N]
    with open(OUTPUT_MAPPING, "w", encoding="utf-8") as handle:
        handle.write("STRING_Protein_ID\tEnsembl_Protein_ID\tEnsembl_Gene_ID\tProtein_Name\n")
        for string_id, ensembl_id, gene_id, name in top_rows:
            handle.write(f"{string_id}\t{ensembl_id}\t{gene_id}\t{name}\n")
    print(f"Wrote {len(top_rows):,} mappings -> {OUTPUT_MAPPING}")

    # -- sample output for the README --------------------------------------
    sample_rows = merged[:SAMPLE_N]
    with open(OUTPUT_SAMPLE, "w", encoding="utf-8") as handle:
        handle.write("STRING_Protein_ID\tEnsembl_Protein_ID\tEnsembl_Gene_ID\tProtein_Name\n")
        for string_id, ensembl_id, gene_id, name in sample_rows:
            handle.write(f"{string_id}\t{ensembl_id}\t{gene_id}\t{name}\n")
    print(f"Wrote {len(sample_rows)} sample rows -> {OUTPUT_SAMPLE}")

    print("\n=== Sample correspondence table (for README) ===")
    print(row_markdown(sample_rows))


if __name__ == "__main__":
    main()