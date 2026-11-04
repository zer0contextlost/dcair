"""Shared identity + pollutant helpers for dcair builds."""
import re

# ---------- identity ----------
DC_NAME = re.compile(
    r'data ?cent|datacent|data ?ctr|\bdc\d|vadata|amazon data serv|amazon web serv|digital realty|equinix|cyrusone|'
    r'\bqts\b|vantage data|coresite|cloudhq|sabey|iron mountain data|raging ?wire|ntt global|ntt data|compass datacenters|'
    r'edgeconnex|stack infra|aligned (data|energy)|aligned\.ai|supernap|switch,? ltd|databank|flexential|cologix|tierpoint|'
    r'h5 data|novva|edgecore|yondr|digital utility|element critical|evocative|latisys|cyxtera|dupont fabros|'
    r'centersquare|sentinel (data|ashburn)|stream data|prime data|powerhouse data|corescale|web hosting|hosting com', re.I)
CRYPTO = re.compile(r'mining|bitcoin|crypto|blockchain|hash|tecfusions|digital mining|\bbtc\b', re.I)
OPERATORS = [
    ('Amazon', r'amazon|vadata|aws\b'), ('Microsoft', r'microsoft'), ('Google', r'google|sharka|montauk innov|magellan enter|design,? llc'),
    ('Meta', r'meta platforms|facebook|\bmeta\b|winner llc'), ('Apple', r'apple'), ('Digital Realty', r'digital realty|dupont fabros|digital loudoun|2055 east technology'),
    ('Equinix', r'equinix'), ('CyrusOne', r'cyrusone'), ('QTS', r'\bqts\b'), ('Vantage', r'vantage data'), ('NTT', r'\bntt\b|raging ?wire'),
    ('Iron Mountain', r'iron mountain|\bio data'), ('CoreSite', r'coresite'), ('Aligned', r'aligned'), ('Compass', r'compass datacenters'),
    ('Stack', r'stack infra|\bstack\b'), ('EdgeConneX', r'edgeconnex'), ('Sabey', r'sabey'), ('CloudHQ', r'cloudhq'), ('H5', r'\bh5\b'),
    ('TierPoint', r'tierpoint'), ('Switch', r'switch,? ltd|supernap'), ('DataBank', r'databank'), ('Flexential', r'flexential'),
    ('Cologix', r'cologix'), ('Cyxtera', r'cyxtera'), ('Oracle', r'oracle'), ('Yahoo', r'yahoo|oath'), ('LinkedIn', r'linkedin'),
]
OPS = [(n, re.compile(p, re.I)) for n, p in OPERATORS]

def operator(*names):
    s = ' | '.join(n for n in names if n)
    for n, p in OPS:
        if p.search(s): return n
    return ''

def tiers(name, owner='', code_says_dc=False, state_flag=False):
    s = f'{name} | {owner}'
    if CRYPTO.search(s): return 'crypto'
    if state_flag: return 'state_flag'
    named = bool(DC_NAME.search(s))
    if code_says_dc and named: return 'code+name'
    if named: return 'name'
    if code_says_dc: return 'code_only'
    return ''

HEADLINE = {'state_flag', 'code+name', 'name'}

# ---------- pollutants ----------
CAS = {'50000': 'FORMALDEHYDE', '50-00-0': 'FORMALDEHYDE', '71432': 'BENZENE', '71-43-2': 'BENZENE',
       '75070': 'ACETALDEHYDE', '75-07-0': 'ACETALDEHYDE', '107028': 'ACROLEIN', '107-02-8': 'ACROLEIN',
       '106990': '1,3-BUTADIENE', '106-99-0': '1,3-BUTADIENE'}
def canon(code='', name=''):
    c = (code or '').strip().upper(); n = (name or '').strip().lower()
    if c in CAS: return CAS[c]
    if c in ('NOX',) or n.startswith('nitrogen ox'): return 'NOX'
    if c in ('CO',) or n == 'carbon monoxide': return 'CO'
    if c in ('VOC', 'ROG') or n.startswith('volatile organic'): return 'VOC'
    if c in ('SO2', 'SOX') or n.startswith(('sulfur diox', 'sulfur ox')): return 'SO2'
    if c in ('PM25-PRI', 'PM 2.5', 'PM2.5') or n in ('particulate matter < 2.5 microns', 'particulate matter 2.5'): return 'PM25'
    if c in ('PM10-PRI', 'PM 10', 'PM10') or n in ('particulate matter < 10 microns', 'particulate matter 10'): return 'PM10'
    if c in ('NH3',) or n == 'ammonia': return 'NH3'
    if n in ('formaldehyde',): return 'FORMALDEHYDE'
    if n in ('benzene',): return 'BENZENE'
    if n in ('acetaldehyde',): return 'ACETALDEHYDE'
    if n in ('acrolein',): return 'ACROLEIN'
    if n.startswith('diesel p') or c in ('DIESEL-PM10', 'DIESEL-PM25', '200'): return 'DIESEL_PM'
    if n.startswith(('carbon dioxide', 'methane', 'nitrous oxide')) or c in ('CO2', 'CH4', 'N2O'): return 'GHG:' + (c or n)
    return 'OTHER:' + (name or code).strip()

