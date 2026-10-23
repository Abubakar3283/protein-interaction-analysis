# Task 121: Sequence Similarity Comparison Between BLASTN and BLASTP

## 1. Overview & Biological Objective
Nucleotide-level similarity (BLASTN) and amino acid-level similarity (BLASTP) provide complementary evolutionary insights. Due to codon degeneracy, nucleotide sequences often diverge faster than corresponding protein sequences.

This task compares:
1. **BLASTN-derived Protein Pairs:** Transcripts aligned via BLASTN and mapped to protein IDs (`results/protein_blastn_translated.tsv`).
2. **Direct BLASTP Pairs:** Protein sequences aligned directly against the mouse proteome (`results/protein_blastp_self_results.tsv`).

The objective is to quantify correlation, find overlapping pairs, and visualize the similarity distribution via a scatterplot.

---

## 2. Execution Pipeline

```text
       Mus_musculus.GRCm39.pep.all.fa
                       │
                       ▼  [ makeblastdb -dbtype prot ]
            data/mouse_protein_db
                       │
                       ▼  [ blastp -num_threads 8 -max_target_seqs 50 -evalue 1e-5 ]
         results/protein_blastp_self_results.tsv  (197 MB | 1,551,771 Unique Pairs)
                       │
                       ├─────────────────────────────────────────────────┐
                       │                                                 │
                       ▼                                                 ▼
       results/protein_blastp_self_results.tsv         results/protein_blastn_translated.tsv
          (Direct Protein Identity %)                   (Translated Nucleotide Identity %)
                       │                                                 │
                       │           [ scripts/compare_blastn_blastp.py ] │
                       └───────────────────────────────┬─────────────────┘
                                                       │
                                        Inner Join on (qseqid, sseqid)
                                                       │
                                                       ▼
                                         COMMON PAIRS: 229,468
                                    Pearson r: 0.6400 | Spearman rho: 0.4387
                                                       │
                                ┌──────────────────────┴──────────────────────┐
                                ▼                                             ▼
            results/blastn_vs_blastp_merged.tsv        results/blastn_vs_blastp_scatterplot.png

project-practice/
├── data/
│   ├── Mus_musculus.GRCm39.pep.all.fa          # Primary mouse protein FASTA
│   └── mouse_protein_db.*                      # Formatted BLASTP database files
├── scripts/
│   └── compare_blastn_blastp.py                # Python analysis & visualization script
├── results/
│   ├── protein_blastn_translated.tsv           # Input 1: Translated BLASTN results
│   ├── protein_blastp_self_results.tsv         # Input 2: BLASTP self-alignment results (197 MB)
│   ├── blastn_vs_blastp_merged.tsv             # Matched common protein pairs (229,468 rows)
│   └── blastn_vs_blastp_scatterplot.png        # Comparative identity scatterplot
└── Task_121_blastn_vs_blastp_comparison.md     # Pipeline documentation


