# Bioinformatics Project: Transcript Alignment & Similarity Heatmap

## 📊 Heatmap & Clustering Visualizations

### 1. Similarity Heatmap (`results/heatmap.png`)
![Similarity Heatmap](results/heatmap.png)

### 2. Hierarchical Clustering Heatmap (`results/clustered_similarity_heatmap.png`)
![Clustered Similarity Heatmap](results/clustered_similarity_heatmap.png)

## 🚀 Project Summary & Workflow
This repository documents the complete bioinformatics workflow for transcript sequence analysis:
1. **BLAST Search:** Performed sequence alignment and similarity searches across transcript datasets.
2. **Distance Matrix Calculation:** Generated pairwise distance matrices using **EMBOSS distmat** (Lower Triangular format).
3. **Heatmap Generation & Clustering:** Developed custom Python scripts to parse distance data, perform hierarchical clustering, and plot high-resolution similarity heatmaps with proper axis labels and color gradients.

## 📁 Results & Output Files
- **Distance Matrix:** `results/distances.txt`
- **Similarity Heatmap:** `results/heatmap.png`
- **Clustered Heatmap:** `results/clustered_similarity_heatmap.png`
