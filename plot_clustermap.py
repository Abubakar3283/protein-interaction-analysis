import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform
import seaborn as sns

# 1. distmat فائل کو پڑھنے کا انتہائی محفوظ طریقہ
file_path = "results/distances.txt"

names = []
rows = []

with open(file_path, "r") as f:
  for line in f:
    line_stripped = line.strip()
    # خالی لائنیں یا وہ لائنیں جو # سے شروع ہوں انہیں چھوڑ دیں
    if not line_stripped or line_stripped.startswith("#"):
      continue

    parts = line_stripped.split()

    # اگر لائن میں صرف ایک عنصر ہو (جیسے کل تعداد '203') تو اسے بھی چھوڑ دیں
    if len(parts) == 1:
      continue

    # پہلا حصہ ٹرانسکرپٹ کا نام ہے
    name = parts[0]

    # باقی حصے فاصلے (distances) ہیں
    vals = []
    for x in parts[1:]:
      try:
        vals.append(float(x))
      except ValueError:
        pass

    if vals:
      names.append(name)
      rows.append(vals)

n_total = len(names)
print(f"📌 Total valid transcripts loaded: {n_total}")

if n_total < 2:
  print("❌ Error: Not enough transcripts found. Please check distances.txt")
  exit()

# لوئر ٹرائینگل سے مکمل اسکوائر میٹرکس (Square Matrix) بنانا
mat = np.zeros((n_total, n_total))
for idx, row_vals in enumerate(rows):
  for j, val in enumerate(row_vals):
    if idx < n_total and j < n_total:
      mat[idx, j] = val
      mat[j, idx] = val

mat = np.nan_to_num(mat, nan=0.0, posinf=0.0, neginf=0.0)

# گراف کو بالکل صاف ستھرا بنانے کے لیے ٹاپ 25 ٹرانسکرپٹس کا انتخاب
subset_size = min(25, n_total)
sub_names = names[:subset_size]
sub_mat = mat[:subset_size, :subset_size]

dist_df = pd.DataFrame(sub_mat, index=sub_names, columns=sub_names)
np.fill_diagonal(dist_df.values, 0)

# ڈسٹنس کو سمیرٹی (Similarity Matrix) میں تبدیل کرنا
min_d = dist_df.min().min()
max_d = dist_df.max().max()
if max_d == min_d:
  sim_df = pd.DataFrame(1.0, index=sub_names, columns=sub_names)
else:
  sim_df = 1.0 - ((dist_df - min_d) / (max_d - min_d))

sim_df = sim_df.fillna(1.0)
sim_df = np.clip(sim_df, 0, 1)
np.fill_diagonal(sim_df.values, 1.0)

# لنکیج میٹرکس بنانا
clean_dist = dist_df.values
np.fill_diagonal(clean_dist, 0)
condensed_dist = squareform(clean_dist, checks=False)
condensed_dist = np.nan_to_num(
    condensed_dist, nan=0.0, posinf=0.0, neginf=0.0
)

linkage_matrix = sch.linkage(condensed_dist, method="average")

print(
    f"🔄 Generating professional Clustermap for top {subset_size} transcripts..."
)

# 2. سیبورن کلسٹر میپ بنانا (اصل ناموں اور بہترین رنگوں کے ساتھ)
g = sns.clustermap(
    sim_df,
    cmap="YlGnBu",
    linewidths=0.6,
    figsize=(12, 12),
    row_linkage=linkage_matrix,
    col_linkage=linkage_matrix,
    xticklabels=True,
    yticklabels=True,
    cbar_kws={"label": "Normalized Similarity Score"},
)

# ناموں کو بالکل واضح اور ترچھا کرنا
plt.setp(
    g.ax_heatmap.get_xticklabels(), rotation=90, fontsize=8, fontweight="bold"
)
plt.setp(
    g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=8, fontweight="bold"
)

g.fig.suptitle(
    f"Transcript Hierarchical Clustering & Similarity Heatmap (Top"
    f" {subset_size})",
    fontsize=14,
    fontweight="bold",
    y=1.03,
)

os.makedirs("results", exist_ok=True)
plt.savefig(
    "results/clustered_similarity_heatmap.png", dpi=300, bbox_inches="tight"
)
print("✅ Perfect Clustered Heatmap successfully generated and saved!")
