#!/bin/sh
# EPA NEI facility summaries 2012-2023 (~350 MB zipped). Then run extract.py.
set -e
D=/srv/airtox/nei/raw; mkdir -p $D; cd $D
for y in $(seq 2012 2023); do
  [ -f ${y}_NEI_Facility_summary.zip ] || curl -sf -o ${y}_NEI_Facility_summary.zip "https://gaftp.epa.gov/air/nei/nei_facility_summaries/${y}_NEI_Facility_summary.zip"
done
sha256sum *.zip > SHA256SUMS
