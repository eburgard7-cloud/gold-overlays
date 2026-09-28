# rogue_applegate -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-123.65, 42.15, -122.85, 42.7)`
Built: 2026-09-28

## Output files
- `rogue_applegate_onx.kml` / `rogue_applegate_onx.gpx` -- 2431 features, 1094 KB KML / 1195 KB GPX
  - layers: Historical workings (USMIN), Mine & prospect sites (MILO/MRDS, gold), Active mining claims (BLM MLRS), Past claim density (closed placer, 500m hex), Open ground to sample

## Layer counts
- My claims & public sites: 0
- USMIN historical workings: 754 (dropped types: borrow pit, gravel pit, open pit mine or quarry, quarry)
- MILO-4 gold sites: 694
- MRDS gold sites (raw / kept after MILO dedup): 586 / 205
- Active BLM claims (Not Closed): 751
- Closed placer claims fetched: 66 (unmatched to any 500m hex: 0)
- Land status polygons fetched: BLM=1, USFS=1
- NHD service reachable for this area: True
- Open ground to sample: 25 waypoints

## My claims & public sites (reference table)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|
| 42.4962 | -123.6317 | 3 | 2020s:3 |
| 42.6479 | -123.2393 | 3 | 2020s:3 |

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|
| OPEN-rogue_applegate-01 | 42.35449 | -123.21976 | placer (heuristic: surface workings) | False |
| OPEN-rogue_applegate-02 | 42.35467 | -123.21870 | placer (heuristic: surface workings) | False |
| OPEN-rogue_applegate-03 | 42.34723 | -123.21782 | placer (heuristic: surface workings) | False |
| OPEN-rogue_applegate-04 | 42.34677 | -123.21927 | placer (heuristic: surface workings) | True |
| OPEN-rogue_applegate-05 | 42.55151 | -123.62536 | placer | False |
| OPEN-rogue_applegate-06 | 42.62623 | -123.59703 | placer | False |
| OPEN-rogue_applegate-07 | 42.65751 | -123.52234 | placer | False |
| OPEN-rogue_applegate-08 | 42.57179 | -123.59870 | placer | False |
| OPEN-rogue_applegate-09 | 42.53956 | -123.50647 | placer | False |
| OPEN-rogue_applegate-10 | 42.36624 | -123.17618 | placer (heuristic: surface workings) | False |

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section; every claim polygon is labeled
  `[APPROX quarter-section]` in its name and description.
- 'Closed-claim density' decade buckets use the MLRS `Created` (database record) date as a proxy for
  located date -- the public feature service does not expose a true located/last-action date.
- 'Open ground' ranking's final tiebreaker is distance-to-stream, not distance-to-road (no road
  dataset was fetched in this build).
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes);
  full deposit-type/production detail lives on the per-site page linked in each description.

## DOGAMI Bulletin 61 notes


**Klamath Mountains regional placer history** (Bulletin 61 p. 167-169) covers this
area's context directly: Oregon's first documented placer gold find was 1850 on the
Illinois River near Josephine Creek; the district-defining 1851 rush was **near
Jacksonville**. Richer placers named include **Sterling Creek** (>$3,000,000,
fed the 23-mile Sterling ditch off the **Little Applegate River**, built 1877),
Althouse Creek, Sailors Diggings, Rich Gulch (Jacksonville) and **Rich Gulch at
Galice**. Placers are also named on Sucker, Josephine, Briggs, **Galice**, **Grave
Creek and its tributaries**, Foots, Sardine, Galls, Forest, Poorman, Humbug, Ferris
Gulch, Powell, and Palmer Creeks. The **Old Channel placer mine near Galice** is
called one of the largest hydraulic operations in the U.S. (peak crew 75 in 1935).
Dredging is documented on Foots Creek (1903, one of Oregon's first dredges, later
electrified from the Gold Hill hydro plant), and on the **Rogue River near Gold
Hill** and near the town of Rogue River, and on the **Applegate River near Ruch**
(p. 169).

**Galice area / Silver Peak lode context** (p. 208-214) documents the Big Yank lode
trend from the Almeda mine (Galice) north to the Silver Peak mine near Canyonville
-- outside this box but geologically related.

**Caveat:** Bulletin 61 does not give a single consolidated production figure for
"the Rogue/Applegate district" as a unit -- figures above are per-creek/per-mine as
cited. Gold Hill waysides and the Grave Creek confluence area are covered by the
general narrative above rather than a dedicated sub-section.

**OHMI (Jackson County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-jackson.aspx -- **(Josephine County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-josephine.aspx

