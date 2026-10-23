import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr

blastn_file = "results/protein_blastn_translated.tsv"
blastp_file = "results/protein_blastp_self_results.tsv"
output_plot = "results/blastn_vs_blastp_scatterplot.png"
output_merged_tsv = "results/blastn_vs_blastp_merged.tsv"

print("1. Loading BLASTN translated data...")
# protein_blastn_translated.tsv has header: q_prot, s_prot, q_trans, s_trans, pident, ...
# So we read by column names: q_prot, s_prot, pident
df_blastn = pd.read_csv(blastn_file, sep="\t", usecols=["q_prot", "s_prot", "pident"])
df_blastn.rename(columns={"q_prot": "qseqid", "s_prot": "sseqid", "pident": "pident_blastn"}, inplace=True)

df_blastn['pident_blastn'] = pd.to_numeric(df_blastn['pident_blastn'], errors='coerce')
df_blastn = df_blastn.dropna(subset=['pident_blastn'])

# Remove version suffix if exists
df_blastn['qseqid'] = df_blastn['qseqid'].astype(str).str.split('.').str[0]
df_blastn['sseqid'] = df_blastn['sseqid'].astype(str).str.split('.').str[0]

# Maximum identity per protein pair
df_blastn = df_blastn.groupby(["qseqid", "sseqid"], as_index=False)["pident_blastn"].max()
print(f"   BLASTN unique pairs: {len(df_blastn):,}")

print("2. Loading BLASTP data...")
# protein_blastp_self_results.tsv has NO header, columns are 0: qseqid, 1: sseqid, 2: pident
df_blastp = pd.read_csv(blastp_file, sep="\t", header=None, usecols=[0, 1, 2])
df_blastp.columns = ["qseqid", "sseqid", "pident_blastp"]

df_blastp['pident_blastp'] = pd.to_numeric(df_blastp['pident_blastp'], errors='coerce')
df_blastp = df_blastp.dropna(subset=['pident_blastp'])

df_blastp['qseqid'] = df_blastp['qseqid'].astype(str).str.split('.').str[0]
df_blastp['sseqid'] = df_blastp['sseqid'].astype(str).str.split('.').str[0]

df_blastp = df_blastp.groupby(["qseqid", "sseqid"], as_index=False)["pident_blastp"].max()
print(f"   BLASTP unique pairs: {len(df_blastp):,}")

print("3. Merging both datasets on common protein pairs...")
df_merged = pd.merge(df_blastn, df_blastp, on=["qseqid", "sseqid"], how="inner")
print(f"   Common pairs found: {len(df_merged):,}")

df_merged.to_csv(output_merged_tsv, sep="\t", index=False)
print(f"   Merged table saved to: {output_merged_tsv}")

df_merged["pident_blastn"] = df_merged["pident_blastn"].astype(float)
df_merged["pident_blastp"] = df_merged["pident_blastp"].astype(float)

r_pearson, _ = pearsonr(df_merged["pident_blastn"], df_merged["pident_blastp"])
r_spearman, _ = spearmanr(df_merged["pident_blastn"], df_merged["pident_blastp"])
print(f"   Pearson correlation (r): {r_pearson:.4f}")
print(f"   Spearman correlation (rho): {r_spearman:.4f}")

print("4. Creating Scatterplot...")
plt.figure(figsize=(9, 7), dpi=300)
sns.set_theme(style="whitegrid")

# Scatterplot
plt.scatter(
    df_merged["pident_blastn"], 
    df_merged["pident_blastp"], 
    alpha=0.2, 
    color="#1f77b4", 
    s=12, 
    edgecolors="none"
)

# Reference identity line (y = x)
plt.plot([0, 100], [0, 100], color="red", linestyle="--", linewidth=1.5, label="Identity line (y = x)")

plt.title("Sequence Identity Comparison: BLASTN vs BLASTP\n(Mus musculus Protein Pairs)", fontsize=13, weight="bold")
plt.xlabel("BLASTN Nucleotide Identity (%) [Translated to Protein]", fontsize=11)
plt.ylabel("BLASTP Amino Acid Identity (%)", fontsize=11)
plt.xlim(0, 102)
plt.ylim(0, 102)

textstr = f"Common Pairs: {len(df_merged):,}\nPearson r: {r_pearson:.3f}\nSpearman rho: {r_spearman:.3f}"
props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='gray')
plt.gca().text(0.05, 0.92, textstr, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top', bbox=props)

plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(output_plot)
plt.close()

print(f"5. Done! Scatterplot successfully saved as: {output_plot}")
