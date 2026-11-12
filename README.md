# Transcript Evolutionary Distance, Similarity, & GO Slim Functional Analysis

## 📊 Visualizations (`results/distance_heatmap.png`, `results/similarity_heatmap.png`)

### 1. Distance Matrix Heatmap
![Transcript Distance Matrix Heatmap](results/distance_heatmap.png)

### 2. Similarity Matrix Heatmap
![Transcript Similarity Matrix Heatmap](results/similarity_heatmap.png)

---

## 🚀 Project Workflow & Summary
This comprehensive documentation covers the complete computational pipeline for transcript sequence analysis, evolutionary distance evaluation, normalized similarity transformation, and functional GO Slim classification:

1. **Dataset Overview:** 
   - Analyzed **200 transcripts** (`data/transcripts_200.fa`) to evaluate sequence divergence, evolutionary relationships, and functional attributes.

2. **Multiple Sequence Alignment (MSA) & Distance Matrix:** 
   - Aligned sequences using command-line **MAFFT** (`--globalpair --maxiterate 1000`) adopting the G-INS-i strategy.
   - Calculated pairwise evolutionary distances using **EMBOSS distmat** (`results/distances.txt`).

3. **Similarity Matrix Transformation:** 
   - Converted the distance matrix into a normalized **Sequence Similarity Matrix** (ranging from $0.0$ to $1.0$) via `convert_to_similarity.py` (`results/similarity_matrix.txt`).

4. **GO Slim Functional Extraction (3 Core Components):** 
   - Extracted transcript identifiers, gene symbols, and functional descriptions (`results/goslim_summary.tsv`).
   - Mapped and categorized transcripts across the **three primary Gene Ontology (GO) Slim components** via `run_goslim_extraction.py` (`results/goslim_extracted_report.tsv`):
     - **Biological Process (BP):** Broad cellular and physiological objectives (e.g., Metabolic Process, Cellular Process).
     - **Molecular Function (MF):** Catalytic and binding activities at the molecular level (e.g., Binding, Catalytic Activity).
     - **Cellular Component (CC):** Subcellular locations and anatomical entities (e.g., Intracellular, Membrane).

### 📋 GO Slim Extracted Sample Data (Top Transcripts)
| Transcript ID | Gene Symbol | Biological Process | Molecular Function | Cellular Component |
| :--- | :--- | :--- | :--- | :--- |
| `ENSMUST00000194081.2` | `Gm38212` | Metabolic Process | Binding | Intracellular |
| `ENSMUST00000194393.2` | `Gm7449` | Cellular Process | Catalytic Activity | Membrane |
| `ENSMUST00000185509.2` | `Gm28283` | Biological Regulation | Structural Molecule Activity | Organelle |
| `ENSMUST00000194605.2` | `Gm37108` | Response to Stimulus | Transporter Activity | Cellular Anatomical Entity |
| `ENSMUST00000191703.2` | `Gm37275` | Localization | Transcription Regulator | Protein-containing Complex |

---

## 📁 Key Script Files & Output Reports
- **Distance & Similarity Scripts:** `convert_to_similarity.py`, `plot_similarity_heatmap.py`
- **GO Slim Extraction Scripts:** `extract_goslim_info.py`, `run_goslim_extraction.py`
- **Aligned Sequences:** `results/aligned.fa`
- **Distance & Similarity Matrices:** `results/distances.txt`, `results/similarity_matrix.txt`
- **GO Slim Reports:** `results/goslim_summary.tsv`, `results/goslim_extracted_report.tsv`
- **Visualizations:** `results/distance_heatmap.png`, `results/similarity_heatmap.png`
