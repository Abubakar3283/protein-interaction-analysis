# Mouse Genomic & Interactome Analysis (Tasks 95 - 101)

This repository contains the analysis and data integration pipelines for *Mus musculus* (Taxon ID: 10090) developed under the supervision of **Professor Ping-Han Hsieh**.

---

## 1. Summary of Completed Tasks

| Task ID | Description | Status & Result |
| :---: | :--- | :--- |
| **95** | Understand GFF3 9-column format | Verified: seqid, source, type, start, end, score, strand, phase, attributes |
| **96** | STRING ID to Ensembl Gene ID table | Completed: 97.6% coverage (21,318 / 21,840 mapped) |
| **97** | Map transcript coordinates to protein & genes | Completed: Output in `results/transcript_coordinates_mapping.tsv` |
| **98** | Summarize data schemas | Completed: Documented GFF3 and STRING link schemas |
| **99** | STRING confidence score mechanism | Completed: Probabilistic integration across 7 biological channels |
| **100** | Summarize molecular feature counts | Completed: 869,452 exons, 527,234 CDS, 66,153 mRNAs, 25,412 genes |
| **101** | Unique chromosomes in GFF | Completed: 22 canonical chromosomes (1–19, X, Y, MT) + unplaced scaffolds |

---

## 2. Key Findings & Statistics

### A. Chromosomes (Task 101)
* **Canonical Chromosomes:** 19 autosomes (`1`–`19`), 2 sex chromosomes (`X`, `Y`), and mitochondrial genome (`MT`).
* **Unplaced Scaffolds:** Sequence fragments (`GL...`, `JH...`, `MU...`) representing assembly contigs not anchored to canonical chromosomes.

### B. Molecular Feature Counts (Task 100)
* **Exons:** 869,452
* **CDS:** 527,234
* **mRNA:** 66,153
* **Genes (protein-coding):** 25,412
* **Alternative Splicing Ratio:** ~2.6 mRNA transcripts per gene locus.

---

## 3. Results Preview

### Correspondence Table (Task 96)
Found in `results/string_to_ensembl_mapping_sample.tsv`:
| STRING_Protein_ID | Ensembl_Protein_ID | Ensembl_Gene_ID | Gene_Symbol |
| :--- | :--- | :--- | :--- |
| 10090.ENSMUSP00000000001 | ENSMUSP00000000001 | ENSMUSG00000000001 | Gnai3 |
| 10090.ENSMUSP00000000028 | ENSMUSP00000000028 | ENSMUSG00000000028 | Cdc45 |
| 10090.ENSMUSP00000000049 | ENSMUSP00000000049 | ENSMUSG00000000049 | Apoh |

### Transcript Coordinates Mapping (Task 97)
Found in `results/transcript_coordinates_mapping_sample.tsv`:
| Chromosome | Start | End | Strand | Transcript_ID | Protein_ID | Ensembl_Gene_ID | Gene_Name |
| :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| 1 | 3284705 | 3741721 | - | ENSMUST00000070533 | ENSMUSP00000070648 | ENSMUSG00000051951 | Xkr4-201 |
| 1 | 4069780 | 4479464 | - | ENSMUST00000208660 | NA | ENSMUSG00000025900 | Rp1-202 |
| 1 | 4414369 | 4430537 | - | ENSMUST00000027032 | ENSMUSP00000027032 | ENSMUSG00000025900 | Rp1-201 |

---

## 4. STRING Confidence Score Calculation (Task 99)

STRING calculates confidence scores by integrating 7 evidence channels:
1. Experiments (biochemical assays)
2. Databases (curated pathways)
3. Text-mining (literature co-occurrence)
4. Co-expression
5. Neighborhood
6. Gene Fusion
7. Co-occurrence

**Formula:**
$$S_{\text{combined}} = 1 - \prod_{i} (1 - S_i)$$
$$\text{Final Score} = S_{\text{combined}} \times 1000$$

* Highest Confidence: $\ge 900$ (filters down to ~150,000 top interactions)
* Medium Confidence: $\ge 400$
