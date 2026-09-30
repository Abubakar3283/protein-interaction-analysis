import os
import pandas as pd

# File paths (using the uncompressed genes.gff3)
GFF3_FILE = "data/genes.gff3"
OUTPUT_FILE = "results/transcript_coordinates_mapping.tsv"
SAMPLE_FILE = "results/transcript_coordinates_mapping_sample.tsv"

os.makedirs("results", exist_ok=True)

print("Parsing GFF3 for transcript coordinates and protein IDs...")

# Dictionaries to store relationships
# transcript_id -> protein_id
transcript_to_protein = {}
# list of transcript records
transcript_records = []

with open(GFF3_FILE, "r") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.strip().split("\t")
        if len(parts) < 9:
            continue

        seqid = parts[0]
        feature_type = parts[2]
        start = parts[3]
        end = parts[4]
        strand = parts[6]
        attributes = parts[8]

        # Parse key=value attributes
        attr_dict = {}
        for item in attributes.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                attr_dict[k] = v

        # 1. Map CDS -> Transcript (to find protein_id for each transcript)
        if feature_type == "CDS":
            protein_id = attr_dict.get("protein_id")
            parent_transcript = attr_dict.get("Parent", "").replace("transcript:", "")
            if protein_id and parent_transcript:
                transcript_to_protein[parent_transcript] = protein_id

        # 2. Extract Transcript coordinates & parent gene
        elif feature_type in ["mRNA", "transcript"]:
            transcript_id = attr_dict.get("ID", "").replace("transcript:", "")
            parent_gene = attr_dict.get("Parent", "").replace("gene:", "")
            gene_name = attr_dict.get("Name", "")

            if transcript_id:
                transcript_records.append({
                    "Chromosome": seqid,
                    "Start": int(start),
                    "End": int(end),
                    "Strand": strand,
                    "Transcript_ID": transcript_id,
                    "Ensembl_Gene_ID": parent_gene,
                    "Gene_Name": gene_name
                })

# Convert to DataFrame
df = pd.DataFrame(transcript_records)

# Map Protein ID using the transcript_to_protein dictionary
df["Protein_ID"] = df["Transcript_ID"].map(transcript_to_protein).fillna("NA")

# Select and order final columns
columns_order = [
    "Chromosome",
    "Start",
    "End",
    "Strand",
    "Transcript_ID",
    "Protein_ID",
    "Ensembl_Gene_ID",
    "Gene_Name"
]
df_final = df[columns_order]

# Save outputs
df_final.to_csv(OUTPUT_FILE, sep="\t", index=False)
df_final.head(10).to_csv(SAMPLE_FILE, sep="\t", index=False)

# Statistics
total_transcripts = len(df_final)
coding_transcripts = (df_final["Protein_ID"] != "NA").sum()

print(f"Done! Results written to {OUTPUT_FILE}")
print(f"Total transcripts parsed: {total_transcripts:,}")
print(f"Transcripts mapped to a protein (CDS): {coding_transcripts:,}")
