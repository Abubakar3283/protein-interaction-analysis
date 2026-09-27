# Mouse Proteome Correspondence & Annotation Analysis

**Organism:** *Mus musculus* (House mouse, NCBI Taxonomy ID: 10090)  
**Data Sources:** Ensembl Genome Browser (genes.gff3.gz) & STRING Database v12.0 (10090.protein.info.v12.0.txt.gz)  
**Environment:** Python 3.12 (bio_project)

---

## 1. Project Objective

The primary objective of this project is to construct a verified Correspondence Table linking STRING protein entities to Ensembl genomic coordinates and official gene nomenclature:

STRING Protein ID <-> Ensembl Protein ID <-> Ensembl Gene ID <-> Gene Symbol

---

## 2. Biological Foundations & Identifier Definitions

### 2.1 Taxon ID.Ensembl Protein ID
* **Definition:** STRING's standard multi-species protein identifier.
* **Format:** It prefixes the Ensembl Protein accession with the NCBI Taxonomy ID followed by a dot:
  10090.ENSMUSP00000000001
  * 10090: NCBI Taxonomy ID for Mus musculus.
  * ENSMUSP00000000001: Ensembl Protein identifier.

### 2.2 HGNC / MGI Gene Symbol
* Standardized, human-readable gene nomenclature approved by official nomenclature authorities (HGNC for human, MGI for mouse).
* Examples: Gnai3, Tp53, Fau, Rps11.

### 2.3 Gene vs. Transcript vs. Protein Hierarchy
Biological information flows sequentially according to the Central Dogma:
Gene (DNA, ENSMUSG) -> Transcript (mRNA, ENSMUST) -> Protein (CDS, ENSMUSP)

* **Gene (DNA / ENSMUSG):** The chromosomal locus encoding instructions.
* **Transcript (mRNA / ENSMUST):** The single-stranded RNA copy. Through alternative splicing, one gene can produce multiple transcript isoforms.
* **Protein (Polypeptide / ENSMUSP):** The functional amino acid machine translated by the ribosome from the coding sequence (CDS).

---

## 3. Correspondence Table (STRING to Ensembl)

### 3.1 Mapping Methodology
Ensembl's genes.gff3.gz encodes features in a parent-child hierarchy:
CDS (Protein ID) -> Transcript -> Gene

The script scripts/map_string_ensembl.py executes a two-step lookup:
1. Resolves CDS entries to parent transcripts (ENSMUST...).
2. Links transcripts to parent genomic genes (ENSMUSG...).
3. Strips the 10090. taxon prefix from STRING entries and performs an exact inner join.

### 3.2 Mapping Statistics
* **STRING Mouse Proteins Parsed:** 21,840
* **Successfully Mapped to Ensembl Gene:** 21,318 (97.6% coverage)
* **Unmapped / Pseudogenes / Non-coding:** 522 (2.4%)

### 3.3 Sample Output (results/string_to_ensembl_mapping_sample.tsv)

| STRING Protein ID | Ensembl Protein ID | Ensembl Gene ID | Gene Symbol |
| :--- | :--- | :--- | :--- |
| 10090.ENSMUSP00000000001 | ENSMUSP00000000001 | ENSMUSG00000000001 | Gnai3 |
| 10090.ENSMUSP00000000003 | ENSMUSP00000000003 | ENSMUSG00000000003 | Pbsn |
| 10090.ENSMUSP00000000010 | ENSMUSP00000000010 | ENSMUSG00000020875 | Hoxb9 |
| 10090.ENSMUSP00000000028 | ENSMUSP00000000028 | ENSMUSG00000000028 | Cdc45 |
| 10090.ENSMUSP00000000049 | ENSMUSP00000000049 | ENSMUSG00000000049 | Apoh |
| 10090.ENSMUSP00000000058 | ENSMUSP00000000058 | ENSMUSG00000000058 | Cav2 |
| 10090.ENSMUSP00000000080 | ENSMUSP00000000080 | ENSMUSG00000000078 | Klf6 |
| 10090.ENSMUSP00000000090 | ENSMUSP00000000090 | ENSMUSG00000000088 | Cox5a |
| 10090.ENSMUSP00000000095 | ENSMUSP00000000095 | ENSMUSG00000000093 | Tbx2 |
| 10090.ENSMUSP00000000122 | ENSMUSP00000000122 | ENSMUSG00000000120 | Ngfr |

Full mapping is saved in results/string_to_ensembl_mapping.tsv.

## 3. Correspondence Table (STRING to Ensembl)

### 3.1 Pipeline Architecture (How We Did It)

The parsing logic in `scripts/map_string_ensembl.py` connects the genomic coordinate layer to the protein interaction space via a two-step hierarchical resolution:

```text
[ genes.gff3.gz ]                                [ 10090.protein.info.v12.0.txt.gz ]
       │                                                          │
       ▼                                                          ▼
1. CDS points to Parent Transcript               1. Strip "10090." Taxon prefix
   (ENSMUSP... -> ENSMUST...)                       (10090.ENSMUSP... -> ENSMUSP...)
       │                                                          │
       ▼                                                          │
2. Transcript points to Parent Gene                               │
   (ENSMUST... -> ENSMUSG...)                                     │
       │                                                          │
       ▼                                                          ▼
  [ CDS -> Gene Dictionary ] ──────── Inner Join ──────── [ Ensembl Protein ID Key ]
                                       │
                                       ▼
                       [ Final Correspondence Table ]
                     (21,318 matched proteins: 97.6%)
---

## 4. Reproducibility Instructions

To reproduce the correspondence table:
conda activate bio_project
python scripts/map_string_ensembl.py
