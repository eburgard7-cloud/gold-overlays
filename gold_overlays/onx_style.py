"""Canonical onX icon/color constants.

Only entries confirmed against real onX exports (onx_samples/*.gpx) or against
onx_samples/STYLE_RESULTS.md (produced by importing out/_test/onx_test.gpx on
the phone and recording what actually rendered) are used anywhere in this
build. Everything in out/_test/onx_test.gpx beyond TEST 1/2/A/B/C is a GUESS
and is never used for real output until STYLE_RESULTS.md confirms it.
"""
import os
import re

ICON_MINERAL_SITE = "Mineral Site"
ICON_LOCATION = "Location"

COLOR_YELLOW = "rgba(255, 255, 0, 1)"
COLOR_RED = "rgba(255, 51, 0, 1)"
COLOR_BLACK = "rgba(0, 0, 0, 1)"

CONFIRMED_ICONS = {ICON_MINERAL_SITE, ICON_LOCATION}
CONFIRMED_COLORS = {COLOR_YELLOW, COLOR_RED, COLOR_BLACK}

_STYLE_RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "onx_samples", "STYLE_RESULTS.md"
)

# {friendly_name_or_hex: rgba string}, populated from STYLE_RESULTS.md if present.
CONFIRMED_EXTRA_COLORS = {}
CONFIRMED_EXTRA_ICONS = set()


def _load_style_results():
    if not os.path.exists(_STYLE_RESULTS_PATH):
        return
    with open(_STYLE_RESULTS_PATH) as f:
        text = f.read()
    # Expect lines documenting confirmed icon/color pairs, e.g.:
    #   TEST 3 Water Source guess-blue -> CONFIRMED: renders as blue teardrop
    # We only trust an entry if the line contains the literal word CONFIRMED.
    for line in text.splitlines():
        if "CONFIRMED" not in line.upper():
            continue
        icon_match = re.search(r"\b(Water Source|Camp|Parking|Trailhead|Hazard)\b", line)
        color_match = re.search(r"rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)", line)
        if icon_match:
            CONFIRMED_EXTRA_ICONS.add(icon_match.group(1))
        if color_match:
            CONFIRMED_EXTRA_COLORS[color_match.group(0)] = color_match.group(0)


_load_style_results()

ALL_CONFIRMED_ICONS = CONFIRMED_ICONS | CONFIRMED_EXTRA_ICONS
ALL_CONFIRMED_COLORS = CONFIRMED_COLORS | set(CONFIRMED_EXTRA_COLORS.values())


def safe_icon(icon):
    """Fall back to Location if an icon isn't in the confirmed set."""
    return icon if icon in ALL_CONFIRMED_ICONS else ICON_LOCATION


def safe_color(color):
    """Fall back to black if a color isn't in the confirmed set."""
    return color if color in ALL_CONFIRMED_COLORS else COLOR_BLACK


# Per-layer style assignments (style guide section 1). All confirmed-only.
LAYER_STYLES = {
    "1_my_claims": {"pin_icon": ICON_MINERAL_SITE, "color": COLOR_YELLOW, "area_style": "solid"},
    "2_public": {"pin_icon": ICON_LOCATION, "color": COLOR_BLACK, "area_style": "dot"},
    "3_other_claims": {"color": COLOR_RED, "area_style": "dot"},
    "4_history": {"color": COLOR_BLACK},
    "5_scout": {"pin_icon": ICON_LOCATION, "color": COLOR_RED},
    "6_access": {"color": COLOR_BLACK, "line_style": "dash"},
}
