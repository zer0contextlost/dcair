"""Write a plain-English summary of dcair v1 best.csv to /srv/airtox/nei/derived/v1/SUMMARY.md."""
import csv, collections
OUT = '/srv/airtox/nei/derived/v1'
rows = [r for r in csv.DictReader(open(f'{OUT}/best.csv')) if not r['qa_flag']]
for r in rows: r['tons'] = float(r['tons'])

src = lambda r: r['source'].split(' (')[0]
by = collections.defaultdict(lambda: collections.defaultdict(lambda: [set(), 0.0, 0.0, 0.0]))
has = collections.defaultdict(set)
for r in rows: has[(r['state'], src(r))].add(r['pollutant'])
for r in rows:
    k = by[(r['state'], src(r))][r['year']]
    k[0].add(r['facility_id'])
    if r['pollutant'] == 'NOX': k[1] += r['tons']
    if r['pollutant'] == 'PM25': k[2] += r['tons']
    if r['pollutant'] in ('FORMALDEHYDE',): k[3] += r['tons']

L = ['# dcair v1 summary', '',
     'Reported annual emissions from data centers, by state source. Tons per year as reported (emission-factor',
     'estimates). QA-flagged values excluded. Each state is its own series; sources and coverage differ.', '']
L += ['## Latest year per state source', '',
      '| state | source | year | facilities | NOx t | PM2.5 t | formaldehyde t |', '|---|---|---|---|---|---|---|']
latest = []
for (st, s), ys in by.items():
    y = max(ys, key=int); f, nox, pm, fo = ys[y]
    latest.append((nox, st, s, y, len(f), pm, fo))
for nox, st, s, y, n, pm, fo in sorted(latest, reverse=True):
    if nox < 1 and n < 3: continue
    h = has[(st, s)]
    f = lambda v, p, d: f'{v:,.{d}f}' if p in h else 'n/a'
    L.append(f"| {st} | {s} | {y} | {n} | {f(nox, 'NOX', 1)} | {f(pm, 'PM25', 1)} | {f(fo, 'FORMALDEHYDE', 3)} |")

L += ['', '## Multi-year state sources (NOx tons, facilities)', '']
for key in sorted(by, key=lambda k: -max(v[1] for v in by[k].values())):
    st, s = key
    if s.startswith('EPA NEI') or len(by[key]) < 3: continue
    ys = by[key]
    L.append(f'- **{st} {s}**: ' + ', '.join(f'{y} {ys[y][1]:,.0f} t ({len(ys[y][0])})' for y in sorted(ys, key=int)))

top = collections.defaultdict(float); meta = {}
for r in rows:
    if r['pollutant'] == 'NOX':
        k = (r['state'], r['facility_id'], r['year']); top[k] += r['tons']
        meta[k] = (r['facility_name'], r['operator'], src(r))
L += ['', '## Largest single facility-years (NOx)', '', '| state | year | facility | operator | NOx t | source |', '|---|---|---|---|---|---|']
for k, v in sorted(top.items(), key=lambda x: -x[1])[:20]:
    n, op, s = meta[k]
    L.append(f'| {k[0]} | {k[2]} | {n[:50]} | {op} | {v:,.1f} | {s} |')

ops = collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    if r['pollutant'] == 'NOX' and r['operator']:
        ops[r['operator']][(r['state'], r['year'])] += r['tons']
L += ['', '## Operators (NOx, latest year per state, matched by name only)', '']
for op, d in sorted(ops.items(), key=lambda x: -sum(x[1].values())):
    last = {}
    for (st, y), v in d.items():
        if st not in last or int(y) > int(last[st][0]): last[st] = (y, v)
    L.append(f'- {op}: ' + ', '.join(f'{st} {y} {v:,.1f} t' for st, (y, v) in sorted(last.items(), key=lambda x: -x[1][1])))
allb = list(csv.DictReader(open(f'{OUT}/best.csv')))
noxs = collections.defaultdict(set); rep = set(); eq = set()
for r in allb:
    if r['pollutant'] != 'NOX': continue
    k = (r['facility_id'], src(r)); noxs[k].add(r['year'])
    if r['pattern_flag'].startswith('repeat'): rep.add(k)
    if 'co_equals_nox' in r['pattern_flag']: eq.add((r['facility_id'], r['year'], r['facility_name']))
multi = {k for k, v in noxs.items() if len(v) >= 3}
L += ['', '## Reporting patterns (pattern_flag)', '',
      f'- {len(rep & multi)} of {len(multi)} facility NOx series with 3+ years repeat an identical nonzero value in 3+ years '
      f'({", ".join(f"{s} {n}" for s, n in collections.Counter(k[1] for k in rep & multi).most_common())}).',
      f'- CO exactly equals NOx in {len(eq)} facility-years: ' + ', '.join(sorted({n for _, _, n in eq})) + '.']
open(f'{OUT}/SUMMARY.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:40]))
