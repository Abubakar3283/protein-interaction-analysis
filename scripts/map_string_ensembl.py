import gzip
import os
import pandas as pd

# File paths
GFF3_FILE = "data/genes.gff3"
STRING_INFO_FILE = "data/10090.protein.info.v12.0.txt.gz"
OUTPUT_FILE = "results/string_to_ensembl_mapping.tsv"
SAMPLE_FILE = "results/string_to_ensembl_mapping_sample.tsv"

os.makedirs("results", exist_ok=True)

print("Parsing GFF3 annotation file for Protein -> Transcript -> Gene mapping...")

protein_to_transcript = {}
transcript_to_gene = {}

with open(GFF3_FILE, "r") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.strip().split("\t")
        if len(parts) < 9:
            continue

        feature_type = parts[2]
        attributes = parts[8]

        # Parse key=value attributes
        attr_dict = {}
        for item in attributes.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                attr_dict[k] = v

        # 1. Map Transcript -> Gene
        if feature_type in ["mRNA", "transcript"]:
            transcript_id = attr_dict.get("ID", "").replace("transcript:", "")
            parent_gene = attr_dict.get("Parent", "").replace("gene:", "")
            if transcript_id and parent_gene:
                transcript_to_gene[transcript_id] = parent_gene

        # 2. Map CDS (Protein) -> Transcript
        elif feature_type == "CDS":
            protein_id = attr_dict.get("protein_id")
            parent_transcript = attr_dict.get("Parent", "").replace("transcript:", "")
            if protein_id and parent_transcript:
                protein_to_transcript[protein_id] = parent_transcript

print(f"Total CDS-to-Transcript pairs resolved: {len(protein_to_transcript):,}")
print(f"Total Transcript-to-Gene pairs resolved: {len(transcript_to_gene):,}")

# Parse STRING protein info file
print("Parsing STRING protein info file...")
string_data = []
with gzip.open(STRING_INFO_FILE, "rt") as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            string_id = parts[0]
            gene_symbol = parts[1]
            ensembl_protein_id = string_id.replace("10090.", "")
            string_data.append((string_id, ensembl_protein_id, gene_symbol))

df_string = pd.DataFrame(string_data, columns=["STRING_Protein_ID", "Ensembl_Protein_ID", "Gene_Symbol"])

# Map Transcript ID and Gene ID
df_string["Ensembl_Transcript_ID"] = df_string["Ensembl_Protein_ID"].map(protein_to_transcript)
df_string["Ensembl_Gene_ID"] = df_string["Ensembl_Transcript_ID"].map(transcript_to_gene)

# Fill unmapped entries with NA
df_string["Ensembl_Transcript_ID"] = df_string["Ensembl_Transcript_ID"].fillna("NA")
df_string["Ensembl_Gene_ID"] = df_string["Ensembl_Gene_ID"].fillna("NA")

# Order the 5 columns cleanly
final_columns = [
    "STRING_Protein_ID",
    "Ensembl_Protein_ID",
    "Ensembl_Transcript_ID",
    "Ensembl_Gene_ID",
    "Gene_Symbol"
]
df_final = df_string[final_columns]

# Save outputs
df_final.to_csv(OUTPUT_FILE, sep="\t", index=False)
df_final.head(10).to_csv(SAMPLE_FILE, sep="\t", index=False)

total = len(df_final)
mapped = (df_final["Ensembl_Gene_ID"] != "NA").sum()
coverage = (mapped / total) * 100

print(f"Success! Updated mapping saved to {OUTPUT_FILE}")
print(f"Summary: {mapped:,} / {total:,} proteins fully mapped ({coverage:.1f}% coverage)")
