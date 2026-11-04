# Research notes (2026-11-04)

How we got here, what each state publishes, and what we checked ourselves vs. took from agency pages or
secondary reporting.

## 1. Can NEI give a data-center emissions trend? No.

Test state: Virginia. Reference list: 183 unique DEQ registration numbers from the Public Evidence Project's
index of DEQ data-center air permits (194 rows). In NEI, Virginia's agency facility ID is the 5-digit DEQ
registration number, so the join is exact.

| NEI year | permitted data centers present | NOx t |
|---|---|---|
| 2012-2014 | 1 | 2-17 |
| 2015-2021 | 3 | 41-85 |
| 2022 | 28 | 362 |
| 2023 | 28 | 394 |

- 155 of 183 permitted registrations never appear in any NEI year 2012-2023.
- The 2022 jump is 25 sites appearing at once, including one permitted since 2003: a reporting change.
- For comparison, DEQ's own 2024 data has 148 data-center sites reporting 796 t NOx.

NAICS 518210 facilities in NEI, 12 large markets, 2017 -> 2023: VA 2 -> 23, TX 1 -> 4, GA 0 -> 1, OH 0 -> 4,
AZ 0 (all years), OR 0 -> 19, WA 0 (all years), NV 2 -> 4, CA 91 -> 118, IL 12 -> 11, IA 2 -> 4, PA 1 -> 6.
NAICS alone undercounts: Virginia data centers also use 541513.

## 2. What states publish

"Verified" = we downloaded the data and found data centers in it. Other entries come from agency pages and
rules as read on 2026-11-04 and were not re-verified row by row.

| State | Public facility-level actuals? | Notes |
|---|---|---|
| VA | yes, 2024 only (verified) | DEQ ArcGIS: Air Sites layer has a data-center flag (199 sites, covering all 183 permit-index registrations); emissions layer is current year only. VCU's 2015-2024 series came from DEQ directly. Emissions statements required at 25 tpy VOC/NOx in emissions control areas (9VAC5-20-160); permits also require annual emissions data. Generator run logs: on site, records request only. |
| CA | yes (CARB verified) | CARB facility tool by SIC, 2000-2024 in our pull, criteria tons, no PM2.5. Bay Area AQMD toxic air contaminant inventory 2012-2024 covers all permitted facilities since reporting year 2020 (diesel PM only for engines). Per-engine hours reported at permit renewal; the spreadsheet has been released by records request, not posted. Other districts not checked. |
| PA | yes (export verified) | DEP 25-year site-level inventory (Power BI) 1999-2025; synthetic minors report since 2020. 23 NAICS-518210 facilities in DEP's facility list, 8 with emission rows. DEP Data Center Permit Tracker lists permits, not emissions. Allegheny County separate. |
| AZ | yes, Maricopa (scraped) | Annual inventories from non-Title V permittees on request (Rule 100 §505), criteria + HAPs per engine, 2001-2025. No bulk export. Other counties/ADEQ not checked. |
| OR | partly (2020 toxics file verified) | Statewide air toxics inventories 2016/2020. Standard ACDP annual reports 2013-2023 (scanned PDFs) include monthly hours per generator split into maintenance, emergency and demand response. Post-2024 reports in DEQ's online records portal (not checked). DEQ counts 39 campuses and 2,482 large generators (2026). |
| TX | partial (verified) | TCEQ STARS site summaries 2010-2024; only sites over 30 TAC 101.10 thresholds; emergency generators under PBR 106.511 need no registration. Abilene/Stargate absent from 2024. |
| OH | partial | EIS archive 2000-2023 covers Title V and synthetic minors; 4 data centers in 2023 (not yet in this dataset beyond NEI). |
| IA | partial | Title V actuals published (Microsoft West Des Moines campuses); minor sources report every 3 years, not published. |
| GA | majors only | Public point-source files cover majors; one data center (QTS Metro). No state list of data-center permits. |
| WA | no (records request) | Ecology approval orders require annual reports with monthly emissions, hours per engine and every engine start with its purpose; not posted. Public point-source file has no data centers. |
| IL | no (records request) | 35 IAC 254 requires annual emission reports from all permitted sources; database not published. |
| NV | no (records request) | Clark County and NDEP collect annual inventories; only a 2017 NDEP summary is public. Washoe County dropped annual reporting in 2025. |

## 3. Known limits of v1

- Reported values are emission-factor estimates. Pollutants and reporting-year definitions differ by state.
- Hyperscaler sites often sit under shell LLCs. We added the ones with documented evidence (`aliases.csv`);
  the rest are missing or unattributed. Google, Apple and Meta are not found by name in Maricopa County.
- Oregon criteria pollutants come from NEI; the state annual reports are not parsed yet.
- Pennsylvania's export was done by hand and isn't scripted.
- Values flagged by `qa_flag` are kept as reported.

## 4. Next

Records requests (Virginia 2015-2023, Washington Ecology annual reports, Illinois annual emission reports),
OCR of Oregon annual reports (which include generator hours), Ohio EIS files, other California districts.
