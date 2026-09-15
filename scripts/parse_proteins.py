import pandas as pd

file_path = "data/10090.protein.info.v12.0.txt.gz"
print("Reading compressed file...")

# Read the first 10 rows
df = pd.read_csv(file_path, sep="\t", nrows=10)

# Save sample output
df.to_csv("results/protein_info_sample.csv", index=False)
print("Sample successfully saved to: results/protein_info_sample.csv")
