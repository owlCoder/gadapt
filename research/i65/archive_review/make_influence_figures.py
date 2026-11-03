"""Descriptive visualisations from the derived source-anchored ledger (not inference)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'I65_I64_R_I2_INFLUENCE_LEDGER_2026-11-03.json').read_text())

rows=sorted(DATA['R']['family_leave_one_out'],key=lambda r:r['c4'])
fig,ax=plt.subplots(figsize=(10,5.3))
y=range(len(rows))
ax.barh(list(y),[r['c4'] for r in rows])
ax.set_yticks(list(y),[r['removed'].replace('_','–') for r in rows])
ax.invert_yaxis()
ax.axvline(.05,linestyle='--',linewidth=1,label='Registered 0.05 point threshold (not a CI)')
ax.axvline(DATA['R']['original_exact_point']['c4'],linestyle=':',linewidth=2,label='Frozen 9-family point estimate')
ax.set_xlabel('c4: added GAdapt loss under orthogonal Q vs IPOP')
ax.set_title('I64-R — post hoc leave-one-function-out point estimates')
ax.set_xlim(0,.092)
ax.legend(loc='lower right',fontsize=8)
fig.text(.01,.01,'Source: pinned I64-R analysis.json.gz; weights renormalized; no leave-one-out bootstrap.',fontsize=8)
fig.tight_layout(rect=(0,.04,1,1))
fig.savefig(HERE/'I65_R_FAMILY_SENSITIVITY_2026-11-03.svg',format='svg',metadata={'Date': None})
plt.close(fig)

rows=DATA['I2']['cells']
labels=[f"{r['network']} / j={r['j']}" for r in rows]
vals=[r['contrasts']['CVaR(IPOP)-CVaR(H)'] for r in rows]
fig,ax=plt.subplots(figsize=(10,5.3))
y=list(range(len(rows)))
ax.barh(y,vals)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.axvline(0,color='black',linewidth=.9)
ax.set_xlabel('Per-cell CVaR90(IPOP) − CVaR90(hybrid): negative favors IPOP')
ax.set_title('I64-I2 — concentration of the negative tail contrast')
for i,val in enumerate(vals):
    ax.text(val+(.014 if val>=0 else -.014),i,f'{val:+.6f}',va='center',ha='left' if val>=0 else 'right',fontsize=8)
ax.set_xlim(-1.23,.16)
fig.text(.01,.01,'Source: 16 pinned I64-I/I2 run parts, 30 seeds/cell; descriptive contributions, not cell-wise CI.',fontsize=8)
fig.tight_layout(rect=(0,.04,1,1))
fig.savefig(HERE/'I65_I2_ORPD_CELL_INFLUENCE_2026-11-03.svg',format='svg',metadata={'Date': None})
plt.close(fig)
print('Generated 2 SVG figures')
