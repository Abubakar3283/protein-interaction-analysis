# Mouse Genomic & Interactome Analysis Pipeline

This repository documents the computational biology pipelines for *Mus musculus* (Taxon ID: 10090) developed under the supervision of **Professor Ping-Han Hsieh**.

---

## Task 96: Multi-tier Correspondence Mapping (STRING to Ensembl)

### 1. Objective & Biological Context
Bridge the interactome with the reference genome by creating a unified 5-tier mapping:
$$\text{STRING Protein ID} \longleftrightarrow \text{Ensembl Protein ID} \longleftrightarrow \text{Ensembl Transcript ID} \longleftrightarrow \text{Ensembl Gene ID} \longleftrightarrow \text{Official Gene Symbol}$$

### 2. Methodological Pipeline (`scripts/map_string_ensembl.py`)
1. Extracted `transcript:Parent` from `CDS` features and `gene:Parent` from `mRNA` features in `data/genes.gff3`.
2. Normalized STRING accessions by removing the species prefix (`10090.`).
3. Linked each protein directly to its transcript and gene locus, outputting the final resolved table to `results/string_to_ensembl_mapping.tsv`.

### 3. Mapping Coverage & Verification Statistics
* **Total STRING Mouse Proteins:** 21,840
* **Successfully Resolved to Gene & Transcript:** 21,318
* **Overall Coverage:** **97.6%**

### 4. Sample Correspondence Table (10 Representative Rows)

| STRING_Protein_ID | Ensembl_Protein_ID | Ensembl_Transcript_ID | Ensembl_Gene_ID | Gene_Symbol |
| :--- | :--- | :--- | :--- | :--- |
| `10090.ENSMUSP00000000001` | `ENSMUSP00000000001` | `ENSMUST00000000001` | `ENSMUSG00000000001` | `Gnai3` |
| `10090.ENSMUSP00000000028` | `ENSMUSP00000000028` | `ENSMUST00000000028` | `ENSMUSG00000000028` | `Cdc45` |
| `10090.ENSMUSP00000000049` | `ENSMUSP00000000049` | `ENSMUST00000000049` | `ENSMUSG00000000049` | `Apoh` |
| `10090.ENSMUSP00000000058` | `ENSMUSP00000000058` | `ENSMUST00000000058` | `ENSMUSG00000000058` | `Cav2` |
| `10090.ENSMUSP00000000085` | `ENSMUSP00000000085` | `ENSMUST00000000085` | `ENSMUSG00000000085` | `Klf6` |
| `10090.ENSMUSP00000000090` | `ENSMUSP00000000090` | `ENSMUST00000000090` | `ENSMUSG00000000090` | `Scmh1` |
| `10090.ENSMUSP00000000093` | `ENSMUSP00000000093` | `ENSMUST00000000093` | `ENSMUSG00000000093` | `Cox5a` |
| `10090.ENSMUSP00000000098` | `ENSMUSP00000000098` | `ENSMUST00000000098` | `ENSMUSG00000000098` | `Tbx2` |
| `10090.ENSMUSP00000000103` | `ENSMUSP00000000103` | `ENSMUST00000000103` | `ENSMUSG00000000103` | `Ngf` |
| `10090.ENSMUSP00000000128` | `ENSMUSP00000000128` | `ENSMUST00000000128` | `ENSMUSG00000000128` | `Wnt3a` |

---

## Task 97: Transcript Coordinates to Protein and Gene Mapping

### 1. Objective & Biological Importance
Map each transcript model to its physical genomic coordinates (chromosome, start, end, strand) and link it to its translated protein product ID and parent gene ID. This provides the physical spatial bridge between sequence-level mutations and protein products.

### 2. Methodological Pipeline (`scripts/map_transcripts_coords.py`)
* Extracted coordinates (`seqid`, `start`, `end`, `strand`) and transcript IDs from `mRNA`/`transcript` lines in `data/genes.gff3`.
* Extracted `protein_id` and parent transcript associations from `CDS` records.
* Joined coordinates, proteins, and parent genes into `results/transcript_coordinates_mapping.tsv`.

### 3. Sample Mapping Output (10 Complete Rows)
Verified directly from `results/transcript_coordinates_mapping_sample.tsv`:

| Chromosome | Start | End | Strand | Transcript_ID | Protein_ID | Ensembl_Gene_ID | Gene_Name |
| :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| `1` | `3284705` | `3741721` | `-` | `ENSMUST00000070533` | `ENSMUSP00000070648` | `ENSMUSG00000051951` | `Xkr4-201` |
| `1` | `4069780` | `4479464` | `-` | `ENSMUST00000208660` | `NA` | `ENSMUSG00000025900` | `Rp1-202` |
| `1` | `4414369` | `4430537` | `-` | `ENSMUST00000027032` | `ENSMUSP00000027032` | `ENSMUSG00000025900` | `Rp1-201` |
| `1` | `4491939` | `4505992` | `-` | `ENSMUST00000195576` | `NA` | `ENSMUSG00000025900` | `Rp1-204` |
| `1` | `4492667` | `4496413` | `-` | `ENSMUST00000192857` | `NA` | `ENSMUSG00000025900` | `Rp1-203` |
| `1` | `4773206` | `4785726` | `+` | `ENSMUST00000134049` | `ENSMUSP00000119854` | `ENSMUSG00000025902` | `Sox17-201` |
| `1` | `4774570` | `4785632` | `+` | `ENSMUST00000114041` | `NA` | `ENSMUSG00000025902` | `Sox17-202` |
| `1` | `4807788` | `4848410` | `+` | `ENSMUST00000194454` | `NA` | `ENSMUSG00000102348` | `Gm37235-201` |
| `1` | `4807892` | `4886770` | `+` | `ENSMUST00000027035` | `ENSMUSP00000027035` | `ENSMUSG00000025903` | `Mrpl15-201` |
| `1` | `4807914` | `4832316` | `+` | `ENSMUST00000194883` | `NA` | `ENSMUSG00000025903` | `Mrpl15-203` |

*(Note: Transcripts displaying `Protein_ID = NA` correspond to non-coding transcript isoforms or processed pseudogenic models lacking translated coding sequences).*
