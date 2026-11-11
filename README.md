# Bioinformatics Project: Transcript Hierarchical Clustering & Similarity Analysis

## 📌 Project Overview
This repository contains the implementation and results of computational bioinformatics workflows designed to analyze transcript sequences. The primary objective is to compute distance matrices from aligned transcript sequences, convert them into normalized similarity matrices, and perform hierarchical clustering visualized through high-resolution heatmaps and dendrograms.

---

## 🛠️ Methodology & Workflow

1. **Multiple Sequence Alignment (MSA):**
   - Executed iterative multiple sequence alignments on nucleotide transcripts using command-line `MAFFT` configurations (global-pair settings).

2. **Distance Matrix Generation:**
   - Generated pairwise distance matrices using EMBOSS `distmat` (Lower Triangular format) to evaluate evolutionary or sequence divergence distances among transcripts.

3. **Data Parsing & Normalization:**
   - Built a robust Python parsing script (`plot_clustermap.py`) to clean and parse EMBOSS output, handling headers, comments, and missing values.
   - Converted raw distance matrices into normalized similarity matrices ($Similarity = 1 - \frac{Dist - Min}{Max - Min}$) to scale scores between 0 and 1.

4. **Hierarchical Clustering & Visualization:**
   - Applied Scipy's hierarchical clustering (`sch.linkage` with average linkage method) on condensed distance vectors.
   - Generated refined sub-sample heatmaps using Seaborn (`clustermap`) combined with dendrograms to ensure optimal label legibility and cluster clarity.

---

## 📊 Results & Outputs
- **Distance Matrix:** Saved under `results/distances.txt`.
- **Clustered Similarity Heatmap:** High-resolution visualization saved under `results/clustered_similarity_heatmap.png`, illustrating clear cluster groups and similarity scores for transcript sub-samples.

---
