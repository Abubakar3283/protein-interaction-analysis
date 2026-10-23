#!/bin/bash
set -e

echo "=========================================================="
echo "   STARTING COMPLETE MOUSE BLAST ANALYSIS PIPELINE        "
echo "=========================================================="

# 1. فولڈرز کی ساخت کی تصدیق
mkdir -p data results scripts

# ------------------------------------------------------------
# مرحلہ ۱: ٹرانسکرپٹ اور BLASTN انالسز (پچھلے ٹاسک: 107-109)
# ------------------------------------------------------------
echo ""
echo ">>> [Phase 1/3] Checking BLASTN & Transcript Translation Tasks..."

# اگر ترجمہ شدہ فائل موجود نہیں تو پائتھن اسکرپٹ چلائیں
if [ ! -f "results/protein_blastn_translated.tsv" ]; then
    if [ -f "scripts/translate_blastn_to_protein.py" ]; then
        echo "Running transcript-to-protein translation script..."
        python3 scripts/translate_blastn_to_protein.py
    else
        echo "Warning: scripts/translate_blastn_to_protein.py not found. Skipping translation."
    fi
else
    echo "✔ results/protein_blastn_translated.tsv already exists. (Skipping)"
fi

# ------------------------------------------------------------
# مرحلہ ۲: پروٹین ڈیٹا بیس اور BLASTP رن (ٹاسک: 119-120)
# ------------------------------------------------------------
echo ""
echo ">>> [Phase 2/3] Checking Protein Database & BLASTP Self-Alignment..."

# پروٹین ڈیٹا بیس چیک کریں
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
    echo "✔ Protein BLAST database already formatted. (Skipping)"
fi

# BLASTP سیلف الائنمنٹ چیک کریں
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
    echo "✔ results/protein_blastp_self_results.tsv already exists. (Skipping)"
fi

# ------------------------------------------------------------
# مرحلہ ۳: تقابلی تجزیہ، کوریلیشن اور گراف بنانا (ٹاسک: 121)
# ------------------------------------------------------------
echo ""
echo ">>> [Phase 3/3] Running BLASTN vs BLASTP Comparison & Visualization..."

if [ -f "scripts/compare_blastn_blastp.py" ]; then
    python3 scripts/compare_blastn_blastp.py
    echo "✔ Comparison complete and scatterplot generated."
else
    echo "Error: scripts/compare_blastn_blastp.py not found!"
    exit 1
fi

echo ""
echo "=========================================================="
echo "✔ ALL TASKS COMPLETED SUCCESSFULLY!"
echo "Master pipeline executed safely without duplicating files."
echo "=========================================================="
