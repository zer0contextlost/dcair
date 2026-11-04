"""CARB facility criteria emissions (CEIDARS) statewide, SIC 7374, one CSV per database year."""
import urllib.request, os, time, sys
OUT = '/srv/airtox/nei/raw_state/ca/carb'; os.makedirs(OUT, exist_ok=True)
U = 'https://www.arb.ca.gov/app/emsinv/iframe/facinfo/faccrit_output.csv?dbyr={y}&fsic_=7374&all_fac=C'
for y in range(int(sys.argv[1]) if len(sys.argv) > 1 else 2000, 2025):
    p = f'{OUT}/carb_sic7374_{y}.csv'
    if os.path.exists(p): continue
    try:
        b = urllib.request.urlopen(urllib.request.Request(U.format(y=y), headers={"User-Agent": "dcair-research/0.1 (zer0contextlost@proton.me)"}), timeout=180).read()
    except Exception as e:
        print(y, 'ERR', e); continue
    open(p, 'wb').write(b); print(y, b.count(b'\n') - 1, 'facilities', flush=True); time.sleep(3)
