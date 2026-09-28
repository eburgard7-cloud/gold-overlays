"""Per-area notes distilled from DOGAMI Bulletin 61, "Gold and Silver in
Oregon" (Brooks & Ramp, 1968), https://pubs.oregon.gov/dogami/B/B-061.pdf.

Page numbers below are the bulletin's own printed page numbers (bottom of
page), not PDF page indices. Extracted by OCR text search
(`pdftotext -layout`); OCR quality is imperfect (ClearScan), so exact
wording was cross-checked against the surrounding text, not copy-pasted
verbatim in every case.

DOGAMI Oregon Historical Mining Information (OHMI) is organized by county,
not by district, so the "per-mine files" links below are the relevant
county index pages rather than individual mine files -- downloading every
individual mine file for these districts would be hundreds of small pages
and was out of scope for this build.
"""

OHMI_BASE = "https://www.oregon.gov/dogami/milo/Pages"

NOTES = {}

NOTES["bohemia"] = """
**Bohemia district** (Bulletin 61 p. 309-317; Lane County, Ts. 22-23 S., Rs. 1-2 E.).
Discovered 1858 (Oglesby & Brass); gold found near the head of City Creek in 1863
by Bohemia Johnson and George Ramsey, triggering the district's main rush. By 1902
more than 2,000 claims had been filed (many duplicates). Main producers: Champion,
Helena, and Musick mines, with lesser output from Noonday, Vesuvius, and Star.
District total production is estimated at **about $1,000,000**; separately, Lane
County (mainly Bohemia) produced 14,590.69 oz gold + 1,418.79 oz silver 1880-1900
per U.S. Mint records, and 13,694.59 oz gold (from 42,548 tons crude ore) 1901-1930
per USBM records (p. 311).

**Caveat:** Bulletin 61's Bohemia coverage is almost entirely about hard-rock LODE
mines (quartz veins with sphalerite/galena/chalcopyrite/pyrite) draining into Brice,
Sharps, and Steamboat Creeks -- it does not separately describe placer bars/benches
on Sharps, Brice, Martin, or Quartz Creek by name. Placer gold in these creeks is
consistent with erosion of the district's many lode workings, but the bulletin gives
no placer-specific production figures for them. Bibliography includes Bales, W.E.,
1951, "Geology of the lower Brice Creek area, Lane County, Oregon" (Univ. Oregon
thesis) -- not independently reviewed for this build.

**OHMI (Lane County):** {ohmi_lane}
""".format(ohmi_lane=f"{OHMI_BASE}/ohmi-lane.aspx")

NOTES["quartzville"] = """
**Quartzville district** (Bulletin 61 p. 295-298; Linn County, mainly T. 11-12 S., R. 4 E.).
One of the five main Western Cascades mineralized districts. Documented mines/claims:
Galena, Lawler, Lucille (Snowstorm & Bell), Munro (Mayflower), Paymaster, Red Heifer
(Silver Signal), Riverside, Savage (Vandalia/Golden West), Tillicum & Cumtillie
(Golden Fleece). First discovery in the district reported 1861 (Lawler mine); the
Lawler is the best-documented producer at **about $100,000** (ground in a 20-stamp
mill, shut down 1898). Munro group owner reported 72.56 oz gold. Savage/Vandalia +
Golden West combined 1921 production about $7,000.

**Caveat:** like Bohemia, this section is lode-focused (quartz veins, shear zones in
andesite/tuff/rhyolite); it does not name placer bars on Quartzville Creek, Canal
Creek, or Dry Gulch specifically. Placer gold reaching these creeks is consistent
with erosion of the many small lode prospects listed above, upstream of Green Peter
Reservoir.

**OHMI (Linn County):** {ohmi_linn}
""".format(ohmi_linn=f"{OHMI_BASE}/ohmi-linn.aspx")

NOTES["calapooia"] = """
**Blue River district** (Bulletin 61 p. 299-306; southern Linn / northern Lane
County, Ts. 15-16 S., R. 4 E., straddling the Calapooia/McKenzie drainage divide).
Bulletin 61 does not have a separate "Calapooia" district -- the upper Calapooia
River headwaters fall within the area the bulletin treats as the Blue River
district. Principal mine: **Lucky Boy** (reached via a road up Quartz Creek from
the town of Blue River), with lesser prospects Cinderella, Great Northern, Poorman,
Rowena, Tate, Treasurer, Union. Veins carry pyrite/sphalerite/galena/chalcopyrite in
a quartz gangue, with calcite locally dominant (Great Northern, Higgins, Cinderella).
Western Cascades total production (combining Blue River + Fall Creek + other minor
districts, not separated out) is given as **about $1.5 million** (p. 306, 15373 in
the OCR text).

**Caveat:** no placer-specific content or named bars/benches for the Calapooia River
itself were found in Bulletin 61 -- treat this area's placer potential as inferred
from lode erosion, not from any documented placer history.

**OHMI (Linn County):** {ohmi_linn}
""".format(ohmi_linn=f"{OHMI_BASE}/ohmi-linn.aspx")

NOTES["lnf_santiam"] = """
**North Santiam district** (Bulletin 61 p. 286-289; Clackamas/Marion Counties,
T. 8 S., Rs. 4-5 E., along the Little North Santiam River). Mineralization
discovered about 1877; most properties located by 1903. District total recorded
production 1896-1947 is **about $25,000** (454 oz gold, 1,412 oz silver, plus
copper/lead/zinc byproduct). Documented zoning from a high-temperature
chalcopyrite-bearing core (Crown mine, along the river) outward through
pyrite-bearing veins (Gold Creek) to complex sulfide veins (Blende Oro, Ruth) to a
low-temperature calcite-vein outer zone (lower Elkhorn Creek, Ogle Mountain mine).
Most-developed mines: Ogle Mountain (~$10,000, worked 1903-1919), Ruth
(zinc-focused, >4,000 ft of workings), Santiam Copper (shipped ore/concentrate
1923-1940, averaging ~10% Cu, 3 oz/ton Ag, 0.03 oz/ton Au).

**Caveat:** again lode-focused; no named placer bars on the Little North Santiam
itself are given, though the district's many creek-adjacent lode workings (Gold
Creek, Elkhorn Creek) are consistent with the placer colors panners find today.

**OHMI (Marion County):** {ohmi_marion} -- **(Clackamas County):** {ohmi_clackamas}
""".format(ohmi_marion=f"{OHMI_BASE}/ohmi-marion.aspx", ohmi_clackamas=f"{OHMI_BASE}/ohmi-clackamas.aspx")

NOTES["cowcreek"] = """
**Silver Peak area** (Bulletin 61 p. 213-214; Douglas County, southwest of
Canyonville, T. 31 S., Rs. 5-6 W., draining to Cow Creek and the South Umpqua).
Lode total for the area is estimated at **about $216,000** prior to 1930 (Silver
Peak mine ~$73,000 of shipped ore 1922-1930; Gold Bluff mine $7,000-$40,000+ across
several owners; Levens Ledge $75,000-$80,000).

**Placer mining** (p. 214, directly relevant to the Cow Creek byway area): "Some
evidence of placer mining can be found on Jordan, Mitchell, Russell, and West Fork
Canyon Creeks and on Middle Creek... but no records of this activity have been
published." **"The most extensive placer-mining operations were in bench gravels
along Cow Creek southwest of this area. Of these, the Victory placer in sec. 33,
T. 32 S., R. 7 W. (about 6 miles west of Glendale) was probably the largest
producer"** -- squarely inside this build's Cow Creek byway box. Diller & Kay
(1924) also describe placer workings on Quaternary bench gravels ~500 ft above
present streams between Riddle and Canyonville, with gold partly derived from
decomposition of the underlying Cretaceous (Riddle Fm) sediments.

Dads Creek and Whitehorse Creek (both hosting WVM claims in the reference table)
are not individually named in Bulletin 61; treat their placer potential as
consistent with the broader Cow Creek bench-gravel pattern documented above.

**OHMI (Douglas County):** {ohmi_douglas}
""".format(ohmi_douglas=f"{OHMI_BASE}/ohmi-douglas.aspx")

NOTES["rogue_applegate"] = """
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

**OHMI (Jackson County):** {ohmi_jackson} -- **(Josephine County):** {ohmi_josephine}
""".format(ohmi_jackson=f"{OHMI_BASE}/ohmi-jackson.aspx", ohmi_josephine=f"{OHMI_BASE}/ohmi-josephine.aspx")

NOTES["sixes"] = """
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

**OHMI (Curry County):** {ohmi_curry} -- **(Coos County):** {ohmi_coos}
""".format(ohmi_curry=f"{OHMI_BASE}/ohmi-curry.aspx", ohmi_coos=f"{OHMI_BASE}/ohmi-coos.aspx")
