import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

file_path = "results/distances.txt"

names = []
matrix_data = []
reading_matrix = False

with open(file_path, "r") as f:
  for line in f:
    line_stripped = line.strip()
    if not line_stripped:
      continue

    # EMBOSS distmat میں اصل ڈیٹا عام طور پر سیکوئنس کے نام سے شروع ہوتا ہے
    # ہم لائن کو ٹکڑوں میں تقسیم کرتے ہیں
    parts = line_stripped.split()

    # اگر پہلی لائن میں ٹوٹل نمبر یا ہیڈر ہو تو اسے چھوڑ دیں
    if (
        "Matrix" in line
        or "distmat" in line
        or line.startswith("#")
        or len(parts) == 1
    ):
      continue

    # اگر لائن میں نام اور نمبرز ہوں
    if len(parts) > 1:
      name = parts[0]
      try:
        # چیک کریں کہ آیا باقی حصے فلوٹ (نمبرز) ہیں یا نہیں
        distances = [float(x) for x in parts[1:]]
        names.append(name)
        matrix_data.append(distances)
      except ValueError:
        # اگر کوئی ہیڈر لائن یا ناموں کی قطار آ جائے تو اسے چھوڑ دیں
        continue

# اگر ڈیٹا مل گیا ہو تو میٹرکس بنائیں
if matrix_data and names:
  # چونکہ distmat بعض اوقات مثلثی (triangular) میٹرکس دیتا ہے، اسے مکمل کرنے کے لیے:
  min_len = min(len(row) for row in matrix_data)
  # حفاظتی تدبیر کے طور پر ڈیٹا کو برابر کرنا
  df = pd.DataFrame([row[:min_len] for row in matrix_data], index=names[: len(matrix_data)])

  # ہیٹ میپ بنانا
  plt.figure(figsize=(12, 10))
  sns.heatmap(
      df.astype(float),
      cmap="coolwarm",
      linewidths=0.5,
      cbar_kws={"label": "Evolutionary Distance"},
  )

  plt.title(
      "Transcript Distance Matrix Heatmap", fontsize=14, fontweight="bold"
  )
  plt.xlabel("Transcripts", fontsize=12)
  plt.ylabel("Transcripts", fontsize=12)

  os.makedirs("results", exist_ok=True)
  plt.savefig("results/distance_heatmap.png", dpi=300, bbox_inches="tight")
  print(
      "✅ Heatmap successfully generated and saved as"
      " 'results/distance_heatmap.png'!"
  )
else:
  print(
      "❌ Error: Could not parse the distances.txt file format properly."
  )
