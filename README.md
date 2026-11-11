# Bioinformatics Project: Transcript Alignment & Similarity Heatmap

## 📊 Heatmap & Clustering Visualization
![Similarity Heatmap](results/heatmap.png)

## 🚀 Project Summary & Workflow
This repository documents the complete bioinformatics workflow for transcript sequence analysis:
1. **BLAST Search:** Performed sequence alignment and similarity searches across transcript datasets.
2. **Distance Matrix Calculation:** Generated pairwise distance matrices using **EMBOSS distmat** (Lower Triangular format).
3. **Heatmap Generation:** Developed a custom Python script to parse the distance data and plot the high-resolution **Blue and Red similarity heatmap** with proper axis labels and hierarchical clustering.

## 📁 Results & Output Files
- **Distance Matrix:** `results/distances.txt`
- **Similarity Heatmap Visualization:** `results/heatmap.png`
