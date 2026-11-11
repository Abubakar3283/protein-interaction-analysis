kk# Bioinformatics Project: Transcript Alignment, Clustering & Similarity Heatmaps

## 🚀 Project Summary & Complete Workflow
This repository documents the complete, step-by-step bioinformatics workflow for transcript sequence analysis:

1. **Multiple Sequence Alignment (MSA):**
   - Executed iterative multiple sequence alignments on nucleotide transcripts using command-line **MAFFT** (`--globalpair --maxiterate 1000` configuration, utilizing G-INS-i strategy for high-accuracy global alignment).
   - Input: `data/transcripts_200.fa` ➡️ Output: `results/aligned.fa`.

2. **Distance Matrix Calculation:**
   - Generated pairwise distance matrices using **EMBOSS distmat** (Lower Triangular format) to evaluate sequence divergence distances among transcripts.

3. **Data Parsing & Normalization:**
   - Developed custom Python scripts to parse distance data, clean formatting, and convert raw distances into normalized similarity scores ($0 \text{ to } 1$).

4. **Hierarchical Clustering & Heatmaps:**
   - Applied Scipy's hierarchical clustering (`sch.linkage`) and visualized high-resolution similarity heatmaps with proper axis labels and color gradients.

---

## 📊 Visualizations & Results

### 1. Standard Similarity Heatmap (`results/heatmap.png`)
![Similarity Heatmap](results/heatmap.png)

### 2. Clustered Similarity Heatmap (`results/clustered_similarity_heatmap.png`)
![Clustered Similarity Heatmap](results/clustered_similarity_heatmap.png)

---

## 📁 Repository Output Files
- **Aligned Sequences:** `results/aligned.fa`
- **Distance Matrix:** `results/distances.txt`
- **Standard Heatmap:** `results/heatmap.png`
- **Clustered Heatmap:** `results/clustered_similarity_heatmap.png`
