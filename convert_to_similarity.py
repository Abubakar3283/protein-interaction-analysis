import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 1. پرانی ڈسٹنس فائل کو پڑھنا
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

  # 2. ڈسٹنس کو سمیرٹی (Similarity) میں تبدیل کرنا
  # طریقہ: Similarity = Max_Distance - Distance (یا نارملائزیشن)
  # تاکہ کم فاصلہ زیادہ سمیرٹی بن جائے اور زیادہ فاصلہ کم سمیرٹی بن جائے۔
  max_val = dist_df.max().max()
  if max_val == 0:
    max_val = 1.0  # زیرو ڈویژن سے بچنے کے لیے

  # یہاں ہم فارمولا استعمال کر رہے ہیں: Similarity = 1 - (Distance / Max_Distance)
  # یا اس کو 0 سے 1 کے اسکیل پر لے آتے ہیں
  sim_df = 1.0 - (dist_df / max_val)

  # 3. نیا سمیرٹی ہیٹ میپ بنانا
  plt.figure(figsize=(12, 10))
  sns.heatmap(
      sim_df,
      cmap="YlGnBu",  # سمیرٹی کے لیے پیلا، ہلا اور نیلا رنگ (خوبصورت کمبینیشن)
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
