#!/usr/bin/env python3
"""Draw ../adapton-logo-bonsai-dark.svg, the dark-ground Adapton bonsai.

The composition is the original logo's — adapton-logo-bonsai.png, in the root of
this branch, which stays the canonical cream-ground version.  This redraws it for
a black page in the palette of the Fumola VS Code theme, and continues the tree
downward: the pot is cut away, so the roots divide below the soil line and give
out into mycelium, each generation finer and whiter than the one it grew from.

Nothing here is hand-written path data.  The trunk, branches and roots are
tapered ribbons — a Catmull-Rom centerline, sampled, offset either side by a
width that falls off along the curve — which is what makes the trunk read as a
trunk rather than a tube.  The mycelium is a recursive branching walk.  Edit the
control points and the widths below, not the SVG.

    python3 tools/bonsai.py [output.svg]

The mycelium's seed is fixed, so a run with the same control points reproduces
the same SVG byte for byte.
"""
import math
import os
import random
import sys

# ---------- tapered ribbons ------------------------------------------------

def catmull(points, n=160):
    """Sample a Catmull-Rom spline through `points`."""
    p = [points[0]] + list(points) + [points[-1]]
    out = []
    segs = len(p) - 3
    for i in range(segs):
        p0, p1, p2, p3 = p[i], p[i + 1], p[i + 2], p[i + 3]
        steps = max(2, n // segs)
        for s in range(steps + (1 if i == segs - 1 else 0)):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def ribbon(points, w0, w1, power=1.6, flare=0.0, n=64, close_tip=True):
    """A tapered outline along the centerline: width w0 at the start, w1 at the
    end, falling off as t**power.  `flare` widens the last few percent, which is
    how a trunk meets the soil."""
    pts = catmull(points, n)
    m = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / (m - 1)
        a = pts[min(i + 1, m - 1)]
        b = pts[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = w1 + (w0 - w1) * (1 - t) ** power
        if flare and t > 0.86:
            k = (t - 0.86) / 0.14
            w += flare * k * k
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    d = "M%.0f %.0f " % left[0]
    d += " ".join("L%.0f %.0f" % q for q in left[1:])
    if close_tip:
        d += " " + " ".join("L%.0f %.0f" % q for q in reversed(right))
    d += " Z"
    return d


def stroke_path(points, n=120):
    pts = catmull(points, n)
    return "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % q for q in pts[1:])


def tri(cx, apex_y, base_y, hw):
    return "%.0f,%.0f %.0f,%.0f %.0f,%.0f" % (cx, apex_y, cx + hw, base_y, cx - hw, base_y)


def inv_tri(cx, base_y, apex_y, hw):
    return "%.0f,%.0f %.0f,%.0f %.0f,%.0f" % (cx, apex_y, cx + hw, base_y, cx - hw, base_y)


# ---------- the tree -------------------------------------------------------

SOIL_Y = 470

# The trunk's S: leans left on the way up, recovers, and thins to a point.
TRUNK = [(352, 486), (344, 440), (322, 396), (302, 340), (296, 282),
         (306, 224), (326, 168), (342, 110), (350, 50)]

# Branches: each leaves the trunk and curls outward, ending in a hook.
BRANCHES = [
    # left side
    [(324, 178), (280, 168), (256, 176), (248, 194), (260, 204), (272, 196), (268, 184)],
    [(310, 248), (262, 250), (226, 268), (200, 292)],
    [(306, 298), (256, 306), (214, 300), (182, 312), (166, 330), (178, 344), (190, 334)],
    [(322, 402), (288, 414), (262, 412), (246, 400)],
    # right side
    [(330, 152), (376, 140), (410, 146), (438, 160)],
    [(322, 216), (372, 220), (412, 240), (440, 262)],
    [(308, 294), (356, 306), (392, 330), (424, 342)],
    [(322, 352), (368, 378), (410, 402), (452, 402), (472, 390), (466, 374), (452, 382)],
    [(340, 122), (382, 104), (416, 102), (444, 112)],
    [(330, 430), (356, 442), (392, 444), (416, 436)],
]

# Roots: the same curve, continued downward, dividing as it goes.
ROOTS = [
    # (points, w0, w1)
    ([(352, 462), (352, 512), (356, 560), (348, 606), (342, 642)], 36, 3),   # taproot
    ([(320, 466), (286, 506), (246, 538), (204, 568), (168, 596)], 32, 3),
    ([(392, 466), (432, 502), (478, 534), (524, 562), (562, 590)], 32, 3),
    ([(332, 466), (306, 520), (288, 574), (280, 628)], 18, 2),
    ([(378, 466), (400, 522), (418, 578), (428, 630)], 18, 2),
]
ROOTLETS = [
    ([(246, 538), (218, 522), (186, 516), (154, 522)], 9, 2),
    ([(204, 568), (188, 596), (178, 620), (176, 640)], 9, 2),
    ([(478, 534), (508, 518), (542, 514), (572, 520)], 9, 2),
    ([(524, 562), (546, 588), (558, 614), (560, 636)], 9, 2),
    ([(288, 574), (256, 588), (228, 606), (210, 628)], 7, 2),
    ([(418, 578), (450, 592), (478, 610), (496, 630)], 7, 2),
    ([(356, 560), (386, 566), (410, 556), (428, 540)], 8, 2),
    ([(348, 606), (318, 616), (296, 632), (288, 648)], 7, 2),
]

# Mycelium: hyphae carrying on where the finest roots give out.  Each generation
# is thinner and closer to white than the one it grew from, so the eye follows
# the branching outward without being told to.
DEPTH = 6
MYCELIUM_SEEDS = [
    # (x, y, heading in degrees, first length)
    (154, 522, 186, 62), (154, 522, 232, 54), (176, 640, 176, 58),
    (176, 640, 128, 48), (204, 568, 200, 44), (246, 538, 168, 40),
    (210, 628, 158, 46), (288, 648, 150, 40), (288, 648, 196, 36),
    (572, 520, -6, 62), (572, 520, -52, 54), (560, 636, 4, 58),
    (560, 636, 52, 48), (524, 562, -20, 44), (478, 534, 12, 40),
    (496, 630, 22, 46), (428, 540, -30, 40), (342, 642, 96, 34),
    (348, 606, 250, 30), (356, 560, 300, 30),
    (342, 642, 84, 30), (280, 628, 214, 34), (428, 630, -34, 34),
    (186, 516, 214, 40), (542, 514, -34, 40), (296, 632, 200, 30),
    (478, 610, -20, 30), (218, 522, 196, 34), (546, 588, -16, 34),
    (168, 596, 150, 34), (562, 590, 30, 34), (410, 556, -50, 26),
    (386, 566, 70, 26), (318, 616, 240, 26),
]

def lerp_hex(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))

HYPHA_COLORS = [lerp_hex("#9b7fa6", "#ffffff", (d / (DEPTH - 1)) ** 0.62) for d in range(DEPTH)]
HYPHA_WIDTHS = [round(1.8 * (0.71 ** d), 2) for d in range(DEPTH)]
HYPHA_OPACITY = [round(0.62 + 0.05 * d, 2) for d in range(DEPTH)]


def grow(x, y, ang, length, depth, out, rnd):
    """One hypha segment, then its children. Quadratic, so each is four numbers."""
    if depth >= DEPTH or length < 5:
        return
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * length, y + math.sin(a) * length
    # bow the segment sideways a little, so nothing in here is straight
    bow = length * rnd.uniform(0.10, 0.26) * rnd.choice((1, -1))
    mx, my = (x + ex) / 2 - math.sin(a) * bow, (y + ey) / 2 + math.cos(a) * bow
    out[depth].append("M%.0f %.0f Q%.0f %.0f %.0f %.0f" % (x, y, mx, my, ex, ey))
    if not (12 < ex < 648 and SOIL_Y + 4 < ey < 648):
        return
    for _ in range(3 if depth < 2 else rnd.choice((2, 2, 3))):
        grow(ex, ey, ang + rnd.uniform(-46, 46), length * rnd.uniform(0.56, 0.76),
             depth + 1, out, rnd)


# Where the coarse threads meet: the graph underneath, drawn small.
NODES = [(154, 522, 3.6), (176, 640, 3.6), (204, 568, 3.0), (246, 538, 3.0),
         (572, 520, 3.6), (560, 636, 3.6), (524, 562, 3.0), (478, 534, 3.0),
         (210, 628, 3.0), (496, 630, 3.0), (428, 540, 3.0), (342, 642, 3.0)]

# Canopies, as in the original: flat-bottomed triangles, loosely radial.
DARK, MID, TEAL, DEEP = "#3d5c34", "#6A9955", "#3f9098", "#2f6f74"
CANOPY = [
    (tri(296, 30, 92, 36), DARK),
    (tri(374, 16, 96, 56), MID),
    (tri(206, 100, 182, 66), DARK),
    (tri(286, 136, 182, 26), DARK),
    (tri(126, 222, 306, 70), DARK),
    (inv_tri(126, 248, 296, 34), MID),
    (tri(232, 282, 312, 20), DARK),
    (tri(442, 100, 248, 96), MID),
    (tri(576, 86, 168, 56), TEAL),
    (tri(552, 186, 302, 86), DEEP),
    (tri(340, 318, 358, 28), DARK),
    (tri(456, 326, 384, 36), MID),
    (tri(552, 342, 404, 44), DARK),
]
# The nested triangles inside the big one: the recursion the original drew.
NESTED = [
    (tri(442, 130, 176, 24), DARK),
    (tri(418, 178, 224, 24), DARK),
    (tri(466, 178, 224, 24), DEEP),
    (tri(442, 178, 224, 12), DEEP),
    (tri(490, 200, 248, 18), DARK),
]


def main():
    L = []
    add = L.append
    add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 660" width="660" height="660"')
    add('     role="img" aria-labelledby="bonsai-title bonsai-desc">')
    add('  <title id="bonsai-title">The Adapton bonsai</title>')
    add('  <desc id="bonsai-desc">A bonsai with a violet trunk and triangular green canopies. Its pot is')
    add('  drawn in cross-section: roots divide below the soil line and give out into mycelium.</desc>')
    add('')
    add('  <!-- The original Adapton bonsai, recoloured for a dark ground in the palette of')
    add('       the Fumola VS Code theme, and continued downward. Generated geometry: the')
    add('       trunk, branches and roots are tapered ribbons along a Catmull-Rom centerline. -->')
    add('')
    add('  <defs>')
    add('    <linearGradient id="ab-trunk" x1="0" y1="1" x2="0" y2="0">')
    add('      <stop offset="0" stop-color="#7461a8"/><stop offset="1" stop-color="#a989d0"/>')
    add('    </linearGradient>')
    add('    <linearGradient id="ab-root" x1="0" y1="0" x2="0" y2="1">')
    add('      <stop offset="0" stop-color="#7461a8"/><stop offset="1" stop-color="#4b3f70"/>')
    add('    </linearGradient>')
    add('    <clipPath id="ab-soil"><rect x="18" y="%d" width="624" height="%d" rx="10"/></clipPath>'
        % (SOIL_Y, 646 - SOIL_Y))
    add('  </defs>')
    add('')
    add('  <rect x="4" y="4" width="652" height="652" rx="26" fill="#0b0b0d" stroke="#212124" stroke-width="3"/>')
    add('')
    add('  <!-- above the soil -->')
    add('  <g fill="url(#ab-trunk)">')
    for pts, w0, w1 in [(b, 8, 2.2) for b in BRANCHES]:
        add('    <path d="%s"/>' % ribbon(pts, w0, w1, power=1.2))
    add('  </g>')
    add('  <path fill="url(#ab-trunk)" d="%s"/>' % ribbon(TRUNK, 50, 11, power=1.5, flare=54))
    add('')
    add('  <g>')
    for pts, fill in CANOPY:
        add('    <polygon points="%s" fill="%s"/>' % (pts, fill))
    for pts, fill in NESTED:
        add('    <polygon points="%s" fill="%s"/>' % (pts, fill))
    add('  </g>')
    add('')
    add('  <!-- the pot, in cross-section -->')
    add('  <rect x="18" y="%d" width="624" height="%d" rx="10" fill="#17122a"/>' % (SOIL_Y, 646 - SOIL_Y))
    add('  <g clip-path="url(#ab-soil)">')
    add('    <g fill="url(#ab-root)">')
    for pts, w0, w1 in ROOTS:
        add('      <path d="%s"/>' % ribbon(pts, w0, w1, power=1.3))
    for pts, w0, w1 in ROOTLETS:
        add('      <path d="%s"/>' % ribbon(pts, w0, w1, power=1.1))
    add('    </g>')
    rnd = random.Random(11)          # fixed seed: the same mycelium every build
    gens = [[] for _ in range(DEPTH)]
    for x, y, ang, length in MYCELIUM_SEEDS:
        grow(x, y, ang, length, 0, gens, rnd)
    add('    <g fill="none" stroke-linecap="round">')
    for d, segs in enumerate(gens):
        if not segs:
            continue
        add('      <path stroke="%s" stroke-width="%s" opacity="%s" d="%s"/>'
            % (HYPHA_COLORS[d], HYPHA_WIDTHS[d], HYPHA_OPACITY[d], " ".join(segs)))
    add('    </g>')
    add('    <g fill="#6A9955" opacity="0.7">')
    for x, y, r in NODES:
        add('      <circle cx="%d" cy="%d" r="%.1f"/>' % (x, y, r))
    add('    </g>')
    add('  </g>')
    add('  <rect x="18" y="%d" width="624" height="%d" rx="10" fill="none" stroke="#2e2545" stroke-width="2"/>'
        % (SOIL_Y, 646 - SOIL_Y))
    add('</svg>')
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                           "adapton-logo-bonsai-dark.svg")
    out = os.path.normpath(sys.argv[1] if len(sys.argv) > 1 else default)
    with open(out, "w") as f:
        f.write(main())
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))
