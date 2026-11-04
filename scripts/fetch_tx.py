"""TCEQ point source emissions inventory, site-wide summary 2010-2024 (one sheet per year)."""
import urllib.request, os
OUT = '/srv/airtox/nei/raw_state/tx'; os.makedirs(OUT, exist_ok=True)
U = 'https://www.tceq.texas.gov/downloads/air-quality/point-source/2010-2024-state-sum.xlsx'
b = urllib.request.urlopen(urllib.request.Request(U, headers={'User-Agent': 'dcair-research/0.1 (zer0contextlost@proton.me)'}), timeout=180).read()
open(f'{OUT}/2010-2024-state-sum.xlsx', 'wb').write(b); print(len(b))
