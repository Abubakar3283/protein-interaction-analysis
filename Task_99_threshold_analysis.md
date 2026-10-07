### Task 99 Follow-up: Physical Links Threshold Filtering (400 - 950)

* **Objective:** Filter mouse physical protein interactome to the confidence band 400 <= combined_score <= 950.
* **Total Interactions in Dataset:** 707,162
* **Interactions in 400-950 Range:** 275,962 (39.02%)
* **Input File:** `data/10090.protein.physical.links.v12.0.txt.gz`
* **Output File:** `data/10090.protein.physical.links.400_950.txt.gz`
* **Filter Pipeline:**
```bash
zcat data/10090.protein.physical.links.v12.0.txt.gz | awk 'NR==1 || ($3 >= 400 && $3 <= 950)' | gzip > data/10090.protein.physical.links.400_950.txt.gz
```
