# sixes -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-124.45, 42.75, -124.2, 42.88)`
Built: 2026-09-28

## Legend

| layer | icon | color | style | meaning |
|---|---|---|---|---|
| 1_my_claims | Mineral Site (pin) / filled Area | yellow | solid | WVM/BMOA club claims -- ours |
| 2_public | Location (pin) | black | n/a (points only) | Public gold-panning sites open to anyone |
| 3_other_claims | Area only, no pins | red | dotted | Other active BLM claims -- don't dig here |
| 4_history | Mineral Site (placer/tailings/hydraulic) / Location (adit/shaft/pit) | black | n/a (points only) | Deduped historical workings |
| 5_scout | Location (pin) | red | n/a (points only) | Open-ground candidates worth scouting |
| 6_access | Line | black | dash/dot | Claim-access route (only where a real source describes one) |

Only confirmed onX icons/colors are used: icons `Mineral Site` / `Location`; colors yellow `rgba(255,255,0,1)`, red `rgba(255,51,0,1)`, black `rgba(0,0,0,1)`. Green for confirmed public sites and any other icon/color in `onx_samples/onx_test.gpx` is a GUESS pending `onx_samples/STYLE_RESULTS.md` -- not used until confirmed (see top-level README).

## Import steps (phone)

1. onX app -> **My Content** -> **Import** -> choose one `<area>_<layer>.gpx` file.
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"sixes <layer>"` (e.g. `"sixes 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `sixes_2_public.gpx` (+ `sixes_2_public.kml` secondary) -- 1 items, 0.6 KB GPX [OK]
- `sixes_3_other_claims.gpx` (+ `sixes_3_other_claims.kml` secondary) -- 34 items, 22.0 KB GPX [OK]
- `sixes_4_history.gpx` (+ `sixes_4_history.kml` secondary) -- 24 items, 5.9 KB GPX [OK]
- `sixes_5_scout.gpx` (+ `sixes_5_scout.kml` secondary) -- 5 items, 1.7 KB GPX [OK]
- `caltopo_sixes.geojson` -- CalTopo bundle, 64 features, all layers combined

## Layer counts
- 1_my_claims: 0
- 2_public: 1 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 34 (excluded as ours: 0, clipped to bbox: 4)
- 4_history: 24 / 150 cap (raw records: 30, clusters before cap: 24, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 0)
- 5_scout: 5 / 10 cap (candidate pool: 6, NHD stream filter skipped: False, land checks: {'public_confirmed': 5, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

## DOGAMI Bulletin 61 notes


**Salmon Mountain-Sixes area** (Bulletin 61 p. 182-183; southern Coos / northern
Curry County, Ts. 32-33 S., Rs. 12-14 W., between the Sixes and Elk Rivers). Diller
(1903) called it the "gold belt of the Port Orford quadrangle" and it "has long been
the most active mining region of the Oregon coast" -- **total production from the
quadrangle since 1852 is estimated at about $1,000,000**, almost entirely from
PLACER, not lode: "Nearly all of the gold which has thus far been obtained... has
come from placer mines, some of which are along beaches... and the rest in river
gravels, especially **along the South Fork of the Sixes** and at the heads of Salmon
and Johnson Creeks" (p. 182-183, quoting Diller 1903).

**Named productive creeks / bars:** Johnson Creek placers (most successful near its
head, close to the dacite-porphyry belt; landslides in spring 1890 buried the
streambed and ended profitable mining; the "Big Slide" placer near NE sec. 34,
T. 32 S., R. 12 W. was later worked seasonally). **"Numerous placer operations were
active along the South Fork of Sixes River during the late 1800's. Many of these
worked bench gravels from about 50 feet to as much as 130 feet above the present
stream."** Very little mining occurred on the Sixes mainstem above the South Fork
mouth (p. 183).

**OHMI (Curry County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-curry.aspx -- **(Coos County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-coos.aspx

