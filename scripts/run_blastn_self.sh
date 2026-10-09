#!/bin/bash
# ==============================================================================
# Script: run_blastn_self.sh
# Purpose: Run BLASTN on mouse cDNA sequences against itself (Task 107 & 108)
# Environment: blast_env
# ==============================================================================

set -e

# 1. Directories setup
DATA_DIR="data"
RESULTS_DIR="results"
mkdir -p ${RESULTS_DIR}

echo "=== Starting BLASTN Self-Alignment Pipeline ==="

# 2. Database verification (Task 107)
if [ ! -f "${DATA_DIR}/mouse_cdna_db.nsq" ]; then
    echo "[Step 1] Building BLAST nucleotide database from ${DATA_DIR}/cdna.fa..."
    makeblastdb -in ${DATA_DIR}/cdna.fa -dbtype nucl -out ${DATA_DIR}/mouse_cdna_db
else
    echo "[Step 1] Database mouse_cdna_db already exists. Skipping makeblastdb."
fi

# 3. Running BLASTN against itself (Task 107)
# Using -outfmt 6 (Tabular), multi-threading for speed, and E-value threshold
echo "[Step 2] Executing blastn (cdna.fa vs mouse_cdna_db)..."
blastn \
    -query ${DATA_DIR}/cdna.fa \
    -db ${DATA_DIR}/mouse_cdna_db \
    -out ${RESULTS_DIR}/cdna_blastn_self_results.tsv \
    -outfmt 6 \
    -evalue 1e-10 \
    -max_target_seqs 5 \
    -num_threads 4

echo "=== BLASTN Self-Alignment Finished Successfully ==="
echo "Output saved to: ${RESULTS_DIR}/cdna_blastn_self_results.tsv"
