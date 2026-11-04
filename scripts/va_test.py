"""Virginia validity test: how many DEQ data-center permits appear in NEI 2012-2023, and what do they report."""
import csv, collections, re
EX = '/srv/airtox/nei/derived/extract.csv'
PE = '/srv/airtox/nei/ref/publicevidence/virginia-data-center-air-permits.csv'
permits = {}
for p in csv.DictReader(open(PE)):
    reg = re.match(r'\s*(\d{5})', p['permit'] or '')
    if reg: permits.setdefault(reg.group(1), p)
print('PE permits:', sum(1 for _ in open(PE)) - 1, 'unique registration numbers:', len(permits))
fac = collections.defaultdict(dict)          # (year, eis) -> info
emis = collections.defaultdict(float)       # (year, eis, pollutant) -> tons
for x in csv.DictReader(open(EX)):
    if x['state'] != 'VA': continue
    y, e = int(x['year']), x['eis facility id']
    tons = float(x['total emissions'] or 0) * (1/2000 if x['emissions uom'].upper() == 'LB' else 1)
    fac[(y, e)] = x
    emis[(y, e, x['pollutant code'])] += tons
years = sorted({y for y, _ in fac})
print('\nyear  VAfac  permit-join  naics518  name-only  | NOx tons (join+naics)  PM25  formaldehyde(t)  dsets')
dc_ids = collections.defaultdict(set)
for y in years:
    j = n = nm = 0; ids = set(); ds = collections.Counter()
    for (yy, e), x in fac.items():
        if yy != y: continue
        ds[x['data set']] += 1
        inj = x['agency facility id'].lstrip('0').zfill(5) in permits
        isn = x['primary naics code'].startswith('5182')
        isnm = 'name' in x['why'] and not (inj or isn)
        j += inj; n += isn; nm += isnm
        if inj or isn: ids.add(e)
    dc_ids[y] = ids
    nox = sum(emis[(y, e, 'NOX')] for e in ids); pm = sum(emis[(y, e, 'PM25-PRI')] for e in ids)
    fo = sum(emis[(y, e, '50000')] for e in ids)
    print(f'{y}  {sum(1 for k in fac if k[0]==y):5d}  {j:11d}  {n:8d}  {nm:9d}  | {nox:10.1f}  {pm:8.1f}  {fo:8.3f}  {dict(ds)}')
# which permits never appear
seen = {fac[k]['agency facility id'].lstrip('0').zfill(5) for k in fac}
never = [r for r in permits if r not in seen]
print('\nregistrations never in NEI 2012-2023:', len(never), 'of', len(permits))
by_prog = collections.Counter(permits[r]['program_type'].strip() for r in never)
print(' by program:', dict(by_prog))
hit = [r for r in permits if r in seen]
print(' present, by program:', dict(collections.Counter(permits[r]['program_type'].strip() for r in hit)))
# NAICS of joined facilities (are data centers coded 518210?)
nc = collections.Counter()
for k, x in fac.items():
    if x['agency facility id'].lstrip('0').zfill(5) in permits: nc[(x['primary naics code'], x['primary naics description'])] += 1
print('\nNAICS of permit-joined rows:', nc.most_common(8))
# top 2023 facilities
y = max(years)
top = sorted(dc_ids[y], key=lambda e: -emis[(y, e, 'NOX')])[:12]
print(f'\ntop {y} by NOx:')
for e in top:
    x = fac[(y, e)]; print(f"  {emis[(y,e,'NOX')]:7.1f} t  {x['site name'][:45]:45s} {x['county']:12s} reg {x['agency facility id']} naics {x['primary naics code']}")
