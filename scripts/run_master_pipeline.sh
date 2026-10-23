#!/bin/bash
set -e

echo "=========================================================="
echo "   STARTING COMPLETE MOUSE BLAST ANALYSIS PIPELINE        "
echo "=========================================================="

# 1. Directory verification
mkdir -p data results scripts

# ------------------------------------------------------------
# Phase 1: Transcript & BLASTN Analysis (Tasks 107-109)
# ------------------------------------------------------------
echo ""
echo ">>> [Phase 1/3] Checking BLASTN & Transcript Translation Tasks..."

# Check if translated protein BLASTN results exist; if not, run translation
if [ ! -f "results/protein_blastn_translated.tsv" ]; then
    if [ -f "scripts/translate_blastn_to_protein.py" ]; then
        echo "Running transcript-to-protein translation script..."
        python3 scripts/translate_blastn_to_protein.py
    else
        echo "Warning: scripts/translate_blastn_to_protein.py not found. Skipping translation."
    fi
else
    echo "[OK] results/protein_blastn_translated.tsv already exists. (Skipping)"
fi

# ------------------------------------------------------------
# Phase 2: Protein Database & BLASTP Run (Tasks 119-120)
# ------------------------------------------------------------
echo ""
echo ">>> [Phase 2/3] Checking Protein Database & BLASTP Self-Alignment..."

# Format BLASTP database if not already present
if [ ! -f "data/mouse_protein_db.phr" ]; then
    if [ -f "data/Mus_musculus.GRCm39.pep.all.fa" ]; then
        echo "Formatting mouse protein BLAST database..."
        makeblastdb -in data/Mus_musculus.GRCm39.pep.all.fa \
                    -dbtype prot \
                    -out data/mouse_protein_db \
                    -title "Mouse_Protein_DB"
    else
        echo "Error: data/Mus_musculus.GRCm39.pep.all.fa missing. Please ensure protein FASTA exists."
        exit 1
    fi
else
    echo "[OK] Protein BLAST database already formatted. (Skipping)"
fi

# Run BLASTP all-against-all self-alignment if output does not exist
if [ ! -f "results/protein_blastp_self_results.tsv" ]; then
    echo "Running all-against-all BLASTP (8 threads)..."
    blastp -query data/Mus_musculus.GRCm39.pep.all.fa \
           -db data/mouse_protein_db \
           -out results/protein_blastp_self_results.tsv \
           -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
           -evalue 1e-5 \
           -max_target_seqs 50 \
           -num_threads 8
    echo "BLASTP search completed."
else
    echo "[OK] results/protein_blastp_self_results.tsv already exists. (Skipping)"
fi

# ------------------------------------------------------------
# Phase 3: Comparative Analysis & Scatterplot (Task 121)
# ------------------------------------------------------------
echo ""
echo ">>> [Phase 3/3] Running BLASTN vs BLASTP Comparison & Visualization..."

if [ -f "scripts/compare_blastn_blastp.py" ]; then
    python3 scripts/compare_blastn_blastp.py
    echo "[OK] Comparison complete and scatterplot generated."
else
    echo "Error: scripts/compare_blastn_blastp.py not found!"
    exit 1
fi

echo ""
echo "=========================================================="
echo "[SUCCESS] ALL TASKS COMPLETED SUCCESSFULLY!"
echo "Master pipeline executed cleanly."
echo "=========================================================="
