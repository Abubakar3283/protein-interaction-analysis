# 🗘 Data Dictionary & Onboarding Guide for Laboratory Research

Welcome! This document provides a complete overview of the raw data files, processed outputs, analytical pipelines, and CLI tools used in this project. Use this reference to navigate the project workspace without needing to inspect large raw files directly.

---

## 📂 Project Data Dictionary

|File Path | Origin / Source | File Type & Format | Core Contents | Project Role & Utility |
|:--- |:--- |:--- |:--- |:--- |
| `data/genes.gff3` | **Ensembl** (Mouse Genome) | GFF3Tabular Annotation | Genomic coordinates of genes, exons, and CDS (plus ENSMUST & ENSMUSP identifiers). | **The Central Dogma Bridge:** Used to extract CDS attributes to map transcripts to proteins. |
| `data/cdna.fa` | **Ensembl** (Mouse cDNA) | FASTASequence File | Complete nucleotide cDNA sequences (used as base for building BLAST database). | **BLASTN Input:** Builds local BLAST db and serves as self-homology query input. |
| `data/protein.links.v12.0.txt` | **STRING DB** v12.0 | Space-delimited Tabular | Pairwise functional protein-associations with combined confidence scores. | **Functional PPI Layer:** Provides cellular-interaction ground truth. |
| `data/transcript_to_protein.tsv` | Extracted from gFF3 | TSV Lookup Table | Two columns mapping ENSMUST directly to ENSMUSP (66,789 coding pairs). | **Fast Lookup Table:** Used by Python translation scripts for memory-efficient ID conversion. |
| `results/cdna_blastn_self_results.tsv` | Output of blastn | TSV Tabular (outfmt 6) | 12 standard BLAST columns recording pairwise nucleotide alignments (920,650 rows). | **Raw Sequence Homology:** Quantifies sequence similarity at transcript level. |
| `results/protein_blastn_translated.tsv` | Output of Translation | TSV Tabular | Translated pairwise alignments mapped to protein pairs (385,773 records). | **Integrated Output:** Clean, protein-level homology pairs ready for data-fusion. |

---

## 🙒 Required Software & Conda Environment

```bash
conda activate blast_env
```

- **NCBI BLAST+:** blastn, makeblastdb for sequence database alignment.
- **GNU Coreutils:** awk, grep, sort, wc, head for stream processing.
- **Python 3:** For ID translation, logical collision audit, and data fusion.

---

## 🔄 Published Task Documentation
- `Task_109_blastn_protein_translation.md`: Full 3-way translation audit (41.90% translated, 58.10% dropped non-coding, 20.96% self-loops).
- `Task_107_108_blastn_self_analysis.md`: BLASTN self-alignment benchmarks.
- `README.md`: Comprehensive Linux, shell, and version-control cheatsheet.
