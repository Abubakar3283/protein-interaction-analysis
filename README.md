# Comprehensive Mouse Genomic & Interactome Analysis Pipeline

This repository hosts computational genomics and network biology pipelines for *Mus musculus* (Taxon ID: `10090`) developed under the supervision of **Professor Ping-Han Hsieh**.

The project integrates reference genomic annotations from **Ensembl** (release GRCm39) with the interactome data from the **STRING Database** (v12.0) to construct verified multi-tier mapping tables and resolve physical genomic loci for downstream bioinformatics analysis.

---

## Project Task Dashboard

| Task ID | Deliverable Scope | Biological & Computational Objective | Status |
| :---: | :--- | :--- | :---: |
| **95** | GFF3 9-Column Specification | Verify and parse genomic annotation coordinates and hierarchical relationships | **Completed** |
| **96** | STRING to Ensembl Correspondence | Build a 5-tier mapping: STRING ID $\leftrightarrow$ Protein $\leftrightarrow$ Transcript $\leftrightarrow$ Gene $\leftrightarrow$ Symbol | **Completed** |
| **97** | Genomic Coordinates Mapping | Map transcript coordinates (`chr`, `start`, `end`, `strand`) to proteins and genes | **Completed** |
| **98** | Data Schema Summary | Formal documentation of file formats, column types, and attribute layouts | **Completed** |
| **99** | STRING Confidence Scoring | Mathematical and biological breakdown of the 7-channel probabilistic scoring | **Completed** |
| **100** | Molecular Type Census | Quantitative distribution of GFF3 Sequence Ontology types (exons, CDS, mRNAs, etc.) | *Pending Documentation* |
| **101** | Chromosomal & Scaffold Diversity | Unique counts and classification of canonical chromosomes vs. unplaced contigs | *Pending Documentation* |

---

## Task 95: Understanding the GFF3 9-Column Format

### 1. Concept & Biological Role
The Generic Feature Format version 3 (GFF3) serves as the spatial index for the *Mus musculus* genome assembly. It defines coordinates, feature types, and parent-child parentage for every annotated segment on the reference chromosomes.

### 2. Specification Table (The 9 Columns)

| Column | Name | Description | Example Record |
| :---: | :--- | :--- | :--- |
| **1** | **Seqid** | Chromosome or unlocalized scaffold identifier | `1`, `X`, `GL456210.1` |
| **2** | **Source** | Annotation pipeline or curated database authority | `ensembl_havana`, `havana` |
| **3** | **Type** | Sequence Ontology molecular feature type | `gene`, `mRNA`, `CDS`, `exon` |
| **4** | **Start** | 1-based start genomic coordinate (base pair) | `3284705` |
| **5** | **End** | Inclusive end genomic coordinate (base pair) | `3741721` |
| **6** | **Score** | Annotation confidence or alignment score (`.` if empty) | `.` |
| **7** | **Strand** | Direction of transcription (`+` forward, `-` reverse) | `-` |
| **8** | **Phase** | Reading frame offset for CDS features (`0`, `1`, `2`) | `.` or `0` |
| **9** | **Attributes** | Semicolon-delimited key-value pairs defining metadata and ancestry | `ID=transcript:ENSMUST...;Parent=gene:...` |

### 3. Biological Ancestry Hierarchy (The Central Dogma in GFF3)
* **Gene (`gene`):** Top-level locus identifier (`ID=gene:ENSMUSG...`).
* **Transcript (`mRNA`):** Spliced intermediate pointing to its parent gene (`ID=transcript:ENSMUST...; Parent=gene:ENSMUSG...`).
* **Coding Sequence (`CDS`):** Polypeptide coding region pointing to its parent transcript (`protein_id=ENSMUSP...; Parent=transcript:ENSMUST...`).

---

## Task 96: Multi-tier Correspondence Mapping (STRING to Ensembl)

### 1. Objective & Methodological Pipeline
Biological databases identify entities through distinct identifiers. This task bridges the STRING interactome with the Ensembl genomic assembly through the script `scripts/map_string_ensembl.py`:
$$\text{STRING Protein ID} \longleftrightarrow \text{Ensembl Protein ID} \longleftrightarrow \text{Ensembl Transcript ID} \longleftrightarrow \text{Ensembl Gene ID} \longleftrightarrow \text{Official Gene Symbol}$$

1. Extracted `transcript:Parent` from each `CDS` record and `gene:Parent` from each `mRNA` record in `data/genes.gff3`.
2. Stripped the species prefix (`10090.`) from the STRING identifiers.
3. Linked every protein to its corresponding transcript, gene, and gene symbol, saving the full result to `results/string_to_ensembl_mapping.tsv`.

### 2. Mapping Statistics
* **Total Mouse Proteins in STRING:** 21,840
* **Successfully Resolved:** 21,318
* **Overall Mapping Coverage:** **97.6%**

### 3. Sample Output Table (10 Representative Rows)
Verified from `results/string_to_ensembl_mapping_sample.tsv`:

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

### 1. Objective & Biological Rationale
Experimental sequence variations (mutations, SNPs) are discovered at specific genomic coordinates. This workflow bridges genomic coordinates (`chr`, `start`, `end`, `strand`) directly with transcript isoforms and protein products via `scripts/map_transcripts_coords.py`.

### 2. Methodological Pipeline
* Extracted genomic boundaries and orientations (`seqid`, `start`, `end`, `strand`) for all transcripts in `data/genes.gff3`.
* Integrated translated polypeptide accessions (`protein_id`) from corresponding `CDS` features.
* Constructed a full lookup table stored in `results/transcript_coordinates_mapping.tsv`.

### 3. Sample Mapping Output (10 Representative Rows)
Verified from `results/transcript_coordinates_mapping_sample.tsv`:

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

*(Note: Transcripts with `Protein_ID = NA` represent non-coding or non-translated isoforms).*

---

## Task 98: Data Schema Summary

### 1. Overview & Data Architecture
A data schema formalizes the technical specification of the datasets used across our analytical pipelines. Defining data types, formats, constraints, and biological descriptions prevents programmatic errors and ensures cross-pipeline interoperability.

### 2. Schema Specification: Ensembl GFF3 (`data/genes.gff3`)
* **Format:** Tab-separated values (TSV), 9 fixed columns, 1-based coordinate indexing.

| Column Index | Field Name | Data Type | Nullable | Biological & Functional Role |
| :---: | :--- | :---: | :---: | :--- |
| **Col 1** | `seqid` | String | No | Chromosomal identifier (e.g., `1`, `X`) or unplaced scaffold accession (`GL...`, `JH...`). |
| **Col 2** | `source` | String | No | Annotation database or pipeline program (e.g., `ensembl_havana`). |
| **Col 3** | `type` | String | No | Sequence Ontology feature classification (e.g., `gene`, `mRNA`, `CDS`, `exon`). |
| **Col 4** | `start` | Integer | No | 1-based start coordinate of the biological feature on the forward strand. |
| **Col 5** | `end` | Integer | No | 1-based inclusive end coordinate of the feature. |
| **Col 6** | `score` | Float | Yes (`.`) | Sequence alignment or annotation confidence metric. |
| **Col 7** | `strand` | Character | No | Orientation of transcription (`+` forward, `-` reverse, `.` unstranded). |
| **Col 8** | `phase` | Integer | Yes (`.`) | Reading frame codon offset for CDS features (`0`, `1`, `2`). |
| **Col 9** | `attributes` | Key-Value List | No | Semicolon-delimited metadata tags establishing feature ID and hierarchical ancestry (`ID=...;Parent=...`). |

### 3. Schema Specification: STRING Physical Links (`data/10090.protein.physical.links...`)
* **Format:** Space/Tab-delimited text, gzipped, 3 fixed columns.

| Column Index | Field Name | Data Type | Value Range | Biological & Functional Role |
| :---: | :--- | :---: | :---: | :--- |
| **Col 1** | `protein1` | String | Taxonomy-prefixed | STRING identifier of the first interacting protein (e.g., `10090.ENSMUSP00000000001`). |
| **Col 2** | `protein2` | String | Taxonomy-prefixed | STRING identifier of the second interacting protein partner. |
| **Col 3** | `combined_score`| Integer | $150 \dots 1000$ | Integrated confidence metric derived probabilistically from multiple biological evidence channels. |

---

## Task 99: STRING Confidence Scoring Methodology

### 1. Conceptual Framework
STRING functional association scores represent an estimate of probability that at least one biological interaction exists between two proteins. These scores range from $0$ to $1000$ (representing probabilities scaled by $1000$).

### 2. The 7 Biological Evidence Channels
STRING derives functional scores by querying 7 independent biological channels:
1. **Experiments:** Direct biochemical evidence (e.g., Co-IP, Yeast Two-Hybrid, tandem affinity purification).
2. **Databases:** Manually curated pathway knowledge from established repositories (KEGG, Reactome, BioCyc).
3. **Text-mining:** Natural language processing of scientific abstracts (PubMed) quantifying joint co-mentions.
4. **Co-expression:** Correlated gene expression across varied microarray and RNA-seq experimental conditions.
5. **Neighborhood:** Genomic proximity of gene pairs across multiple bacterial and eukaryotic genomes.
6. **Gene Fusion:** Orthologous gene pairs fused into a single polypeptide chain in other evolutionary lineages.
7. **Co-occurrence:** Phylogenetic profiling tracking simultaneous presence or absence across taxonomic clades.

### 3. Mathematical Integration Model
Each channel calculates an individual confidence score $S_i \in [0, 1]$ corrected against random background expectations. Assuming the evidence sources provide independent observations, individual error probabilities $(1 - S_i)$ are combined:

$$S_{\text{combined}} = 1 - \prod_{i=1}^{7} (1 - S_i)$$

The integrated score is then scaled to an integer range:
$$\text{Score}_{\text{final}} = \text{round}(S_{\text{combined}} \times 1000)$$

### 4. Standard Operational Thresholds
* **Highest Confidence ($\ge 900$):** Used for strict interactome topological analyses to eliminate false-positive edges.
* **High Confidence ($\ge 700$):** High-reliability interactions.
* **Medium Confidence ($\ge 400$):** Default STRING threshold balancing sensitivity and specificity.
* **Low Confidence ($\ge 150$):** Broad exploratory discovery.
