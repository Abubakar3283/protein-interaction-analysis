import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 1.
file_path = "results/distances.txt"

names = []
matrix_data = []

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
      name = parts[0]
      try:
        distances = [float(x) for x in parts[1:]]
        names.append(name)
        matrix_data.append(distances)
      except ValueError:
        continue

if matrix_data and names:
  min_len = min(len(row) for row in matrix_data)
  dist_df = pd.DataFrame(
      [row[:min_len] for row in matrix_data], index=names[: len(matrix_data)]
  )
  dist_df = dist_df.astype(float)

  # 2. (Similarity)
  #  Similarity = Max_Distance - Distance
  max_val = dist_df.max().max()
  if max_val == 0:
    max_val = 1.0

  Similarity = 1 - (Distance / Max_Distance)
  sim_df = 1.0 - (dist_df / max_val)

  #
  plt.figure(figsize=(12, 10))
  sns. heatmap(
      sim_df,
      cmap="YlGnBu",
      linewidths=0.5,
      cbar_kws={"label": "Sequence Similarity Score (0 to 1)"},
  )

  plt.title(
      "Transcript Similarity Matrix Heatmap", fontsize=14, fontweight="bold"
  )
  plt.xlabel("Transcripts", fontsize=12)
  plt.ylabel("Transcripts", fontsize=12)

  os.makedirs("results", exist_ok=True)
  plt.savefig("results/similarity_heatmap.png", dpi=300, bbox_inches="tight")
  print(
      "✅ Similarity Matrix Heatmap successfully generated and saved as"
      " 'results/similarity_heatmap.png'!"
  )
  plt.show()
else:
  print("❌ Error: Could not read distance matrix.")
