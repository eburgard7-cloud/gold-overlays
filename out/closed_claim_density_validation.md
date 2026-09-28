# Closed-claim density validation (task step 3)

- `BLM_Natl_MLRS_Mining_Claims_Closed` (old approach): 8 placer claims for Bohemia -- confirmed to lack legacy geometry for most historical claims.
- `gis.blm.gov/nlsdb/.../MiningClaims/MapServer` layer 3 (`NLSDB_LND_HIST`) is an action-history **table** with no geometry of its own; it joins 1:1 to layer 0 (`Case Feature Layer`, `CSE_OBJECTID`) which *does* carry full case geometry for every record type (active, closed, historical, patented, excluded, conveyed).
- Layer 0 case count intersecting the Bohemia bbox: **1925**.
- The Diggings' estimate for Bohemia: ~1550.
- Ratio: 1.24x (within 3x -- PASS)

**Decision:** The NLSDB Case Feature Layer is plausible for Bohemia and could support a future 'closed-claim density' layer. It is NOT added as a 7th onX layer in this build because the style guide (section 1 of the task) defines only the 6 layers 1_my_claims..6_access; no density layer is in scope for onX output. This validation is recorded here for the record.
