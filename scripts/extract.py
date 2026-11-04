"""Stream NEI facility summaries; keep all VA rows + national data-center candidates.
Output: /srv/airtox/nei/derived/extract.csv (year column added, columns normalized)."""
import csv, io, re, sys, zipfile, glob, os
RAW = '/srv/airtox/nei/raw'
OUT = '/srv/airtox/nei/derived/extract.csv'
NAME = re.compile(r'data ?cent|datacent|\bdata\b|server|colo|cloud|hosting|digital realty|equinix|'
                  r'amazon|aws\b|vadata|microsoft|google|meta platforms|facebook|qts|cyrusone|vantage|'
                  r'coresite|cloudhq|sabey|iron mountain|stack infra|aligned|raging ?wire|ntt|switch,? ltd|'
                  r'compass datacenters|edgecore|corescale|yondr|stream data|rowan|apple|oracle|t5|dupont fabros|'
                  r'cologix|flexential|databank|h5|tierpoint|centersquare|evoque|digital bridge|quality technology', re.I)
KEEP = ['year','state','fips code','county','eis facility id','agency facility id','company name','site name',
        'primary naics code','primary naics description','facility source type','site latitude','site longitude',
        'address','city','zip code','pollutant code','pollutant desc','pollutant type(s)','total emissions',
        'emissions uom','data set']
csv.field_size_limit(10**8)
with open(OUT + '.tmp', 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(KEEP + ['why'])
    for z in sorted(glob.glob(f'{RAW}/*_NEI_Facility_summary.zip')):
        year = os.path.basename(z)[:4]
        zf = zipfile.ZipFile(z)
        name = [n for n in zf.namelist() if n.endswith('.csv')][0]
        n = k = 0
        with zf.open(name) as fb:
            r = csv.reader(io.TextIOWrapper(fb, encoding='latin-1', newline=''))
            hdr = [h.strip().lower() for h in next(r)]
            ix = {h: i for i, h in enumerate(hdr)}
            for row in r:
                n += 1
                st = row[ix['state']]; naics = row[ix['primary naics code']]
                nm = row[ix['site name']] + ' | ' + row[ix['company name']]
                why = []
                if st == 'VA': why.append('va')
                if naics.startswith('5182'): why.append('naics')
                if NAME.search(nm): why.append('name')
                if not why: continue
                # national name-only hits: keep only non-manufacturing-ish to limit size
                if why == ['name'] and not naics.startswith(('51', '54', '22', '53', '56', '92', '')):
                    continue
                k += 1
                w.writerow([year] + [row[ix[c]] if c in ix else '' for c in KEEP[1:]] + ['+'.join(why)])
        print(year, n, 'rows scanned,', k, 'kept', flush=True)
os.replace(OUT + '.tmp', OUT)
print('done')
