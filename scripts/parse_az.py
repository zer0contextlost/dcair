"""Parse saved Maricopa County AQ Data Viewer emissions-inventory detail pages into build.py rows."""
import glob, json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))

DIR = '/srv/airtox/nei/raw_state/az'
TOTAL = re.compile(r'^\s*([-\d.,Ee+]+)\s+(POUNDS|TONS)\s*$')
NUM = re.compile(r'^\s*[-\d.,Ee+]+\s*$')

def parse_page(text):
    head = dict(re.findall(r'^(Facility ID|Facility Name|Emissions Inventory ID|Reporting Year|Reporting State|Content Type):\s+(.+)$',
                           text, re.M))
    out, name, on = [], None, False
    for line in text.splitlines():
        if line.startswith('Pollutant\tFugitive'):
            on = True; name = None; continue
        if not on: continue
        if line.startswith('___') or not line.strip(): continue
        m = TOTAL.match(line)
        if m and name:
            v = float(m.group(1).replace(',', ''))
            out.append((name, v / 2000 if m.group(2) == 'POUNDS' else v)); name = None
        elif not NUM.match(line) and 'Emissions Reported' not in line:
            name = line.strip()
    return head, out

AZ_MAP = {'NOx': 'NOX', 'CO': 'CO', 'SO2': 'SO2', 'VOC': 'VOC', 'PM2.5': 'PM25', 'PM10': 'PM10', 'PM': 'PM',
          'Ammonia': 'NH3', 'Butadiene,': '1,3-BUTADIENE'}
def az_pol(pol):
    from common import canon
    first = pol.split(' ')[0]
    return AZ_MAP.get(first) or canon('', pol)

def parse_all():
    from common import canon, operator, tiers
    jobs = {j['ei']: j for j in json.load(open(f'{DIR}/jobs.json'))}
    for p in sorted(glob.glob(f'{DIR}/ei/EI*.txt')):
        head, pols = parse_page(open(p).read())
        j = jobs.get(head.get('Emissions Inventory ID', ''), {})
        name = head.get('Facility Name', j.get('name', ''))
        for pol, tons in pols:
            short = re.split(r' - | \(', pol)[0]
            yield dict(state='AZ', source='Maricopa County AQD annual emissions inventory (AQ Data Viewer)',
                       source_url='https://aqdata.maricopa.gov/disclaimer.jsf', year=head.get('Reporting Year', j.get('year', '')),
                       facility_id=f"AZ-MC-{head.get('Facility ID', j.get('fid', ''))}", facility_name=name, owner=j.get('owner', ''),
                       operator=operator(name, j.get('owner', '')), tier=tiers(name, j.get('owner', '')) or 'name', county='Maricopa',
                       pollutant=az_pol(pol),
                       pollutant_original=pol, tons=tons,
                       note=f"{head.get('Emissions Inventory ID')} {head.get('Content Type', '')} {head.get('Reporting State', '')} {j.get('program', '')}".strip())

if __name__ == '__main__':
    for p in sorted(glob.glob(f'{DIR}/ei/EI*.txt'))[:1]:
        h, pols = parse_page(open(p).read()); print(h); [print(' ', x) for x in pols[:12]]; print(len(pols))
