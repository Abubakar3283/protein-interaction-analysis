import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

print("Step 1: Reading distances.txt...")

# Read the file
with open("results/distances.txt", "r") as f:
    lines = f.readlines()

# Skip header lines - find where numbers start
data_lines = []
seq_names = []

for line in lines:
    line = line.strip()
    # Skip empty lines and header lines
    if not line:
        continue
    if line.startswith("Distance") or \
       line.startswith("---") or \
       line.startswith("Using") or \
       line.startswith("Gap"):
        continue
    # Skip the column number header line
    if line.strip().startswith("1 ") and "ENSMUST" not in line:
        continue
    # This is a data line if it contains ENSMUST
    if "ENSMUST" in line:
        data_lines.append(line)

print(f"Found {len(data_lines)} sequence rows")

# Parse each row
matrix = []
names = []

for line in data_lines:
    # Get sequence name (second to last element)
    parts = line.split()
    
    # Last element = row number, second to last = transcript ID
    seq_name = parts[-2]  # ENSMUST00000194081.2
    names.append(seq_name)
    
    # Get all numbers (everything except last 2 elements)
    values = parts[:-2]
    
    row = []
    for v in values:
        try:
            val = float(v)
            # Replace inf and nan with large number
            if np.isinf(val) or np.isnan(val):
                val = np.nan
            row.append(val)
        except:
            continue
    
    matrix.append(row)

print(f"Number of sequences: {len(names)}")
print(f"First sequence: {names[0]}")
print(f"Row lengths: {[len(r) for r in matrix[:5]]}")

# Find max row length
max_len = max(len(r) for r in matrix)
print(f"Max row length: {max_len}")

# Pad shorter rows with nan
for i in range(len(matrix)):
    while len(matrix[i]) < max_len:
        matrix[i].append(np.nan)

# Convert to numpy array
dist_array = np.array(matrix, dtype=float)
print(f"Matrix shape: {dist_array.shape}")

# Fix: Fill NaN with column/row mean or max
# Replace NaN with max valid value for now
max_val = np.nanmax(dist_array)
print(f"Max distance value: {max_val:.2f}")
print(f"Min distance value: {np.nanmin(dist_array):.2f}")

# Fill diagonal with 0
np.fill_diagonal(dist_array, 0)

# Replace remaining NaN with max_val
dist_filled = np.where(np.isnan(dist_array), max_val, dist_array)

# ============================================
# Convert to Similarity Matrix (0 to 1)
# ============================================
print("\nStep 2: Converting to similarity...")

max_dist = np.max(dist_filled)
similarity = 1.0 - (dist_filled / max_dist)
np.fill_diagonal(similarity, 1.0)

print(f"Similarity range: {similarity.min():.4f} to {similarity.max():.4f}")

# Save similarity matrix
print("\nStep 3: Saving similarity matrix...")
sim_df = pd.DataFrame(similarity, 
                       index=names, 
                       columns=names)
sim_df.to_csv("results/similarity_matrix_FIXED.txt", sep="\t")
print("Saved: results/similarity_matrix_FIXED.txt")

# ============================================
# Plot 1: Distance Heatmap
# ============================================
print("\nStep 4: Plotting Distance Heatmap...")

fig, ax = plt.subplots(figsize=(14, 12))

# Use short names for display (just numbers)
short_names = [str(i+1) for i in range(len(names))]

sns.heatmap(
    dist_filled,
    cmap="coolwarm",
    square=True,
    xticklabels=20,
    yticklabels=20,
    cbar_kws={"label": "Evolutionary Distance"},
    ax=ax
)

ax.set_title("Transcript Distance Matrix Heatmap\n(200 Mouse Transcripts)", 
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Transcripts", fontsize=13)
ax.set_ylabel("Transcripts", fontsize=13)

plt.tight_layout()
plt.savefig("results/distance_heatmap_FIXED.png", 
            dpi=300, bbox_inches="tight")
plt.close()
print("Saved: results/distance_heatmap_FIXED.png")

# ============================================
# Plot 2: Similarity Heatmap
# ============================================
print("\nStep 5: Plotting Similarity Heatmap...")

fig, ax = plt.subplots(figsize=(14, 12))

sns.heatmap(
    similarity,
    cmap="YlOrRd",
    square=True,
    xticklabels=20,
    yticklabels=20,
    vmin=0,
    vmax=1,
    cbar_kws={"label": "Sequence Similarity (0 to 1)"},
    ax=ax
)

ax.set_title("Transcript Similarity Matrix Heatmap\n(200 Mouse Transcripts)",
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Transcripts", fontsize=13)
ax.set_ylabel("Transcripts", fontsize=13)

plt.tight_layout()
plt.savefig("results/similarity_heatmap_FIXED.png",
            dpi=300, bbox_inches="tight")
plt.close()
print("Saved: results/similarity_heatmap_FIXED.png")

# ============================================
# Plot 3: Clustered Heatmap
# ============================================
print("\nStep 6: Plotting Clustered Heatmap...")

g = sns.clustermap(
    sim_df,
    cmap="YlOrRd",
    figsize=(16, 14),
    xticklabels=False,
    yticklabels=False,
    cbar_pos=(0.02, 0.8, 0.03, 0.18),
    dendrogram_ratio=0.15,
    vmin=0,
    vmax=1
)

g.fig.suptitle("Clustered Similarity Heatmap\n(200 Mouse Transcripts)",
               fontsize=16, fontweight="bold", y=1.02)

plt.savefig("results/clustered_similarity_heatmap_FIXED.png",
            dpi=300, bbox_inches="tight")
plt.close()
print("Saved: results/clustered_similarity_heatmap_FIXED.png")

# ============================================
# Print Summary Stats
# ============================================
print("\n" + "="*50)
print("SUMMARY STATISTICS")
print("="*50)
print(f"Total transcripts:       {len(names)}")
print(f"Matrix shape:            {dist_array.shape}")
print(f"Max distance:            {np.nanmax(dist_array):.2f}")
print(f"Min distance (non-zero): {np.nanmin(dist_array[dist_array>0]):.2f}")
print(f"Mean distance:           {np.nanmean(dist_array):.2f}")
print(f"Max similarity:          {similarity.max():.4f}")
print(f"Min similarity:          {similarity.min():.4f}")
print(f"Mean similarity:         {similarity.mean():.4f}")
print("="*50)
print("\n✅ ALL 3 HEATMAPS GENERATED SUCCESSFULLY!")
