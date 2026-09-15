cat << 'EOF' > scripts/extract_info.py
import gzip
import pandas as pd

input_file = "data/10090.protein.info.v12.0.txt.gz"

# کمپریسڈ فائل کو پڑھ کر صرف پہلے چار بنیادی کالمز منتخب کرنا
df = pd.read_csv(input_file, sep="\t", nrows=10)

# نتائج کو ٹرمینل پر صاف دکھانا
print("=== Preview of Selected Protein Annotations ===")
print(df.to_markdown(index=False))
EOF
