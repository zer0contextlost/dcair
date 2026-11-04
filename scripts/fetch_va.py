"""VA DEQ ArcGIS: Air Sites (294, data-center flag) + AIR SITES EMISSIONS TPY (292, current year only). Dated snapshot."""
import json, urllib.request, urllib.parse, datetime, os
B = 'https://gisdata.deq.virginia.gov/arcgis/rest/services/public/EDMA/MapServer'
OUT = f'/srv/airtox/nei/raw_state/va/{datetime.date.today()}'
os.makedirs(OUT, exist_ok=True)
def pull(layer, where='1=1'):
    rows, off = [], 0
    while True:
        q = urllib.parse.urlencode({'where': where, 'outFields': '*', 'f': 'json', 'returnGeometry': 'true',
                                    'outSR': 4326, 'resultOffset': off, 'resultRecordCount': 2000})
        d = json.load(urllib.request.urlopen(f'{B}/{layer}/query?{q}', timeout=120))
        f = d.get('features', []); rows += f; off += len(f)
        if not f or not d.get('exceededTransferLimit'): return rows
for layer, name in ((294, 'air_sites'), (292, 'emissions_tpy')):
    r = pull(layer); json.dump(r, open(f'{OUT}/{name}.json', 'w')); print(name, len(r))
