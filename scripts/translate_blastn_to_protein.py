import sys

print("[INFO] Loading transcript-to-protein mapping...")
mapping = {}
with open("data/transcript_to_protein.tsv") as f:
    for line in f:
        t, p = line.strip().split("\t")
        mapping[t] = p
print(f"[INFO] Loaded {len(mapping)} protein mappings.")

input_file = "results/cdna_blastn_self_results.tsv"
output_file = "results/protein_blastn_translated.tsv"

total_records = 0
both_mapped = 0
dropped_non_coding = 0
self_protein_loops = 0

print("[INFO] Processing BLASTN tabular alignments...")
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    # Write Header
    outfile.write("q_prot\ts_prot\tq_trans\ts_trans\tpident\tlength\tevalue\tbitscore\n")
    
    for line in infile:
        total_records += 1
        cols = line.strip().split("\t")
        q_trans_full = cols[0]
        s_trans_full = cols[1]
        
        q_trans = q_trans_full.split(".")[0]
        s_trans = s_trans_full.split(".")[0]
        
        q_prot = mapping.get(q_trans)
        s_prot = mapping.get(s_trans)
        
        # Check if both are protein-coding
        if q_prot and s_prot:
            both_mapped += 1
            if q_prot == s_prot:
                self_protein_loops += 1
            outfile.write(f"{q_prot}\t{s_prot}\t{q_trans_full}\t{s_trans_full}\t{cols[2]}\t{cols[3]}\t{cols[10]}\t{cols[11]}\n")
        else:
            dropped_non_coding += 1

print("\n" + "=" * 50)
print("             TRANSLATION AUDIT SUMMARY           ")
print("=" * 50)
print(f"Total Input BLASTN Alignments : {total_records:,}")
print(f"Successfully Translated Pairs : {both_mapped:,} ({(both_mapped/total_records)*100:.2f}%)")
print(f"Dropped (Non-coding involved) : {dropped_non_coding:,} ({(dropped_non_coding/total_records)*100:.2f}%)")
print(f"Identical Protein Self-Loops  : {self_protein_loops:,} ({(self_protein_loops/both_mapped)*100:.2f}%)")
print(f"\n[SUCCESS] Output saved to: {output_file}")
