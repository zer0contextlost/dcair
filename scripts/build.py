"""dcair v1 build: normalize state + NEI data-center emissions into one long table.

Output (/srv/airtox/nei/derived/v1/):
  long.csv        every row from every source (source, year, facility, pollutant, tons, tiers)
  best.csv        one source per state-year-pollutant group (state source beats NEI), headline tiers only
  coverage.csv    facilities and NOx by state, year, source
Every row says where it came from. Values are what the facility/agency reported (mostly emission-factor
estimates), never our estimates.
"""
import csv, glob, io, json, os, re, sys, collections
import openpyxl

RAW = '/srv/airtox/nei'
OUT = f'{RAW}/derived/v1'
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DC_NAME, CRYPTO, OPS, operator, tiers, HEADLINE, CAS, canon

COLS = ['state', 'source', 'source_url', 'year', 'facility_id', 'facility_name', 'owner', 'operator', 'tier',
        'county', 'city', 'lat', 'lon', 'naics_or_sic', 'pollutant', 'pollutant_original', 'tons', 'note', 'qa_flag']
rows = []
def add(**kw):
    r = {c: kw.get(c, '') for c in COLS}
    r = {c: (re.sub(r'\s+', ' ', v).strip() if isinstance(v, str) else ('' if v is None else v)) for c, v in r.items()}
    if r['tons'] in ('', None): return
    r['tons'] = float(r['tons'])
    rows.append(r)

# ---------- Virginia DEQ (2024, state flag) ----------
def load_va():
    d = sorted(glob.glob(f'{RAW}/raw_state/va/*/'))[-1]
    sites = {f['attributes']['PLA_REG_NUM']: f for f in json.load(open(d + 'air_sites.json'))}
    n = 0
    for e in json.load(open(d + 'emissions_tpy.json')):
        a = e['attributes']; s = sites.get(a['PLA_REG_NUM'])
        if not s or s['attributes']['PLA_DATA_CENTER_YN'] != 'Y': continue
        sa, g = s['attributes'], s.get('geometry') or {}
        add(state='VA', source='VA DEQ air sites emissions (ArcGIS EDMA 292/294)',
            source_url='https://gisdata.deq.virginia.gov/arcgis/rest/services/public/EDMA/MapServer/292',
            year=a['EMISSIONSYEAR'], facility_id=f"VA-REG-{sa['PLA_REG_NUM']}", facility_name=sa['PLA_NAME'],
            operator=operator(sa['PLA_NAME']), tier='state_flag', city=sa['FAC_L_CITY'], lat=g.get('y', ''), lon=g.get('x', ''),
            naics_or_sic=f"NAICS {sa['PLA_NAC_CODE_PRIMARY']}", pollutant=canon(a['CPL_SHORT_NAME'], a['CPL_POLLUTANT_NAME']),
            pollutant_original=a['CPL_POLLUTANT_NAME'], tons=a['EMISSION_VALUE'], note=sa['PCL_STATE_DESC'])
        n += 1
    print('VA DEQ rows', n)

# ---------- California CARB (SIC 7374, 1987+ database years) ----------
def load_ca():
    n = 0
    for p in sorted(glob.glob(f'{RAW}/raw_state/ca/carb/carb_sic7374_*.csv')):
        y = p[-8:-4]
        for r in csv.DictReader(open(p, encoding='latin-1')):
            name = r['FNAME'].strip()
            t = tiers(name, code_says_dc=True)
            for col, pol in (('NOXT', 'NOX'), ('COT', 'CO'), ('ROGT', 'VOC'), ('SOXT', 'SO2'), ('PM10T', 'PM10'), ('PMT', 'PM')):
                add(state='CA', source='CARB facility criteria emissions (CEIDARS)',
                    source_url='https://www.arb.ca.gov/app/emsinv/facinfo/facinfo.php', year=y,
                    facility_id=f"CA-{r['CO']}-{r['AB']}-{r['DIS']}-{r['FACID']}", facility_name=name, operator=operator(name),
                    tier=t, county=r['COID'], city=r['FCITY'], naics_or_sic='SIC 7374', pollutant=pol, pollutant_original=col,
                    tons=r[col] or 0, note=f"district {r['DISN']}; ROG used as VOC")
                n += 1
    print('CA CARB rows', n)

# ---------- Pennsylvania DEP (Power BI export, NAICS 518210) ----------
def load_pa():
    p = sorted(glob.glob(f'{RAW}/raw_state/pa/pbi_naics518210_export_*.csv'))[-1]
    lines = open(p, encoding='utf-8-sig').read().splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith('Region,'))
    n = 0
    for r in csv.DictReader(lines[i:]):
        name = r['PF Name']
        add(state='PA', source='PA DEP 25-year site-level emission inventory (Power BI export)',
            source_url='https://cedatareporting.pa.gov/reports/powerbi/Public/DEP/AQ/PBI/25%20Year%20Site%20%20Level%20Emission%20Inventory%20Report',
            year=r['Emission Year'], facility_id=f"PA-PF-{r['PF ID']}", facility_name=name, owner=r['Client'],
            operator=operator(name, r['Client']), tier=tiers(name, r['Client'], code_says_dc=True), county=r['County'],
            city=r['Municipality'], lat=r['Latitude'], lon=r['Longitude'], naics_or_sic='NAICS 518210',
            pollutant=canon('', r['Pollutant']), pollutant_original=r['Pollutant'], tons=r['Amount Emissions (Short Tons)'] or 0,
            note=f"EPA EIS {r['EPA EIS ID']}")
        n += 1
    print('PA DEP rows', n)

# ---------- Oregon DEQ air toxics (2016, 2020; lb/yr) ----------
def load_or():
    n = 0
    for p, y in ((f'{RAW}/raw_state/or/or_atei_2016.xlsx', '2016'), (f'{RAW}/raw_state/or/or_atei_2020.xlsx', '2020')):
        ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]
        hdr = None
        for r in ws.iter_rows(values_only=True):
            if hdr is None:
                if r and r[0] and str(r[0]).startswith('Source'): hdr = [str(c or '').replace('\n', ' ') for c in r]
                continue
            if not r or not r[1]: continue
            d = dict(zip(hdr, r))
            name = str(d.get('Facility Name') or d.get('Source Name') or '')
            t = tiers(name)
            if t not in HEADLINE and t != 'crypto': continue
            lb = next((v for k, v in d.items() if 'Emissions' in k and isinstance(v, (int, float))), None)
            if lb is None: continue
            cas = str(d.get('CAS Code') or d.get('CAS  Code') or '')
            add(state='OR', source=f'Oregon DEQ {y} Air Toxics Emissions Inventory',
                source_url='https://www.oregon.gov/deq/aq/air-toxics/Pages/Air-Toxics-Emissions-Inventory.aspx', year=y,
                facility_id=f"OR-SRC-{d.get('Source Number')}", facility_name=name, operator=operator(name), tier=t,
                naics_or_sic='', pollutant=canon(cas, str(d.get('Pollutant Name') or '')),
                pollutant_original=str(d.get('Pollutant Name')), tons=float(lb) / 2000, note=f"permit {d.get('Permit Type')}; lb/yr / 2000")
            n += 1
    print('OR DEQ rows', n)

# ---------- NEI facility summaries 2012-2023 (all states) ----------
def va_flagged():
    d = sorted(glob.glob(f'{RAW}/raw_state/va/*/'))[-1]
    return {str(f['attributes']['PLA_REG_NUM']).zfill(5) for f in json.load(open(d + 'air_sites.json'))
            if f['attributes']['PLA_DATA_CENTER_YN'] == 'Y'}

def load_nei():
    n = 0; vaf = va_flagged()
    for r in csv.DictReader(open(f'{RAW}/derived/extract.csv')):
        naics = r['primary naics code']
        flag = r['state'] == 'VA' and r['agency facility id'].lstrip('0').zfill(5) in vaf
        t = tiers(r['site name'], r['company name'], code_says_dc=naics.startswith('5182'), state_flag=flag)
        if r['state'] == 'VA' and t in ('name', 'code+name', 'code_only') and not flag:
            t = 'code_only' if t != 'name' else 'name'  # not in DEQ's data-center list
            if t == 'name': t = 'code_only'
        if not t: continue
        uom = r['emissions uom'].upper()
        tons = float(r['total emissions'] or 0) * (1 / 2000 if uom == 'LB' else 1)
        add(state=r['state'], source=f"EPA NEI facility summary ({r['data set']})",
            source_url='https://gaftp.epa.gov/air/nei/nei_facility_summaries/', year=r['year'],
            facility_id=f"EIS-{r['eis facility id']}", facility_name=r['site name'], owner=r['company name'],
            operator=operator(r['site name'], r['company name']), tier=t, county=r['county'], city=r['city'],
            lat=r['site latitude'], lon=r['site longitude'], naics_or_sic=f'NAICS {naics}',
            pollutant=canon(r['pollutant code'], r['pollutant desc']), pollutant_original=r['pollutant desc'], tons=tons,
            note=f"agency id {r['agency facility id']}")
        n += 1
    print('NEI rows', n)

# ---------- Texas TCEQ point source EI site summaries (2010-2024) ----------
def load_tx():
    wb = openpyxl.load_workbook(f'{RAW}/raw_state/tx/2010-2024-state-sum.xlsx', read_only=True)
    n = 0
    for ws in wb.worksheets:
        if not ws.title.isdigit(): continue
        it = ws.iter_rows(values_only=True); hdr = list(next(it))
        for r in it:
            d = dict(zip(hdr, r))
            if not d.get('SITE'): continue
            sic = str(d.get('SIC') or ''); name = str(d['SITE']).strip(); comp = str(d.get('COMPANY') or '')
            t = tiers(name, comp, code_says_dc=sic in ('7374', '7376'))
            if not t and not re.search(r'^(SHARKA|ALLIANCE SITE|MICROSOFT)$', name): continue
            for col, pol in (('NOX TPY', 'NOX'), ('CO TPY', 'CO'), ('VOC TPY', 'VOC'), ('SO2 TPY', 'SO2'),
                             ('PM2.5 TPY', 'PM25'), ('PM10 TPY', 'PM10'), ('PM TPY', 'PM'), ('Pb TPY', 'OTHER:Lead')):
                if d.get(col) in (None, ''): continue
                add(state='TX', source='TCEQ point source emissions inventory (STARS site summary)',
                    source_url='https://www.tceq.texas.gov/airquality/point-source-ei/psei.html', year=d.get('REPORTING YEAR') or ws.title,
                    facility_id=f"TX-RN-{d['RN']}", facility_name=name, owner=comp, operator=operator(name, comp), tier=t,
                    county=d.get('COUNTY'), city=d.get('NEAR CITY'), lat=d.get('LATITUDE'), lon=d.get('LONGITUDE'),
                    naics_or_sic=f'SIC {sic}', pollutant=pol, pollutant_original=col, tons=d[col], note=f"account {d.get('ACCOUNT')}")
                n += 1
    print('TX TCEQ rows', n)

# ---------- Maricopa County AZ (scraped EI detail pages) ----------
def load_az():
    sys.path.insert(0, os.path.dirname(__file__))
    from parse_az import parse_all
    n = 0
    for r in parse_all():
        add(**r); n += 1
    print('AZ Maricopa rows', n)

for f in (load_va, load_ca, load_pa, load_or, load_tx, load_nei, load_az):
    try: f()
    except FileNotFoundError as e: print(f.__name__, 'skipped:', e)
    except ModuleNotFoundError as e: print(f.__name__, 'skipped:', e)

# curated identities (shell LLCs, sites without data-center wording); evidence goes into note
ALIASES = [(a['state'], re.compile(a['name_regex'], re.I), a['operator'], a['evidence'])
           for a in csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aliases.csv')))]
for r in rows:
    for st, rx, op, ev in ALIASES:
        if r['state'] == st and rx.search(r['facility_name'] or ''):
            r['operator'], r['tier'] = op, 'curated'
            r['note'] = (r['note'] + '; ' if r['note'] else '') + 'identity: ' + ev
HEADLINE = HEADLINE | {'curated'}

with open(f'{OUT}/long.csv', 'w', newline='') as fo:
    w = csv.DictWriter(fo, COLS); w.writeheader(); w.writerows(rows)

# ---------- best view: state source beats NEI for the same state/year/pollutant group ----------
STATE_SRC = {'TX': 'TCEQ', 'VA': 'VA DEQ', 'CA': 'CARB', 'PA': 'PA DEP', 'AZ': 'Maricopa', 'OR': 'Oregon DEQ'}
def group(p): return 'HAP' if p in CAS.values() or p == 'DIESEL_PM' or p.startswith('OTHER:') else p
have = {(r['state'], str(r['year']), group(r['pollutant'])) for r in rows if not r['source'].startswith('EPA NEI')}
best = [r for r in rows if r['tier'] in HEADLINE and not r['pollutant'].startswith('GHG:')
        and (not r['source'].startswith('EPA NEI') or (r['state'], str(r['year']), group(r['pollutant'])) not in have)
        and not (r['state'] == 'CA' and r['source'].startswith('EPA NEI'))]  # CARB is the CA source of record
# QA: flag values (wording: check, not error; some are real step changes) >= 10 t that are >= 20x the same facility+pollutant's median in other years (likely unit errors).
# Flag only; reported values are never changed.
import statistics
series = collections.defaultdict(list)
for r in best: series[(r['facility_id'], r['pollutant'])].append(r)
for k, rs in series.items():
    for r in rs:
        others = [o['tons'] for o in rs if o is not r and o['tons'] > 0]
        if len(others) >= 1 and r['tons'] >= 10 and r['tons'] >= 20 * statistics.median(others):
            r['qa_flag'] = f"check (possible unit error): {r['tons']:.1f} t vs median {statistics.median(others):.2f} t in other years"
print('qa outliers flagged', sum(1 for r in best if r['qa_flag']))
with open(f'{OUT}/best.csv', 'w', newline='') as fo:
    w = csv.DictWriter(fo, COLS); w.writeheader(); w.writerows(best)

cov = collections.defaultdict(lambda: [set(), 0.0])
for r in best:
    k = (r['state'], str(r['year']), r['source'].split(' (')[0])
    cov[k][0].add(r['facility_id'])
    if r['pollutant'] == 'NOX' and not r['qa_flag']: cov[k][1] += r['tons']
with open(f'{OUT}/coverage.csv', 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['state', 'year', 'source', 'facilities', 'nox_tons_excl_qa_flagged'])
    for k in sorted(cov): w.writerow([*k, len(cov[k][0]), round(cov[k][1], 2)])
print('long', len(rows), 'best', len(best), '->', OUT)
