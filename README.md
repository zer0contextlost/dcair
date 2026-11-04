# dcair: reported air emissions from US data centers

Facility-level air emissions that US data centers report to state and local air agencies, compiled from
every public source we could find, with EPA's National Emissions Inventory (NEI) filling the gaps.
Nearly all of it comes from on-site backup generators (mostly diesel, some gas turbines). Version 1, November 2026.

Data: [huggingface.co/datasets/zer0contextlost/dcair](https://huggingface.co/datasets/zer0contextlost/dcair) · Code and notes: this repo.

## Why this exists

No federal program tracks data-center air pollution as a category. Data centers don't report to TRI,
grid electricity isn't counted under GHGRP, and NEI only includes the sites each state chooses to submit.
In Virginia, the state with the most data centers, **only 28 of 183 DEQ-permitted data centers appear in any
NEI year from 2012 to 2023**. Twenty-five of them show up at once in 2022, including one permitted since
2003, because Virginia started sending them, not because they were built then. Building a trend from
NEI mostly measures reporting changes.

Several state and county agencies do publish facility-level actual emissions that include smaller
(minor and synthetic-minor) sources. This dataset puts those together.

## What the numbers are

- What the facility or agency **reported**: annual estimates from fuel use or run hours times emission
  factors. Not measurements, and not our estimates.
- Each state is **its own series**. Sources differ in which sites must report, which pollutants are
  included and how the reporting year is defined. Don't add states into a national total or compare
  them as if they were measured the same way.
- Coverage grows over time in most sources, so rising totals partly reflect more sites entering the
  data. Facility counts are shown next to every total.
- This covers on-site emissions only. Emissions from the power plants supplying data centers are a
  separate (and larger) question; see Hernandez-Cortes, Meng & Weber (2026) and Muller (2026).

## Latest year per source

<!-- from SUMMARY.md; NOx/PM2.5/formaldehyde in short tons per year, QA-flagged values excluded -->

| state | source | year | facilities | NOx t | PM2.5 t |
|---|---|---|---|---|---|
| VA | Virginia DEQ air sites emissions | 2024 | 148 | 796.2 | 38.4 |
| AZ | Maricopa County AQD annual emissions inventory | 2025 | 12 | 213.9 | 4.3 |
| CO | EPA NEI | 2023 | 15 | 136.0 | 10.6 |
| OR | EPA NEI | 2023 | 14 | 129.9 | 8.6 |
| TX | TCEQ point source emissions inventory | 2024 | 7 | 110.9 | 2.0 |
| IL | EPA NEI | 2023 | 13 | 83.9 | 3.3 |
| CA | CARB facility criteria emissions | 2024 | 26 | 40.9 | n/a |
| UT | EPA NEI | 2023 | 4 | 32.1 | 4.4 |
| PA | PA DEP site-level emission inventory | 2025 | 5 | 11.7 | 0.2 |

Multi-year state series (NOx tons, facilities in parentheses):
- **Maricopa County, AZ:** 2016 15 t (7), 2019 74 t (6), 2021 95 t (10), 2023 185 t (15), 2025 214 t (12)
- **Texas:** 2021 45 t (3), 2022 15 t (5), 2023 28 t (5), 2024 111 t (7)
- **California:** 2016 4 t (6), 2020 12 t (12), 2024 41 t (26)

Largest single facility-years: Amazon IAD-132/133, VA (77.6 t NOx, 2023 NEI); Iron Mountain, Manassas VA
(74.0 t, 2024); Microsoft, Bexar County TX (66.8 t, 2024); CyrusOne Chandler, AZ (63.9 t, 2023);
Microsoft Broadway Rd, AZ (59.4 t, 2025). Full tables in [SUMMARY.md](SUMMARY.md).

## Sources

| State | Source | Years | Covers | Pollutants | Gaps |
|---|---|---|---|---|---|
| VA | DEQ "Air Sites" + "Air Sites Emissions TPY" (ArcGIS EDMA layers 294/292) | 2024 | 148 of 199 sites DEQ flags as data centers, incl. minor sources | NOx CO VOC SO2 PM PM10 PM2.5, some HAPs | DEQ publishes only the current year; earlier years need a records request |
| CA | CARB facility emissions (CEIDARS), SIC 7374, statewide | 2000-2024 | permitted facilities reported by air districts | NOx CO ROG (as VOC) SOx PM PM10 | no PM2.5; SIC 7374 includes offices, so only name-confirmed sites are headline |
| TX | TCEQ point source emissions inventory, site summaries | 2010-2024 | sites over 30 TAC 101.10 thresholds | NOx CO VOC SO2 PM PM10 PM2.5 Pb | most data centers fall under thresholds; generators under PBR 106.511 need no registration |
| PA | DEP 25-year site-level emission inventory (Power BI), NAICS 518210 | 2017-2025 in our export | DEP-notified sources incl. synthetic minors (since 2020) | criteria, GHGs, a few HAPs | one manual export (2026-11-04), not yet scripted; non-518210 data centers missing |
| AZ | Maricopa County AQD annual emissions inventory (AQ Data Viewer) | 2001-2025 (one site before 2015) | non-Title V permittees, inventory requested yearly | criteria + HAP list, per engine | scraped (no bulk export); Google/Apple/Meta not found under their own names; viewer "total" tons include CO2 |
| OR | DEQ Air Toxics Emissions Inventory | 2016, 2020 | Title V + Simple/Standard ACDP | HAPs + diesel PM | criteria pollutants come from NEI; per-site annual reports with generator hours (2013-2023) are scanned PDFs, not yet parsed |
| all | EPA NEI facility summaries | 2012-2023 | whatever each state submitted | criteria + HAPs | misses most data centers |

In `best.csv` a state source replaces NEI for the same state, year and pollutant group (CA always uses CARB).

Not public, needs records requests: Virginia before 2024, Washington Ecology (annual reports incl. every
engine start), Illinois EPA annual emission reports, Clark County and NDEP (NV), Georgia minor sources.
Details per state in [NOTES.md](NOTES.md).

## Files

| file | rows | what |
|---|---|---|
| `data/best.csv` | 21,627 | headline view: confirmed data centers, one source per state-year-pollutant group |
| `data/long.csv` | 69,022 | every row from every source and identity tier, incl. code-only candidates and crypto mines |
| `data/coverage.csv` | | facilities and NOx by state, year and source |
| `aliases.csv` | | hand-checked identities (shell LLCs etc.) with evidence |

Columns: `state, source, source_url, year, facility_id, facility_name, owner, operator, tier, county, city,
lat, lon, naics_or_sic, pollutant, pollutant_original, tons, note, qa_flag, pattern_flag` (`pattern_flag` in `best.csv`). `tons` = short tons/year.
Pollutants are normalized (`NOX, CO, VOC, SO2, PM25, PM10, PM, NH3, FORMALDEHYDE, BENZENE, ACETALDEHYDE,
ACROLEIN, 1,3-BUTADIENE, DIESEL_PM`); everything else is `OTHER:<name as reported>` or `GHG:<name>`.

## Identity tiers (`tier`)

- `state_flag`: the agency marks the site as a data center (Virginia's `PLA_DATA_CENTER_YN`). Virginia NEI
  rows get this tier by registration-number join; other Virginia NEI rows are not headline.
- `code+name`: industry code (NAICS 5182xx / SIC 7374/7376) and a data-center name or known operator.
- `name`: data-center name or known operator under another industry code (NAICS 541513, 531120, etc.).
- `curated`: listed in `aliases.csv` with evidence (e.g. Sharka LLC = Google Midlothian, Winner LLC = Meta Fort Worth).
- `code_only`: industry code only. In `long.csv`, not headline (many are offices).
- `crypto`: crypto-mining sites coded 518210. In `long.csv`, kept separate.

`operator` is matched from names only; most hyperscaler shell entities are not matched.

## QA

`qa_flag` marks values of 10 t or more that are at least 20x the same facility's median for that pollutant
in other years (e.g. Evocative, MA: 0.4 t NOx in 2022, 90.6 t in 2023). Values are never changed.
Flagged rows are excluded from the summary totals. Some flags may be real step changes.

`pattern_flag` marks two reporting patterns. These rows are kept and counted; the flag says how much to trust
year-to-year change:
- `repeat`: the same nonzero value for a facility, pollutant and source in 3 or more years. **45 of the 112
  facility NOx series with 3+ years contain a repeated value; 39 of those are NEI series** (e.g. Equinix Denver
  VDC I, 35.67 t every year 2014-2021). A flat line usually means the number was carried forward, not re-estimated.
- `co_equals_nox`: CO exactly equal to NOx in the same facility-year. All 9 cases are one Maricopa site (APS
  Aligned Energy Data Center, 2016-2025), which points to one emission factor applied to both pollutants.

## Reproduce

```
scripts/fetch_nei.sh && python3 scripts/extract.py        # NEI 2012-2023, filtered
python3 scripts/fetch_va.py; python3 scripts/fetch_ca.py; python3 scripts/fetch_or.py; python3 scripts/fetch_tx.py
node scripts/az_list.js "%data cent%" ...  > list.txt     # Maricopa search (playwright), then az_detail.js
python3 scripts/build.py && python3 scripts/summarize.py
```
Paths are set to `/srv/airtox/nei`; edit `RAW` in the scripts. Pennsylvania's Power BI export was made by
hand. `scripts/va_test.py` reproduces the Virginia NEI coverage test (uses the Public Evidence Project permit CSV).

## Related work

- Public Evidence Project (publicevidence.org): 2020 NEI facilities coded 518210 and an index of Virginia DEQ
  data-center air permits (CC BY 4.0). We used their permit index for the Virginia NEI coverage test.
- Pitt, Suen & Plisko (2026), VCU ISEE, "Localized Air Pollution Impacts from Data Centers in Northern
  Virginia": dispersion modeling from DEQ-provided actual emissions 2015-2024.
- Hernandez-Cortes, Meng & Weber (2026), Energy Institute at Haas WP 363: grid-electricity emissions and
  siting of data centers; no on-site generator emissions.
- FracTracker Alliance national data-center map; datacenterpermits.org (PA/VA/TX permits); Sierra Club and
  Piedmont Environmental Council Virginia permit surveys.

## License and credit

Agency data from Virginia DEQ, CARB, TCEQ, Pennsylvania DEP, Maricopa County Air Quality Department,
Oregon DEQ and US EPA (public records). This compilation is CC BY 4.0; code is MIT.
Corrections and additions welcome via issues.
