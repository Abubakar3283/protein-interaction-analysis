import os
import numpy as np

# Define file paths
distances_file = "results/distances.txt"
similarity_file = "results/similarity_matrix.txt"

print("Reading distance matrix...")

# Read the distance matrix and skip non-numeric header lines
matrix_data = []
with open(distances_file, "r") as f:
    for line in f:
        parts = line.strip().split()
        # Check if the line contains valid distance data (must have multiple elements and start with a number or valid row identifier)
        if len(parts) > 1:
            try:
                # Try converting parts[1:] to float. If it fails (e.g. header line containing 'Matrix'), it skips.
                distances = [float(val) for val in parts[1:]]
                matrix_data.append(distances)
            except ValueError:
                # Skip header or text lines like 'Matrix'
                continue

dist_matrix = np.array(matrix_data)

# Handle case where matrix might be empty
if dist_matrix.size == 0:
    raise ValueError("Error: No valid distance data found in distances.txt. Please check the file format.")

# Find the maximum distance to normalize values
max_distance = np.max(dist_matrix)
if max_distance == 0:
    max_distance = 1.0  # Prevent division by zero

# Convert distance matrix to similarity matrix: Similarity = 1 - (Distance / Max_Distance)
sim_matrix = 1.0 - (dist_matrix / max_distance)

# Ensure the results directory exists and save the similarity matrix
os.makedirs("results", exist_ok=True)
np.savetxt(similarity_file, sim_matrix, fmt="%.4f")

print(f"Similarity matrix successfully generated and saved at: {similarity_file}")
