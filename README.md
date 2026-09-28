# Oregon gold-prospecting overlays (onX-first, phone-usable)

Reproducible pipeline that builds real onX-format GPX overlays (one small
file per layer per area, matching onX's own export schema exactly) plus a
secondary KML export and a CalTopo GeoJSON bundle, for seven weekend-
prospecting areas around Eugene, OR, for Willamette Valley Miners (WVM) and
Bohemia Mine Owners Association (BMOA) members. Every coordinate in the
output either comes from a downloaded public dataset (USGS USMIN/MRDS,
DOGAMI MILO-4, BLM MLRS, BLM SMA, USGS NHD, DOGAMI lidar, TNM historical
topos) or from the verified reference table in `gold_overlays/config.py` --
nothing is estimated or hand-placed, and nothing is styled with a guessed
onX icon/color.

**GPX is the primary format** (real onX schema: `onx:icon`/`onx:color` on
waypoints, `onx:style`/`onx:weight`/`onx:color` on `Area`/`Line` routes) --
KML is a secondary export for onX Web Map, kept for polygon fills there.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
sudo apt-get install -y gdal-bin poppler-utils qpdf   # gdal_translate/ogr2ogr + PDF verification tools

python build.py --area all                            # 6 layers/area -> out/<area>/<area>_<n>_<layer>.gpx(+.kml) + caltopo_<area>.geojson
python build.py --area all --rasters --skip-vectors    # lidar GeoPDFs (with vector overlay + scale bar/north arrow/title) + historical topo PDFs
python build.py --validate-density                     # one-time closed-claim-density plausibility check (see below)
python refresh_claims.py                               # monthly: re-pull active claims, diff vs last run
```

## Areas

| area | coverage | bbox (minLon,minLat,maxLon,maxLat) |
|---|---|---|
| bohemia | Sharps/Brice/Martin/Quartz Creeks, Row River headwaters | -122.95, 43.45, -122.50, 43.78 |
| quartzville | Quartzville Creek (Green Peter Res. to Galena Creek), Canal Creek, Dry Gulch | -122.50, 44.48, -122.15, 44.68 |
| calapooia | upper Calapooia River | -122.55, 44.15, -122.28, 44.32 |
| lnf_santiam | Little North Santiam River | -122.62, 44.75, -122.40, 44.86 |
| cowcreek | Cow Creek byway (Glendale-Riddle), Dads Creek, Whitehorse Creek | -123.70, 42.68, -123.10, 42.98 |
| rogue_applegate | Rogue R. (Applegate confluence-Grave Creek), Gold Hill, Little Applegate | -123.65, 42.15, -122.85, 42.70 |
| sixes | Sixes River | -124.45, 42.75, -124.20, 42.88 |

## Layers (style guide)

One GPX (+ KML) per layer per area: `out/<area>/<area>_<n>_<layer>.gpx`.
Only **confirmed** onX icons/colors are ever written -- icons `Mineral Site` /
`Location`; colors yellow `rgba(255,255,0,1)`, red `rgba(255,51,0,1)`, black
`rgba(0,0,0,1)`. A layer file is only written if it has content for that area
(e.g. an area with no club claim has no `1_my_claims` file).

| layer | content | icon | color | style | meaning |
|---|---|---|---|---|---|
| `1_my_claims` | WVM/BMOA claims as filled Areas + a Mineral Site pin at each centroid | Mineral Site | yellow | solid | ours |
| `2_public` | Public gold-panning sites (points only -- see gap below) | Location | black* | -- | open to anyone |
| `3_other_claims` | Other active BLM claims, no pins | -- | red | dotted | don't dig here |
| `4_history` | Deduped historical workings (USMIN+MILO+MRDS, merged within 75m) | Mineral Site (placer/tailings/hydraulic) or Location (adit/shaft/pit/other) | black | -- | historical context |
| `5_scout` | Top-10 open-ground candidates | Location | red | -- | worth scouting |
| `6_access` | Claim-access route from club handbook directions | -- | black | dash | how to get there |

\* Public-site pins are **black**, not green: green is not in the confirmed
onX color set (see "Style testing" below), so per the spec's own fallback
rule ("use a confirmed [color]") black is used until green is confirmed.

### Style testing (`onx_samples/STYLE_RESULTS.md`)

`out/_test/onx_test.gpx` has 7 test
waypoints and 3 test routes: TEST 1/2 and TEST A/B/C use only confirmed
icons/colors (already used throughout this build); TEST 3-7 and the orange
Area test are **guesses** pending your phone import. Once you've imported it
and recorded what actually rendered, add `onx_samples/STYLE_RESULTS.md` with
one line per confirmed entry containing the literal word `CONFIRMED` (e.g.
`TEST 4 Camp guess-green -> CONFIRMED renders as green tent icon`) --
`gold_overlays/onx_style.py` will pick it up automatically on the next
`python build.py` run and those entries join the confirmed set. Until then,
every layer above uses only the 2 confirmed icons and 3 confirmed colors.

### Gaps (documented, not invented)

- **Layer 1 "directions"**: no club handbook source exists in this repo, so
  each claim's description reads `directions: not available` rather than a
  fabricated route.
- **Layer 2 public-corridor Areas**: no verified extent-polygon source for
  the public panning corridors exists (only point coordinates) -- only pins
  are rendered, not invented boundaries.
- **Layer 6 access routes**: skipped for every area. No club handbook /
  access-directions text exists anywhere in this repo (checked by grep), so
  per the spec's own instruction ("otherwise skip; don't invent routes") no
  `6_access` file is produced this build.

## CalTopo bundle

`out/<area>/caltopo_<area>.geojson` -- all layers combined into one
FeatureCollection using simplestyle-spec properties (`marker-color`,
`marker-symbol`, `stroke`, `stroke-width`, `fill`, `fill-opacity`, `title`,
`description`) so CalTopo can import it directly (Import Data Overlay ->
choose file).

## Lidar GeoPDFs (`out/<area>/lidar/*.pdf`)

Each GeoPDF now carries a real vector overlay layer (claim shape, or a point
if no digitized polygon resolved, plus every layer-4-style historical site
inside that 2km tile) burned in via GDAL's `OGR_DATASOURCE` PDF creation
option -- selectable/queryable in Avenza/QGIS, not just a flat raster. A
title bar, north arrow, and scale bar are composited on top via the PDF
driver's `EXTRA_IMAGES` option (a page-space PNG overlay, not georeferenced).
**Verified two ways** (see `gold_overlays/sources/lidar.py`):
1. `ogrinfo <pdf>` shows the `overlay` vector layer; the PDF's decompressed
   content stream (`qpdf --qdf`) contains real path-drawing operators
   (`m`/`l`/`re`/`S`/`f`), not just an embedded raster.
2. `pdftoppm` render of page 1, inspected pixel-by-pixel, confirms the title
   bar (top), north arrow (top-right), scale bar (bottom-left), and claim
   polygon all actually appear in the rendered output.

**Correction to a previous README claim**: an earlier version of this repo
said the lidar GeoPDFs already carried a vector overlay -- they didn't
(`rasters.py` passed `None` for the overlay datasource). That's fixed now;
see `gold_overlays/rasters.py::_build_tile_overlay_gpkg`.

## Closed-claim density validation (task step 3)

`gis.blm.gov/nlsdb/.../MiningClaims/MapServer` layer 3 (`NLSDB_LND_HIST`) is
an action-history **table** with no geometry of its own -- it joins 1:1 to
layer 0 (`Case Feature Layer`, via `CSE_OBJECTID`), which *does* carry real
geometry for every claim record type (active, closed, historical, patented,
excluded, conveyed). Querying layer 0 for Bohemia's bbox returns **1,925**
cases, vs. The Diggings' ~1,550 estimate (ratio 1.24x, well within the 3x
tolerance -- **PASS**, vs. the old `BLM_Natl_MLRS_Mining_Claims_Closed`
service's 8 placer-only records for the same area). Full detail in
`out/closed_claim_density_validation.md` (`python build.py --validate-density`
regenerates it). **Not added as a 7th onX layer**: the style guide (this
task's own section 1) defines only the 6 layers above; no density layer is
in scope for onX output in this build.

## Private-land check (task step 2)

ORMAP's statewide taxlot service (`arcgis.oregonexplorer.info`) is blocked by
this build environment's egress policy (403 on connect) -- confirmed via
`/root/.ccr/__agentproxy/status`, not retried per that policy's own
instructions. Falls back to the spec's documented alternative: a **point-
level** query against BLM's `BLM_Natl_SMA_Cached_with_PriUnk` service (layers
22=BLM, 24=USFS, 31=Private/Unknown) for each scout candidate -- small point
queries avoid the 500/502 that service throws on `returnGeometry=true` over a
large bbox (see `gold_overlays/sources/land_status.py`'s existing caveat
about the same service). A candidate confirmed private is dropped; if the
point-level service itself errors for a candidate, it's kept but flagged
`(check owner)` in its description, per the spec's own fallback.

## Import steps

**onX phone app (GPX, primary):**
1. My Content -> **Import** -> choose one `out/<area>/<area>_<n>_<layer>.gpx`.
2. Select all the newly-imported items -> **Add to folder** -> name it
   `"<area> <layer>"` (e.g. `"bohemia 1_my_claims"`).
3. Repeat per layer file -- each is small (a few KB to ~600 KB) and
   single-purpose so this stays quick, and you end up with clean per-layer
   onX folders instead of one giant mixed import.

**onX Web Map (KML, secondary, for polygon fills):**
1. My Content -> **Import** -> upload `out/<area>/<area>_<n>_<layer>.kml`.

**CalTopo:**
1. Import Data Overlay -> `out/<area>/caltopo_<area>.geojson`.

**Avenza Maps (lidar/topo GeoPDFs):**
1. Copy `out/<area>/lidar/*.pdf` and `out/<area>/topo/*.pdf` to your phone.
2. Avenza reads the embedded georeferencing directly; toggle the vector
   overlay layer (claim + historical sites) in Avenza's layer list.

## Sampling log

Copy `sampling_log_template.csv` and fill it in after each trip:
```
date,area,waypoint,lat,lon,material,pans,colors,est_size,notes
```

## Layer sources, versions, download dates

| source | URL | version/date |
|---|---|---|
| USGS USMIN | https://mrdata.usgs.gov/usmin/ (WFS) | live service |
| USGS MRDS | https://mrdata.usgs.gov/mrds/ (WFS) | live service |
| DOGAMI MILO-4 | `MILO4_GIS_bundle.zip` | build-time |
| BLM MLRS Not Closed | `.../BLM_Natl_MLRS_Mining_Claims_Not_Closed/FeatureServer/0` | live service |
| BLM SMA LimitedScale | `.../BLM_Natl_SMA_LimitedScale/MapServer` (layers 7, 9) | live service |
| BLM SMA Cached (point-level) | `.../BLM_Natl_SMA_Cached_with_PriUnk/MapServer` (layers 22,24,31) | live service |
| BLM NLSDB Case Feature Layer | `.../nlsdb/.../MiningClaims/MapServer/0` | live service, validation only |
| USGS NHD | `.../nhd/MapServer/6` | live service |
| DOGAMI lidar | `.../lidar/DIGITAL_TERRAIN_MODEL_MOSAIC_HS/ImageServer` | live mosaic |
| TNM historical topos | `https://tnmaccess.nationalmap.gov/api/v1/products` | live catalog |
| DOGAMI Bulletin 61 | https://pubs.oregon.gov/dogami/B/B-061.pdf | Brooks & Ramp, 1968 |
| ORMAP taxlots | `arcgis.oregonexplorer.info` | **blocked by egress policy in this build environment** -- see fallback above |

Exact download dates per run are in `out/<area>/build_report.json` (`built_at`).

## What worked / what didn't (this cleanup+restyle pass, 2026-09-28)

**Worked:**
- Every data source reached from this build environment except ORMAP
  (policy-blocked, see above and `gold_overlays/config.py`'s `ormap_taxlots`
  entry) -- documented fallback used instead.
- Real onX GPX schema (`onx:icon`/`onx:color`/`onx:style`/`onx:weight`)
  reproduced exactly against `onx_samples/*.gpx`; all 6 layers write only
  confirmed icons/colors, verified by `build.py::verify_area` scanning every
  `<onx:icon>`/`<onx:color>` against the confirmed whitelist.
- Per-area, per-layer split keeps every file tiny (largest is
  `rogue_applegate_3_other_claims.gpx` at ~600 KB / 751 items -- both far
  under onX's 4 MB / 3000-item caps) and lets you import+folder one layer at
  a time on the phone as requested.
- Layer 4 dedup (greedy centroid clustering within 75m, not single-linkage,
  to avoid one giant merged blob along dense creeks) collapsed e.g.
  Bohemia's raw MILO/USMIN/MRDS record count down to the 150 cap cleanly,
  dropping only over-cap prospect pits and generic-unnamed MILO records far
  from any USMIN feature.
- Lidar GeoPDF vector overlay + scale bar/north arrow/title actually renders
  now (previous README claim was wrong -- see correction above); verified by
  both content-stream inspection and a pixel-level PNG render check.
- Closed-claim density validated via the NLSDB Case Feature Layer (1,925 vs.
  ~1,550 for Bohemia, within 3x).
- All 3 spot-check claims (ORMC171094, ORMC30445, ORMC163049) confirmed
  present in their area's `1_my_claims.gpx` by `build.py`'s final check.

**Didn't work cleanly / gaps:**
- ORMAP statewide taxlots blocked by this environment's egress policy --
  private-land check falls back to point-level BLM SMA queries (see above).
- No club handbook / access-directions text exists anywhere in this repo, so
  layer 6 (`access`) and layer 1's "directions" field are honestly empty
  rather than invented.
- No verified public-corridor extent polygon source -- layer 2 renders pins
  only.
- `onx_samples/STYLE_RESULTS.md` doesn't exist yet (you add it after testing
  `out/_test/onx_test.gpx` on your phone) -- until then, green public-site
  pins and any icon/color beyond the 2 confirmed icons / 3 confirmed colors
  stay unused, per the spec's own "use a confirmed one" fallback rule.
- MRDS's public WFS doesn't expose a placer/lode deposit-type field, so
  layer 5's placer-vs-lode labeling relies on `dev_stat`/name text matches
  for MRDS and on proximity (<=50m) to a USMIN surface working or a
  placer-mentioning MRDS record, per the spec's own rule -- not a full
  deposit-type join.
- Layer 5's ranking tiebreaker is still distance-to-stream, not
  distance-to-road (no road dataset fetched in this build).

**Per-area layer counts (this build):**

| area | 1_my_claims | 2_public | 3_other_claims | 4_history | 5_scout | 6_access |
|---|---|---|---|---|---|---|
| bohemia | 18 | 1 | 138 | 150/150 | 10/10 | -- |
| quartzville | 4 | -- | 48 | 121/150 | 10/10 | -- |
| calapooia | 2 | -- | 20 | 150/150 | 9/10 | -- |
| lnf_santiam | 1 | -- | 5 | -- | -- | -- |
| cowcreek | 8 | 1 | 203 | 150/150 | 10/10 | -- |
| rogue_applegate | -- | -- | 751 | 150/150 | 10/10 | -- |
| sixes | -- | 1 | 34 | 24/150 | 5/10 | -- |

## Hard constraints / how they were honored

- **No invented coordinates.** Every point/polygon traces to a WFS/REST
  query result or the reference table in `gold_overlays/config.py`.
- **BLM claim polygons are quarter-section approximate.** Every claim's
  description carries "boundary approx (BLM quarter-section)"; names never
  carry an `[APPROX ...]` suffix per the new 32-char naming rule.
- **No claimant names anywhere in output** -- only claim name, serial, type,
  acres, status (the queried BLM MLRS schema has no claimant-name field).
- **Only confirmed onX icons/colors used** -- enforced both at write time
  (`gold_overlays/onx_style.py::safe_icon`/`safe_color` fall back to
  Location/black for anything unconfirmed) and at verify time
  (`build.py::verify_area` scans every output file).

## Repository layout

```
gold-overlays/
  build.py                     6-layer GPX/KML + CalTopo build, verification, density validation
  refresh_claims.py            monthly re-pull of active claims, diffs vs last run
  gold_overlays/
    onx_gpx.py                 real onX GPX writer (wpt onx:icon/color, rte Area/Line onx:style/weight/color)
    onx_style.py                confirmed icon/color whitelist + onx_samples/STYLE_RESULTS.md loader
    layers.py                   builds the 6 layers from raw source fetches
    render_layers.py            layer items -> GPX + KML + CalTopo features
    caltopo.py                   CalTopo simplestyle GeoJSON writer
    reference_layer.py           WVM/BMOA claim polygon resolution (layer 1)
    rasters.py / sources/lidar.py  lidar GeoPDF (+ vector overlay + HUD) and historical topo downloads
    sources/                     per-data-source fetchers (usmin, mrds, milo, blm_claims, land_status, nhd, lidar, topo)
  onx_samples/                  real onX exports (format reference) + STYLE_RESULTS.md (you add this)
  out/_test/onx_test.gpx        style-testing file: import on phone, record results in onx_samples/STYLE_RESULTS.md
  out/<area>/
    <area>_<n>_<layer>.gpx/.kml  per-layer onX output (primary GPX, secondary KML)
    caltopo_<area>.geojson       CalTopo bundle, all layers combined
    build_report.json            machine-readable counts/verification for this run
    README.md                    per-area legend, import steps, layer counts, caveats
    lidar/*.tif,*.pdf,*.gpkg      lidar hillshade + GeoPDF + vector overlay source
    topo/*.pdf                    historical topo sheets
  out/closed_claim_density_validation.md   task step 3 validation record
  cache/                        gitignored: raw API responses
```
