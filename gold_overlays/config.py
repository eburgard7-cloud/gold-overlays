"""Area definitions and the verified reference-point table."""

# name: (minLon, minLat, maxLon, maxLat)
# NOTE: any expansion from the originally-specified box is recorded in
# EXPANSION_NOTES below and in the top-level README.
AREAS = {
    "bohemia": (-122.95, 43.45, -122.50, 43.78),
    "quartzville": (-122.50, 44.48, -122.15, 44.68),
    "calapooia": (-122.55, 44.15, -122.28, 44.32),
    "lnf_santiam": (-122.62, 44.75, -122.40, 44.86),  # expanded from spec box, see EXPANSION_NOTES
    "cowcreek": (-123.70, 42.68, -123.10, 42.98),
    "rogue_applegate": (-123.65, 42.15, -122.85, 42.70),
    "sixes": (-124.45, 42.75, -124.20, 42.88),
}

AREA_LABELS = {
    "bohemia": "Bohemia Mining District (Sharps/Brice/Martin/Quartz Creeks, Row River headwaters)",
    "quartzville": "Quartzville Creek (Green Peter Reservoir to Galena Creek), Canal Creek, Dry Gulch",
    "calapooia": "Upper Calapooia River",
    "lnf_santiam": "Little North Santiam River",
    "cowcreek": "Cow Creek byway (Glendale to Riddle), Dads Creek, Whitehorse Creek",
    "rogue_applegate": "Rogue River (Applegate confluence to Grave Creek), Gold Hill, Little Applegate",
    "sixes": "Sixes River",
}

# Recorded because the automated NHD gnis_name check (build.py --check-bboxes)
# found the named creek's mapped flowline extends outside the originally
# specified box. See README "Bounding box notes".
EXPANSION_NOTES = {
    "lnf_santiam": (
        "Original spec box (-122.60, 44.75, -122.40, 44.85) clipped part of the Little "
        "North Santiam River's mapped NHD flowline near its headwaters (Opal Creek/Battle "
        "Ax area): ~750 m over the west edge, ~1.1 km over the north edge. Expanded to "
        "(-122.62, 44.75, -122.40, 44.86) to fully contain that reach."
    ),
}

# name,group,serial,lat,lon,precision
REFERENCE_POINTS = [
    dict(name="WVM #1B Dry Gulch", group="WVM", serial="ORMC171094", lat=44.5966, lon=-122.3011, precision="gps"),
    dict(name="Cedar Bend Placer", group="WVM", serial="ORMC30445", lat=44.5776, lon=-122.3158, precision="blm"),
    dict(name="Golden Dollar", group="WVM", serial="ORMC168629", lat=44.2359, lon=-122.3750, precision="gps"),
    dict(name="WVM-LNF25 Little North Santiam", group="WVM", serial="A02SJ00000B7SAVYAN", lat=44.7984, lon=-122.5237, precision="blm"),
    dict(name="WVM #3 Dads Creek", group="WVM", serial="ORMC159208", lat=42.7709, lon=-123.5372, precision="gps"),
    dict(name="WVM #4 Dads Creek", group="WVM", serial="ORMC161475", lat=42.7843, lon=-123.5099, precision="gps"),
    dict(name="WVM #5 Dads Creek", group="WVM", serial="ORMC161445", lat=42.7881, lon=-123.5080, precision="gps"),
    dict(name="Pure White Gold (Whitehorse Cr)", group="WVM", serial="ORMC172749", lat=42.8111, lon=-123.1747, precision="gps"),
    dict(name="BMOA War Eagle III", group="BMOA", serial="ORMC156963", lat=43.6856, lon=-122.8331, precision="blm"),
    dict(name="BMOA Westside", group="BMOA", serial="ORMC86891", lat=43.6713, lon=-122.8132, precision="blm"),
    dict(name="BMOA Y Not", group="BMOA", serial="ORMC173540", lat=43.6564, lon=-122.8007, precision="blm"),
    dict(name="BMOA Placer Claim", group="BMOA", serial="ORMC147500", lat=43.5866, lon=-122.7173, precision="blm"),
    dict(name="BMOA Little Red", group="BMOA", serial="ORMC163049", lat=43.5620, lon=-122.7463, precision="blm"),
    dict(name="BMOA Big Bend", group="BMOA", serial="ORMC159678", lat=43.5620, lon=-122.7463, precision="blm"),
    dict(name="BMOA Argentite", group="BMOA", serial="ORMC159677", lat=43.5585, lon=-122.7464, precision="blm"),
    dict(name="BMOA Exodus", group="BMOA", serial="ORMC163687", lat=43.5551, lon=-122.7465, precision="blm"),
    dict(name="BMOA 4 Aces", group="BMOA", serial="ORMC163686", lat=43.5541, lon=-122.7321, precision="blm"),
    dict(name="Cow Creek Recreational Gold Panning Area", group="public", serial="", lat=42.8296, lon=-123.6180, precision="published"),
    dict(name="Sixes River Campground (rec mining)", group="public", serial="", lat=42.8050, lon=-124.3127, precision="published"),
    dict(name="Cedar Creek Campground (Brice Cr)", group="public", serial="", lat=43.6710, lon=-122.7080, precision="published"),
]

# USMIN feature types to KEEP (historical workings). Everything else
# (gravel pit, borrow pit, quarry, clay pit, open pit mine or quarry) is dropped.
USMIN_KEEP_TYPES = {
    "prospect pit", "shaft", "adit", "adit/tunnel", "tunnel", "tailings",
    "mine dump", "dump", "placer", "placer mine", "hydraulic", "hydraulic mine",
    "mine", "open pit mine", "pit", "trench", "mine shaft", "underground mine",
}
USMIN_DROP_TYPES = {
    "gravel pit", "borrow pit", "quarry", "clay pit", "open pit mine or quarry",
}

SOURCES = {
    "usmin": {
        "url": "https://mrdata.usgs.gov/usmin/",
        "wfs_base": "https://mrdata.usgs.gov/services/wfs/usmin",
    },
    "mrds": {
        "url": "https://mrdata.usgs.gov/mrds/",
        "wfs_base": "https://mrdata.usgs.gov/services/wfs/mrds",
    },
    "milo4": {
        "url": "https://www.oregon.gov/dogami/pubs/pages/dds/p-milo-4.aspx",
        "gis_bundle": "https://pubs.oregon.gov/dogami/dds/milo/MILO-4/MILO4_GIS_bundle.zip",
    },
    "blm_active": {
        "url": "https://gis.blm.gov/nlsdb/rest/services/HUB/BLM_Natl_MLRS_Mining_Claims_Not_Closed/FeatureServer/0",
    },
    "blm_closed": {
        "url": "https://gis.blm.gov/nlsdb/rest/services/HUB/BLM_Natl_MLRS_Mining_Claims_Closed/FeatureServer/0",
    },
    "sma": {
        "url": "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_without_PriUnk/MapServer/1",
    },
    "nhd": {
        "url": "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/6",
    },
    "lidar": {
        "url": "https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_TERRAIN_MODEL_MOSAIC_HS/ImageServer",
        "viewer": "https://gis.dogami.oregon.gov/maps/lidarviewer/",
    },
    "topo": {
        "url": "https://tnmaccess.nationalmap.gov/api/v1/products",
    },
    "bulletin61": {
        "url": "https://pubs.oregon.gov/dogami/B/B-061.pdf",
    },
    "nlsdb_case": {
        "url": "https://gis.blm.gov/nlsdb/rest/services/Mining_Claims/MiningClaims/MapServer/0",
        "note": (
            "'Case Feature Layer' -- all mining-claim cases (active, closed, historical) with real "
            "geometry, joined 1:1 to layer 3 NLSDB_LND_HIST (action-history table) via CSE_OBJECTID. "
            "Used only to validate closed-claim density plausibility (see build.py "
            "validate_closed_claim_density()), not as an onX layer source."
        ),
    },
    "ormap_taxlots": {
        "url": "https://arcgis.oregonexplorer.info/arcgis/rest/services",
        "note": (
            "Blocked by this build environment's egress policy (403 on CONNECT) -- private-land "
            "checks fall back to a point-level BLM SMA 'Cached_with_PriUnk' query instead (see "
            "gold_overlays/layers.py::_point_land_check), per the spec's documented fallback."
        ),
    },
}
