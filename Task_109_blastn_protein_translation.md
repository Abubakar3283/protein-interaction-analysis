python3 -c '
content = """# 🧬 Task 109: BLASTN Transcript-to-Protein Translation & Biological Collision Audit

## 📌 Executive Summary
In this task, we resolved the biological granularity gap between nucleotide sequence alignments and downstream protein-protein interaction networks. Using standard Ensembl CDS annotations from `genes.gff3`, we mapped raw transcript identifiers (`ENSMUST`) generated from the self-alignment BLASTN workflow to their corresponding translated protein identifiers (`ENSMUSP`).

The audit systematically identifies and quantifies biological clashes, specifically unmapped non-coding transcripts (lncRNA, pseudogenes, TEC biotypes) and many-to-one alternative splicing collisions (self-protein loops).

---

## 🔬 Biological Context & Motivation
- **The Problem:** BLASTN self-alignment records pairwise sequence homology at the transcript (cDNA nucleotide) level. However, downstream functional interaction datasets (e.g., STRING) are mapped strictly at the translated protein level (`ENSMUSP`).
- **The Central Dogma Bridge:**
  $$\\\\text{mRNA Transcript } (ENSMUST) \\\\xrightarrow{\\\\text{Translation via CDS}} \\\\text{Functional Protein } (ENSMUSP)$$
- **Primary Challenges (Biological Clashes):**
  1. **Non-coding Transcripts (58.10%):** Not all cDNA transcripts encode proteins (e.g., TEC biotypes, lncRNAs). Pairwise alignments involving non-coding transcripts cannot be mapped to protein nodes.
  2. **Isoform Self-Loops (20.96% of mapped):** Multiple transcript isoforms from the same gene locus frequently translate into the same primary protein sequence, introducing identical self-protein pairs ($P_A \\\\longleftrightarrow P_A$).

---

## 🛠️ Complete 3-Way Pipeline Architecture

```text
                  Raw BLASTN Tabular Alignments
              [ results/cdna_blastn_self_results.tsv ]
                           (920,650 rows)
                                 │
                                 ▼
                Ensembl GFF3 CDS Attribute Parsing
                      [ data/genes.gff3 ]
                                 │
                                 ▼
               Transcript-to-Protein Lookup Table
                [ data/transcript_to_protein.tsv ]
                       (66,789 unique pairs)
                                 │
                                 ▼
            Python Stream Translation & Collision Audit
              [ scripts/translate_blastn_to_protein.py ]
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
   DROPPED (58.10%)                             TRANSLATED (41.90%)
  534,877 Alignments                             385,773 Alignments
(Non-coding / TEC / lncRNA)                              │
                                          ┌──────────────┴──────────────┐
                                          ▼                             ▼
                                IDENTICAL SELF-LOOPS           HOMOLOGOUS PAIRS
                                  80,844 (20.96%)              304,929 (79.04%)
                              Isoform Redundancy               Distinct Proteins
                                 (P_A <-> P_A)                   (P_A <-> P_B)
                                          │                             │
                                          └──────────────┬──────────────┘
                                                         ▼
                                       Saved to: results/protein_blastn_translated.tsv
