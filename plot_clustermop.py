import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 1. distmat فائل کو پڑھنا اور مثلثی ڈیٹا کو مکمل اسکوائر میٹرکس بنانا
file_path = "results/distances.txt"

names = []
rows = []

with open(file_path, "r") as f:
  for line in f:
    line_stripped = line.strip()
    if not line_stripped:
      continue
    parts = line_stripped.split()
    if (
        "Matrix" in line
        or "distmat" in line
        or line.startswith("#")
        or len(parts) == 1
    ):
      continue
    if len(parts) > 1:
      try:
        float(parts[1])
        name = parts[0]
        distances = [float(x) for x in parts[1:]]
        names.append(name)
        rows.append(distances)
      except ValueError:
        continue

# اسکوائر میٹرکس (Square Matrix) بنانا
n = len(names)
mat = np.zeros((n, n))

for i, row in enumerate(rows):
  for j, val in enumerate(row):
    if j < len(names):
      mat[i, j] = val
      mat[j, i] = val  # ارتقائی فاصلہ دونوں طرف برابر ہوتا ہے (Symmetric)

dist_df = pd.DataFrame(mat, index=names, columns=names)

# 2. ڈسٹنس کو سمیرٹی (Similarity Matrix) میں تبدیل کرنا
max_val = dist_df.max().max()
if max_val == 0:
  max_val = 1.0
sim_df = 1.0 - (dist_df / max_val)
sim_df = sim_df.fillna(1.0)

print(
    "🔄 Generating Clustermap with Hierarchical Clustering for 200"
    " transcripts..."
)

# 3. سیبورن کلسٹر میپ (Clustermap) بنانا
g = sns.clustermap(
    sim_df,
    cmap="YlGnBu",
    linewidths=0,
    figsize=(12, 12),
    col_cluster=True,
    row_cluster=True,
    cbar_kws={"label": "Similarity Score"},
)

g.fig.suptitle(
    "Transcript Hierarchical Clustering & Similarity Heatmap",
    fontsize=16,
    fontweight="bold",
    y=1.02,
)

os.makedirs("results", exist_ok=True)
plt.savefig("results/clustered_similarity_heatmap.png", dpi=300, bbox_inches="tight")
print(
    "✅ Clustered Heatmap successfully generated and saved as"
    " 'results/clustered_similarity_heatmap.png'!"
)
