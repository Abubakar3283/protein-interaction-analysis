# Mus musculus Protein Pipeline

Analysis of the mouse (*Mus musculus*) proteome using STRINGdb v12.0 protein information data.

## Data Source

| Attribute | Value |
|---|---|
| Database | STRINGdb v12.0 |
| Organism | *Mus musculus* (house mouse) |
| NCBI Taxonomy ID | 10090 |
| Input file | `data/10090.protein.info.v12.0.txt.gz` (tab-separated, gzipped) |
| Columns | `#string_protein_id`, `preferred_name`, `protein_size`, `annotation` |

## Analysis Script

The script [`scripts/analyze_lengths.py`](scripts/analyze_lengths.py) reads the gzipped TSV, parses every protein record, and computes length statistics. Results are printed to the console and saved as JSON in `results/protein_length_stats.json`.

```bash
python3 scripts/analyze_lengths.py
```

## Summary Statistics

| Metric | Value |
|---|---|
| **Total proteins** | 21,840 |
| **Min length** | 12 aa |
| **Max length** | 32,000 aa |
| **Mean length** | 537.82 aa |

## Top 5 Largest Proteins

| Rank | Protein ID | Preferred Name | Length (aa) |
|---:|---|---|---:|
| 1 | `10090.ENSMUSP00000107477` | Ttn (Titin) | 32,000 |
| 2 | `10090.ENSMUSP00000147104` | Muc16 | 8,478 |
| 3 | `10090.ENSMUSP00000038264` | Obscn | 8,032 |
| 4 | `10090.ENSMUSP00000138308` | Dst | 7,717 |
| 5 | `10090.ENSMUSP00000095507` | Macf1 | 7,355 |

## Notes

- **Titin (Ttn)** dwarfs every other protein — at 32,000 amino acids it is nearly 4× larger than the runner-up (Muc16, 8,478 aa). Titin is the largest known protein in mammals and acts as a molecular spring in sarcomeres.
- The minimum protein length is 12 aa. STRINGdb occasionally reports very short or truncated entries; the mean of ~538 aa is typical for a mammalian proteome.
- Length values are in amino acids (aa).

## Results JSON

Structured output is written to `results/protein_length_stats.json` for downstream tooling:

```json
{
  "total_proteins": 21840,
  "min_length": 12,
  "max_length": 32000,
  "mean_length": 537.82,
  "top_5_largest": [
    { "rank": 1, "protein_id": "10090.ENSMUSP00000107477", "preferred_name": "Ttn", "protein_size": 32000 }
  ]
}
```