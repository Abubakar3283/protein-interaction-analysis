### Task 107 & 108: BLASTN Self-Alignment Analysis

* **Task Objective:** Run BLASTN (-outfmt 6) on cDNA.fa against itself to identify sequence similarities and gene duplications.
* **Database:** mouse_cdna_db (149,547 transcripts indexed)
* **Query File:** `data/cdna.fa`
* **Total Alignments Found:** 920,650 alignments
* **Execution Script:** `scripts/run_blastn_self.sh`
* **Output File Location:** `results/cdna_blastn_self_results.tsv`

#### Pipeline Details:
```bash
blastn -query data/cdna.fa -db data/mouse_cdna_db -out results/cdna_blastn_self_results.tsv -outfmt 6
```
