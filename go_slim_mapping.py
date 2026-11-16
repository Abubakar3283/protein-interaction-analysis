import gzip
import os
import pandas as pd
from goatools.obo_parser import GODag
from goatools.go_search import GoSearch

# ============================================
# FILE PATHS
# ============================================
FASTA_FILE     = "data/transcripts_200.fa"
GAF_FILE       = "data/go_annotations/mgi.gaf.gz"
SLIM_FILE      = "data/go_annotations/goslim_generic.obo"
OUTPUT_FILE    = "results/transcript_go_slim.tsv"
DETAIL_FILE    = "results/transcript_go_detail.tsv"

print("="*55)
print("GO SLIM ANNOTATION PIPELINE")
print("="*55)

# ============================================
# STEP 1: Load GO Slim terms
# ============================================
print("\nStep 1: Loading GO Slim terms...")
godag = GODag(SLIM_FILE)

slim_terms = set()
for go_id, term in godag.items():
    if term.namespace in ['biological_process',
                          'molecular_function',
                          'cellular_component']:
        slim_terms.add(go_id)

print(f"Total GO Slim terms loaded: {len(slim_terms)}")

# ============================================
# STEP 2: Load Mouse GO Annotations (GAF)
# ============================================
print("\nStep 2: Loading mouse GO annotations...")

gene_go = {}

with gzip.open(GAF_FILE, 'rt') as f:
    for line in f:
        if line.startswith('!'):
            continue
        parts = line.strip().split('\t')
        if len(parts) < 15:
            continue

        db          = parts[0]
        gene_symbol = parts[2].strip()
        qualifier   = parts[3].strip()
        go_id       = parts[4].strip()
        evidence    = parts[6].strip()
        aspect      = parts[8].strip()

        # Skip negated annotations
        if 'NOT' in qualifier:
            continue

        # Skip IEA if you want high quality only
        # if evidence == 'IEA':
        #     continue

        if gene_symbol not in gene_go:
            gene_go[gene_symbol] = {
                'BP': [], 'MF': [], 'CC': []
            }

        if aspect == 'P':
            gene_go[gene_symbol]['BP'].append(
                (go_id, evidence))
        elif aspect == 'F':
            gene_go[gene_symbol]['MF'].append(
                (go_id, evidence))
        elif aspect == 'C':
            gene_go[gene_symbol]['CC'].append(
                (go_id, evidence))

print(f"Genes with GO annotations: {len(gene_go)}")

# ============================================
# STEP 3: Map GO terms to GO Slim terms
# ============================================
print("\nStep 3: Mapping to GO Slim terms...")

def map_to_slim(go_terms, slim_set, godag):
    slim_mapped = []
    for go_id, evidence in go_terms:
        if go_id not in godag:
            continue
        # Check if term itself is in slim
        if go_id in slim_set:
            term_name = godag[go_id].name
            slim_mapped.append(
                (go_id, term_name, evidence))
            continue
        # Walk up to find slim ancestor
        ancestors = godag[go_id].get_all_parents()
        for anc in ancestors:
            if anc in slim_set:
                term_name = godag[anc].name
                slim_mapped.append(
                    (anc, term_name, evidence))
                break
    # Remove duplicates
    seen = set()
    unique = []
    for item in slim_mapped:
        if item[0] not in seen:
            seen.add(item[0])
            unique.append(item)
    return unique

# ============================================
# STEP 4: Parse your 200 transcripts
# ============================================
print("\nStep 4: Processing your 200 transcripts...")

import re

transcripts = []
with open(FASTA_FILE, 'r') as f:
    for line in f:
        if line.startswith('>'):
            header = line.strip()
            tid = re.search(r'>(\S+)', header)
            gid = re.search(r'gene:(\S+)', header)
            sym = re.search(r'gene_symbol:(\S+)', header)
            desc = re.search(r'description:"([^"]+)"',
                             header)
            transcripts.append({
                'transcript_id': tid.group(1) if tid else 'N/A',
                'gene_id': gid.group(1) if gid else 'N/A',
                'gene_symbol': sym.group(1) if sym else 'N/A',
                'description': desc.group(1) if desc else 'N/A'
            })

print(f"Transcripts loaded: {len(transcripts)}")

# ============================================
# STEP 5: Annotate each transcript
# ============================================
print("\nStep 5: Annotating transcripts...")

results = []
detail_rows = []

mapped_count   = 0
unmapped_count = 0

for t in transcripts:
    gene_sym = t['gene_symbol']
    tid      = t['transcript_id']
    gid      = t['gene_id']

    bp_slim = []
    mf_slim = []
    cc_slim = []
    status  = "Unmapped"

    if gene_sym in gene_go:
        raw = gene_go[gene_sym]

        bp_slim = map_to_slim(
            raw['BP'], slim_terms, godag)
        mf_slim = map_to_slim(
            raw['MF'], slim_terms, godag)
        cc_slim = map_to_slim(
            raw['CC'], slim_terms, godag)

        if bp_slim or mf_slim or cc_slim:
            status = "Mapped"
            mapped_count += 1
        else:
            status = "No_GO_Slim_Terms"
            unmapped_count += 1
    else:
        unmapped_count += 1

    # Format terms for output
    bp_str = "|".join(
        [f"{i}({e})" for i,n,e in bp_slim]
    ) if bp_slim else "Unmapped"

    mf_str = "|".join(
        [f"{i}({e})" for i,n,e in mf_slim]
    ) if mf_slim else "Unmapped"

    cc_str = "|".join(
        [f"{i}({e})" for i,n,e in cc_slim]
    ) if cc_slim else "Unmapped"

    bp_names = "|".join(
        [n for i,n,e in bp_slim]
    ) if bp_slim else "Unmapped"

    mf_names = "|".join(
        [n for i,n,e in mf_slim]
    ) if mf_slim else "Unmapped"

    cc_names = "|".join(
        [n for i,n,e in cc_slim]
    ) if cc_slim else "Unmapped"

    results.append({
        'Transcript_ID':        tid,
        'Gene_ID':              gid,
        'Gene_Symbol':          gene_sym,
        'BP_GO_IDs':            bp_str,
        'BP_Terms':             bp_names,
        'MF_GO_IDs':            mf_str,
        'MF_Terms':             mf_names,
        'CC_GO_IDs':            cc_str,
        'CC_Terms':             cc_names,
        'Mapping_Status':       status
    })

    # Detail table
    all_terms = (
        [(tid, gid, gene_sym, 'BP', i, n, e)
         for i,n,e in bp_slim] +
        [(tid, gid, gene_sym, 'MF', i, n, e)
         for i,n,e in mf_slim] +
        [(tid, gid, gene_sym, 'CC', i, n, e)
         for i,n,e in cc_slim]
    )
    detail_rows.extend(all_terms)

# ============================================
# STEP 6: Save output files
# ============================================
print("\nStep 6: Saving results...")

os.makedirs("results", exist_ok=True)

# Main output
df = pd.DataFrame(results)
df.to_csv(OUTPUT_FILE, sep='\t', index=False)
print(f"Saved: {OUTPUT_FILE}")

# Detail table
detail_cols = ['Transcript_ID', 'Gene_ID',
               'Gene_Symbol', 'Aspect',
               'GO_ID', 'GO_Term', 'Evidence']
df_detail = pd.DataFrame(detail_rows,
                          columns=detail_cols)
df_detail.to_csv(DETAIL_FILE, sep='\t',
                  index=False)
print(f"Saved: {DETAIL_FILE}")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*55)
print("TASK 3 SUMMARY")
print("="*55)
print(f"Total transcripts:     {len(transcripts)}")
print(f"Successfully mapped:   {mapped_count}")
print(f"Unmapped:              {unmapped_count}")
print(f"GO Slim source:        goslim_generic.obo")
print(f"Annotation source:     mgi.gaf.gz")
print(f"GO Slim terms loaded:  {len(slim_terms)}")
print(f"Detail records:        {len(detail_rows)}")
print("="*55)
print("\nMapping Status Breakdown:")
print(df['Mapping_Status'].value_counts().to_string())
print("\nSample Results (first 3):")
print(df[['Transcript_ID','Gene_Symbol',
          'BP_Terms','MF_Terms',
          'CC_Terms','Mapping_Status']].head(3).to_string())
print("\n✅ TASK 3 COMPLETE!")
