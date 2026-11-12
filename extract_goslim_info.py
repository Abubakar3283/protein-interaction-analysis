import os
import re

# Define file paths
input_fasta = "data/transcripts_200.fa"
output_summary = "results/goslim_summary.tsv"

print("Extracting transcript and gene information for GO Slim analysis...")

transcripts_data = []

# Read FASTA file and parse headers
with open(input_fasta, "r") as f:
    for line in f:
        if line.startswith(">"):
            header = line.strip()
            
            # Extract Transcript ID
            transcript_id_match = re.search(r">(\S+)", header)
            transcript_id = transcript_id_match.group(1) if transcript_id_match else "N/A"
            
            # Extract Gene ID
            gene_match = re.search(r"gene:(\S+)", header)
            gene_id = gene_match.group(1) if gene_match else "N/A"
            
            # Extract Gene Symbol
            symbol_match = re.search(r"gene_symbol:(\S+)", header)
            gene_symbol = symbol_match.group(1) if symbol_match else "N/A"
            
            # Extract Description
            desc_match = re.search(r'description:"([^"]+)"', header)
            description = desc_match.group(1) if desc_match else "N/A"
            
            transcripts_data.append({
                "Transcript_ID": transcript_id,
                "Gene_ID": gene_id,
                "Gene_Symbol": gene_symbol,
                "Description": description
            })

# Ensure results directory exists and save summary as TSV
os.makedirs("results", exist_ok=True)
with open(output_summary, "w") as out:
    out.write("Transcript_ID\tGene_ID\tGene_Symbol\tDescription\n")
    for item in transcripts_data:
        out.write(f"{item['Transcript_ID']}\t{item['Gene_ID']}\t{item['Gene_Symbol']}\t{item['Description']}\n")

print(f"Successfully extracted {len(transcripts_data)} transcripts summary into: {output_summary}")
