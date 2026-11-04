"""Oregon DEQ statewide air toxics emissions inventories (2016, 2020): HAPs + diesel PM, lb/yr."""
import urllib.request, os
OUT = '/srv/airtox/nei/raw_state/or'; os.makedirs(OUT, exist_ok=True)
for name, u in (('or_atei_2016.xlsx', 'https://www.oregon.gov/deq/FilterDocs/caoemissions2016.XLSX'),
                ('or_atei_2020.xlsx', 'https://www.oregon.gov/deq/aq/Documents/2020ATEI-Emissions.xlsx')):
    b = urllib.request.urlopen(u, timeout=180).read(); open(f'{OUT}/{name}', 'wb').write(b); print(name, len(b))
