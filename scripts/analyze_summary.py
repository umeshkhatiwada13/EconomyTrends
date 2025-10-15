import pandas as pd
from datetime import datetime
import os
proc_dir = "data/processed"

# find latest summary file
files = [f for f in os.listdir(proc_dir) if f.startswith("latest_summary_")]
if not files:
    print("No summary found.")
    exit()
latest = sorted(files)[-1]
df = pd.read_csv(os.path.join(proc_dir, latest))

# Build a short markdown insight
lines = []
lines.append(f"# EconomyTrends — Insights ({datetime.utcnow().strftime('%Y-%m-%d')})\n")
for _, r in df.iterrows():
    pct = r['pct_change']
    if pct == "" or pd.isna(pct):
        change = "no data"
    else:
        change = f"{pct:+.2f}% vs previous period"
    lines.append(f"- **{r['indicator']}** ({r['last_date']}): {r['last_value']} — {change}")

output = "data/processed/insights_{}.md".format(datetime.utcnow().strftime("%Y%m%d"))
with open(output, "w") as f:
    f.write("\n".join(lines))
print("Insights written to", output)
