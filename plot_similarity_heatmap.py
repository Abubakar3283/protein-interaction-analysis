import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Define file paths
similarity_file = "results/similarity_matrix.txt"
output_image = "results/similarity_heatmap.png"

print("Reading similarity matrix...")

try:
    sim_matrix = np.loadtxt(similarity_file, delimiter="\t")
except Exception as e:
    sim_matrix = np.loadtxt(similarity_file)

# Set up the matplotlib figure
plt.figure(figsize=(12, 10), dpi=300)

# Create heatmap using Seaborn (Coolwarm colormap representing similarity score from 0 to 1)
sns.heatmap(
    sim_matrix,
    cmap="coolwarm",
    vmin=0.0,
    vmax=1.0,
    cbar_kws={"label": "Sequence Similarity Score (0 to 1)"},
    xticklabels=20,
    yticklabels=20,
)

# Add title and axis labels
plt.title("Transcript Similarity Matrix Heatmap", fontsize=16, fontweight="bold", pad=15)
plt.xlabel("Transcripts", fontsize=14)
plt.ylabel("Transcripts", fontsize=14)

# Ensure results directory exists and save the plot
os.makedirs("results", exist_ok=True)
plt.tight_layout()
plt.savefig(output_image, dpi=300)
print(f"Similarity heatmap successfully generated and saved at: {output_image}")
