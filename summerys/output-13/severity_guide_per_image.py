"""
Ticket-013 Table 3: Severity Breakdown Per Image (Guide only)
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Load guide master CSV
guide = pd.read_csv('../guide_master.csv')

os.makedirs('output', exist_ok=True)

# ============================================================
# TABLE 3 — Severity Breakdown Per Image
# ============================================================
print("=" * 60)
print("TABLE 3 — Severity Breakdown Per Image (Guide)")
print("=" * 60)

# Crosstab: image × severity (counts)
severity_counts = pd.crosstab(guide['image_name'], guide['severity'])

# Make sure all columns exist
for col in ['Clean', 'Early', 'Mid', 'Late', 'Error']:
    if col not in severity_counts.columns:
        severity_counts[col] = 0
severity_counts = severity_counts[['Clean', 'Early', 'Mid', 'Late', 'Error']]

# Add sporulation % per image
severity_counts['Sporulation_%'] = guide.groupby('image_name')['sporulation'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
).round(1)

# Add avg confidence per image
severity_counts['Avg_Confidence'] = guide.groupby('image_name')['confidence'].mean().round(3)

# Print
print(severity_counts.to_string())

severity_counts.to_csv('output/table3_severity_per_image.csv')
print("\nSaved: output/table3_severity_per_image.csv")

# ============================================================
# PLOT — Stacked horizontal bar chart (percentage)
# ============================================================
# Convert to percentages
totals = severity_counts[['Clean', 'Early', 'Mid', 'Late']].sum(axis=1)
pct = severity_counts[['Clean', 'Early', 'Mid', 'Late']].div(totals, axis=0) * 100

short_names = [name.replace('.JPG', '')[:40] for name in pct.index]
y = np.arange(len(short_names))

fig, ax = plt.subplots(figsize=(12, 8))

colors = {'Clean': '#3fb950', 'Early': '#d29922', 'Mid': '#f0883e', 'Late': '#da3633'}
left = np.zeros(len(pct))

for severity in ['Clean', 'Early', 'Mid', 'Late']:
    vals = pct[severity].values
    ax.barh(y, vals, left=left, label=severity, color=colors[severity])
    left += vals

ax.set_xlabel('% of Patches')
ax.set_ylabel('Image')
ax.set_title('Table 3 — Severity Distribution Per Image (Guide)')
ax.set_yticks(y)
ax.set_yticklabels(short_names, fontsize=8)
ax.legend(loc='lower right')
ax.set_xlim(0, 100)

plt.tight_layout()
plt.savefig('output/table3_severity_per_image.png', dpi=150)
plt.show()
print("Saved: output/table3_severity_per_image.png")