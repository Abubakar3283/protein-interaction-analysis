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


---


### Task: Sequence Similarity Matrix and Heatmap Generation

In this task, we extended our evolutionary distance analysis by transforming the distance matrix into a normalized **Sequence Similarity Matrix** and visualizing it using a comprehensive heatmap.

#### 1. Objective and Significance
* **Why it was done:** While evolutionary distance matrices highlight divergence between transcripts, many downstream clustering and machine learning algorithms perform more effectively with **Similarity Scores** (ranging from $0.0$ to $1.0$, where $1.0$ represents identical transcripts). 
* **Transformation Method:** The distance matrix values were normalized and converted using the formula:
  $$\text{Similarity} = 1.0 - \left( \frac{\text{Distance}}{\text{Max\_Distance}} \right)$$

#### 2. Implementation Scripts
* **`convert_to_similarity.py`**: A Python script that reads `results/distances.txt`, filters out non-numeric headers using robust exception handling, normalizes the distances, and outputs a 2D sequence similarity matrix at `results/similarity_matrix.txt`.
* **`plot_similarity_heatmap.py`**: A Python script that loads the generated similarity matrix and builds a high-resolution heatmap (`results/similarity_heatmap.png`) using the `seaborn` and `matplotlib` libraries with a `coolwarm` colormap.

#### 3. Generated Results & Outputs
* **`results/similarity_matrix.txt`**: Contains the full pairwise sequence similarity score matrix (normalized between 0 and 1).
* **`results/similarity_heatmap.png`**: A 2D matrix heatmap representing the global sequence similarity distribution across all aligned transcripts, allowing clear visual inspection of highly conserved versus divergent transcript clusters.
