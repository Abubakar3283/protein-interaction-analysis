import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("Loading GO Slim results...")

df = pd.read_csv("results/transcript_go_slim.tsv",
                 sep="\t")
detail = pd.read_csv("results/transcript_go_detail.tsv",
                     sep="\t")

print(f"Total transcripts: {len(df)}")
print(f"Detail records: {len(detail)}")

os.makedirs("results", exist_ok=True)

# ============================================
# Graph 1: Mapping Status Pie Chart
# ============================================
print("Plotting Graph 1: Mapping Status...")

import os
os.makedirs("results", exist_ok=True)

status_counts = df['Mapping_Status'].value_counts()

colors = ['#2ecc71', '#e74c3c', '#f39c12']
explode = [0.05] * len(status_counts)

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    status_counts.values,
    labels=status_counts.index,
    colors=colors[:len(status_counts)],
    autopct='%1.1f%%',
    explode=explode[:len(status_counts)],
    startangle=90,
    textprops={'fontsize': 12}
)
for at in autotexts:
    at.set_fontweight('bold')

ax.set_title(
    f"GO Slim Mapping Status\n(200 Mouse Transcripts)",
    fontsize=15, fontweight='bold', pad=20)

legend_labels = [
    f"{idx}: {val} transcripts"
    for idx, val in status_counts.items()
]
ax.legend(wedges, legend_labels,
          loc="lower center",
          bbox_to_anchor=(0.5, -0.12),
          fontsize=11)

plt.tight_layout()
plt.savefig("results/go_mapping_status.png",
            dpi=300, bbox_inches='tight')
plt.close()
print("Saved: results/go_mapping_status.png")

# ============================================
# Graph 2: Top GO Slim Terms per Aspect
# ============================================
print("Plotting Graph 2: Top GO Terms...")

fig, axes = plt.subplots(1, 3, figsize=(20, 8))

aspects = [
    ('BP', 'Biological Process', '#3498db'),
    ('MF', 'Molecular Function', '#e74c3c'),
    ('CC', 'Cellular Component', '#2ecc71')
]

for ax, (aspect, title, color) in zip(axes, aspects):
    # Get terms for this aspect
    aspect_data = detail[detail['Aspect'] == aspect]

    if len(aspect_data) == 0:
        ax.text(0.5, 0.5, 'No data',
                ha='center', va='center',
                transform=ax.transAxes,
                fontsize=14)
        ax.set_title(title)
        continue

    # Count term frequencies
    term_counts = aspect_data['GO_Term'].value_counts().head(10)

    # Plot horizontal bar
    bars = ax.barh(range(len(term_counts)),
                   term_counts.values,
                   color=color, alpha=0.8,
                   edgecolor='black', linewidth=0.5)

    ax.set_yticks(range(len(term_counts)))
    ax.set_yticklabels(
        [t[:35]+'...' if len(t)>35 else t
         for t in term_counts.index],
        fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Transcripts', fontsize=11)
    ax.set_title(f'Top GO Slim Terms\n{title}',
                 fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # Add count labels
    for i, (bar, val) in enumerate(
            zip(bars, term_counts.values)):
        ax.text(bar.get_width() + 0.1, i,
                str(val), va='center', fontsize=9)

plt.suptitle(
    'Top GO Slim Terms Across Three Aspects\n(87 Mapped Mouse Transcripts)',
    fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig("results/go_top_terms.png",
            dpi=300, bbox_inches='tight')
plt.close()
print("Saved: results/go_top_terms.png")

# ============================================
# Graph 3: Transcripts per Aspect Bar Chart
# ============================================
print("Plotting Graph 3: Aspect Coverage...")

mapped_df = df[df['Mapping_Status'] == 'Mapped']

bp_mapped = sum(1 for x in mapped_df['BP_Terms']
                if x != 'Unmapped')
mf_mapped = sum(1 for x in mapped_df['MF_Terms']
                if x != 'Unmapped')
cc_mapped = sum(1 for x in mapped_df['CC_Terms']
                if x != 'Unmapped')

aspects_names = ['Biological\nProcess (BP)',
                 'Molecular\nFunction (MF)',
                 'Cellular\nComponent (CC)']
aspects_vals  = [bp_mapped, mf_mapped, cc_mapped]
aspects_colors = ['#3498db', '#e74c3c', '#2ecc71']

fig, ax = plt.subplots(figsize=(10, 7))

bars = ax.bar(aspects_names, aspects_vals,
              color=aspects_colors,
              edgecolor='black', linewidth=0.8,
              width=0.5)

for bar, val in zip(bars, aspects_vals):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            str(val),
            ha='center', va='bottom',
            fontsize=14, fontweight='bold')

ax.set_ylabel('Number of Transcripts',
              fontsize=13)
ax.set_title(
    'GO Slim Annotation Coverage\nper Aspect (200 Mouse Transcripts)',
    fontsize=15, fontweight='bold', pad=15)
ax.set_ylim(0, max(aspects_vals) + 10)
ax.axhline(y=87, color='gray',
           linestyle='--', alpha=0.5,
           label='Total mapped (87)')
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("results/go_aspect_coverage.png",
            dpi=300, bbox_inches='tight')
plt.close()
print("Saved: results/go_aspect_coverage.png")

# ============================================
# Summary Stats
# ============================================
print("\n" + "="*55)
print("TASK 3 GRAPH SUMMARY")
print("="*55)
print(f"Mapped transcripts:   {len(mapped_df)}")
print(f"BP annotated:         {bp_mapped}")
print(f"MF annotated:         {mf_mapped}")
print(f"CC annotated:         {cc_mapped}")
print(f"\nTop BP term: {detail[detail['Aspect']=='BP']['GO_Term'].value_counts().index[0] if len(detail[detail['Aspect']=='BP'])>0 else 'N/A'}")
print(f"Top MF term: {detail[detail['Aspect']=='MF']['GO_Term'].value_counts().index[0] if len(detail[detail['Aspect']=='MF'])>0 else 'N/A'}")
print(f"Top CC term: {detail[detail['Aspect']=='CC']['GO_Term'].value_counts().index[0] if len(detail[detail['Aspect']=='CC'])>0 else 'N/A'}")
print("="*55)
print("\n✅ ALL TASK 3 GRAPHS GENERATED!")
