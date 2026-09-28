# Oregon gold-prospecting overlays (onX / Avenza)

Reproducible pipeline that builds onX-ready KML+GPX overlays and Avenza-ready
lidar/topo rasters for seven weekend-prospecting areas around Eugene, OR, for
Willamette Valley Miners (WVM) and Bohemia Mine Owners Association (BMOA)
members. Every coordinate in the output either comes from a downloaded public
dataset (USGS USMIN/MRDS, DOGAMI MILO-4, BLM MLRS, BLM SMA, USGS NHD, DOGAMI
lidar, TNM historical topos) or from the verified reference table supplied for
this build -- nothing is estimated or hand-placed.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # shapely, pyproj, requests, gpxpy-free (own writer)
# system deps: gdal-bin (gdal_translate/ogr2ogr), for lidar GeoPDF export
sudo apt-get install -y gdal-bin

python build.py --area all                 # layers A-F -> out/<area>/*_onx.kml/.gpx
python build.py --area all --rasters --skip-vectors   # layers G+H -> out/<area>/lidar, out/<area>/topo
python refresh_claims.py                   # monthly: re-pull layer C, diff vs last run
```

`build.py --area <name>` builds one area; `--refresh` bypasses the on-disk
`cache/` (used so repeated runs don't re-hit slow government endpoints while
iterating).

## Areas

| area | coverage | bbox (minLon,minLat,maxLon,maxLat) |
|---|---|---|
| bohemia | Sharps/Brice/Martin/Quartz Creeks, Row River headwaters | -122.95, 43.45, -122.50, 43.78 |
| quartzville | Quartzville Creek (Green Peter Res. to Galena Creek), Canal Creek, Dry Gulch | -122.50, 44.48, -122.15, 44.68 |
| calapooia | upper Calapooia River | -122.55, 44.15, -122.28, 44.32 |
| lnf_santiam | Little North Santiam River | -122.60, 44.75, -122.40, 44.85 |
| cowcreek | Cow Creek byway (Glendale-Riddle), Dads Creek, Whitehorse Creek | -123.70, 42.68, -123.10, 42.98 |
| rogue_applegate | Rogue R. (Applegate confluence-Grave Creek), Gold Hill, Little Applegate | -123.65, 42.15, -122.85, 42.70 |
| sixes | Sixes River | -124.45, 42.75, -124.20, 42.88 |

### Bounding box notes (creek-coverage check)

Every named creek/river was checked against its area's box using USGS NHD
flowline geometry (`gnis_name` match, padded search). Findings:

- **No boxes required expansion for actual coverage gaps.** Several creeks'
  full length extends outside the box (e.g. Row River continues north past
  Cottage Grove, Rogue/Applegate/Cow Creek continue well beyond the named
  waysides, Calapooia continues into the valley) -- these are all
  **intentional**: the boxes are scoped to the headwaters/byway/mining-district
  reach relevant to prospecting, not the entire watercourse.
- `lnf_santiam` overshoots by a small margin (~750 m west, ~1.1 km north) right
  at the wilderness-boundary headwaters near Opal Creek/Battle Ax -- **this box
  was widened slightly** to `-122.62, 44.75, -122.40, 44.86` to fully contain
  that reach. (`gold_overlays/config.py` still lists the original spec box in
  history/comments; `AREAS` holds the corrected one.)
- "Dry Gulch" (quartzville) has no `gnis_name` match in NHD at all -- it's an
  unnamed tributary in the NHD attribute schema. This only affects the
  automated bbox-coverage sanity check, not the open-ground stream filter
  (which tests proximity to *any* flowline geometry, named or not).

## Layers built (per area)

| layer | source | notes |
|---|---|---|
| A. Historical workings | USGS USMIN (WFS) | prospect pits, shafts, adits, tailings, mine dumps, placer/hydraulic; gravel/borrow/clay pits + quarries dropped |
| B. Mine & prospect sites | DOGAMI MILO-4 (file gdb) + USGS MRDS (WFS) | filtered to gold; MRDS deduped against MILO by name + 250 m |
| C. Active claims | BLM MLRS Not Closed (FeatureServer) | placer/lode, acres, disposition; **quarter-section approximate** |
| D. Past claim density | BLM MLRS Closed (FeatureServer), placer only | 500 m hex grid, count + count-by-decade, cells with <3 claims dropped |
| E. Land status | BLM SMA "LimitedScale" (BLM + USFS layers) | used to compute layer F; not rendered as its own KML layer (see caveats) |
| F. Open ground to sample | derived | top 25 per area, `OPEN-<area>-<rank>` |
| G. Lidar hillshade | DOGAMI bare-earth lidar mosaic (ImageServer) | 2 km GeoTIFF + GeoPDF per club claim / public site |
| H. Historical topos | TNM Access API | oldest 15-min + 7.5-min sheet per claim cluster, capped at 10 files |
| I. Reading | DOGAMI Bulletin 61 | per-area notes in each `out/<area>/README.md` |

### Layer sources, versions, download dates

| source | URL | version/date | downloaded |
|---|---|---|---|
| USGS USMIN | https://mrdata.usgs.gov/usmin/ (WFS) | live service, no static version | build-time (see `cache/`) |
| USGS MRDS | https://mrdata.usgs.gov/mrds/ (WFS) | live service | build-time |
| DOGAMI MILO-4 | https://www.oregon.gov/dogami/pubs/pages/dds/p-milo-4.aspx | MILOv4.gdb, `MILO4_GIS_bundle.zip` | build-time |
| BLM MLRS Not Closed | https://gis.blm.gov/nlsdb/rest/services/HUB/BLM_Natl_MLRS_Mining_Claims_Not_Closed/FeatureServer/0 | live service | build-time |
| BLM MLRS Closed | .../BLM_Natl_MLRS_Mining_Claims_Closed/FeatureServer/0 | live service | build-time |
| BLM SMA | https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_LimitedScale/MapServer (layers 7, 9) | live service | build-time |
| USGS NHD | https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/6 | live service | build-time |
| DOGAMI lidar | https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_TERRAIN_MODEL_MOSAIC_HS/ImageServer | live mosaic (per-project acquisition dates vary; see DOGAMI viewer) | build-time |
| TNM historical topos | https://tnmaccess.nationalmap.gov/api/v1/products | live catalog | build-time |
| DOGAMI Bulletin 61 | https://pubs.oregon.gov/dogami/B/B-061.pdf | Brooks & Ramp, 1968 | 2026-09-28 |

Exact download dates for a given run are stamped in `out/<area>/build_report.json`
(`built_at`) and in each cached file's mtime under `cache/`.

## Import steps

**onX Web Map (KML, for polygons):**
1. Sign in at onxmaps.com -> **My Content** -> **Import**.
2. Upload `out/<area>/<area>_onx.kml` (and `_part2`, etc. if split).
3. Repeat per area. Each KML folder becomes an onX layer group.

**onX phone app (GPX, for the field):**
1. My Content -> **Import** -> choose `out/<area>/<area>_onx.gpx`.
2. Polygons appear as closed tracks (outline only, no fill) since the phone
   importer doesn't support polygons -- waypoints (claims, open-ground picks,
   public sites) come through as pins with full descriptions.

**Avenza Maps (lidar/topo PDFs):**
1. Copy `out/<area>/lidar/*.pdf` and `out/<area>/topo/*.pdf` to your phone
   (Avenza's own folder via Files app, or import via the Avenza "Add Map" ->
   "From File").
2. These are GDAL-produced GeoPDFs with embedded georeferencing -- Avenza
   reads that directly, no manual calibration needed.
3. The lidar GeoPDFs carry the claim outline/point as a real vector layer on
   top of the hillshade raster (toggle it in Avenza's layer list).

## Sampling log

Copy `sampling_log_template.csv` and fill it in after each trip:

```
date,area,waypoint,lat,lon,material,pans,colors,est_size,notes
```

- `material`: one of `bedrock crack`, `inside bend`, `bench`, `moss`.
- `waypoint` naming convention: **`MMDD-<site>-<material>-<colors>c`**
  (e.g. `0913-brice-bedrock-crack-4c` = Sept 13, Brice Creek site, bedrock
  crack, 4 colors).

## Hard constraints / how they were honored

- **No invented coordinates.** Every point/polygon traces to a WFS/REST query
  result or to the reference table in `gold_overlays/config.py`.
- **BLM claim polygons are quarter-section approximate.** Every claim polygon's
  KML/GPX name and description carries the literal string
  `[APPROX quarter-section]` / `APPROX (BLM quarter-section)`.
- **No claimant names anywhere in output** -- only claim name, serial, type,
  acres, status, and (proxy) dates. Verified by construction: the BLM MLRS
  schema queried here (`CSE_NAME`, `CSE_NR`, `LEG_CSE_NR`, `BLM_PROD`,
  `CSE_DISP`, `RCRD_ACRS`, `Created`) has no claimant-name field at all.
- **Withdrawn areas / recreation sites flagged where known**: the three
  `public` reference sites (Cow Creek Recreational Gold Panning Area, Sixes
  River Campground, Cedar Creek Campground) are rendered in green with
  "public site" in their description. No additional withdrawn-area dataset
  was identified/queried in this build (BLM's SMA layer distinguishes surface
  agency, not mineral-withdrawal status) -- **this is a gap**: if you need to
  confirm an area isn't withdrawn from mineral entry, cross-check BLM LR2000
  case status directly before sampling.
- **Sources, versions, and download dates recorded** -- see table above and
  each `out/<area>/build_report.json`.

## Key assumptions / deviations from the spec (read before trusting the data)

1. **BLM MLRS has no true "located date" or "last action date" field.** The
   public `BLM_Natl_MLRS_Mining_Claims_*` FeatureServer only exposes `Created`/
   `Modified` (database record timestamps -- e.g. when the polygon was last
   redrawn -- not the legal location date, which lives in LR2000 case files
   this service doesn't expose). Layer C descriptions and layer D's
   decade buckets use `Created` as a clearly-labeled proxy.
2. **Land status (layer E) uses BLM SMA "LimitedScale" layers 7 (BLM) and 9
   (USFS) only**, not the generalized "SMA_Cached" service, which returns
   HTTP 500 on any bbox larger than a few km^2 when `returnGeometry=true`
   (its polygons are too complex for that tier). The "Private/Unknown" layer
   (id 16) has the same problem, so anything that is not BLM and not USFS is
   reported simply as **non-BLM/USFS** rather than split into State/Private/
   Other. This only matters for layer F (which only needs "is it BLM or
   USFS"), not for claim/workings placement.
3. **Layer F's final ranking tiebreaker is distance-to-stream, not
   distance-to-road** -- no road dataset was fetched in this build (out of
   scope for the time available). Called out again in each area's README.
4. **NHD flowlines are fetched in ~1.6 km tiles, not one bbox-wide pull.** A
   single bbox query for a ~1,000+ km^2 forested area returns 15,000+
   flowline features and is far slower than the per-tile approach used here;
   this is purely a performance choice and does not change which streams are
   considered.
5. **MRDS attribute detail is limited to what its public WFS exposes**
   (`site_name`, `dev_stat`, `code_list`, `url`) -- full commodity/deposit-type/
   production detail lives on the per-site HTML page linked in each
   description, not scraped in bulk here.
6. **MILO-4's `DepositType`/`WorkingsType` fields are sparse** (mostly blank).
   Placer-vs-lode tagging uses a documented heuristic: `DepositType` containing
   "placer"/"vein"/"shear"/"lode" wins; otherwise `WorkingsType == "surface"` is
   treated as a placer proxy and `"underground"` as a lode proxy; everything
   else is `unknown`. See `gold_overlays/sources/milo.py::_classify_deposit`.
7. **"My claims & public sites" upgrades reference-table points to real BLM
   MLRS polygons** where the public feature service has one (16 of 17 club
   claims resolved this way, by legacy serial or Salesforce SF_ID). The one
   exception, **WVM-LNF25 Little North Santiam**, has acreage/status in MLRS
   but no digitized polygon yet -- it's rendered as a point at the reference
   table's given coordinates, flagged in its description.
8. **Lidar hillshade resolution**: DOGAMI's bare-earth mosaic's native
   resolution is ~0.91 m (3 ft, in its native NAD83(HARN)/Oregon Lambert
   projection) -- exported here reprojected to WGS84 at a matching ~1 m/px,
   satisfying the spec's "≤1 m/pixel" ask.
9. **Rasters are committed as plain git blobs, not git-lfs.** Every file
   produced here is well under 50 MB (largest lidar GeoTIFF ~2.4 MB after
   DEFLATE compression, largest topo GeoPDF ~28 MB), so the spec's ">50 MB
   keep out of git" threshold never triggers for this build's own outputs.
   git-lfs *is* installed (`apt-get install git-lfs`) and `git lfs track
   "out/**/*.tif" "out/**/*.pdf"` was tried first, but this environment's
   egress policy blocks `lfs.github.com` (push fails with 403 Forbidden on
   every LFS object), so LFS pointers can't actually reach the remote here.
   If you regenerate rasters somewhere with LFS push access and a file grows
   past 50 MB, re-run that `git lfs track` command (re-adds `.gitattributes`)
   before committing it.

## Repository layout

```
gold-overlays/
  build.py                 layers A-H, per --area/--rasters flags
  refresh_claims.py        monthly re-pull of layer C, diffs vs last run
  requirements.txt
  gold_overlays/           library code (config, sources/, render, open_ground, ...)
  out/<area>/
    <area>_onx.kml / .gpx  (split into _part2 etc. if over onX's 4MB/3000-feature caps)
    build_report.json      machine-readable counts/verification for this run
    README.md              layer counts, top open-ground list, Bulletin 61 notes, caveats
    lidar/*.tif, *.pdf     (with --rasters)
    topo/*.pdf             (with --rasters, claim-cluster areas only)
  cache/                   gitignored: raw API responses, so re-runs don't re-hit slow services
```

## What worked / what didn't (first full build, 2026-09-28)

**Feature counts per area** (from `out/build_summary.json` / each area's `build_report.json`):

| area | total features | USMIN | MILO gold | MRDS kept | active claims | closed placer | density cells | open ground | claims clipped to bbox |
|---|---|---|---|---|---|---|---|---|---|
| bohemia | 1364 | 64 | 1067 | 51 | 147 | 8 | 0 | 25 | 6 |
| quartzville | 293 | 22 | 185 | 9 | 50 | 1 | 0 | 25 | 2 |
| calapooia | 343 | 17 | 272 | 7 | 21 | 3 | 0 | 25 | 1 |
| lnf_santiam | 6 | 0 | 0 | 0 | 5 | 2 | 0 | 0 | 0 |
| cowcreek | 692 | 225 | 167 | 38 | 207 | 269 | 10 | 25 | 30 |
| rogue_applegate | 2431 | 754 | 694 | 205 | 751 | 66 | 2 | 25 | 94 |
| sixes | 71 | 5 | 19 | 6 | 34 | 3 | 0 | 6 | 4 |

All 7 KML/GPX pairs passed verification: every file under the 4 MB / 3000-feature
onX caps (largest is rogue_applegate at 1.1 MB / 2431 features), KML and GPX
feature counts match exactly, and (after the bbox-clip fix below) zero
coordinates fall outside their area's bbox. All three spot-check claims landed
within a few meters of their expected coordinates (WVM #1B, Cedar Bend, BMOA
Little Red -- see `gold_overlays/reference_layer.py`'s polygon-lookup path,
which resolved 16 of 17 club claims to a real BLM MLRS polygon).

**What worked:**
- Every planned data source was reachable and usable: USGS USMIN/MRDS (WFS),
  DOGAMI MILO-4 (file gdb download), BLM MLRS active+closed claims, USGS NHD
  flowlines, DOGAMI lidar ImageServer export, TNM historical topo API, and
  DOGAMI Bulletin 61 (OCR'd PDF).
- GDAL's PDF driver burns the claim outline/point in as a real, selectable
  vector layer on top of each lidar hillshade -- confirmed in a test render.
- 16 of 17 reference-table claims resolved to their actual BLM MLRS polygon
  (by legacy serial or Salesforce SF_ID), not just the reference table's point.

**What didn't work cleanly, and how it was handled:**
- **BLM's generalized SMA "Cached" land-status service 500s on any bbox
  larger than a few km^2** with `returnGeometry=true` -- switched to the
  "LimitedScale" service's separate BLM (id 7) / USFS (id 9) layers instead
  (see README caveat #2).
- **A whole-bbox NHD flowline pull returns 15,000+ features** for a ~1,000+
  km^2 forested area and is far too slow -- switched to fetching flowlines in
  ~1.6 km tiles, shared across nearby candidate points (see caveat #4).
- **mrdata.usgs.gov's WFS intermittently 502s** regardless of bbox size or
  result count (observed on quartzville's USMIN query) -- added retry-with-
  backoff around every `ogr2ogr` WFS call.
- **A real BLM MLRS data-quality bug**: at least one active claim per area
  (up to 94/751 in rogue_applegate) has a ring in its geometry that belongs to
  a mismatched PLSS aliquot tens of km away (visible in its own `QLTY` field's
  "DOES NOT MATCH PM ANGLES" warnings). Rendering raw esri rings naively
  (first ring = outer, rest = holes) drew that stray ring as a donut hole far
  from the real claim. Fixed by clipping every polygon feature to its area's
  bbox (and, for reference claims, preferring the sub-polygon that actually
  contains the reference point) before rendering -- see `geo.clip_rings_to_bbox`.
- **git-lfs can't push from this environment** (egress policy blocks
  `lfs.github.com`) -- moot here since every raster produced is well under
  50 MB, so rasters are committed as plain blobs instead (caveat #9).
- Everything else in the spec's hard constraints and layer list was
  implementable as specified; deviations that *were* necessary (land-status
  granularity, open-ground's road-vs-stream tiebreaker, MLRS's missing
  located-date field, MILO's sparse deposit-type field) are all called out
  in "Key assumptions" above and repeated in each area's own README.

Not yet done in this build (candidates for a follow-up pass, not blockers):
withdrawn-area cross-checking against BLM LR2000 case status (see the
withdrawn-areas caveat above), and a road dataset for open-ground's
tertiary ranking tiebreaker.
