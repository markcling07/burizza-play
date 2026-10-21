"""Skill icons for Burizza.

Writes one SVG per skill and passive into this folder, named after it (see slug()):
    skills/<slug>.svg      e.g. "Siren's Hush" -> skills/sirens-hush.svg
plus skills/gallery.html, a preview page grouped by faction.

The game finds an icon by the skill's name, so renaming a skill in index.html
means renaming (or regenerating) its icon. A missing icon just isn't shown.

Run:  python make_icons.py
Every icon = faction frame (gold frame + star for signature skills, round for passives) + a glyph.
Glyphs are drawn on a 64x64 canvas, roughly inside 8..56.
"""
import math
import re
from html import escape
from pathlib import Path

OUT = Path(__file__).parent
INK = '#15121d'

# Faction frame colors: (background top, background bottom, accent)
PAL = {
    'common':  ('#4c4f60', '#18191f', '#c9ccd8'),
    'mech':    ('#3e4c61', '#12171f', '#f0a73a'),
    'orc':     ('#61361f', '#1e0e08', '#d48c3c'),
    'human':   ('#2d4678', '#0e1730', '#e0bb55'),
    'stone':   ('#355d40', '#0e1d12', '#a8d06b'),
    'tide':    ('#1c6b7c', '#091f26', '#7fe3d8'),
    'crimson': ('#5c1a2d', '#18060d', '#e0455a'),
    'undead':  ('#3f5244', '#0e1510', '#8ee696'),
    'riftborn': ('#2a2440', '#0e0c1a', '#b9c0e0'),
    # The Cogbound: cast out of the Ironclad foundries and still running on their fire. Warmer and
    # dirtier than the Union's steel blue, so the two read as kin without reading as the same.
    'cog':     ('#5a4028', '#180f08', '#ffa64d'),
    'monster': ('#4a4038', '#16110d', '#c0a080'),
    # The Stray Banner: masterless blades. Night ink with a crimson edge (Ryuunosuke's trim).
    'stray':   ('#2c2a3c', '#0b0a12', '#c04848'),
}

DEFS = f'''
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f7fc"/><stop offset=".5" stop-color="#aab4c7"/><stop offset="1" stop-color="#5d6780"/></linearGradient>
<linearGradient id="iron" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9aa3b5"/><stop offset="1" stop-color="#454d61"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe9a8"/><stop offset=".55" stop-color="#e0a83c"/><stop offset="1" stop-color="#8a5a14"/></linearGradient>
<linearGradient id="fire" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8391c"/><stop offset=".55" stop-color="#ff9a2e"/><stop offset="1" stop-color="#ffe680"/></linearGradient>
<radialGradient id="fireR" cx=".45" cy=".45" r=".6"><stop offset="0" stop-color="#fff6c2"/><stop offset=".45" stop-color="#ffb43d"/><stop offset="1" stop-color="#d9361a"/></radialGradient>
<linearGradient id="bolt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#a6ecff"/><stop offset="1" stop-color="#3fa2f0"/></linearGradient>
<linearGradient id="blood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff6060"/><stop offset="1" stop-color="#9a0f1c"/></linearGradient>
<linearGradient id="poison" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d6ff86"/><stop offset="1" stop-color="#4c9a28"/></linearGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b4f4ff"/><stop offset="1" stop-color="#2a86b8"/></linearGradient>
<linearGradient id="ink" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9474c4"/><stop offset="1" stop-color="#2a1d40"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c48e56"/><stop offset="1" stop-color="#6b4422"/></linearGradient>
<linearGradient id="leaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c4f58a"/><stop offset="1" stop-color="#3a8a38"/></linearGradient>
<linearGradient id="hex" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e09aff"/><stop offset="1" stop-color="#5a1f7a"/></linearGradient>
<linearGradient id="bone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbf4e2"/><stop offset="1" stop-color="#b8a684"/></linearGradient>
<linearGradient id="heal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d4ffb0"/><stop offset="1" stop-color="#3fae4f"/></linearGradient>
<linearGradient id="mana" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfe6ff"/><stop offset="1" stop-color="#2f6fd0"/></linearGradient>
<linearGradient id="clay" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d98a5a"/><stop offset="1" stop-color="#7a3a1e"/></linearGradient>
<linearGradient id="hide" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a604a"/><stop offset="1" stop-color="#3e2e22"/></linearGradient>
<linearGradient id="demon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c84a4a"/><stop offset="1" stop-color="#5a1418"/></linearGradient>
<radialGradient id="holy" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fffbe6"/><stop offset=".5" stop-color="#ffe08a" stop-opacity=".8"/><stop offset="1" stop-color="#ffd060" stop-opacity="0"/></radialGradient>
<radialGradient id="pearl" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#f2e6f0"/><stop offset="1" stop-color="#b8a8c4"/></radialGradient>
<linearGradient id="grave" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dcffe6"/><stop offset="1" stop-color="#4f8a60"/></linearGradient>
<radialGradient id="graveR" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#eafff0"/><stop offset=".5" stop-color="#9fe8b4" stop-opacity=".75"/><stop offset="1" stop-color="#6fcf8a" stop-opacity="0"/></radialGradient>
<linearGradient id="shroud" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a9a8c"/><stop offset="1" stop-color="#2e3a30"/></linearGradient>
<linearGradient id="gravity" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9da6e0"/><stop offset="1" stop-color="#3a3870"/></linearGradient>
<radialGradient id="gravR" cx=".5" cy=".4" r=".6"><stop offset="0" stop-color="#d0d4ff"/><stop offset=".5" stop-color="#6b74c8"/><stop offset="1" stop-color="#2a2440"/></radialGradient>
<linearGradient id="lightG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff8d0"/><stop offset=".5" stop-color="#e8d26a"/><stop offset="1" stop-color="#a88a20"/></linearGradient>
<linearGradient id="blade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffbe0"/><stop offset=".5" stop-color="#ffe489"/><stop offset="1" stop-color="#e8b23a"/></linearGradient>
<radialGradient id="lightR" cx=".45" cy=".35" r=".6"><stop offset="0" stop-color="#fffef0"/><stop offset=".4" stop-color="#ffe680"/><stop offset="1" stop-color="#c8a030" stop-opacity="0"/></radialGradient>
<linearGradient id="sound" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a8eef4"/><stop offset="1" stop-color="#2a7a8a"/></linearGradient>
<linearGradient id="void" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c89eff"/><stop offset="1" stop-color="#3a1a5c"/></linearGradient>
<radialGradient id="voidR" cx=".5" cy=".5" r=".55"><stop offset="0" stop-color="#15121d"/><stop offset=".5" stop-color="#5a2e8a"/><stop offset="1" stop-color="#c89eff" stop-opacity="0"/></radialGradient>
<linearGradient id="cosmic" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d0d4ff"/><stop offset=".5" stop-color="#8a7ec8"/><stop offset="1" stop-color="#3a2860"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
<filter id="ds" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="1.4" stdDeviation="1" flood-color="#000" flood-opacity=".55"/></filter>
'''


# ---------------------------------------------------------------- helpers
def T(x, y, r=0, s=1):
    out = f'translate({x} {y})'
    if r:
        out += f' rotate({r})'
    if s != 1:
        out += f' scale({s})'
    return out


def g(content, x=0, y=0, r=0, s=1, extra=''):
    return f'<g transform="{T(x, y, r, s)}"{extra}>{content}</g>'


def star_pts(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append(f'{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}')
    return ' '.join(pts)


def burst(cx, cy, r_in, r_out, n=10, fill='url(#fireR)', rot=-90, extra=''):
    return f'<polygon points="{star_pts(cx, cy, r_out, r_in, n, rot)}" fill="{fill}"{extra}/>'


def line(x1, y1, x2, y2, color, w=2.4, outline=True):
    """A line with an ink outline underneath."""
    out = ''
    if outline:
        out += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="{w + 2.4}"/>'
    return out + f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>'


def poly(d, color, w=2.4):
    """An open path stroked in color over an ink outline."""
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 2.4}"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"/>')


def glow(content, opacity=.8):
    return f'<g filter="url(#blur)" opacity="{opacity}" stroke="none">{content}</g>'


def twinkle(x, y, s=1, fill='#ffe680'):
    return g(f'<path d="M0 -5 L1.3 -1.3 L5 0 L1.3 1.3 L0 5 L-1.3 1.3 L-5 0 L-1.3 -1.3 Z" fill="{fill}" stroke-width="1"/>', x, y, 0, s)


def stun_stars(x, y, w=26):
    return twinkle(x - w / 2, y, .8) + twinkle(x, y - 4, 1) + twinkle(x + w / 2, y, .8)


def speed_lines(x, y, n=3, length=10, gap=5, color='#ffffff', angle=0, op=.7):
    out = ''
    for i in range(n):
        yy = y + (i - (n - 1) / 2) * gap
        ln = length * (1 if i == (n - 1) // 2 else .65)
        out += f'<line x1="{x}" y1="{yy}" x2="{x + ln}" y2="{yy}" stroke="{color}" stroke-width="2" opacity="{op}"/>'
    return g(out, 0, 0, angle) if angle else out


def arc_lines(cx, cy, r0, n, spread, color, rot=0, w=2.2, step=5):
    """Concentric arcs (sound waves / ripples) facing angle rot."""
    out = ''
    for i in range(n):
        r = r0 + i * step
        a0, a1 = math.radians(rot - spread / 2), math.radians(rot + spread / 2)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        out += f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{color}" stroke-width="{w}" opacity="{1 - i * .22:.2f}"/>'
    return out


# ---------------------------------------------------------------- primitives (local coords, origin = center)
def sword(blade='url(#steel)'):
    return (f'<path d="M0 -25 L3.4 -20 L3.4 7 L-3.4 7 L-3.4 -20 Z" fill="{blade}"/>'
            '<line x1="0" y1="-19" x2="0" y2="5" stroke="#5d6780" stroke-width="1"/>'
            '<rect x="-9.5" y="6.5" width="19" height="4" rx="1.6" fill="url(#gold)"/>'
            '<rect x="-1.9" y="10.5" width="3.8" height="8" fill="#5a3520"/>'
            '<circle cx="0" cy="20.5" r="2.8" fill="url(#gold)"/>')


def axe(head='url(#steel)'):
    return ('<rect x="-1.9" y="-20" width="3.8" height="40" rx="1.6" fill="url(#wood)"/>'
            f'<path d="M1.5 -17 L8 -19.5 Q20 -13 17.5 0 Q13 -4 8 -4.5 L1.5 -6.5 Z" fill="{head}"/>'
            '<path d="M-1.5 -16 L-6 -14 L-6 -9 L-1.5 -8 Z" fill="url(#iron)"/>'
            '<rect x="-2.6" y="-19" width="5.2" height="4" rx="1" fill="url(#iron)"/>')


def hammer(head='url(#iron)'):
    return ('<rect x="-1.9" y="-12" width="3.8" height="32" rx="1.6" fill="url(#wood)"/>'
            f'<rect x="-12" y="-22" width="24" height="12" rx="2.2" fill="{head}"/>'
            '<rect x="-3.5" y="-22" width="7" height="12" fill="url(#gold)"/>'
            '<circle cx="0" cy="20" r="2.4" fill="url(#iron)"/>')


def mace():
    spikes = burst(0, -15, 6, 10.5, 8, 'url(#iron)')
    return ('<rect x="-1.9" y="-10" width="3.8" height="30" rx="1.6" fill="url(#wood)"/>'
            + spikes + '<circle cx="0" cy="-15" r="6.5" fill="url(#steel)"/>')


def arrow(tip='url(#steel)', fletch='#e0455a', length=40):
    h = length / 2
    return (f'<line x1="0" y1="{h - 2}" x2="0" y2="{-h + 8}" stroke="{INK}" stroke-width="4.6"/>'
            f'<line x1="0" y1="{h - 2}" x2="0" y2="{-h + 8}" stroke="#b07a46" stroke-width="2.2"/>'
            f'<path d="M0 {-h} L5.5 {-h + 10} L0 {-h + 7.5} L-5.5 {-h + 10} Z" fill="{tip}"/>'
            f'<path d="M0 {h - 9} L-5 {h - 3} L-5 {h + 2} L0 {h - 3} Z" fill="{fletch}"/>'
            f'<path d="M0 {h - 9} L5 {h - 3} L5 {h + 2} L0 {h - 3} Z" fill="{fletch}"/>')


def flame(fill='url(#fire)', inner='#fff1a0'):
    return (f'<path d="M0 -21 C4 -13 12 -9 12 3 C12 11 6 16 0 16 C-6 16 -12 11 -12 3 C-12 -4 -7 -7 -6 -14 C-3 -9 -2 -9 0 -21 Z" fill="{fill}"/>'
            f'<path d="M0 -5 C3 0 7 3 6 8.5 C5.5 12 3 14 0 14 C-3 14 -6 12 -6 8.5 C-6 4.5 -3 2.5 0 -5 Z" fill="{inner}" stroke="none"/>')


def bolt(fill='url(#bolt)'):
    return f'<path d="M3 -22 L-9 3 L-1.5 3 L-5 22 L10 -5 L2.5 -5 L8.5 -22 Z" fill="{fill}"/>'


def bolt(tip='url(#steel)', vane='#9ac46b', length=34):
    """A crossbow bolt: shorter and thicker than an arrow, broad head, stubby vanes."""
    h = length / 2
    return (f'<line x1="0" y1="{h - 2}" x2="0" y2="{-h + 9}" stroke="{INK}" stroke-width="6.4"/>'
            f'<line x1="0" y1="{h - 2}" x2="0" y2="{-h + 9}" stroke="#8a5a32" stroke-width="3.4"/>'
            f'<path d="M0 {-h} L7 {-h + 11} L0 {-h + 8} L-7 {-h + 11} Z" fill="{tip}"/>'
            f'<path d="M0 {h - 7} L-5.5 {h - 1} L-4 {h + 2} L0 {h - 2} Z" fill="{vane}"/>'
            f'<path d="M0 {h - 7} L5.5 {h - 1} L4 {h + 2} L0 {h - 2} Z" fill="{vane}"/>')


def drop(fill='url(#blood)'):
    return f'<path d="M0 -8 C3 -3.5 5.2 -.5 5.2 2.8 A5.2 5.2 0 0 1 -5.2 2.8 C-5.2 -.5 -3 -3.5 0 -8 Z" fill="{fill}"/>'


def heater(fill='url(#steel)', rim='url(#gold)'):
    return (f'<path d="M0 -21 L17 -16 L16 2 Q13 14 0 22 Q-13 14 -16 2 L-17 -16 Z" fill="{rim}"/>'
            f'<path d="M0 -17 L13.5 -13 L12.5 2 Q10 11 0 17.5 Q-10 11 -12.5 2 L-13.5 -13 Z" fill="{fill}" stroke-width="1.2"/>')


def plus(fill='url(#heal)'):
    return f'<path d="M-4.5 -13 H4.5 V-4.5 H13 V4.5 H4.5 V13 H-4.5 V4.5 H-13 V-4.5 H-4.5 Z" fill="{fill}"/>'


def heart(fill='url(#blood)'):
    return f'<path d="M0 10 C-14 1 -12 -10 -5.5 -10 C-2.5 -10 -.8 -8 0 -6 C.8 -8 2.5 -10 5.5 -10 C12 -10 14 1 0 10 Z" fill="{fill}"/>'


def sawblade(r=17, teeth=14, fill='url(#steel)'):
    pts = []
    for i in range(teeth):
        a0 = 2 * math.pi * i / teeth
        a1 = a0 + 2 * math.pi / teeth * .55
        pts.append(f'{r * math.cos(a0):.1f},{r * math.sin(a0):.1f}')
        pts.append(f'{(r + 5) * math.cos(a1):.1f},{(r + 5) * math.sin(a1):.1f}')
        pts.append(f'{r * math.cos(a1 + .05):.1f},{r * math.sin(a1 + .05):.1f}')
    return (f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'
            f'<circle r="{r * .55:.1f}" fill="none" stroke="#5d6780" stroke-width="1"/>'
            '<circle r="5.5" fill="url(#gold)"/><circle r="2" fill="#2a2a33"/>')


def gear(r=7, teeth=8, fill='#f0a73a'):
    pts = []
    for i in range(teeth * 2):
        rr = r + 2.6 if i % 2 == 0 else r
        for k in (-.28, .28):
            a = math.pi * i / teeth + k * math.pi / teeth
            pts.append(f'{rr * math.cos(a):.1f},{rr * math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/><circle r="{r * .4:.1f}" fill="#2a2a33"/>'


def skull(fill='url(#bone)', eye='#2a1a1a'):
    return (f'<path d="M-11 -2 C-11 -12 -6 -16 0 -16 C6 -16 11 -12 11 -2 C11 3 8 5 7 6 L7 11 L-7 11 L-7 6 C-8 5 -11 3 -11 -2 Z" fill="{fill}"/>'
            f'<ellipse cx="-4.6" cy="-2.5" rx="3.2" ry="3.6" fill="{eye}"/>'
            f'<ellipse cx="4.6" cy="-2.5" rx="3.2" ry="3.6" fill="{eye}"/>'
            f'<path d="M0 2 L-1.8 5.5 L1.8 5.5 Z" fill="{eye}" stroke="none"/>'
            '<path d="M-3.5 7.5 V11 M0 7.5 V11 M3.5 7.5 V11" stroke-width="1"/>')


def mechfist(main='url(#steel)'):
    """Blocky mech fist punching right; spans roughly -21..19 x -12..12."""
    return ('<rect x="-21" y="-6.5" width="18" height="13" rx="2" fill="url(#iron)"/>'
            '<rect x="-18" y="-11" width="12" height="4" rx="1.5" fill="#f0a73a"/>'
            '<rect x="-18" y="7" width="12" height="4" rx="1.5" fill="#f0a73a"/>'
            f'<rect x="-4" y="-12" width="22" height="24" rx="4.5" fill="{main}"/>'
            '<path d="M10 -6 H18 M10 0 H18 M10 6 H18" stroke-width="1.4"/>'
            '<rect x="-1" y="5" width="9" height="6" rx="2" fill="url(#iron)" stroke-width="1.2"/>'
            '<circle cx="1" cy="-7" r="1.3" fill="#f0a73a" stroke="none"/><circle cx="1" cy="-1" r="1.3" fill="#f0a73a" stroke="none"/>')


def wrench(fill='url(#iron)'):
    return (f'<rect x="-3" y="-6" width="6" height="27" rx="3" fill="{fill}"/>'
            f'<path d="M4 -21 A9 9 0 1 1 -4 -21 L-4 -14 L4 -14 Z" fill="{fill}"/>')


def spear(head='url(#steel)', length=46):
    h = length / 2
    return (f'<line x1="0" y1="{h}" x2="0" y2="{-h + 9}" stroke="{INK}" stroke-width="5"/>'
            f'<line x1="0" y1="{h}" x2="0" y2="{-h + 9}" stroke="#b07a46" stroke-width="2.6"/>'
            f'<path d="M0 {-h - 2} C4.5 {-h + 4} 4.5 {-h + 8} 0 {-h + 12} C-4.5 {-h + 8} -4.5 {-h + 4} 0 {-h - 2} Z" fill="{head}"/>'
            f'<rect x="-2.6" y="{-h + 11}" width="5.2" height="3" fill="#c9b28a" stroke-width="1"/>')


def trident(fill='url(#gold)'):
    return ('<rect x="-1.7" y="-10" width="3.4" height="34" rx="1.5" fill="url(#iron)"/>'
            f'<rect x="-11.5" y="-13" width="23" height="4.2" rx="1.6" fill="{fill}"/>'
            f'<path d="M-2.2 -12 V-21 L0 -27 L2.2 -21 V-12 Z" fill="{fill}"/>'
            f'<path d="M-11.5 -10 V-20 L-9.8 -25 L-8 -20 V-10 Z" fill="{fill}"/>'
            f'<path d="M11.5 -10 V-20 L9.8 -25 L8 -20 V-10 Z" fill="{fill}"/>')


def dagger(blade='url(#steel)'):
    return (f'<path d="M0 -15 L2.6 -10 L2.4 2 L-2.4 2 L-2.6 -10 Z" fill="{blade}"/>'
            '<rect x="-6" y="1.5" width="12" height="3" rx="1.2" fill="#e05a9a"/>'
            '<rect x="-1.4" y="4.5" width="2.8" height="6" fill="#3d1f4a"/>')


def rapier():
    return ('<path d="M0 -27 L1.5 -24 L1.5 6 L-1.5 6 L-1.5 -24 Z" fill="url(#steel)"/>'
            '<path d="M-9 6 Q-9 -1 0 -1 Q9 -1 9 6 Z" fill="url(#gold)"/>'
            '<rect x="-12" y="5.5" width="24" height="3" rx="1.4" fill="url(#gold)"/>'
            '<rect x="-1.6" y="8.5" width="3.2" height="8" fill="#3a2433"/>'
            '<circle cx="0" cy="18" r="2.5" fill="#c0303f"/>')


def octo(fill='url(#ink)', eyes=True):
    body = (f'<path d="M-12 0 C-12 -11 -7 -16 0 -16 C7 -16 12 -11 12 0 Q15 6 16 14 Q11 11 8 6 Q8 12 5 17 Q2 12 2 7 '
            f'Q0 9 -2 7 Q-2 12 -5 17 Q-8 12 -8 6 Q-11 11 -16 14 Q-15 6 -12 0 Z" fill="{fill}"/>')
    if eyes:
        body += ('<ellipse cx="-4.8" cy="-5" rx="3" ry="3.4" fill="#fff6dc" stroke-width="1"/><circle cx="-4.2" cy="-4.5" r="1.4" fill="#15121d" stroke="none"/>'
                 '<ellipse cx="4.8" cy="-5" rx="3" ry="3.4" fill="#fff6dc" stroke-width="1"/><circle cx="5.4" cy="-4.5" r="1.4" fill="#15121d" stroke="none"/>')
    return body


def jaws(lip='#5fa38a'):
    return ('<ellipse rx="14" ry="10" fill="#3a0e14"/>'
            '<path d="M-12.5 -4 Q0 -12 12.5 -4 L10 2 L7.5 -3 L5 3 L2.5 -4 L0 3 L-2.5 -4 L-5 3 L-7.5 -3 L-10 2 Z" fill="#fbf4e2" stroke-width="1"/>'
            '<path d="M-11 5 Q0 11 11 5 L8.5 0 L6 5 L3.5 -1 L1 5 L-1.5 -1 L-4 5 L-6.5 -1 L-9 4 Z" fill="#fbf4e2" stroke-width="1"/>'
            f'<ellipse rx="14" ry="10" fill="none" stroke="{lip}" stroke-width="3.4"/>'
            '<ellipse rx="15.8" ry="11.8" fill="none" stroke-width="1"/>')


def note(fill='#f2c6d8'):
    return (f'<ellipse cx="-4" cy="9" rx="5" ry="3.8" fill="{fill}" transform="rotate(-20 -4 9)"/>'
            f'<rect x="-0.4" y="-12" width="2.8" height="21" fill="{fill}" stroke-width="1"/>'
            f'<path d="M1 -12 Q10 -9 9 -1 Q7 -6 1 -6 Z" fill="{fill}"/>')


# ---------------------------------------------------------------- the icons
ICONS = {}


def icon(name):
    def wrap(fn):
        ICONS[name] = fn
        return fn
    return wrap


# ---- common
@icon('Attack')
def _():
    return g(sword(), 32, 32, 45, 1.05) + twinkle(49, 15, .8, '#ffffff')


@icon('Guard')
def _():
    return (g(heater(), 32, 32, 0, 1.05)
            + '<path d="M32 21 V43 M23 28 H41" stroke="#d9b44a" stroke-width="3"/>'
            + '<path d="M32 21 V43 M23 28 H41" stroke="#8a5a14" stroke-width="1" fill="none"/>')


# ---- Ironclad Union
@icon('Piston Punch')
def _():
    return (speed_lines(6, 33, 3, 9, 6, '#f0a73a') + g(mechfist(), 31, 33)
            + burst(53, 33, 4, 9, 8, '#ffd166'))


@icon('Hydraulic Slam')
def _():
    return ('<rect x="7" y="47" width="50" height="8" rx="2" fill="#5a4a3a"/>'
            '<path d="M32 47 L27 55 M32 47 L38 55 M32 47 L32 52" stroke-width="1.4"/>'
            + burst(32, 46, 4, 10, 10, '#ffd166')
            + g(mechfist(), 32, 24, 90, .9) + twinkle(13, 36, .8) + twinkle(51, 36, .8))


@icon('Rip Saw')
def _():
    return (g(sawblade(16), 32, 32, 8)
            + '<path d="M9 22 A24 24 0 0 1 22 9" fill="none" stroke="#ffd166" stroke-width="2.6"/>'
            + '<path d="M55 42 A24 24 0 0 1 42 55" fill="none" stroke="#ffd166" stroke-width="2.6"/>')


@icon('Grinder')
def _():
    return (g(sawblade(15, 16), 30, 29, 0)
            + '<path d="M18 18 L22 21 M39 16 L37 20 M44 33 L40 32" stroke="#c81e2a" stroke-width="2.4"/>'
            + g(drop(), 46, 48, 0, .85) + g(drop(), 37, 53, 0, .65) + g(drop(), 53, 39, 0, .55))


@icon('Arc Bolt')
def _():
    return (glow(g(bolt('#7fe3ff'), 30, 30, 10, 1.1)) + g(bolt(), 30, 30, 10, 1.05)
            + g(drop('url(#mana)'), 47, 44, 0, .75) + g(drop('url(#mana)'), 52, 53, 0, .55)
            + g(drop('url(#mana)'), 43, 54, 0, .45))


@icon('Chain Surge')
def _():
    zig = ('M32 22 L25 30 L29 33 L15 49', 'M32 22 L34 32 L29 37 L32 51', 'M32 22 L40 30 L36 34 L49 49')
    return (glow('<circle cx="32" cy="20" r="9" fill="#7fe3ff"/>')
            + ''.join(poly(d, '#bff3ff', 2.2) for d in zig)
            + '<circle cx="32" cy="19" r="6.5" fill="url(#bolt)"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="4" fill="url(#bolt)"/>' for x, y in ((15, 49), (32, 51), (49, 49))))


@icon('Flak Burst')
def _():
    shards = ''.join(g('<rect x="-2" y="-3" width="4" height="6" rx="1" fill="url(#iron)" stroke-width="1"/>', x, y, r)
                     for x, y, r in ((12, 14, 30), (52, 13, -20), (11, 50, -35), (53, 51, 25), (32, 8, 0), (32, 57, 0)))
    return (glow('<circle cx="32" cy="32" r="16" fill="#ff9a2e"/>', .7) + shards
            + burst(32, 32, 9, 20, 12) + burst(32, 32, 5, 11, 10, '#fff1a0', -72))


@icon('Siege Shell')
def _():
    shell = ('<path d="M0 -22 C6 -16 7.5 -10 7.5 -4 V14 H-7.5 V-4 C-7.5 -10 -6 -16 0 -22 Z" fill="url(#steel)"/>'
             '<rect x="-7.5" y="5" width="15" height="10" fill="url(#gold)"/>'
             '<rect x="-7.5" y="-3" width="15" height="3.5" fill="#e0455a"/>')
    return (glow(g(flame(), 20, 44, 225, .9), .7) + g(flame(), 21, 43, 225, .75)
            + g(shell, 36, 28, 45, 1.05))


@icon('Field Weld')
def _():
    return (g(heater('#7fe3ff', '#7fe3ff'), 32, 33, 0, 1.2, ' opacity=".28"')
            + g(wrench(), 27, 35, -40, 1.0)
            + glow(g(plus('#8be28b'), 45, 19, 0, .75)) + g(plus(), 45, 19, 0, .7)
            + twinkle(37, 44, .7) + twinkle(43, 49, .5))


@icon('Assemble Scrapbot')
def _():
    return ('<path d="M32 42 L20 55 M32 42 L44 55 M32 42 V55" stroke-width="2.6"/>'
            '<path d="M32 42 L20 55 M32 42 L44 55 M32 42 V55" stroke="#8a826e" stroke-width="1.2"/>'
            '<rect x="43" y="29" width="13" height="6" rx="1.5" fill="url(#iron)"/>'
            '<rect x="18" y="21" width="27" height="22" rx="5" fill="#a39a86"/>'
            '<line x1="25" y1="21" x2="22" y2="13" stroke-width="1.6"/><circle cx="22" cy="12" r="2.2" fill="#8be28b"/>'
            + glow('<circle cx="30" cy="32" r="5" fill="#8be28b"/>')
            + '<circle cx="30" cy="32" r="4.6" fill="#8be28b"/><circle cx="31" cy="31" r="1.5" fill="#fff" stroke="none"/>'
            + g(gear(5.5), 49, 15))


# ---- Bloodtusk Horde
@icon('Cleave')
def _():
    return ('<path d="M7 36 Q30 62 57 34 Q31 50 7 36 Z" fill="#ffffff" opacity=".9" stroke="none"/>'
            '<path d="M7 36 Q30 62 57 34" fill="none" stroke="#ffd18a" stroke-width="1.4"/>'
            + g(axe(), 30, 29, -35, 1.1))


@icon('Blood Frenzy')
def _():
    return (glow('<circle cx="32" cy="32" r="18" fill="#e0242f"/>', .55)
            + g(axe(), 32, 32, -30, 1.0)
            + g('<g transform="scale(-1 1)">' + axe() + '</g>', 32, 32, 30, 1.0)
            + g(drop(), 18, 22, 0, .6) + g(drop(), 46, 22, 0, .6) + g(drop(), 32, 52, 0, .7))


@icon('Skull Rattler')
def _():
    return (g(skull(), 39, 40, 12, .95)
            + '<path d="M50 26 Q54 30 52 35 M54 22 Q60 28 57 37" fill="none" stroke="#ffd166" stroke-width="2"/>'
            + '<path d="M24 50 Q20 54 23 58" fill="none" stroke="#ffd166" stroke-width="2"/>'
            + g(mace(), 22, 25, -50, .95) + twinkle(30, 26, .8))


@icon('Iron Hide')
def _():
    return (glow('<circle cx="32" cy="32" r="20" fill="#e0242f"/>', .45)
            + burst(32, 32, 15, 22, 12, 'url(#iron)')
            + '<circle cx="32" cy="32" r="15.5" fill="url(#hide)"/>'
            + '<circle cx="32" cy="32" r="15.5" fill="none" stroke="#9aa3b5" stroke-width="2.4"/>'
            + '<circle cx="32" cy="32" r="17" fill="none" stroke-width="1"/>'
            + '<path d="M25 35 Q22 26 26 21 Q26 28 29 33 Z" fill="url(#bone)" stroke-width="1.2"/>'
            + '<path d="M39 35 Q42 26 38 21 Q38 28 35 33 Z" fill="url(#bone)" stroke-width="1.2"/>'
            + '<circle cx="32" cy="37" r="4" fill="url(#gold)"/>')


@icon('Call the War Boar')
def _():
    return ('<path d="M20 22 L15 9 L27 17 Z" fill="#5a4636"/><path d="M44 22 L49 9 L37 17 Z" fill="#5a4636"/>'
            '<path d="M32 14 C44 14 50 22 50 32 C50 42 44 50 32 53 C20 50 14 42 14 32 C14 22 20 14 32 14 Z" fill="url(#hide)"/>'
            '<path d="M24 16 L27 10 L30 15 L32 8 L34 15 L37 10 L40 16 Z" fill="#2b1e16"/>'
            '<path d="M20 26 L28 29 M44 26 L36 29" stroke-width="2"/>'
            '<circle cx="25" cy="31" r="2.4" fill="#ff4a3a" stroke="none"/><circle cx="39" cy="31" r="2.4" fill="#ff4a3a" stroke="none"/>'
            '<ellipse cx="32" cy="43" rx="9.5" ry="7" fill="#a07a5e"/>'
            '<ellipse cx="28.5" cy="43" rx="1.8" ry="2.6" fill="#2b1e16" stroke="none"/><ellipse cx="35.5" cy="43" rx="1.8" ry="2.6" fill="#2b1e16" stroke="none"/>'
            '<path d="M24 46 Q15 46 15 34 Q19 41 26 42 Z" fill="url(#bone)"/>'
            '<path d="M40 46 Q49 46 49 34 Q45 41 38 42 Z" fill="url(#bone)"/>')


@icon('Gutpiercer')
def _():
    plate = ('<path d="M-13 -14 Q0 -19 13 -14 L12 6 Q8 15 0 18 Q-8 15 -12 6 Z" fill="url(#iron)"/>'
             '<path d="M0 -17 V17" stroke-width="1"/>'
             '<path d="M-6 -4 L-2 1 L-5 6 M6 -6 L3 -1 L7 3" stroke-width="1.2"/>')
    return (g(plate, 30, 34, -8, 1.05)
            + burst(31, 33, 3, 7, 8, '#2a1a1a')
            + g(spear(), 32, 32, 45, 1.1)
            + g(drop(), 49, 23, 0, .6) + g(drop(), 45, 27, 0, .45))


@icon('Firepot')
def _():
    return (glow(g(flame(), 32, 19, 0, .7), .7) + g(flame(), 32, 19, 0, .62)
            + '<ellipse cx="32" cy="41" rx="13" ry="12" fill="url(#clay)"/>'
            + '<rect x="26" y="26" width="12" height="6" fill="url(#clay)"/>'
            + '<rect x="24" y="24.5" width="16" height="4" rx="2" fill="#a0522d"/>'
            + '<path d="M20 40 Q32 45 44 40" fill="none" stroke-width="2.2"/>'
            + '<path d="M20 40 Q32 45 44 40" fill="none" stroke="#e8a548" stroke-width="1"/>')


@icon('Powder Keg')
def _():
    return ('<path d="M17 25 Q15 39 17 54 H43 Q45 39 43 25 Z" fill="url(#wood)"/>'
            '<ellipse cx="30" cy="25" rx="13" ry="3.6" fill="#8a5a32"/>'
            '<path d="M24 26 Q22 40 24 54 M36 26 Q38 40 36 54" stroke-width="1"/>'
            '<path d="M16.5 31 H43.5 M16.5 48 H43.5" stroke="#454d61" stroke-width="2.6"/>'
            '<path d="M16.5 31 H43.5 M16.5 48 H43.5" stroke="#9aa3b5" stroke-width="1"/>'
            '<path d="M24 37 L27 40 L24 43 M36 37 L33 40 L36 43" stroke="#2a1a1a" stroke-width="1.6"/>'
            + poly('M30 24 Q31 14 40 15 Q46 16 47 12', '#c9b28a', 1.6)
            + burst(48, 11, 3, 8, 9, '#ffd166') + burst(48, 11, 1.5, 4, 6, '#ffffff', -60, ' stroke="none"'))


@icon('Spirit Ward')
def _():
    return (glow('<circle cx="32" cy="32" r="19" fill="#bff0ff"/>', .45)
            + '<circle cx="32" cy="32" r="18" fill="#bff0ff" fill-opacity=".18" stroke="#bff0ff" stroke-width="2.2"/>'
            + '<circle cx="32" cy="32" r="13" fill="none" stroke="#bff0ff" stroke-width="1" stroke-dasharray="3 3" opacity=".8"/>'
            + poly('M32 32 m0 -1 a2 2 0 1 1 -2 2 a4 4 0 1 1 5 -4 a7 7 0 1 1 -8 7', '#e0645a', 2.2)
            + twinkle(47, 15, .7, '#ffffff') + twinkle(15, 47, .6, '#ffffff') + twinkle(50, 45, .5, '#ffffff'))


@icon('Drums of the Horde')
def _():
    return (arc_lines(32, 40, 18, 2, 70, '#ff8a3d', 180, 2.2) + arc_lines(32, 40, 18, 2, 70, '#ff8a3d', 0, 2.2)
            + '<path d="M18 35 V50 Q32 57 46 50 V35 Z" fill="#8a3a2a"/>'
            + '<path d="M18 37 L25 52 L32 38 L39 52 L46 37" fill="none" stroke="#e8dcc4" stroke-width="1.4"/>'
            + '<ellipse cx="32" cy="35" rx="14" ry="5" fill="#e8dcc4"/>'
            + g('<rect x="-1.5" y="-14" width="3" height="18" rx="1.5" fill="url(#wood)"/><circle cy="-15" r="3" fill="#e8dcc4"/>', 24, 22, -35)
            + g('<rect x="-1.5" y="-14" width="3" height="18" rx="1.5" fill="url(#wood)"/><circle cy="-15" r="3" fill="#e8dcc4"/>', 40, 22, 35))


# ---- Kingdom of Aldmere
@icon('Power Slash')
def _():
    return ('<path d="M10 14 Q50 12 54 52 Q44 24 10 14 Z" fill="#ffffff" opacity=".9" stroke="none"/>'
            '<path d="M10 14 Q50 12 54 52" fill="none" stroke="#e0bb55" stroke-width="1.4"/>'
            + g(sword(), 27, 36, 45, 1.0))


@icon('Thunderclap')
def _():
    return (glow('<circle cx="32" cy="30" r="15" fill="#7fe3ff"/>', .55)
            + g(sword('url(#bolt)'), 32, 33, 0, 1.0)
            + g(bolt(), 15, 26, -15, .5) + g(bolt(), 49, 26, 15, .5)
            + twinkle(18, 46, .7) + twinkle(46, 46, .7))


@icon('Smite')
def _():
    return (f'<circle cx="32" cy="30" r="22" fill="url(#holy)" stroke="none"/>'
            + g(hammer('url(#steel)'), 30, 31, -30, 1.0)
            + g(heart(), 47, 47, 0, .62) + g(plus('#ffffff'), 47, 46, 0, .25))


@icon('Oathguard')
def _():
    arrows = ('<path d="M51 22 A21 21 0 0 1 54 38" fill="none" stroke="#7fe3ff" stroke-width="2.4"/>'
              '<path d="M50 40 L55 40 L55 34" fill="none" stroke="#7fe3ff" stroke-width="2.4"/>'
              '<path d="M13 42 A21 21 0 0 1 10 26" fill="none" stroke="#7fe3ff" stroke-width="2.4"/>'
              '<path d="M14 24 L9 24 L9 30" fill="none" stroke="#7fe3ff" stroke-width="2.4"/>')
    return (arrows + g(heater('#3e5a8c'), 32, 32, 0, 1.0)
            + '<path d="M32 21 V42 M24 28 H40" stroke="url(#gold)" stroke-width="3.2"/>')


@icon('Aimed Shot')
def _():
    return ('<circle cx="32" cy="32" r="17" fill="none" stroke="#e0bb55" stroke-width="2.4"/>'
            '<circle cx="32" cy="32" r="10" fill="none" stroke="#e0bb55" stroke-width="1.4" opacity=".8"/>'
            '<path d="M32 8 V20 M32 44 V56 M8 32 H20 M44 32 H56" stroke="#e0bb55" stroke-width="2.4"/>'
            '<circle cx="32" cy="32" r="4.5" fill="url(#steel)"/><circle cx="32" cy="32" r="1.6" fill="#e0455a" stroke="none"/>'
            + twinkle(49, 15, .8, '#ffffff'))


@icon('Powder Shot')
def _():
    musket = ('<path d="M-25 -1 L-8 -3 L-6 3 L-25 7 Q-27 3 -25 -1 Z" fill="url(#wood)"/>'
              '<rect x="-8" y="-2.5" width="30" height="4.2" rx="1" fill="url(#iron)"/>'
              '<rect x="-12" y="-4.5" width="5" height="3" fill="url(#gold)" stroke-width="1"/>')
    return ('<circle cx="53" cy="34" r="4.5" fill="#8a8a96" opacity=".7" stroke="none"/><circle cx="56" cy="41" r="3.2" fill="#8a8a96" opacity=".55" stroke="none"/>'
            + burst(47, 25, 4, 11, 9) + burst(47, 25, 2, 5, 7, '#fff1a0', -50, ' stroke="none"')
            + g(musket, 27, 37, -32, 1.0))


@icon('Fireball')
def _():
    return (glow(g(flame(), 34, 30, 45, 1.0), .6) + g(flame(), 34, 30, 45, .95)
            + '<circle cx="26" cy="38" r="11" fill="url(#fireR)"/>'
            + '<circle cx="23" cy="35" r="3.5" fill="#fffbe0" stroke="none" opacity=".9"/>')


@icon('Inferno')
def _():
    return (glow('<ellipse cx="32" cy="44" rx="22" ry="10" fill="#ff7a2e"/>', .7)
            + g(flame(), 17, 41, -8, .7) + g(flame(), 47, 41, 8, .7) + g(flame(), 32, 35, 0, 1.0)
            + '<rect x="9" y="51" width="46" height="4" rx="2" fill="#5a2a1a"/>')


@icon('Sacred Light')
def _():
    rays = ''.join(g(f'<path d="M-2 0 L0 {-25 if i % 2 == 0 else -18} L2 0 Z" fill="#ffe08a" stroke="none" opacity=".9"/>', 32, 32, i * 30)
                   for i in range(12))
    return (rays + '<circle cx="32" cy="32" r="16" fill="url(#holy)" stroke="none"/>'
            + '<circle cx="32" cy="32" r="10" fill="#fffbe6"/>'
            + g(plus('url(#gold)'), 32, 32, 0, .55))


@icon('Prayer of Dawn')
def _():
    rays = ''.join(g('<path d="M-2 -15 L0 -26 L2 -15 Z" fill="#ffe08a" stroke="none"/>', 32, 42, a)
                   for a in (-75, -50, -25, 0, 25, 50, 75))
    return (rays + glow('<circle cx="32" cy="42" r="15" fill="#ffd060"/>', .7)
            + '<path d="M18 42 A14 14 0 0 1 46 42 Z" fill="url(#gold)"/>'
            + '<rect x="7" y="42" width="50" height="12" rx="2" fill="#1d2c55"/>'
            + '<path d="M11 47 H23 M30 47 H40 M45 50 H53" stroke="#6fb5e6" stroke-width="1.4"/>'
            + g(drop('url(#mana)'), 13, 22, 0, .6) + g(drop('url(#mana)'), 51, 22, 0, .6))


# ---- Stoneleaf Accord
@icon('Hammerfall')
def _():
    return ('<path d="M10 26 A26 26 0 0 1 26 9" fill="none" stroke="#ffffff" stroke-width="2.4" opacity=".75"/>'
            '<path d="M15 31 A22 22 0 0 1 30 14" fill="none" stroke="#ffffff" stroke-width="2" opacity=".5"/>'
            '<rect x="8" y="51" width="48" height="5" rx="2" fill="#4a3a2e"/>'
            + burst(42, 50, 4, 10, 10, '#ffd166')
            + g(hammer(), 32, 27, 150, 1.0))


@icon('Mountain Breaker')
def _():
    return ('<path d="M7 54 L28 16 L35 27 L40 21 L57 54 Z" fill="url(#iron)"/>'
            '<path d="M28 16 L22 27 L27 25 L31 29 L35 27 Z" fill="#f4f7fc" stroke-width="1.2"/>'
            '<path d="M30 54 L33 44 L28 37 L33 30 L31 22" fill="none" stroke="#ffd166" stroke-width="2.6"/>'
            '<path d="M30 54 L33 44 L28 37 L33 30 L31 22" fill="none" stroke="#fff6c2" stroke-width="1"/>'
            + g(hammer(), 45, 16, 40, .6) + burst(34, 21, 2.5, 6, 8, '#ffd166'))


@icon('Shield Bash')
def _():
    return (speed_lines(6, 34, 3, 10, 6, '#ffffff')
            + '<circle cx="30" cy="34" r="15" fill="#8a5a32"/>'
            + '<path d="M30 19 V49 M15 34 H45" stroke="#5e3a1c" stroke-width="1.4"/>'
            + '<circle cx="30" cy="34" r="15" fill="none" stroke="#9aa3b5" stroke-width="2.6"/>'
            + '<circle cx="30" cy="34" r="16.6" fill="none" stroke-width="1"/>'
            + '<circle cx="30" cy="34" r="5" fill="url(#steel)"/>'
            + burst(49, 33, 4, 9, 8, '#ffd166') + stun_stars(32, 14, 20))


@icon('Stand Firm')
def _():
    return (arc_lines(32, 32, 20, 2, 60, '#ff6a5a', 180) + arc_lines(32, 32, 20, 2, 60, '#ff6a5a', 0)
            + '<path d="M12 56 L18 47 L27 50 L33 45 L41 49 L47 46 L53 56 Z" fill="#6b6f7a"/>'
            + g(heater('#40597a', 'url(#gold)'), 32, 29, 0, 1.0)
            + '<path d="M26 24 L32 20 L38 24 L38 32 L32 37 L26 32 Z" fill="#c9a25e" stroke-width="1.2"/>')


@icon('Swift Arrows')
def _():
    return (g(arrow(), 25, 27, 45, .95) + g(arrow(), 38, 39, 45, .95)
            + '<path d="M8 32 L14 38 M20 48 L26 54" stroke="#ffffff" stroke-width="2" opacity=".6"/>')


@icon('Hawkeye')
def _():
    return ('<path d="M32 9 V18 M32 46 V55 M9 32 H16 M48 32 H55" stroke="#ffffff" stroke-width="2" opacity=".85"/>'
            '<path d="M12 32 Q32 12 52 32 Q32 52 12 32 Z" fill="#f4f0e2"/>'
            '<circle cx="32" cy="32" r="9" fill="url(#gold)"/>'
            '<circle cx="32" cy="32" r="4" fill="#15121d" stroke="none"/>'
            '<circle cx="29" cy="29" r="1.8" fill="#ffffff" stroke="none"/>'
            '<path d="M12 32 Q20 26 26 24" fill="none" stroke="#3f7a4f" stroke-width="2"/>'
            + twinkle(49, 15, 1, '#ffffff'))


@icon('Venom Bolt')
def _():
    return (glow('<circle cx="43" cy="21" r="8" fill="#b8ff6a"/>', .8)
            + g(bolt('url(#poison)', '#3f7a4f'), 31, 33, 45, 1.15)
            + g(drop('url(#poison)'), 47, 33, 0, .6) + g(drop('url(#poison)'), 53, 25, 0, .45))


@icon('Thornvolley')
def _():
    vine = ('M7 52 Q16 44 24 52 T40 52 T57 50')
    thorns = ''.join(f'<path d="M{x} {y} l2 -4 l2 4 Z" fill="#9ac46b" stroke-width="1"/>' for x, y in ((12, 49), (28, 53), (44, 51)))
    return (g(arrow('url(#poison)', '#9ac46b', 30), 17, 22, 180, .9)
            + g(arrow('url(#poison)', '#9ac46b', 30), 32, 28, 180, .9)
            + g(arrow('url(#poison)', '#9ac46b', 30), 47, 22, 180, .9)
            + poly(vine, '#3f7a4f', 2.4) + thorns)


@icon('Regrowth')
def _():
    return ('<path d="M12 54 Q32 42 52 54 Z" fill="#6b4422"/>'
            + poly('M32 50 Q30 38 33 28', '#4c9a28', 2.4)
            + '<path d="M33 30 C24 30 18 24 17 17 C25 16 32 21 33 30 Z" fill="url(#leaf)"/>'
            + '<path d="M33 34 C40 34 47 29 48 21 C40 21 34 26 33 34 Z" fill="url(#leaf)"/>'
            + glow(g(plus('#b8ff6a'), 47, 44, 0, .4)) + g(plus(), 47, 44, 0, .38)
            + twinkle(18, 36, .6, '#d4ffb0'))


@icon('Bloom of Spring')
def _():
    petals = ''.join(g('<ellipse cx="0" cy="-10" rx="5.5" ry="9" fill="#f7c6dc"/>', 32, 29, a) for a in range(0, 360, 60))
    return ('<path d="M32 40 V56" stroke="#2f6a2a" stroke-width="3"/>'
            '<path d="M32 50 C24 50 19 46 17 40 C24 39 30 43 32 50 Z" fill="url(#leaf)"/>'
            '<path d="M32 47 C40 47 45 43 47 37 C40 36 34 40 32 47 Z" fill="url(#leaf)"/>'
            + petals + '<circle cx="32" cy="29" r="5.5" fill="url(#gold)"/>'
            + twinkle(12, 14, .7, '#d4ffb0') + twinkle(52, 12, .6, '#d4ffb0') + twinkle(53, 46, .5, '#d4ffb0'))


# ---- The Tideborn
@icon('Trident Lunge')
def _():
    return ('<path d="M7 43 L13 37 M21 57 L27 51 M12 52 L16 48" stroke="#7fe3d8" stroke-width="2" opacity=".7"/>'
            + g(trident(), 30, 34, 45, 1.0) + g(drop(), 51, 22, 0, .65))


@icon('Blood in the Water')
def _():
    return ('<path d="M22 44 Q28 22 44 13 Q39 28 44 44 Z" fill="#7d93a6"/>'
            '<path d="M44 13 Q39 28 44 44 L39 44 Q35 30 44 13 Z" fill="#53687a" stroke="none"/>'
            '<path d="M6 44 Q12 40 18 44 T30 44 T42 44 T58 43 V56 H6 Z" fill="#b8202e"/>'
            '<path d="M6 49 Q12 45 18 49 T30 49 T42 49 T58 48" fill="none" stroke="#ff7a7a" stroke-width="1.4"/>'
            + g(drop(), 14, 30, 0, .55) + g(drop(), 53, 28, 0, .45))


@icon('Rimebite')
def _():
    # Two bites now instead of three nibbles, and the cold comes off them.
    return (g(jaws('#5fb2dc'), 24, 25, -15, .74) + g(jaws('#5fb2dc'), 43, 43, -15, .66)
            + '<path d="M11 42 L17 46 M13 52 L18 55" stroke="#bff3ff" stroke-width="2.2" opacity=".75"/>'
            + twinkle(15, 17, .8, '#dcf8ff'))


@icon('Glacial Frenzy')
def _():
    motes = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#bff3ff" fill-opacity=".3" stroke="#bff3ff" stroke-width="1.2"/>'
                    for x, y, r in ((12, 14, 3.5), (52, 12, 2.6), (54, 50, 3.2), (11, 50, 2.4), (47, 22, 1.8)))
    return (motes + glow('<ellipse cx="32" cy="33" rx="20" ry="15" fill="#4fc8f0"/>', .5)
            + g(jaws('#5fb2dc'), 32, 33, 0, 1.15)
            + '<path d="M8 30 L13 32 M56 30 L51 32 M32 10 V15" stroke="#9fe8ff" stroke-width="2.2"/>')


@icon("Siren's Hush")
def _():
    return (g(note('#ffffff'), 29, 31, 0, 1.3)
            + '<circle cx="32" cy="32" r="18" fill="none" stroke="#15121d" stroke-width="5.4"/>'
            + '<circle cx="32" cy="32" r="18" fill="none" stroke="#e0455a" stroke-width="3"/>'
            + '<line x1="19.3" y1="19.3" x2="44.7" y2="44.7" stroke="#15121d" stroke-width="5.4"/>'
            + '<line x1="19.3" y1="19.3" x2="44.7" y2="44.7" stroke="#e0455a" stroke-width="3"/>')


@icon('Lure Song')
def _():
    return (poly('M32 34 m0 0 a2.5 2.5 0 1 1 3 -3 a5 5 0 1 1 -7 6 a9 9 0 1 1 12 -11 a13 13 0 1 1 -17 16', '#f2c6d8', 1.8)
            + g(note(), 17, 20, -12, .7) + g(note('#bff3ff'), 49, 41, 12, .62)
            + g(heart('#ff7ab0'), 32, 34, 0, .38))


@icon('Ink Double')
def _():
    return (g(octo('#9474c4', False), 23, 30, -8, .95,
              ' opacity=".5" stroke-dasharray="2.5 2"')
            + g(octo(), 38, 34, 0, 1.0))


@icon('Ink Cloud')
def _():
    return ('<path d="M14 40 C7 40 7 30 14 29 C13 20 24 17 28 22 C31 14 44 14 46 23 C54 22 58 31 52 36 C57 42 50 48 44 45 '
            'C41 51 31 51 28 46 C22 50 13 47 14 40 Z" fill="url(#ink)"/>'
            '<path d="M22 47 Q22 53 20 56 M34 48 Q35 53 33 57 M44 46 Q46 50 45 53" fill="none" stroke="#5a4a8a" stroke-width="2.6"/>'
            '<path d="M22 34 Q32 42 42 34" fill="none" stroke="#e8dcff" stroke-width="2.2"/>'
            '<path d="M25 37 L23 41 M32 39 V43 M39 37 L41 41" stroke="#e8dcff" stroke-width="1.6"/>')


@icon('Healing Tide')
def _():
    return ('<path d="M7 50 C11 34 22 23 36 23 C47 23 54 31 51 39 C49 44 42 44 41 39 C40 34 35 33 32 36 C27 41 29 47 35 50 Z" fill="url(#water)"/>'
            '<path d="M14 42 C18 32 26 27 35 27 C43 27 49 31 49 37" fill="none" stroke="#ffffff" stroke-width="1.6" opacity=".8"/>'
            '<rect x="6" y="49" width="52" height="6" rx="2" fill="#2a86b8"/>'
            + glow(g(plus('#b8ff6a'), 47, 15, 0, .55)) + g(plus(), 47, 15, 0, .5))


@icon('Pearl Barrier')
def _():
    ridges = ''.join(f'<line x1="32" y1="50" x2="{32 + 15 * math.cos(math.radians(a)):.1f}" y2="{50 - 13 * math.sin(math.radians(a)):.1f}" stroke-width="1"/>'
                     for a in (30, 60, 90, 120, 150))
    return ('<circle cx="32" cy="34" r="23" fill="#bff3ff" fill-opacity=".15" stroke="#bff3ff" stroke-width="2.2"/>'
            '<path d="M44 20 A16 16 0 0 1 50 30" fill="none" stroke="#ffffff" stroke-width="2" opacity=".7"/>'
            '<path d="M17 37 Q15 21 32 19 Q49 21 47 37 Q32 33 17 37 Z" fill="#e8b4cc"/>'
            '<path d="M32 34 L24 22 M32 34 V20 M32 34 L40 22" stroke-width="1"/>'
            '<path d="M14 50 Q16 37 32 37 Q48 37 50 50 Q32 56 14 50 Z" fill="#f2c6d8"/>'
            + ridges + '<circle cx="32" cy="37" r="7" fill="url(#pearl)"/>')


# ---- The Crimson Court
@icon('Crimson Lunge')
def _():
    return (glow('<path d="M22 42 L48 16" stroke="#ff3a4a" stroke-width="7"/>', .7)
            + g(rapier(), 28, 36, 45, 1.0)
            + g(drop(), 50, 15, 0, .6) + g(drop(), 51, 31, 0, .45) + g(drop(), 41, 45, 0, .4))


@icon('Execute')
def _():
    # The warband's blood, gathered into one beam that pours down from the sky onto the doomed:
    # drops streaming in from both sides at the top, the torrent, and a skull splashed under it.
    beam = '<path d="M27 5 H37 L43 40 H21 Z" fill="#ff2a3e"/>'
    return (glow(beam, .75)
            + '<path d="M27.5 5 H36.5 L41 40 H23 Z" fill="url(#blood)" stroke-width="1.2"/>'
            + '<path d="M31 5 H33 L34.5 40 H29.5 Z" fill="#ffc0c8" stroke="none"/>'
            + g(skull(), 32, 47, 0, .82)
            + burst(32, 36.5, 3, 9.5, 8, '#ff3a4a', extra=' stroke-width="1"')
            + burst(32, 36.5, 1.5, 4.8, 8, '#ffe0e4', extra=' stroke="none"')
            + g(drop(), 13, 14, 55, .62) + g(drop(), 51, 14, -55, .62)
            + g(drop(), 18, 24, 40, .45) + g(drop(), 46, 24, -40, .45))


@icon('Exsanguinate')
def _():
    return ('<path d="M9 22 Q32 12 55 22 Q48 34 32 34 Q16 34 9 22 Z" fill="#7a1424"/>'
            '<path d="M14 25 Q32 31 50 25 L49 28 Q32 34 15 28 Z" fill="#fbf4e2" stroke-width="1"/>'
            '<path d="M21 28 L24 44 L27 30 Z" fill="#fbf4e2"/><path d="M43 28 L40 44 L37 30 Z" fill="#fbf4e2"/>'
            + g(drop(), 24, 50, 0, .55) + g(drop(), 40, 52, 0, .65)
            + '<path d="M24 41 V44 M40 41 V45" stroke="#c81e2a" stroke-width="2"/>')


@icon('Hellfire Slam')
def _():
    return (glow('<ellipse cx="32" cy="48" rx="24" ry="8" fill="#ff4a1a"/>', .8)
            + '<ellipse cx="32" cy="49" rx="23" ry="6" fill="#3a0e0e"/>'
            + '<path d="M32 49 L22 52 M32 49 L42 53 M32 49 L30 54" stroke="#ff9a2e" stroke-width="1.6"/>'
            + g(flame(), 13, 41, -15, .5) + g(flame(), 51, 41, 15, .5)
            + g(axe('url(#demon)'), 30, 25, 160, .95))


@icon('Infernal Wrath')
def _():
    horns = ('<path d="M-9 -12 C-16 -16 -18 -24 -14 -30 C-13 -24 -9 -21 -4 -16 Z" fill="#2a1a1f"/>'
             '<path d="M9 -12 C16 -16 18 -24 14 -30 C13 -24 9 -21 4 -16 Z" fill="#2a1a1f"/>')
    return (glow(g(flame(), 32, 30, 0, 1.4), .7) + g(flame('url(#fire)', '#ffb43d'), 32, 28, 0, 1.25, ' opacity=".55"')
            + g(horns + skull('url(#demon)', '#ffd166'), 32, 38, 0, 1.0)
            + glow('<circle cx="27.4" cy="35.5" r="3" fill="#ffd166"/><circle cx="36.6" cy="35.5" r="3" fill="#ffd166"/>', .9))


@icon('Kiss of Ruin')
def _():
    return (glow('<circle cx="20" cy="18" r="6" fill="#9a4ad0"/><circle cx="44" cy="16" r="5" fill="#9a4ad0"/>', .9)
            + poly('M22 26 Q18 18 23 12 M42 24 Q46 17 42 10', '#b07ae0', 1.6)
            + '<path d="M10 34 Q20 22 32 30 Q44 22 54 34 Q44 37 32 36 Q20 37 10 34 Z" fill="#e05a9a"/>'
            + '<path d="M10 34 Q20 37 32 36 Q44 37 54 34 Q44 50 32 50 Q20 50 10 34 Z" fill="#b83a78"/>'
            + '<path d="M14 34.5 Q32 39 50 34.5" fill="none" stroke-width="1.2"/>'
            + '<path d="M50 44 L50 54 M46 50 L50 55 L54 50" fill="none" stroke="#b07ae0" stroke-width="2.4"/>')


@icon('Dance of Knives')
def _():
    knives = ''.join(g(g(dagger(), 0, -13), 32, 32, a) for a in range(0, 360, 72))
    return ('<circle cx="32" cy="32" r="20" fill="none" stroke="#e05a9a" stroke-width="1.6" stroke-dasharray="6 5" opacity=".8"/>'
            + knives + burst(32, 32, 2.5, 6, 8, '#ff9ad0'))


@icon('Rend')
def _():
    slash = '<path d="M0 -22 Q5 0 0 22 Q-2 0 0 -22 Z" fill="url(#blood)"/>'
    return (g(slash, 22, 31, 25, 1.0) + g(slash, 32, 32, 25, 1.08) + g(slash, 42, 33, 25, 1.0)
            + g(drop(), 16, 52, 0, .5) + g(drop(), 50, 50, 0, .45))


@icon('Hellhound Howl')
def _():
    return (arc_lines(42, 20, 5, 3, 70, '#ff9a2e', 25, 2.2, 4.5)
            + '<g transform="translate(-4 4)">'
            + '<path d="M18 56 L21 38 C22 30 26 25 31 21 L41 12 L44 16 L39 22 L47 21 L42 27 C38 31 37 35 37 41 L40 56 Z" fill="url(#demon)"/>'
            + '<path d="M28 23 L23 12 L33 19 Z" fill="#4a1f1f"/>'
            + '<path d="M21 44 L17 41 M22 37 L18 33 M38 45 L42 43" stroke="#ff7a2f" stroke-width="2"/>'
            + glow('<circle cx="33" cy="25" r="2.6" fill="#ffd166"/>', 1)
            + '<circle cx="33" cy="25" r="1.9" fill="#ffd166" stroke="none"/></g>')


@icon('Blight Hex')
def _():
    hexpts = ' '.join(f'{32 + 19 * math.cos(math.radians(a)):.1f},{32 + 19 * math.sin(math.radians(a)):.1f}' for a in range(-90, 270, 60))
    cross = g(plus(), 32, 32, 0, .78)
    return (glow(f'<polygon points="{hexpts}" fill="#a04ad0"/>', .55)
            + f'<polygon points="{hexpts}" fill="#2a0f30" stroke="#d07aff" stroke-width="2.2"/>'
            + '<clipPath id="hexA"><polygon points="0,0 63,0 0,63"/></clipPath>'
            + '<clipPath id="hexB"><polygon points="65,1 65,65 1,65"/></clipPath>'
            + f'<g clip-path="url(#hexA)"><g transform="translate(-1.5 -1.5)">{cross}</g></g>'
            + f'<g clip-path="url(#hexB)" opacity=".35"><g transform="translate(1.5 1.5)">{cross}</g></g>'
            + '<path d="M17 47 L47 17" stroke="#d07aff" stroke-width="2"/>')


@icon('Blood Communion')
def _():
    return ('<path d="M18 16 H46 Q46 34 32 36 Q18 34 18 16 Z" fill="url(#gold)"/>'
            '<ellipse cx="32" cy="17" rx="13" ry="3" fill="#b8202e"/>'
            '<path d="M21 17 Q20 24 22 26 Q24 22 24 18 Z M40 17 Q42 22 41 27 Q39 23 38 18 Z" fill="#b8202e" stroke-width="1"/>'
            '<rect x="30" y="35" width="4" height="12" fill="url(#gold)"/>'
            '<path d="M22 54 Q22 46 32 46 Q42 46 42 54 Z" fill="url(#gold)"/>'
            '<circle cx="32" cy="27" r="2.4" fill="#c0303f" stroke-width="1"/>'
            + g(drop(), 22, 33, 0, .5) + g(drop(), 46, 34, 0, .55))


# ---- Summons
# The Scrapbot's turret fires light, so both glyphs are beams rather than the steel rivets they
# used to draw: a green hairline with a white core, and the flare where it lands. Green is #8be28b,
# the bot's own trim (SUMMONS.scrapbot.look), the same colour as .proj-laser in flight.
def _beam(x1, y1, x2, y2, w=2.0):
    return (poly(f'M{x1} {y1} L{x2} {y2}', '#5ac46e', w)
            + f'<path d="M{x1 + 2} {y1} L{x2} {y2}" stroke="#f2fff2" stroke-width="{w * .55}" stroke-linecap="round"/>')


@icon('Beam Shot')
def _():
    return (_beam(9, 32, 45, 32, 2.4)
            + burst(49, 32, 2.4, 8.5, 8, '#eaffea')
            + twinkle(15, 21, .5, '#8be28b'))


@icon('Beam Burst')
def _():
    # Three at once, fanned out of the one barrel.
    return (_beam(9, 32, 43, 17) + _beam(9, 32, 45, 32) + _beam(9, 32, 43, 47)
            + burst(46, 16, 1.7, 6.2, 7, '#eaffea')
            + burst(48, 32, 1.7, 6.2, 7, '#eaffea')
            + burst(46, 48, 1.7, 6.2, 7, '#eaffea'))


@icon('Ink Lash')
def _():
    suckers = ''.join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#e8dcff" stroke="none"/>' for x, y in ((20, 46), (27, 37), (35, 30), (43, 25)))
    return ('<path d="M10 56 C10 42 20 36 30 32 C40 28 46 24 50 14 C53 22 48 30 40 34 C30 39 18 44 16 56 Z" fill="url(#ink)"/>'
            + suckers + burst(51, 13, 2.5, 6, 7, '#5a4a8a'))


@icon('Gore')
def _():
    return (burst(46, 18, 4, 9, 8, '#ffd166')
            + '<path d="M14 54 C14 38 26 24 44 18 C34 28 28 40 26 54 Z" fill="url(#bone)"/>'
            + '<path d="M18 50 C20 40 26 32 34 26" fill="none" stroke="#b8a684" stroke-width="1.4"/>')


@icon('Tusk Charge')
def _():
    tusk = '<path d="M0 0 C-8 0 -12 -8 -10 -18 C-7 -11 -3 -7 4 -5 Z" fill="url(#bone)"/>'
    return (speed_lines(5, 32, 3, 10, 7, '#e8dcc4')
            + g(tusk, 32, 40) + g('<g transform="scale(-1 1)">' + tusk + '</g>', 44, 40)
            + '<ellipse cx="38" cy="42" rx="8" ry="5.5" fill="#a07a5e"/>'
            + '<ellipse cx="35" cy="42" rx="1.6" ry="2.2" fill="#2b1e16" stroke="none"/><ellipse cx="41" cy="42" rx="1.6" ry="2.2" fill="#2b1e16" stroke="none"/>'
            + stun_stars(40, 18, 18))


# ================================================================ second skills
# ---- Ironclad Union
@icon('Steam Vent')
def _():
    puffs = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#eef2f8" opacity="{o}" stroke="none"/>'
                    for x, y, r, o in ((32, 24, 9, .95), (22, 20, 7, .85), (42, 19, 7.5, .85), (14, 28, 5.5, .7), (50, 27, 6, .7), (32, 12, 6, .6)))
    return (glow(puffs, .6) + puffs
            + '<path d="M18 34 Q20 30 18 26 M46 34 Q44 30 46 26" fill="none" stroke="#ff9a2e" stroke-width="1.8" opacity=".8"/>'
            + '<rect x="20" y="38" width="24" height="14" rx="2.5" fill="url(#iron)"/>'
            + '<path d="M24 42 H40 M24 46 H40" stroke-width="1.6"/>'
            + '<rect x="17" y="36" width="30" height="4" rx="1.5" fill="#f0a73a"/>')


@icon('Shrapnel Spin')
def _():
    shards = ''.join(g('<path d="M-3 -2 L3 -3 L2 3 L-2 2 Z" fill="url(#steel)" stroke-width="1"/>', x, y, r)
                     for x, y, r in ((10, 18, 20), (54, 16, -30), (9, 46, 60), (55, 48, -15), (32, 7, 45), (33, 57, 10)))
    return ('<circle cx="32" cy="32" r="21" fill="none" stroke="#ffd166" stroke-width="2" stroke-dasharray="9 7" opacity=".85"/>'
            + shards + g(sawblade(11, 12), 32, 32, 15))


@icon('Discharge')
def _():
    return (glow('<circle cx="34" cy="38" r="13" fill="#6fb5e6"/>', .7)
            + '<circle cx="34" cy="38" r="12" fill="url(#mana)"/>'
            + '<path d="M28 30 L32 36 L29 40 L34 46 M40 32 L37 38 L41 42" fill="none" stroke="#ffffff" stroke-width="1.6"/>'
            + g(bolt(), 25, 22, -25, .75)
            + g('<path d="M-2 -2 L2 -3 L1 2 Z" fill="#bfe6ff" stroke-width="1"/>', 50, 30, 20)
            + g('<path d="M-2 -2 L2 -3 L1 2 Z" fill="#bfe6ff" stroke-width="1"/>', 48, 50, 70)
            + g('<path d="M-2 -2 L2 -3 L1 2 Z" fill="#bfe6ff" stroke-width="1"/>', 19, 49, -40))


@icon('AP Round')
def _():
    plate = ('<rect x="-13" y="-15" width="26" height="30" rx="4" fill="url(#iron)"/>'
             '<path d="M-13 -5 H13 M-13 5 H13" stroke-width="1"/>'
             '<circle cx="-9" cy="-11" r="1.2" fill="#2a2a33" stroke="none"/><circle cx="9" cy="-11" r="1.2" fill="#2a2a33" stroke="none"/>')
    shell = ('<path d="M0 -20 L5 -10 L5 12 H-5 V-10 Z" fill="url(#steel)"/>'
             '<path d="M0 -20 L5 -10 H-5 Z" fill="#3a3f4f"/>'
             '<rect x="-5" y="6" width="10" height="6" fill="url(#gold)"/>')
    return (g(plate, 28, 36, -10) + burst(32, 32, 3, 8, 8, '#ffd166')
            + g(shell, 36, 28, 45, 1.0)
            + '<path d="M10 52 L16 46 M18 56 L22 52" stroke="#ffffff" stroke-width="2" opacity=".6"/>')


@icon('Overclock')
def _():
    ticks = ''.join(g('<line x1="0" y1="-17" x2="0" y2="-13" stroke-width="1.6"/>', 32, 38, a) for a in range(-80, 81, 32))
    return ('<path d="M12 40 A20 20 0 0 1 52 40 Z" fill="#2a2f3d"/>'
            '<path d="M44.2 24.2 A20 20 0 0 1 52 40 H44 A12 12 0 0 0 40.5 31.5 Z" fill="#e0455a" stroke="none" opacity=".9"/>'
            '<path d="M12 40 A20 20 0 0 1 52 40" fill="none" stroke="url(#gold)" stroke-width="3"/>'
            + ticks
            + '<line x1="32" y1="38" x2="46" y2="27" stroke="#15121d" stroke-width="4.2"/><line x1="32" y1="38" x2="46" y2="27" stroke="#ffd166" stroke-width="2"/>'
            + '<circle cx="32" cy="38" r="3.2" fill="url(#gold)"/>'
            + '<path d="M22 52 L32 45 L42 52" fill="none" stroke="#f0a73a" stroke-width="3"/>'
            + '<path d="M22 57 L32 50 L42 57" fill="none" stroke="#f0a73a" stroke-width="3" opacity=".6"/>')


# ---- Bloodtusk Horde
@icon('Reckless Swing')
def _():
    shield = ('<path d="M-8 -9 L8 -9 L7 3 Q4 9 0 11 Q-4 9 -7 3 Z" fill="url(#hide)"/>'
              '<path d="M-1 -9 L2 -2 L-2 3 L1 11" fill="none" stroke="#ff6a5a" stroke-width="1.6"/>')
    return ('<path d="M10 20 A26 26 0 0 1 44 9" fill="none" stroke="#ff6a5a" stroke-width="3" opacity=".85"/>'
            '<path d="M14 27 A22 22 0 0 1 42 15" fill="none" stroke="#ff6a5a" stroke-width="2" opacity=".55"/>'
            + g(axe(), 34, 32, 25, 1.15) + g(shield, 16, 46, -12, .8))


@icon('Ground Pound')
def _():
    return (arc_lines(32, 48, 16, 2, 60, '#ffd166', 180, 2.4, 6) + arc_lines(32, 48, 16, 2, 60, '#ffd166', 0, 2.4, 6)
            + '<rect x="8" y="47" width="48" height="8" rx="2" fill="#5a4636"/>'
            + '<path d="M32 47 L26 55 M32 47 L39 55" stroke-width="1.4"/>'
            + burst(32, 45, 4, 9, 9, '#ffd166')
            + g(mace(), 32, 26, 180, 1.0)
            + twinkle(16, 22, .8) + twinkle(48, 22, .8))


@icon("Hunter's Mark")
def _():
    return ('<circle cx="32" cy="32" r="18" fill="none" stroke="#e0242f" stroke-width="2.6"/>'
            '<circle cx="32" cy="32" r="18" fill="#e0242f" fill-opacity=".12" stroke="none"/>'
            '<path d="M32 8 V16 M32 48 V56 M8 32 H16 M48 32 H56" stroke="#e0242f" stroke-width="2.6"/>'
            + ''.join(g('<path d="M0 -10 Q3 0 0 10 Q-1.5 0 0 -10 Z" fill="url(#blood)"/>', x, 32, 20, 1.0) for x in (26, 32, 38)))


@icon('Napalm Jar')
def _():
    return (glow(g(flame(), 32, 18, 0, .6), .6) + g(flame(), 32, 18, 0, .55)
            + '<path d="M22 28 Q20 44 24 50 H40 Q44 44 42 28 Z" fill="url(#clay)"/>'
            + '<rect x="24" y="25" width="16" height="5" rx="2" fill="#a0522d"/>'
            + '<path d="M22 32 Q26 36 24 42 Q27 38 29 34 Q30 40 33 36 Q36 41 38 35 Q40 39 42 32" fill="#ff8a1d" stroke-width="1.2"/>'
            + g(drop('url(#fire)'), 25, 53, 0, .5) + g(drop('url(#fire)'), 38, 55, 0, .45))


@icon('Bone Charm')
def _():
    bone = ('<circle cx="-10" cy="-3" r="3.4" fill="url(#bone)"/><circle cx="-10" cy="3" r="3.4" fill="url(#bone)"/>'
            '<circle cx="10" cy="-3" r="3.4" fill="url(#bone)"/><circle cx="10" cy="3" r="3.4" fill="url(#bone)"/>'
            '<rect x="-10" y="-2.6" width="20" height="5.2" fill="url(#bone)"/>'
            '<path d="M-10 -2.6 H10 M-10 2.6 H10" stroke="#fbf4e2" stroke-width="1.6"/>')
    return (glow('<circle cx="32" cy="36" r="14" fill="#bff0ff"/>', .45)
            + '<path d="M14 10 Q32 22 50 10" fill="none" stroke="#8a5a32" stroke-width="2"/>'
            + '<line x1="32" y1="16" x2="32" y2="26" stroke="#8a5a32" stroke-width="2"/>'
            + g(bone, 32, 33, 0, 1.0)
            + '<path d="M24 40 L22 50 L26 46 Z M40 40 L42 50 L38 46 Z" fill="url(#bone)" stroke-width="1.2"/>'
            + '<path d="M32 40 Q35 47 32 55 Q29 47 32 40 Z" fill="#e0645a"/>'
            + twinkle(16, 30, .6, '#ffffff') + twinkle(49, 28, .6, '#ffffff'))


# ---- Kingdom of Aldmere
@icon('Arcane Edge')
def _():
    runes = ''.join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#e8dcff" stroke="none"/>' for x, y in ((26, 30), (30, 26), (34, 22)))
    return (glow(g('<path d="M0 -25 L3.4 -20 L3.4 7 L-3.4 7 L-3.4 -20 Z" fill="#9a6aff"/>', 32, 32, 45, 1.2), .9)
            + g(sword('url(#ink)'), 32, 32, 45, 1.05) + runes
            + poly('M14 50 a8 8 0 1 1 10 -6', '#b07ae0', 1.6) + twinkle(50, 14, .8, '#e8dcff') + twinkle(44, 22, .5, '#e8dcff'))


@icon('Consecrate')
def _():
    pillars = ''.join(f'<rect x="{x - 2.5}" y="12" width="5" height="34" fill="#ffe08a" opacity=".55" stroke="none"/>' for x in (18, 32, 46))
    return (glow(pillars, .9) + pillars
            + '<ellipse cx="32" cy="47" rx="23" ry="7" fill="#ffd060" fill-opacity=".25" stroke="url(#gold)" stroke-width="2.4"/>'
            + '<ellipse cx="32" cy="47" rx="15" ry="4.4" fill="none" stroke="#ffe08a" stroke-width="1.2" stroke-dasharray="3 2"/>'
            + g(plus('url(#gold)'), 32, 28, 0, .55))


@icon('Ricochet')
def _():
    return (poly('M8 48 L30 14 L54 40', '#e0bb55', 1.6)
            + '<path d="M8 48 L30 14 L54 40" fill="none" stroke="#fff6c2" stroke-width="1" stroke-dasharray="3 3"/>'
            + burst(30, 14, 3, 8, 8, '#ffd166')
            + '<rect x="22" y="8" width="16" height="4" rx="1" fill="url(#iron)"/>'
            + '<circle cx="54" cy="40" r="4.5" fill="url(#steel)"/>' + burst(54, 40, 5, 10, 8, '#ffd166', -90, ' opacity=".7"')
            + '<circle cx="9" cy="48" r="3" fill="#8a8a96" stroke="none" opacity=".8"/>')


@icon('Ignite')
def _():
    return (burst(32, 40, 8, 20, 12, 'url(#fireR)', -90, ' opacity=".9"')
            + glow(g(flame(), 32, 30, 0, 1.0), .7) + g(flame(), 32, 30, 0, .95)
            + '<path d="M24 52 L40 52 M28 56 L36 56" stroke="#5a2a1a" stroke-width="3"/>'
            + twinkle(14, 18, .7, '#ffd166') + twinkle(50, 16, .8, '#ffd166'))


@icon('Guardian Angel')
def _():
    wing = ('<path d="M0 0 C-6 -10 -16 -14 -24 -12 C-20 -8 -21 -5 -18 -2 C-22 -1 -22 2 -19 4 C-22 6 -20 9 -16 9 C-10 10 -4 7 0 4 Z" fill="#f4f7fc"/>'
            '<path d="M-6 -2 C-10 -4 -14 -5 -18 -5 M-6 2 C-10 2 -14 2 -17 1" fill="none" stroke-width="1"/>')
    return ('<ellipse cx="32" cy="12" rx="9" ry="3" fill="none" stroke="#ffe08a" stroke-width="2.4"/>'
            + g(wing, 28, 30, 0, 1.0) + g('<g transform="scale(-1 1)">' + wing + '</g>', 36, 30, 0, 1.0)
            + g(heater('#2d4678'), 32, 36, 0, .7) + g(plus('url(#heal)'), 32, 35, 0, .4))


# ---- Stoneleaf Accord
@icon('Anvil Strike')
def _():
    return ('<path d="M12 36 H46 Q46 42 40 43 L38 48 H44 V54 H18 V48 H24 L22 43 Q14 42 12 36 Z" fill="url(#iron)"/>'
            '<path d="M46 36 Q54 36 56 33 Q54 40 46 40 Z" fill="url(#iron)"/>'
            '<path d="M12 36 H46" stroke="#9aa3b5" stroke-width="1"/>'
            + burst(30, 34, 3, 9, 9, '#ffd166')
            + ''.join(f'<line x1="30" y1="34" x2="{x}" y2="{y}" stroke="#ffd166" stroke-width="1.6"/>' for x, y in ((16, 24), (44, 22), (22, 18), (38, 16)))
            + g(hammer(), 40, 18, 55, .7))


@icon('Shieldwall')
def _():
    return (g(heater('#40597a'), 22, 32, -8, .82) + g(heater('#8a5a32'), 42, 32, 8, .82)
            + g(heater('url(#steel)'), 32, 36, 0, .9)
            + '<path d="M26 30 L32 26 L38 30 L38 38 L32 43 L26 38 Z" fill="#c9a25e" stroke-width="1.2"/>')


@icon('Arrow Rain')
def _():
    arrows = ''.join(g(arrow('url(#steel)', '#a8d06b', 22), x, y, 200, .8) for x, y in ((16, 20), (30, 16), (44, 22), (23, 38), (38, 40)))
    return (arrows + '<path d="M6 54 Q32 48 58 54" fill="none" stroke="#4a3a2e" stroke-width="3"/>')


@icon('Envenom')
def _():
    return (glow('<ellipse cx="32" cy="40" rx="12" ry="12" fill="#b8ff6a"/>', .55)
            + '<path d="M27 12 H37 V22 Q46 26 46 38 A14 14 0 0 1 18 38 Q18 26 27 22 Z" fill="#2a3a2a"/>'
            + '<path d="M19.5 36 Q32 32 44.5 36 A13 13 0 0 1 19.5 36 Z" fill="url(#poison)" stroke-width="1.2"/>'
            + '<path d="M19 38 A13 13 0 0 0 45 38 Q32 34 19 38 Z" fill="url(#poison)"/>'
            + '<rect x="26" y="9" width="12" height="5" rx="1.5" fill="url(#wood)"/>'
            + g(skull('#e8f4d8', '#2a3a2a'), 32, 40, 0, .42)
            + g(drop('url(#poison)'), 47, 52, 0, .5))


@icon('Entangle')
def _():
    thorns = ''.join(f'<path d="M{x} {y} l{dx} {dy} l2 1 Z" fill="#9ac46b" stroke-width="1"/>' for x, y, dx, dy in ((18, 40, -4, -3), (44, 30, 4, -3), (24, 22, -3, -4), (40, 46, 4, 2)))
    return (poly('M10 54 C10 38 30 44 32 32 C34 20 20 18 24 12', '#3f7a4f', 3)
            + poly('M54 54 C54 40 36 46 34 34 C32 24 46 22 42 12', '#4c9a28', 3)
            + thorns
            + '<path d="M24 12 C18 10 14 14 14 18 C19 18 23 16 24 12 Z" fill="url(#leaf)"/>'
            + '<path d="M42 12 C48 10 52 14 52 18 C47 18 43 16 42 12 Z" fill="url(#leaf)"/>'
            + twinkle(16, 30, .7))


# ---- The Tideborn
@icon('Riptide')
def _():
    return ('<circle cx="32" cy="34" r="20" fill="url(#water)"/>'
            + ''.join(f'<path d="M{32 + r * math.cos(math.radians(a0)):.1f} {34 + r * math.sin(math.radians(a0)):.1f} '
                      f'A{r} {r} 0 1 1 {32 + r * math.cos(math.radians(a0 + 250)):.1f} {34 + r * math.sin(math.radians(a0 + 250)):.1f}" '
                      f'fill="none" stroke="#eaffff" stroke-width="2" opacity="{op}"/>'
                      for r, a0, op in ((5, 0, 1), (10, 120, .85), (15, 240, .7)))
            + '<circle cx="32" cy="34" r="2" fill="#0a3a4a" stroke="none"/>'
            + '<path d="M10 14 H24 M10 14 L15 9 M10 14 L15 19" fill="none" stroke="#15121d" stroke-width="5"/>'
            + '<path d="M10 14 H24 M10 14 L15 9 M10 14 L15 19" fill="none" stroke="#ffd166" stroke-width="2.6"/>')


@icon('Slippery Scales')
def _():
    fish = ('<path d="M-16 0 C-8 -11 8 -11 14 0 C8 11 -8 11 -16 0 Z" fill="url(#water)"/>'
            '<path d="M14 0 L24 -8 L22 0 L24 8 Z" fill="#5fa38a"/>'
            '<circle cx="-9" cy="-2" r="2" fill="#15121d" stroke="none"/>'
            '<path d="M-2 -6 Q2 0 -2 6 M4 -6 Q8 0 4 6" fill="none" stroke="#ffffff" stroke-width="1" opacity=".8"/>')
    return (g(fish, 34, 30, -15, 1.05, ' opacity=".35"') + g(fish, 28, 36, -15, 1.05)
            + '<path d="M44 46 Q52 50 58 46 M42 52 Q50 56 56 52" fill="none" stroke="#bff3ff" stroke-width="2"/>'
            + g(drop('#bff3ff'), 16, 18, 0, .5) + g(drop('#bff3ff'), 24, 12, 0, .4))


@icon('Dirge of the Deep')
def _():
    return ('<path d="M6 46 Q12 42 18 46 T30 46 T42 46 T58 45 V56 H6 Z" fill="#14485a"/>'
            '<path d="M6 46 Q12 42 18 46 T30 46 T42 46 T58 45" fill="none" stroke="#7fe3d8" stroke-width="1.4"/>'
            + g(note('#7fa8c8'), 22, 26, -10, .85) + g(note('#5a7a9a'), 40, 22, 10, .75)
            + '<path d="M50 28 L50 40 M45 35 L50 41 L55 35" fill="none" stroke="#b07ae0" stroke-width="2.6"/>')


@icon('Tentacle Snare')
def _():
    suckers = ''.join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#e8dcff" stroke="none"/>' for x, y in ((18, 48), (22, 40), (30, 38), (40, 36)))
    return ('<circle cx="34" cy="26" r="8" fill="url(#steel)"/>'
            '<path d="M8 58 C10 44 16 38 26 38 C36 38 46 36 44 26 C42 16 30 14 26 22 C23 28 30 32 34 28 C36 32 30 36 26 34 '
            'C20 31 20 18 30 15 C42 12 52 20 50 30 C48 42 34 44 24 44 C18 44 16 50 14 58 Z" fill="url(#ink)"/>'
            + suckers)


@icon('Tide Pool')
def _():
    bubbles = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#d4ffb0" fill-opacity=".3" stroke="#d4ffb0" stroke-width="1.2"/>'
                      for x, y, r in ((22, 28, 3), (40, 22, 2.4), (32, 16, 3.4), (46, 32, 2)))
    return ('<path d="M6 46 Q8 34 20 36 Q32 32 44 36 Q56 34 58 46 Q56 56 32 56 Q8 56 6 46 Z" fill="#6b6f7a"/>'
            '<ellipse cx="32" cy="45" rx="20" ry="6.5" fill="url(#water)"/>'
            '<path d="M18 45 Q24 42 30 45 M34 46 Q40 43 46 46" fill="none" stroke="#ffffff" stroke-width="1.2" opacity=".8"/>'
            + bubbles + g(plus(), 32, 30, 0, .45))


# ---- The Crimson Court
@icon('Night Waltz')
def _():
    return ('<path d="M38 10 A18 18 0 1 0 54 34 A14 14 0 1 1 38 10 Z" fill="#f4ecd8"/>'
            + g(rapier(), 28, 38, 45, .9)
            + burst(48, 18, 1.5, 4, 6, '#ff6a7a') + burst(42, 26, 1.5, 3.5, 6, '#ff6a7a') + burst(51, 26, 1.2, 3, 6, '#ff6a7a'))


@icon('Demonic Roar')
def _():
    horns = ('<path d="M-9 -12 C-16 -16 -18 -24 -14 -30 C-13 -24 -9 -21 -4 -16 Z" fill="#2a1a1f"/>'
             '<path d="M9 -12 C16 -16 18 -24 14 -30 C13 -24 9 -21 4 -16 Z" fill="#2a1a1f"/>')
    head = (horns + '<path d="M-11 -2 C-11 -12 -6 -16 0 -16 C6 -16 11 -12 11 -2 C11 2 9 4 8 5 L8 6 L-8 6 L-8 5 C-9 4 -11 2 -11 -2 Z" fill="url(#demon)"/>'
            '<path d="M-7 -5 L-2 -3 M7 -5 L2 -3" stroke-width="1.6"/>'
            '<circle cx="-4.5" cy="-2" r="1.8" fill="#ffd166" stroke="none"/><circle cx="4.5" cy="-2" r="1.8" fill="#ffd166" stroke="none"/>'
            '<path d="M-8 5 Q0 22 8 5 Z" fill="#2a0a0e"/>'
            '<path d="M-6 6 L-4 10 L-2 6 M2 6 L4 10 L6 6" fill="#fbf4e2" stroke-width="1"/>')
    return (arc_lines(32, 40, 18, 2, 60, '#ff6a2e', 180) + arc_lines(32, 40, 18, 2, 60, '#ff6a2e', 0)
            + g(head, 32, 36, 0, 1.1))


@icon('Shadowstep')
def _():
    return (g(dagger('#5a2a6a'), 20, 40, 45, 1.3, ' opacity=".35"')
            + g(dagger('#7a3d8f'), 27, 35, 45, 1.3, ' opacity=".6"')
            + g(dagger(), 36, 28, 45, 1.5)
            + '<path d="M10 52 Q16 46 22 50 M14 58 Q20 52 26 56" fill="none" stroke="#9a4ad0" stroke-width="2" opacity=".7"/>'
            + twinkle(50, 14, .8, '#ff9ad0'))


@icon('Savage Maul')
def _():
    return (g(jaws('#4a1f1f'), 32, 30, 0, 1.2)
            + glow('<circle cx="32" cy="30" r="6" fill="#ff7a2f"/>', .4)
            + g(drop(), 24, 50, 0, .55) + g(drop(), 40, 51, 0, .65) + g(drop(), 32, 55, 0, .4))


@icon('Blood Siphon')
def _():
    return (g(drop(), 16, 20, 0, 1.3)
            + poly('M20 30 Q24 50 40 44', '#c0303f', 2.6)
            + '<path d="M36 40 L42 44 L36 48" fill="none" stroke="#c0303f" stroke-width="2.4"/>'
            + g(heart(), 44, 40, 0, .9)
            + g(plus('#ffffff'), 44, 39, 0, .28))


# ================================================================ passives (drawn a little smaller: they sit in a round frame)
# ---- Ironclad Union
@icon('Reactive Plating')
def _():
    return ('<path d="M14 18 L32 12 L50 18 L48 40 Q42 50 32 54 Q22 50 16 40 Z" fill="url(#iron)"/>'
            '<path d="M18 22 L32 17 L46 22 L44.5 39 Q40 46 32 49 Q24 46 19.5 39 Z" fill="url(#steel)" stroke-width="1.2"/>'
            '<path d="M18 30 H46 M19 38 H45" stroke-width="1"/>'
            + burst(48, 22, 2.5, 7, 8, '#ffd166')
            + '<path d="M56 14 L50 20" stroke="#ffd166" stroke-width="2"/>')


@icon('Serrated')
def _():
    teeth = ' '.join(f'L{14 + i * 4} {44 - i * 4 - (3 if i % 2 else 0)}' for i in range(10))
    return (f'<path d="M12 48 {teeth} L54 10 L46 20 L18 52 Z" fill="url(#steel)"/>'
            + '<rect x="6" y="50" width="12" height="6" rx="2" fill="#9b5d3c" transform="rotate(-45 12 53)"/>'
            + g(drop(), 46, 42, 0, .65) + g(drop(), 38, 50, 0, .45))


@icon('Feedback Loop')
def _():
    return ('<path d="M18 22 A17 17 0 0 1 48 24" fill="none" stroke="#7fe3ff" stroke-width="3"/>'
            '<path d="M44 18 L49 25 L41 26" fill="none" stroke="#7fe3ff" stroke-width="3"/>'
            '<path d="M46 42 A17 17 0 0 1 16 40" fill="none" stroke="#7fe3ff" stroke-width="3"/>'
            '<path d="M20 46 L15 39 L23 38" fill="none" stroke="#7fe3ff" stroke-width="3"/>'
            + g(bolt(), 32, 32, 10, .6))


@icon('Big Guns')
def _():
    return ('<rect x="14" y="22" width="34" height="13" rx="4" fill="url(#iron)" transform="rotate(-18 31 28)"/>'
            '<rect x="44" y="14" width="6" height="15" rx="2" fill="url(#steel)" transform="rotate(-18 47 21)"/>'
            '<path d="M14 30 L22 26 L24 31 L16 35 Z" fill="#f0a73a"/>'
            '<circle cx="24" cy="44" r="9" fill="url(#wood)"/><circle cx="24" cy="44" r="3" fill="url(#gold)"/>'
            '<path d="M24 35 V53 M15 44 H33" stroke-width="1"/>'
            '<rect x="30" y="42" width="20" height="5" rx="2" fill="#5a4a3a"/>'
            + burst(53, 15, 2.5, 6, 8, '#ffd166'))


@icon('Maintenance Drone')
def _():
    return ('<path d="M24 38 L20 52 H44 L40 38 Z" fill="#8be28b" opacity=".3" stroke="none"/>'
            '<line x1="12" y1="16" x2="28" y2="20" stroke-width="2"/><line x1="52" y1="16" x2="36" y2="20" stroke-width="2"/>'
            '<ellipse cx="12" cy="15" rx="7" ry="2" fill="#c9ccd8"/><ellipse cx="52" cy="15" rx="7" ry="2" fill="#c9ccd8"/>'
            '<rect x="22" y="18" width="20" height="16" rx="6" fill="#a39a86"/>'
            '<circle cx="32" cy="26" r="4" fill="#8be28b"/>'
            '<path d="M26 34 L24 39 M38 34 L40 39" stroke-width="1.6"/>'
            + g(plus(), 32, 48, 0, .38))


# ---- Bloodtusk Horde
@icon('Grudge Axe')
def _():
    # Krug's last throw: a spinning axe outlined in blood-red, with the arc of its bounce behind it.
    return (glow('<circle cx="34" cy="28" r="15" fill="#e0242f"/>', .55)
            + '<path d="M8 50 Q20 30 34 34 Q44 37 52 22" fill="none" stroke="#e0242f" stroke-width="2.4" stroke-dasharray="3 3" opacity=".85"/>'
            + g(axe('url(#steel)'), 34, 28, 35, 1.05)
            + '<path d="M22 14 A14 14 0 0 1 46 16 M46 42 A14 14 0 0 1 24 42" fill="none" stroke="#ff6a6a" stroke-width="2" opacity=".8"/>'
            + g(drop(), 12, 50, 0, .45))


@icon('Bloodlust')
def _():
    return (glow('<circle cx="32" cy="32" r="16" fill="#e0242f"/>', .6)
            + '<path d="M10 32 Q32 12 54 32 Q32 52 10 32 Z" fill="#2a0a0e"/>'
            + '<circle cx="32" cy="32" r="9" fill="#e0242f"/>'
            + '<path d="M32 23 L34 32 L32 41 L30 32 Z" fill="#15121d" stroke="none"/>'
            + '<path d="M12 25 L20 29 M52 25 L44 29" stroke-width="2.4"/>'
            + g(drop(), 32, 52, 0, .55))


@icon('Thick Skull')
def _():
    helm = ('<path d="M-15 4 C-15 -12 -8 -18 0 -18 C8 -18 15 -12 15 4 Z" fill="url(#iron)"/>'
            '<path d="M-17 4 H17 V8 H-17 Z" fill="#8a5a32"/>'
            '<path d="M-12 -12 C-20 -16 -22 -24 -18 -28 C-16 -22 -12 -20 -8 -16 Z" fill="url(#bone)"/>'
            '<path d="M12 -12 C20 -16 22 -24 18 -28 C16 -22 12 -20 8 -16 Z" fill="url(#bone)"/>'
            '<circle cx="0" cy="-6" r="3" fill="url(#gold)"/>')
    return (g(helm, 32, 40, 0, 1.0)
            + twinkle(13, 30, .8) + twinkle(51, 30, .8)
            + '<path d="M16 22 L11 18 M48 22 L53 18" stroke="#ffd166" stroke-width="2"/>'
            + '<path d="M22 53 Q32 58 42 53" fill="none" stroke="#7a9a5e" stroke-width="2.4"/>')


@icon('Steppe Hunter')
def _():
    return ('<rect x="10" y="40" width="44" height="9" rx="3" fill="#2a1a1a"/>'
            '<rect x="12" y="42" width="19" height="5" rx="2" fill="#e0242f" stroke="none"/>'
            '<path d="M32 38 V51" stroke="#ffd166" stroke-width="1.6" stroke-dasharray="2 2"/>'
            + g(spear(), 34, 26, 60, .85))


@icon('Pyromaniac')
def _():
    return (glow(g(flame(), 32, 34, 0, 1.25), .6) + g(flame('url(#fire)', '#ffb43d'), 32, 34, 0, 1.2)
            + '<path d="M25 34 L29 36 M39 34 L35 36" stroke-width="2"/>'
            + '<circle cx="27" cy="38" r="2" fill="#15121d" stroke="none"/><circle cx="37" cy="38" r="2" fill="#15121d" stroke="none"/>'
            + '<path d="M25 44 Q32 50 39 44 Q32 47 25 44 Z" fill="#15121d"/>')


@icon('Ancestral Watch')
def _():
    return ('<rect x="20" y="12" width="24" height="42" rx="4" fill="url(#wood)"/>'
            '<path d="M20 30 H44 M20 42 H44" stroke-width="1.4"/>'
            '<path d="M16 16 L20 20 L20 14 Z M48 16 L44 20 L44 14 Z" fill="#e0645a"/>'
            + glow('<circle cx="27" cy="22" r="3" fill="#bff0ff"/><circle cx="37" cy="22" r="3" fill="#bff0ff"/>', 1)
            + '<circle cx="27" cy="22" r="2.4" fill="#bff0ff"/><circle cx="37" cy="22" r="2.4" fill="#bff0ff"/>'
            + '<path d="M27 36 L32 33 L37 36 L32 39 Z" fill="#e0645a" stroke-width="1"/>'
            + '<path d="M26 48 H38" stroke="#d8c8a8" stroke-width="2"/>')


# ---- Kingdom of Aldmere
@icon('Arcane Ward')
def _():
    runes = ''.join(g('<path d="M0 -2.5 L2 0 L0 2.5 L-2 0 Z" fill="#e8dcff" stroke="none"/>', 32 + 19 * math.cos(math.radians(a)), 32 + 19 * math.sin(math.radians(a)))
                    for a in range(0, 360, 45))
    return (glow('<circle cx="32" cy="32" r="18" fill="#9a6aff"/>', .4)
            + '<circle cx="32" cy="32" r="19" fill="#9a6aff" fill-opacity=".18" stroke="#b07ae0" stroke-width="2.2"/>'
            + runes
            + g(heater('#5a3a9a', '#b07ae0'), 32, 33, 0, .62)
            + '<path d="M32 25 L35 32 L32 39 L29 32 Z" fill="#e8dcff" stroke-width="1"/>')


@icon('Shield of the Realm')
def _():
    return (g(heater('#3e5a8c'), 32, 38, 0, .85)
            + '<path d="M20 18 L22 8 L27 14 L32 6 L37 14 L42 8 L44 18 Z" fill="url(#gold)"/>'
            + '<circle cx="32" cy="11" r="1.6" fill="#e0455a" stroke="none"/>'
            + '<path d="M26 32 L30 38 L26 44 M38 32 L34 38 L38 44" fill="none" stroke="#d9b44a" stroke-width="2.4"/>')


@icon('Deadeye')
def _():
    return ('<circle cx="32" cy="32" r="19" fill="#f4ecd8"/>'
            '<circle cx="32" cy="32" r="13" fill="#e0455a"/>'
            '<circle cx="32" cy="32" r="7.5" fill="#f4ecd8"/>'
            '<circle cx="32" cy="32" r="3" fill="#15121d"/>'
            '<path d="M32 32 L27 25 M32 32 L39 27 M32 32 L35 40" stroke-width="1.2"/>'
            + twinkle(50, 14, 1, '#ffffff') + twinkle(14, 50, .7, '#ffffff'))


@icon('Kindling')
def _():
    return (glow(g(flame(), 32, 28, 0, .9), .6) + g(flame(), 32, 28, 0, .85)
            + g('<rect x="-16" y="-3.5" width="32" height="7" rx="3.5" fill="url(#wood)"/><circle cx="-16" cy="0" r="3.5" fill="#d9a46a"/>', 32, 46, 18)
            + g('<rect x="-16" y="-3.5" width="32" height="7" rx="3.5" fill="url(#wood)"/><circle cx="16" cy="0" r="3.5" fill="#d9a46a"/>', 32, 46, -18))


@icon('Mercy')
def _():
    hand = '<path d="M0 0 C-4 -2 -12 -2 -16 2 L-20 8 L-8 12 C-2 12 2 8 4 4 Z" fill="#e2b48f"/>'
    return (glow('<circle cx="32" cy="28" r="12" fill="#ffd060"/>', .55)
            + g(heart(), 32, 28, 0, 1.15)
            + g(hand, 30, 42, 0, 1.0) + g('<g transform="scale(-1 1)">' + hand + '</g>', 34, 42, 0, 1.0))


# ---- Stoneleaf Accord
@icon('Grudge')
def _():
    return ('<rect x="14" y="12" width="34" height="42" rx="3" fill="#6b4422"/>'
            '<rect x="16" y="14" width="30" height="38" rx="2" fill="#8a5a32" stroke-width="1"/>'
            '<rect x="44" y="12" width="6" height="42" rx="2" fill="#5a3a1c"/>'
            '<path d="M22 22 L40 44 M40 22 L22 44" stroke="#15121d" stroke-width="6"/>'
            '<path d="M22 22 L40 44 M40 22 L22 44" stroke="#e0242f" stroke-width="3.4"/>'
            '<path d="M36 54 V60 L39 57 L42 60 V54" fill="#e0242f" stroke-width="1"/>')


@icon('Unbreakable')
def _():
    return (g(heater('url(#iron)', 'url(#gold)'), 32, 32, 0, 1.0)
            + '<path d="M32 14 L29 24 L35 30 L28 38 L33 48" fill="none" stroke="#15121d" stroke-width="2.4"/>'
            + '<path d="M22 28 H42 M23 38 H41" stroke="url(#gold)" stroke-width="3"/>'
            + '<path d="M22 28 H42 M23 38 H41" stroke="#8a5a14" stroke-width="1" fill="none"/>')


@icon('Keen Eye')
def _():
    chev = ''.join(f'<path d="M{x - 4} 18 L{x} 13 L{x + 4} 18" fill="none" stroke="#a8d06b" stroke-width="2.4"/>' for x in (24, 32, 40))
    return (chev + '<path d="M10 36 Q32 18 54 36 Q32 50 10 36 Z" fill="#f4f0e2"/>'
            '<circle cx="32" cy="35" r="8" fill="url(#leaf)"/><circle cx="32" cy="35" r="3.4" fill="#15121d" stroke="none"/>'
            '<circle cx="29.5" cy="32.5" r="1.5" fill="#ffffff" stroke="none"/>'
            '<path d="M10 36 Q18 30 24 28" fill="none" stroke="#3f7a4f" stroke-width="2"/>')


@icon('Debilitating Venom')
def _():
    return ('<path d="M10 30 C10 18 22 12 34 14 C46 16 54 24 52 30 C46 30 40 32 36 36 C30 40 18 40 10 30 Z" fill="url(#leaf)"/>'
            '<path d="M14 28 C20 22 30 20 40 22" fill="none" stroke="#2f6a2a" stroke-width="1.2"/>'
            '<circle cx="40" cy="22" r="2.4" fill="#ffd166"/><path d="M40 20 V24" stroke-width="1"/>'
            '<path d="M38 34 L40 46 L42 34 Z M46 31 L48 42 L49 31 Z" fill="#fbf4e2"/>'
            + g(drop('url(#poison)'), 40, 52, 0, .5)
            + '<path d="M18 44 L18 54 M14 50 L18 55 L22 50" fill="none" stroke="#b07ae0" stroke-width="2.4"/>')


@icon('Verdant Aura')
def _():
    leaves = ''.join(g('<path d="M0 -8 C5 -4 5 4 0 8 C-5 4 -5 -4 0 -8 Z" fill="url(#leaf)" stroke-width="1.2"/>',
                       32 + 17 * math.cos(math.radians(a)), 32 + 17 * math.sin(math.radians(a)), a + 90)
                     for a in range(0, 360, 45))
    return (glow('<circle cx="32" cy="32" r="12" fill="#b8ff6a"/>', .7) + leaves + g(plus(), 32, 32, 0, .45))


# ---- The Tideborn
@icon('Blood Scent')
def _():
    return ('<path d="M8 36 C14 24 30 18 44 22 L54 18 L50 28 C52 32 50 38 44 40 C34 44 18 44 8 36 Z" fill="#7d93a6"/>'
            '<path d="M8 36 C18 40 34 40 44 38" fill="none" stroke="#e9e4d8" stroke-width="1.4"/>'
            '<path d="M18 38 L20 42 L22 38 L24 42 L26 38" fill="none" stroke="#fbf4e2" stroke-width="1"/>'
            '<circle cx="16" cy="30" r="1.8" fill="#15121d" stroke="none"/>'
            '<path d="M30 26 L32 32 M35 25 L37 31" stroke-width="1.2"/>'
            + arc_lines(6, 30, 4, 2, 60, '#ff6a7a', 180, 1.8, 4)
            + g(drop(), 16, 14, 0, .6) + g(drop(), 8, 20, 0, .4))


@icon('Frostplate')
def _():
    # The first blow of the turn goes into the rime-plate rather than into him.
    return (g(heater('url(#steel)', '#9fe8ff'), 32, 31, 0, 1.3)
            + '<path d="M21 28 L32 34 L43 28 M21 39 L32 45 L43 39" stroke="#3b4556" stroke-width="2.6" fill="none" stroke-linejoin="round"/>'
            + '<path d="M24 20 Q32 16 40 20" stroke="#eaf1f8" stroke-width="1.4" fill="none" opacity=".55"/>'
            + twinkle(13, 15, .85, '#dcf8ff') + twinkle(51, 45, .65, '#dcf8ff'))


@icon('Echo')
def _():
    return (arc_lines(26, 34, 10, 4, 80, '#7fe3d8', 0, 2.2, 6)
            + '<path d="M10 40 C10 28 20 20 28 24 C34 27 32 36 26 38 C22 40 20 36 22 33 L16 44 C14 48 10 46 10 40 Z" fill="#f2c6d8"/>'
            + '<path d="M22 33 C24 30 28 30 28 33" fill="none" stroke-width="1"/>')


@icon('Ink Sac')
def _():
    return ('<path d="M32 12 C38 16 44 12 46 18 C52 18 54 24 50 28 C56 32 54 40 48 40 C50 46 44 52 38 48 C34 54 26 54 24 48 '
            'C18 52 12 46 16 40 C10 38 10 30 16 28 C12 22 18 16 24 18 C26 12 30 10 32 12 Z" fill="url(#ink)"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#5a4a8a"/>' for x, y, r in ((10, 16, 2.4), (54, 12, 2), (56, 50, 2.6), (9, 50, 1.8)))
            + '<ellipse cx="32" cy="32" rx="6" ry="6.5" fill="#fff6dc" stroke-width="1.2"/><circle cx="33" cy="33" r="3" fill="#15121d" stroke="none"/>')


@icon('Tidecaller')
def _():
    ridges = ''.join(f'<line x1="30" y1="46" x2="{30 + 18 * math.cos(math.radians(a)):.1f}" y2="{46 - 18 * math.sin(math.radians(a)):.1f}" stroke="#c48aa8" stroke-width="1.2"/>'
                     for a in (40, 65, 90, 115, 140))
    return ('<path d="M30 46 L14 34 Q12 18 30 13 Q48 18 46 34 Z" fill="#f2c6d8"/>'
            + ridges
            + '<path d="M24 46 H36 L33 52 H27 Z" fill="#e8b4cc"/>'
            + g(drop('url(#mana)'), 48, 48, 0, .7) + g(drop('url(#water)'), 40, 54, 0, .5))


# ---- The Crimson Court
@icon('Riposte')
def _():
    return (g(rapier(), 26, 34, 40, .85) + g('<g transform="scale(-1 1)">' + rapier() + '</g>', 38, 34, -40, .85)
            + burst(32, 22, 2.5, 6, 8, '#ffd166')
            + '<path d="M50 44 A14 14 0 0 1 30 52" fill="none" stroke="#ff6a7a" stroke-width="2.4"/>'
            + '<path d="M34 48 L29 52 L34 56" fill="none" stroke="#ff6a7a" stroke-width="2.4"/>')


@icon('Brimstone Hide')
def _():
    scales = ''.join(f'<path d="M{x - 5} {y} Q{x} {y + 7} {x + 5} {y}" fill="none" stroke="#2a0a0e" stroke-width="1.2"/>'
                     for y in (30, 37, 44) for x in (22, 32, 42))
    return (g(flame(), 18, 22, -20, .45) + g(flame(), 46, 22, 20, .45) + g(flame(), 32, 18, 0, .5)
            + '<path d="M14 28 Q32 22 50 28 L48 44 Q40 54 32 56 Q24 54 16 44 Z" fill="url(#demon)"/>'
            + scales)


@icon('Flurry')
def _():
    return (g(dagger(), 22, 34, 35, 1.3) + g(dagger(), 32, 30, 35, 1.3) + g(dagger(), 42, 26, 35, 1.3)
            + '<path d="M8 50 L18 44 M12 56 L22 50" stroke="#ff9ad0" stroke-width="2" opacity=".7"/>'
            + '<path d="M48 44 H56 M52 40 V48" stroke="#ffd166" stroke-width="2.6"/>')


@icon('Withering Curse')
def _():
    petals = ''.join(g('<ellipse cx="0" cy="-6" rx="4.5" ry="7" fill="#5a1f3a"/>', 30, 24, a) for a in range(0, 360, 72))
    return ('<path d="M30 30 Q32 42 26 54" fill="none" stroke="#2a1a1f" stroke-width="3"/>'
            '<path d="M29 42 C22 42 18 38 18 34 C24 34 28 38 29 42 Z" fill="#4a4a2a"/>'
            + petals + '<circle cx="30" cy="24" r="3" fill="#9a4ad0"/>'
            + g('<ellipse cx="0" cy="0" rx="3" ry="5" fill="#5a1f3a"/>', 44, 44, 40)
            + g('<ellipse cx="0" cy="0" rx="2.6" ry="4.4" fill="#5a1f3a"/>', 50, 54, -20)
            + '<path d="M48 20 L48 30 M44 26 L48 31 L52 26" fill="none" stroke="#b07ae0" stroke-width="2.4"/>')


# ================================================================ alternative own passives (now the default; the old one is 'alt')
@icon('Retribution')
def _():
    rays = ''.join(g('<path d="M0 -25 L3.5 -16 L0 -18 L-3.5 -16 Z" fill="#ffe08a" stroke-width="1"/>', 32, 33, a) for a in (-60, -20, 20, 60, 120, 160, 200, 240))
    return (glow('<circle cx="32" cy="33" r="16" fill="#ffd060"/>', .55) + rays
            + g(heater('#3e5a8c'), 32, 33, 0, .62)
            + '<path d="M32 25 V41 M26 30 H38" stroke="url(#gold)" stroke-width="3"/>')


@icon('Backwash')
def _():
    return ('<path d="M54 46 C50 30 38 20 24 22 C14 23 10 32 14 38 C17 42 23 41 23 36 C23 32 28 31 31 34 C35 38 33 46 27 50 Z" fill="url(#water)"/>'
            '<path d="M48 40 C44 30 36 26 27 26 C20 26 15 30 15 35" fill="none" stroke="#ffffff" stroke-width="1.4" opacity=".8"/>'
            '<rect x="8" y="49" width="48" height="6" rx="2" fill="#2a86b8"/>'
            '<path d="M8 16 H22 M8 16 L13 11 M8 16 L13 21" fill="none" stroke="#15121d" stroke-width="5"/>'
            '<path d="M8 16 H22 M8 16 L13 11 M8 16 L13 21" fill="none" stroke="#ff6a7a" stroke-width="2.6"/>'
            + g(drop(), 50, 16, 0, .6))


@icon('Forest Stride')
def _():
    leaf = '<path d="M0 -10 C6 -5 6 5 0 10 C-6 5 -6 -5 0 -10 Z" fill="url(#leaf)"/><path d="M0 -8 V8" stroke-width="1"/>'
    return (speed_lines(5, 36, 3, 14, 7, '#d4ffb0')
            + g(leaf, 30, 34, 60, 1.25) + g(leaf, 44, 26, 60, 1.0) + g(leaf, 42, 44, 60, .85)
            + '<path d="M18 52 Q32 46 50 52" fill="none" stroke="#6b4422" stroke-width="2.4"/>')


# ================================================================ neutral skills (the rest of NEUTRAL_SKILLS' icons are hand-drawn files in this folder)
@icon('Provoke')
def _():
    return (glow('<circle cx="32" cy="34" r="15" fill="#e0242f"/>', .5)
            + g(heater('#2a2f3d'), 32, 34, 0, .8)
            + '<circle cx="32" cy="33" r="8.5" fill="#e0455a"/><circle cx="32" cy="33" r="5" fill="#f4ecd8"/><circle cx="32" cy="33" r="2" fill="#e0455a"/>'
            + ''.join(g(g('<path d="M-13 0 H-4 M-8 -4 L-3 0 L-8 4" fill="none" stroke="#15121d" stroke-width="4.6"/>'
                          '<path d="M-13 0 H-4 M-8 -4 L-3 0 L-8 4" fill="none" stroke="#ffd166" stroke-width="2.4"/>', -14, 0), 32, 33, a)
                      for a in (0, 180, -45, -135)))


# ================================================================ generic passives (any champion can equip; GENERIC_PASSIVES in index.html)
@icon('Toughness')
def _():
    return (g(heart(), 32, 34, 0, 2.0)
            + '<path d="M22 30 H42 M22 38 H42" stroke="#9aa3b5" stroke-width="3"/>'
            + '<path d="M22 30 H42 M22 38 H42" stroke="#454d61" stroke-width="1" fill="none"/>'
            + g(plus('#ffffff'), 32, 34, 0, .3))


@icon('Might')
def _():
    return ('<path d="M18 40 C14 30 18 18 28 16 C34 15 36 20 34 24 L30 26 C36 26 44 28 46 36 C48 46 40 52 30 52 C22 52 20 46 18 40 Z" fill="#e2b48f"/>'
            '<path d="M30 26 C27 30 27 34 30 36 M34 36 C38 34 42 36 42 40" fill="none" stroke-width="1.4"/>'
            '<path d="M48 20 L48 10 M44 14 L48 9 L52 14" fill="none" stroke="#ffd166" stroke-width="2.6"/>')


@icon('Swiftness')
def _():
    return (speed_lines(5, 40, 3, 12, 6, '#ffffff')
            + '<path d="M24 14 H38 V36 L50 42 Q54 44 54 48 V52 H22 Z" fill="url(#hide)"/>'
            + '<path d="M22 46 H54" stroke-width="1.4"/><rect x="22" y="50" width="32" height="4" rx="1.5" fill="#2b1e16"/>'
            + '<rect x="23" y="14" width="16" height="5" rx="1.5" fill="#c9a25e"/>'
            + '<path d="M38 24 C44 18 52 18 56 22 C50 23 46 25 44 28 Z" fill="#f4f7fc"/>'
            + '<path d="M38 30 C44 26 50 27 53 31 C48 31 44 32 42 34 Z" fill="#f4f7fc"/>')


@icon('Keen Edge')
def _():
    return (g(sword(), 30, 34, 45, 1.0)
            + twinkle(46, 16, 1.2, '#ffffff') + twinkle(52, 28, .6, '#ffffff') + twinkle(38, 12, .5, '#ffffff'))


@icon('Deep Well')
def _():
    return ('<ellipse cx="32" cy="22" rx="17" ry="5" fill="#2a2f3d"/>'
            '<ellipse cx="32" cy="22" rx="13" ry="3.4" fill="url(#mana)" stroke-width="1"/>'
            '<path d="M15 22 V46 Q32 54 49 46 V22 Q32 30 15 22 Z" fill="#7a7f8c"/>'
            '<path d="M15 32 Q32 38 49 32 M15 40 Q32 46 49 40 M24 25 V34 M40 25 V34 M32 36 V46" fill="none" stroke-width="1.2"/>'
            + g(drop('url(#mana)'), 32, 12, 0, .8))


@icon('Second Wind')
def _():
    return (poly('M10 26 H36 A6 6 0 1 0 30 20', '#c9ecff', 2.4)
            + poly('M10 36 H44 A6 6 0 1 1 38 42', '#c9ecff', 2.4)
            + poly('M14 46 H28', '#c9ecff', 2.4)
            + g(plus(), 48, 18, 0, .45))


# ================================================================ skills and passives added later
@icon('Molotov')
def _():
    return (g(flame('url(#fire)'), 32, 14, 0, .5)
            + '<rect x="28" y="18" width="8" height="6" rx="1.6" fill="#17171e"/>'
            + '<path d="M23 26 Q20 31 20 38 V50 Q20 57 32 57 Q44 57 44 50 V38 Q44 31 41 26 Z" fill="#1b1b24"/>'
            + '<path d="M24 38 Q32 42 40 38" fill="none" stroke="#e0455a" stroke-width="3"/>')


@icon('Shieldbearer')
def _():
    return (g(heater(), 24, 34, 0, 1.0) + g(heater('url(#iron)'), 42, 36, 0, .8)
            + twinkle(47, 16, .8, '#e0bb55'))


@icon('Anchor Chain')
def _():
    return ('<path d="M14 12 q5 4 0 8 q-5 4 0 8 q5 4 0 8" fill="none" stroke="#9aa3b5" stroke-width="3.4"/>'
            + '<path d="M32 20 V50" stroke="url(#iron)" stroke-width="5"/>'
            + '<circle cx="32" cy="16" r="5" fill="none" stroke="url(#iron)" stroke-width="4"/>'
            + '<path d="M18 40 Q32 58 46 40" fill="none" stroke="url(#iron)" stroke-width="5"/>'
            + '<path d="M22 26 H42" stroke="url(#iron)" stroke-width="4"/>')


@icon('Stinging Veil')
def _():
    return ('<path d="M18 30 Q32 14 46 30 Q40 36 32 36 Q24 36 18 30 Z" fill="#f2a0c8"/>'
            + '<path d="M22 36 q-3 12 1 18 M28 37 q-2 12 1 17 M36 37 q2 12 -1 17 M42 36 q3 12 -1 18"'
              ' fill="none" stroke="#f2a0c8" stroke-width="3" stroke-linecap="round"/>'
            + burst(32, 26, 2, 6, 7, '#fff1a0'))


@icon('Heroic')
def _():
    return (g(heater(), 26, 34, -14, 1.0)
            + '<path d="M40 20 L52 32 L40 44" fill="none" stroke="#e0bb55" stroke-width="4"/>'
            + twinkle(50, 15, .7, '#ffffff'))


@icon('Tear Apart')
def _():
    return (g(jaws('#8a3a3a'), 20, 32, -20, .9) + g(jaws('#8a3a3a'), 44, 32, 160, .9)
            + g(drop(), 32, 44, 0, .7))


@icon('Come Apart')
def _():
    # Tear Apart's living twin: the same two jaws, but run APART on purpose — dashes trailing
    # the sprint, and in the middle only a crimson flicker where the Gorehound has stopped being.
    return (burst(32, 32, 2.2, 6, 8, '#e0455a')
            + poly('M25 27 l-6 -4 M27 36 l-8 1', '#c86a6a', 2.0)
            + poly('M39 37 l6 4 M37 28 l8 -1', '#c86a6a', 2.0)
            + g(jaws('#8a3a3a'), 16, 19, 195, .72) + g(jaws('#8a3a3a'), 48, 45, 15, .72))


@icon('Dispel')
def _():
    return ('<circle cx="32" cy="32" r="15" fill="none" stroke="#bfa0ff" stroke-width="3" opacity=".9"/>'
            + '<circle cx="32" cy="32" r="9" fill="none" stroke="#bfa0ff" stroke-width="2" opacity=".5"/>'
            + poly('M14 50 L50 14', '#ffffff', 4.2)
            + burst(32, 32, 3, 8, 8, '#e0e6ff'))


@icon('Jump Start')
def _():
    # Her bolt leaping into a cog that is already turning — the ally kicked into motion ahead of its time.
    return (g(gear(11, 9, '#9aa3b5'), 40, 38)
            + poly('M26 8 L14 32 H24 L18 54 L38 28 H27 Z', 'url(#bolt)', 2.2)
            + arc_lines(40, 38, 17, 3, 70, '#7fe3ff', -90, 2)
            + twinkle(52, 16, .8, '#a6ecff'))


@icon('Turncoat Verse')
def _():
    # Her note, and a blade swung back along the line it came down — the song turns it round.
    return (g(note('#f2c6d8'), 21, 22, -8, .95)
            + g(sword('url(#steel)'), 45, 34, 205, .78)
            + '<path d="M18 50 q14 9 28 -1" fill="none" stroke="#7fe3d8" stroke-width="3.2"/>'
            + '<path d="M20 44 l-3 7 l8 1 Z" fill="#7fe3d8"/>'
            + g(drop(), 52, 50, 0, .5))


# ---- monster passives
@icon('Hardened Crust')
def _():
    return ('<path d="M12 44 Q20 26 32 26 Q44 26 52 44 Z" fill="#6a4030"/>'
            + '<path d="M12 44 Q32 52 52 44 L52 50 Q32 58 12 50 Z" fill="url(#fire)"/>'
            + '<path d="M20 38 L26 32 L32 38 L38 32 L44 38" fill="none" stroke="#2a1a14" stroke-width="2"/>')


@icon('Reassemble')
def _():
    return (g(skull(), 32, 24, 0, .72)
            + '<path d="M16 44 h12 M36 44 h12 M22 52 h20" stroke="url(#bone)" stroke-width="5" stroke-linecap="round"/>'
            + arc_lines(32, 40, 15, 3, 70, '#cfe6ff', -90, 2))


@icon('Troll Blood')
def _():
    return (g(drop('url(#heal)'), 32, 30, 0, 1.25) + g(plus(), 32, 34, 0, .5)
            + arc_lines(32, 34, 19, 3, 80, '#9ae0a0', -90, 2))


@icon('Grave Hunger')
def _():
    return (g(jaws('#7a6a52'), 32, 30, 0, 1.15)
            + '<path d="M20 50 h24" stroke="url(#bone)" stroke-width="5" stroke-linecap="round"/>'
            + twinkle(48, 18, .7, '#8ee696'))


@icon('Incorporeal')
def _():
    return ('<path d="M20 48 Q16 22 32 16 Q48 22 44 48 Q38 44 32 50 Q26 44 20 48 Z" fill="#cfe6ff" opacity=".45"/>'
            + '<circle cx="27" cy="30" r="2.6" fill="#2a3a4a"/><circle cx="37" cy="30" r="2.6" fill="#2a3a4a"/>'
            + speed_lines(10, 32, 3, 8, 6, '#cfe6ff'))


@icon('Iron Plating')
def _():
    return ('<path d="M16 16 H48 V40 Q32 52 16 40 Z" fill="url(#iron)"/>'
            + '<path d="M16 28 H48" stroke="#2a2f3f" stroke-width="2"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="2" fill="#c9ccd8"/>'
                      for x, y in ((21, 21), (43, 21), (21, 35), (43, 35))))


@icon('Second Intention')
def _():
    return (g(rapier(), 24, 34, -28, .9) + g(rapier(), 42, 34, 28, .9)
            + arc_lines(32, 30, 16, 2, 50, '#cfe6ff', -90, 2))


@icon('Fading')
def _():
    return ('<path d="M22 50 Q18 24 32 18 Q46 24 42 50 Q37 46 32 51 Q27 46 22 50 Z" fill="#dfe8f5" opacity=".7"/>'
            + '<path d="M26 44 Q24 28 32 24 Q40 28 38 44 Z" fill="#dfe8f5" opacity=".35"/>'
            + twinkle(47, 20, .7, '#ffffff'))


@icon('Pack Hunter')
def _():
    def paw(x, y, s):
        return g('<ellipse cx="0" cy="4" rx="6" ry="5" fill="#b9a68a"/>'
                 '<circle cx="-5" cy="-3" r="2.4" fill="#b9a68a"/><circle cx="0" cy="-5" r="2.4" fill="#b9a68a"/>'
                 '<circle cx="5" cy="-3" r="2.4" fill="#b9a68a"/>', x, y, 0, s)
    return paw(21, 24, .9) + paw(41, 30, .9) + paw(28, 44, 1.0)


@icon('Dread Armor')
def _():
    return ('<path d="M18 22 Q32 12 46 22 V38 Q32 52 18 38 Z" fill="#3a3f52"/>'
            + '<path d="M22 28 H42 V33 H22 Z" fill="#12151e"/>'
            + '<circle cx="27" cy="30.5" r="1.8" fill="#e0455a"/><circle cx="37" cy="30.5" r="1.8" fill="#e0455a"/>'
            + '<path d="M32 14 V8" stroke="#8a2030" stroke-width="3"/>')


@icon('Stone Skin')
def _():
    return ('<path d="M16 20 H48 V44 Q32 54 16 44 Z" fill="#7a7f8c"/>'
            + '<path d="M16 30 H48 M26 20 V44 M38 20 V46" stroke="#4a4f5c" stroke-width="2"/>'
            + '<path d="M20 24 L24 27 L20 27 Z M42 34 L46 37 L42 37 Z" fill="#9aa0ad"/>')


# ---- champion Natures (always-on traits; the round passive frame)
@icon('Built to Hold')
def _():
    return g(heater('url(#iron)'), 32, 32, 0, 1.15) + '<path d="M32 22 V42" stroke="#f0a73a" stroke-width="3"/>'


@icon('Flywheel')
def _():
    return g(gear(13, 10, '#f0a73a'), 32, 32) + arc_lines(32, 32, 20, 3, 70, '#ffd166', -90, 2)


@icon('Arc Transfer')
def _():
    return (poly('M28 12 L18 34 H29 L24 52 L46 28 H33 L40 12 Z', 'url(#bolt)', 2.2)
            + twinkle(14, 44, .8, '#a6ecff'))


@icon('Dug In')
def _():
    return ('<path d="M10 44 H54 L48 54 H16 Z" fill="#6a5844"/>'
            + g(heater('url(#iron)'), 32, 28, 0, .95)
            + '<path d="M14 44 L20 36 M50 44 L44 36" stroke="#f0a73a" stroke-width="3"/>')


@icon('Oil Can')
def _():
    return ('<path d="M20 30 H40 V48 Q30 52 20 48 Z" fill="url(#iron)"/>'
            + '<path d="M40 34 L54 22" stroke="#9aa3b5" stroke-width="3.4"/>'
            + '<rect x="25" y="24" width="10" height="6" rx="2" fill="#6a7180"/>'
            + g(drop('#f0a73a'), 54, 30, 0, .6))


@icon('Red Mist')
def _():
    return (g(axe('#b03040'), 24, 34, -26, .85) + g(axe('#b03040'), 42, 34, 26, .85)
            + '<ellipse cx="32" cy="44" rx="20" ry="8" fill="#9a0f1c" opacity=".45"/>')


@icon('Tusk and Board')
def _():
    return (g(heater('url(#iron)'), 26, 34, 0, .95)
            + '<path d="M42 42 Q52 36 50 24 Q44 30 42 42 Z" fill="url(#bone)"/>')


@icon('Two on the Trail')
def _():
    return (g(spear('url(#steel)', 38), 24, 32, 12, .85) + g(spear('url(#steel)', 38), 42, 32, 12, .85)
            + twinkle(50, 16, .7, '#d48c3c'))


@icon('Long Fuse')
def _():
    return (g(flame(), 46, 18, 0, .62)
            + '<path d="M44 22 Q30 26 24 38" fill="none" stroke="#c9b28a" stroke-width="3"/>'
            + '<circle cx="22" cy="42" r="9" fill="#2a2a33"/>')


@icon("Ancestors' Whisper")
def _():
    return (g(skull(), 32, 28, 0, .78)
            + arc_lines(32, 30, 18, 3, 80, '#8ee696', -90, 2)
            + twinkle(16, 44, .7, '#8ee696'))


@icon("Spellblade's Rhythm")
def _():
    return (g(sword(), 32, 32, 40, 1.0)
            + arc_lines(32, 32, 20, 3, 60, '#a6ecff', 40, 2)
            + twinkle(16, 18, .8, '#cfe6ff'))


@icon('Sworn Shield')
def _():
    return (g(heater(), 32, 32, 0, 1.1)
            + '<path d="M32 23 L35 30 H42 L36 34 L38 42 L32 37 L26 42 L28 34 L22 30 H29 Z" fill="#e0bb55"/>')


@icon('Ember-Warm')
def _():
    return (g(flame(), 32, 34, 0, 1.0)
            + arc_lines(32, 34, 20, 4, 90, '#ffb347', -90, 2))


@icon('Undimmed')
def _():
    return (burst(32, 32, 7, 17, 10, '#fff1a0', -90)
            + '<circle cx="32" cy="32" r="7" fill="#ffffff"/>')


@icon('Anvil-Patient')
def _():
    return ('<path d="M14 30 H44 L50 24 V34 H42 L38 44 H22 Z" fill="url(#iron)"/>'
            + '<path d="M20 46 H42 V52 H20 Z" fill="#4a4f5c"/>'
            + twinkle(49, 16, .7, '#a8d06b'))


@icon('Deep Foundation')
def _():
    return ('<path d="M12 36 H52 V44 H12 Z" fill="#7a7f8c"/>'
            + '<path d="M18 44 H28 V56 H18 Z M36 44 H46 V56 H36 Z" fill="#5a606c"/>'
            + g(heater('url(#iron)'), 32, 24, 0, .85))


@icon("Fletcher's Line")
def _():
    return (g(arrow('url(#steel)', '#a8d06b', 36), 32, 24, 0, .9)
            + g(arrow('url(#steel)', '#a8d06b', 36), 32, 42, 0, .9))


@icon('Crawling Venom')
def _():
    return ('<path d="M14 44 q8 -10 16 0 q8 10 16 0" fill="none" stroke="url(#poison)" stroke-width="4.2"/>'
            + g(drop('url(#poison)'), 32, 22, 0, .95)
            + twinkle(48, 18, .7, '#d6ff86'))


@icon('Evergreen')
def _():
    return ('<path d="M32 12 L44 32 H36 L46 50 H18 L28 32 H20 Z" fill="url(#leaf)"/>'
            + '<path d="M32 50 V56" stroke="#6b4422" stroke-width="4"/>')


@icon('Tide-Runner')
def _():
    return ('<path d="M8 40 q8 -8 16 0 t16 0 t16 0" fill="none" stroke="url(#water)" stroke-width="4"/>'
            + '<path d="M8 50 q8 -8 16 0 t16 0 t16 0" fill="none" stroke="url(#water)" stroke-width="3" opacity=".6"/>'
            + speed_lines(10, 24, 3, 11, 6, '#b4f4ff'))


@icon('Snapback')
def _():
    return (g(jaws(), 32, 32, 0, 1.15) + arc_lines(32, 32, 19, 2, 50, '#7fe3d8', -90, 2))


@icon('Sea-Sung')
def _():
    return (g(note(), 26, 34, -8, 1.0) + g(note('#b4f4ff'), 42, 26, 8, .8)
            + '<path d="M10 50 q8 -6 16 0 t16 0" fill="none" stroke="url(#water)" stroke-width="3"/>')


@icon('Vanish in Ink')
def _():
    return (g(octo(), 32, 28, 0, .95)
            + '<ellipse cx="32" cy="46" rx="18" ry="8" fill="#2a1d40" opacity=".75"/>')


@icon('Gift of the Reef')
def _():
    return ('<path d="M32 50 V32 M32 38 L24 28 M32 38 L40 28 M32 44 L22 38 M32 44 L42 38"'
            ' fill="none" stroke="#f2a0c8" stroke-width="3.4" stroke-linecap="round"/>'
            + g(plus(), 32, 18, 0, .55))


@icon('Noble Blood')
def _():
    return (g(drop(), 32, 32, 0, 1.2)
            + '<path d="M22 14 L26 20 L32 12 L38 20 L42 14 L40 24 H24 Z" fill="url(#gold)"/>')


@icon('Pit-Forged')
def _():
    return (g(flame(), 32, 38, 0, 1.0)
            + '<path d="M16 18 H48 V26 H16 Z" fill="url(#iron)"/>'
            + twinkle(14, 34, .7, '#ff9a2e'))


@icon('Slips the Line')
def _():
    return ('<path d="M16 18 V46 M26 18 V46" stroke="#5a606c" stroke-width="3"/>'
            + g(jaws('#8a3a3a'), 42, 32, 0, .9)
            + speed_lines(30, 32, 3, 9, 5, '#e0455a'))


@icon('Overflowing Cup')
def _():
    return ('<path d="M22 22 H42 L39 40 Q32 46 25 40 Z" fill="url(#gold)"/>'
            + '<path d="M28 46 H36 V52 H28 Z M22 52 H42 V56 H22 Z" fill="#8a5a14"/>'
            + g(drop(), 22, 24, 0, .55) + g(drop(), 42, 26, 0, .5))


@icon('The Slow March')
def _():
    return ('<path d="M24 14 H40 V50 H24 Z" fill="url(#bone)"/>'
            + '<path d="M16 24 H48" stroke="url(#bone)" stroke-width="6" stroke-linecap="round"/>'
            + speed_lines(10, 44, 2, 8, 6, '#8ee696', 0, .5))


@icon('Lord of the Mound')
def _():
    return ('<path d="M10 48 Q32 32 54 48 Z" fill="#4a4030"/>'
            + '<path d="M24 20 H40 V44 H24 Z" fill="#9aa0ad"/>'
            + '<path d="M28 26 H36 M32 26 V36" stroke="#5a606c" stroke-width="2.4"/>')


@icon('Bone-Thrift')
def _():
    return ('<path d="M18 40 h12 M34 40 h12" stroke="url(#bone)" stroke-width="6" stroke-linecap="round"/>'
            + g(skull(), 32, 24, 0, .66)
            + twinkle(48, 46, .7, '#8ee696'))


@icon('Breathless')
def _():
    return (g(skull(), 32, 30, 0, 1.0)
            + '<path d="M14 48 q6 -5 12 0 t12 0 t12 0" fill="none" stroke="#8ee696" stroke-width="2.6" opacity=".7"/>')


@icon('The Dead Listen')
def _():
    return ('<path d="M26 20 Q40 16 42 28 Q44 40 34 42 L30 50" fill="none" stroke="url(#bone)" stroke-width="5"'
            ' stroke-linecap="round"/>'
            + arc_lines(24, 30, 13, 3, 80, '#8ee696', 180, 2))


# ---- The Cogbound --------------------------------------------------------
# Orin rides and clamps, so his read as a machine getting hold of something.
# (Riven, who used to stand here as Vharo, has his own section under The Stray Banner.)

@icon('Spanner Swing')
def _():
    # Whatever is to hand: the spanner, swung, with the arc it travelled.
    return (poly('M14 46 Q22 20 46 14', '#ffa64d', 2.2)
            + g(wrench(), 36, 36, 35, 1.05)
            + twinkle(18, 20, .7, '#ffd9a8'))


@icon('Piggyback Rig')
def _():
    # He bolts onto someone else's back and makes that body the weapon: a small rig riding a big one.
    return ('<path d="M18 52 V34 a10 10 0 0 1 20 0 V52 Z" fill="url(#iron)"/>'
            + '<circle cx="28" cy="24" r="8" fill="url(#steel)"/>'
            + '<rect x="38" y="22" width="15" height="15" rx="3" fill="#ffa64d"/>'
            + '<circle cx="45.5" cy="29.5" r="3.4" fill="#2a2a33"/>'
            + poly('M38 30 L33 30', '#ffd9a8', 2.0)
            + g(gear(5, 7, '#ffd9a8'), 49, 45, 0, 1))


@icon('Seize the Arm')
def _():
    # The clamp closing on an arm — disarmed, and ground down for as long as he holds on.
    return ('<rect x="10" y="28" width="26" height="9" rx="4" fill="url(#iron)"/>'
            + '<path d="M34 20 h8 v10 h-8 Z M34 36 h8 v10 h-8 Z" fill="url(#steel)"/>'
            + '<path d="M42 23 h9 v8 h-9 Z M42 35 h9 v8 h-9 Z" fill="#ffa64d"/>'
            + poly('M48 33 h7', '#ffd9a8', 2.0)
            + burst(38, 33, 2, 6, 8, '#ff7a2f'))


@icon('Rush Bot')
def _():
    # A welded bot that charges the moment it lands.
    return (speed_lines(8, 32, 3, 11, 7, '#ffd9a8', 0, .7)
            + '<rect x="24" y="24" width="20" height="18" rx="4" fill="url(#iron)"/>'
            + '<circle cx="31" cy="31" r="3" fill="#ffa64d"/><circle cx="39" cy="31" r="3" fill="#ffa64d"/>'
            + '<path d="M28 42 v6 M40 42 v6" stroke="url(#steel)" stroke-width="3.4" stroke-linecap="round"/>'
            + '<path d="M32 24 v-6" stroke="url(#steel)" stroke-width="2.4"/>'
            + twinkle(32, 15, .7, '#ffd9a8'))


@icon('Hammer Weld')
def _():
    # A mend, but struck rather than prayed: his hammer coming down on a seam, the weld sparking
    # green where it takes. Best on anything cast rather than born.
    return (glow('<circle cx="30" cy="40" r="11" fill="#7ef09a"/>', .45)
            + g(hammer('url(#iron)'), 38, 26, 38, .92)
            + poly('M18 46 L30 38 L42 46', '#9dffb4', 2.4)
            + burst(30, 40, 2.5, 7, 8, '#d4ffb0')
            + twinkle(16, 30, .7, '#d4ffb0'))


@icon('Foundry-Cast')
def _():
    # Built in the Union's own moulds: the mould, and the heat still in it.
    return (glow('<rect x="20" y="30" width="24" height="14" rx="2" fill="#ff7a2f"/>', .55)
            + '<path d="M16 26 h32 l-4 20 h-24 Z" fill="url(#iron)"/>'
            + '<path d="M22 32 h20 l-2.5 10 h-15 Z" fill="url(#fireR)"/>'
            + arc_lines(32, 24, 10, 3, 60, '#ffa64d', -90, 2)
            + g(gear(5.5, 7, '#ffd9a8'), 50, 48, 0, 1))


# ---------------------------------------------------------------- catalog (for the frame + gallery)
# kind: "skill", "sig" (★ signature, gold frame), "passive" or "neutral" (round frame).
# Per champion: skill, second skill, ★ signature, passive. Mirrors ROSTER / SUMMONS in index.html.
CATALOG = {
    'common': ('Everyone', [('Attack', 'All champions', 'skill'), ('Guard', 'All champions', 'skill'),
        ('Provoke', 'Neutral skill', 'neutral'), ('Dispel', 'Neutral skill', 'neutral'),
        ('Toughness', 'Any champion', 'passive'), ('Might', 'Any champion', 'passive'), ('Swiftness', 'Any champion', 'passive'),
        ('Keen Edge', 'Any champion', 'passive'), ('Deep Well', 'Any champion', 'passive'), ('Second Wind', 'Any champion', 'passive'), ('Quick Hands', 'Any champion', 'passive')]),
    'mech': ('Ironclad Union', [
        ('Jump Start', 'Arclight', 'skill'),
        ('Built to Hold', 'Bulwark-7 · Nature', 'passive'), ('Flywheel', 'Sawtooth · Nature', 'passive'),
        ('Arc Transfer', 'Arclight · Nature', 'passive'), ('Dug In', 'Howitzer · Nature', 'passive'),
        ('Oil Can', 'Patchwork · Nature', 'passive'),
        ('Piston Punch', 'Bulwark-7', 'skill'), ('Steam Vent', 'Bulwark-7', 'skill'), ('Hydraulic Slam', 'Bulwark-7', 'sig'), ('Piledriver', 'Bulwark-7', 'skill'), ('Bunker', 'Bulwark-7', 'skill'), ('Tow Chain', 'Bulwark-7', 'skill'), ('Bulkhead', 'Bulwark-7', 'skill'), ('Reactive Plating', 'Bulwark-7', 'passive'), ('Counterweight', 'Bulwark-7', 'passive'),
        ('Rip Saw', 'Sawtooth', 'skill'), ('Shrapnel Spin', 'Sawtooth', 'skill'), ('Grinder', 'Sawtooth', 'sig'), ('Limb Shear', 'Sawtooth', 'skill'), ('Rev Up', 'Sawtooth', 'skill'), ('Tooth Breaker', 'Sawtooth', 'skill'), ('Buzz Lash', 'Sawtooth', 'skill'), ('Serrated', 'Sawtooth', 'passive'), ('Ragged Edge', 'Sawtooth', 'passive'),
        ('Arc Bolt', 'Arclight', 'skill'), ('Discharge', 'Arclight', 'skill'), ('Chain Surge', 'Arclight', 'sig'), ('Overload Coil', 'Arclight', 'skill'), ('Static Field', 'Arclight', 'skill'), ('Condenser Burst', 'Arclight', 'skill'), ('Brownout', 'Arclight', 'skill'), ('Feedback Loop', 'Arclight', 'passive'), ('Storm Caller', 'Arclight', 'passive'),
        ('Flak Burst', 'Howitzer', 'skill'), ('AP Round', 'Howitzer', 'skill'), ('Siege Shell', 'Howitzer', 'sig'), ('Mortar Walk', 'Howitzer', 'skill'), ('Shell Shock', 'Howitzer', 'skill'), ('Incendiary Shell', 'Howitzer', 'skill'), ('Creeping Barrage', 'Howitzer', 'skill'), ('Big Guns', 'Howitzer', 'passive'), ('Ranging Shot', 'Howitzer', 'passive'),
        ('Field Weld', 'Patchwork', 'skill'), ('Overclock', 'Patchwork', 'skill'), ('Assemble Scrapbot', 'Patchwork', 'sig'), ('Jury Rig', 'Patchwork', 'skill'), ('Coolant Flush', 'Patchwork', 'skill'), ('Plate Patch', 'Patchwork', 'skill'), ('Throw a Wrench', 'Patchwork', 'skill'), ('Maintenance Drone', 'Patchwork', 'passive'), ('Well Oiled', 'Patchwork', 'passive'),
        ('Beam Shot', 'Scrapbot (summon)', 'skill'),
        ('Beam Burst', 'Scrapbot (summon)', 'skill'),
    ]),
    'orc': ('Bloodtusk Horde', [
        ('Molotov', 'Drekka Firegut', 'skill'),
        ('Red Mist', 'Krug · Nature', 'passive'), ('Tusk and Board', 'Mogra · Nature', 'passive'),
        ('Two on the Trail', 'Vashka · Nature', 'passive'), ('Long Fuse', 'Drekka · Nature', 'passive'),
        ("Ancestors' Whisper", 'Hesk · Nature', 'passive'),
        ('Cleave', 'Krug Skullsplitter', 'skill'), ('Reckless Swing', 'Krug Skullsplitter', 'skill'), ('Blood Frenzy', 'Krug Skullsplitter', 'sig'), ('Twin Axes', 'Krug Skullsplitter', 'skill'), ("Warchief's Fury", 'Krug Skullsplitter', 'skill'), ('Headtaker', 'Krug Skullsplitter', 'skill'), ('Red Charge', 'Krug Skullsplitter', 'skill'), ('Bloodlust', 'Krug Skullsplitter', 'passive'), ('Grudge Axe', 'Krug Skullsplitter', 'passive'), ('Splitting Blow', 'Krug Skullsplitter', 'passive'),
        ('Skull Rattler', 'Mogra Ironhide', 'skill'), ('Ground Pound', 'Mogra Ironhide', 'skill'), ('Iron Hide', 'Mogra Ironhide', 'sig'), ('Bonebreaker', 'Mogra Ironhide', 'skill'), ('Hold the Line', 'Mogra Ironhide', 'skill'), ('Shield Crush', 'Mogra Ironhide', 'skill'), ('Gore and Pin', 'Mogra Ironhide', 'skill'), ('Thick Skull', 'Mogra Ironhide', 'passive'), ('Hidebound', 'Mogra Ironhide', 'passive'),
        ('Call the War Boar', 'Vashka Spearthrower', 'skill'), ("Hunter's Mark", 'Vashka Spearthrower', 'skill'), ('Gutpiercer', 'Vashka Spearthrower', 'sig'), ('Pinning Throw', 'Vashka Spearthrower', 'skill'), ('Volley of Spears', 'Vashka Spearthrower', 'skill'), ('Cull the Weak', 'Vashka Spearthrower', 'skill'), ('Hobbling Cast', 'Vashka Spearthrower', 'skill'), ('Steppe Hunter', 'Vashka Spearthrower', 'passive'), ('Marked for the Pot', 'Vashka Spearthrower', 'passive'),
        ('Firepot', 'Drekka Firegut', 'skill'), ('Napalm Jar', 'Drekka Firegut', 'skill'), ('Powder Keg', 'Drekka Firegut', 'sig'), ('Cinder Spray', 'Drekka Firegut', 'skill'), ('Sticky Tar', 'Drekka Firegut', 'skill'), ('Shrapnel Bomb', 'Drekka Firegut', 'skill'), ('Blastcap', 'Drekka Firegut', 'skill'), ('Pyromaniac', 'Drekka Firegut', 'passive'), ('Wide Spread', 'Drekka Firegut', 'passive'),
        ('Spirit Ward', 'Old Mother Hesk', 'skill'), ('Bone Charm', 'Old Mother Hesk', 'skill'), ('Drums of the Horde', 'Old Mother Hesk', 'sig'), ("Ancestor's Balm", 'Old Mother Hesk', 'skill'), ('Totem of Stone', 'Old Mother Hesk', 'skill'), ('Quickstep Drums', 'Old Mother Hesk', 'skill'), ("Ancestors' Rebuke", 'Old Mother Hesk', 'skill'), ('Bind the Breath', 'Old Mother Hesk', 'skill'), ('Ancestral Watch', 'Old Mother Hesk', 'passive'), ('Long Memory', 'Old Mother Hesk', 'passive'),
        ('Gore', 'War Boar (summon)', 'skill'),
        ('Tusk Charge', 'War Boar (summon)', 'skill'),
    ]),
    'human': ('Kingdom of Aldmere', [
        ('Shieldbearer', 'Sir Garrick Vane', 'skill'), ('Heroic', 'Wren / Garrick · alt passive', 'passive'),
        ("Spellblade's Rhythm", 'Wren · Nature', 'passive'), ('Sworn Shield', 'Garrick · Nature', 'passive'),
        ('Ember-Warm', 'Aldous · Nature', 'passive'), ('Undimmed', 'Liesl · Nature', 'passive'),
        ('Power Slash', 'Wren', 'skill'), ('Arcane Edge', 'Wren', 'skill'), ('Thunderclap', 'Wren', 'sig'), ('Mageslayer', 'Wren', 'skill'), ('Runed Thrust', 'Wren', 'skill'), ('Arcane Ward', 'Wren', 'passive'), ('Spellbreak Arc', 'Wren', 'skill'), ('Null Edge', 'Wren', 'skill'), ('Disrupting Edge', 'Wren', 'passive'),
        ('Smite', 'Sir Garrick Vane', 'skill'), ('Consecrate', 'Sir Garrick Vane', 'skill'), ('Oathguard', 'Sir Garrick Vane', 'sig'), ('Hammer of Judgement', 'Sir Garrick Vane', 'skill'), ('Lionheart', 'Sir Garrick Vane', 'skill'), ('Retribution', 'Sir Garrick Vane', 'passive'), ('Shield of the Realm', 'Sir Garrick Vane', 'passive'), ('Castigate', 'Sir Garrick Vane', 'skill'), ('Shield Charge', 'Sir Garrick Vane', 'skill'), ('Last Oath', 'Sir Garrick Vane', 'passive'),
        ('Aimed Shot', 'Mara Holt', 'skill'), ('Ricochet', 'Mara Holt', 'skill'), ('Powder Shot', 'Mara Holt', 'sig'), ('Pistol Whip', 'Mara Holt', 'skill'), ('Volley Fire', 'Mara Holt', 'skill'), ('Deadeye', 'Mara Holt', 'passive'), ('Punch-Through', 'Mara Holt', 'skill'), ('Called Shot', 'Mara Holt', 'skill'), ('Finishing Round', 'Mara Holt', 'passive'),
        ('Fireball', 'Aldous Emberfall', 'skill'), ('Ignite', 'Aldous Emberfall', 'skill'), ('Inferno', 'Aldous Emberfall', 'sig'), ('Flame Lance', 'Aldous Emberfall', 'skill'), ('Mantle of Flame', 'Aldous Emberfall', 'skill'), ('Kindling', 'Aldous Emberfall', 'passive'), ('Backdraft', 'Aldous Emberfall', 'skill'), ('Draw the Ember', 'Aldous Emberfall', 'skill'), ('Kindled', 'Aldous Emberfall', 'passive'),
        ('Sacred Light', 'Sister Liesl', 'skill'), ('Guardian Angel', 'Sister Liesl', 'skill'), ('Prayer of Dawn', 'Sister Liesl', 'sig'), ('Benediction', 'Sister Liesl', 'skill'), ('Censure', 'Sister Liesl', 'skill'), ('First Light', 'Sister Liesl', 'skill'), ('Mercy', 'Sister Liesl', 'passive'), ('Dawnbreak', 'Sister Liesl', 'skill'), ('Absolution', 'Sister Liesl', 'skill'), ('Dawnward March', 'Sister Liesl', 'passive'),
    ]),
    'stone': ('Stoneleaf Accord', [
        ('Anvil-Patient', 'Durgan · Nature', 'passive'), ('Deep Foundation', 'Hilda · Nature', 'passive'),
        ("Fletcher's Line", 'Aelira · Nature', 'passive'), ('Crawling Venom', 'Faelan · Nature', 'passive'),
        ('Evergreen', 'Elowen · Nature', 'passive'),
        ('Hammerfall', 'Durgan Anvilbeard', 'skill'), ('Anvil Strike', 'Durgan Anvilbeard', 'skill'), ('Mountain Breaker', 'Durgan Anvilbeard', 'sig'), ('Forge Strike', 'Durgan Anvilbeard', 'skill'), ('Quake Hammer', 'Durgan Anvilbeard', 'skill'), ('Grudge', 'Durgan Anvilbeard', 'passive'), ('Anvil Drop', 'Durgan Anvilbeard', 'skill'), ('Hold the Pass', 'Durgan Anvilbeard', 'skill'), ('Hammer and Anvil', 'Durgan Anvilbeard', 'passive'),
        ('Shield Bash', 'Hilda Stonewall', 'skill'), ('Shieldwall', 'Hilda Stonewall', 'skill'), ('Stand Firm', 'Hilda Stonewall', 'sig'), ('Boulder Toss', 'Hilda Stonewall', 'skill'), ('Bulwark of the Accord', 'Hilda Stonewall', 'skill'), ('Unbreakable', 'Hilda Stonewall', 'passive'), ('Mountainside', 'Hilda Stonewall', 'skill'), ('Set in Stone', 'Hilda Stonewall', 'skill'), ('Seamless Plate', 'Hilda Stonewall', 'passive'),
        ('Swift Arrows', 'Aelira Swiftwind', 'skill'), ('Arrow Rain', 'Aelira Swiftwind', 'skill'), ('Hawkeye', 'Aelira Swiftwind', 'sig'), ('Piercing Shot', 'Aelira Swiftwind', 'skill'), ('Steady Aim', 'Aelira Swiftwind', 'skill'), ('Keen Eye', 'Aelira Swiftwind', 'passive'), ('Threadneedle', 'Aelira Swiftwind', 'skill'), ('Loose and Move', 'Aelira Swiftwind', 'skill'), ('Second Nock', 'Aelira Swiftwind', 'passive'),
        ('Venom Bolt', 'Faelan Thornshot', 'skill'), ('Envenom', 'Faelan Thornshot', 'skill'), ('Thornvolley', 'Faelan Thornshot', 'sig'), ('Crippling Bolt', 'Faelan Thornshot', 'skill'), ('Toxic Barrage', 'Faelan Thornshot', 'skill'), ('Debilitating Venom', 'Faelan Thornshot', 'passive'), ('Blinding Toxin', 'Faelan Thornshot', 'skill'), ('Marrowrot', 'Faelan Thornshot', 'skill'), ('Rotgut', 'Faelan Thornshot', 'passive'),
        ('Regrowth', 'Elowen Greenmantle', 'skill'), ('Entangle', 'Elowen Greenmantle', 'skill'), ('Bloom of Spring', 'Elowen Greenmantle', 'sig'), ('Barkskin', 'Elowen Greenmantle', 'skill'), ('Thornlash', 'Elowen Greenmantle', 'skill'), ('Wind at the Back', 'Elowen Greenmantle', 'skill'), ('Forest Stride', 'Elowen Greenmantle', 'passive'), ('Verdant Aura', 'Elowen Greenmantle', 'passive'), ('Grasping Roots', 'Elowen Greenmantle', 'skill'), ('Oaken Vigil', 'Elowen Greenmantle', 'skill'), ('Deeproot', 'Elowen Greenmantle', 'passive'),
    ]),
    'tide': ('The Tideborn', [
        ('Anchor Chain', 'Tharos Razorfin', 'skill'), ('Stinging Veil', 'Octavia Inkveil', 'skill'),
        ('Turncoat Verse', 'Seraphine Wavecaller', 'skill'),
        ('Tide-Runner', 'Tharos · Nature', 'passive'), ('Snapback', 'Grubblefin · Nature', 'passive'),
        ('Sea-Sung', 'Seraphine · Nature', 'passive'), ('Vanish in Ink', 'Octavia · Nature', 'passive'),
        ('Gift of the Reef', 'Maren · Nature', 'passive'),
        ('Trident Lunge', 'Tharos Razorfin', 'skill'), ('Riptide', 'Tharos Razorfin', 'skill'), ('Blood in the Water', 'Tharos Razorfin', 'sig'), ('Feeding Frenzy', 'Tharos Razorfin', 'skill'), ('Undertow', 'Tharos Razorfin', 'skill'), ('Blood Scent', 'Tharos Razorfin', 'passive'), ('Chum the Water', 'Tharos Razorfin', 'skill'), ('Gutter', 'Tharos Razorfin', 'skill'), ('Red Water', 'Tharos Razorfin', 'passive'),
        ('Rimebite', 'Grubblefin', 'skill'), ('Slippery Scales', 'Grubblefin', 'skill'), ('Glacial Frenzy', 'Grubblefin', 'sig'), ('Barnacle Bite', 'Grubblefin', 'skill'), ('Tail Whip', 'Grubblefin', 'skill'), ('Choking Bite', 'Grubblefin', 'skill'), ('Frostplate', 'Grubblefin', 'passive'), ('Bait the Hook', 'Grubblefin', 'skill'), ('Icebreaker', 'Grubblefin', 'skill'), ('Gnashing', 'Grubblefin', 'passive'),
        ("Siren's Hush", 'Seraphine Wavecaller', 'skill'), ('Dirge of the Deep', 'Seraphine Wavecaller', 'skill'), ('Lure Song', 'Seraphine Wavecaller', 'sig'), ('Drowning Chorus', 'Seraphine Wavecaller', 'skill'), ('Song of the Depths', 'Seraphine Wavecaller', 'skill'), ('Echo', 'Seraphine Wavecaller', 'passive'), ('Abyssal Note', 'Seraphine Wavecaller', 'skill'), ('Hollow the Throat', 'Seraphine Wavecaller', 'skill'), ('Hush the Deep', 'Seraphine Wavecaller', 'passive'),
        ('Ink Double', 'Octavia Inkveil', 'skill'), ('Tentacle Snare', 'Octavia Inkveil', 'skill'), ('Ink Cloud', 'Octavia Inkveil', 'sig'), ('Ink Whip', 'Octavia Inkveil', 'skill'), ('Crushing Grip', 'Octavia Inkveil', 'skill'), ('Ink Sac', 'Octavia Inkveil', 'passive'), ('Eight Arms', 'Octavia Inkveil', 'skill'), ('Abyssal Ink', 'Octavia Inkveil', 'skill'), ('Clouded Eyes', 'Octavia Inkveil', 'passive'),
        ('Healing Tide', 'Maren Pearlheart', 'skill'), ('Tide Pool', 'Maren Pearlheart', 'skill'), ('Pearl Barrier', 'Maren Pearlheart', 'sig'), ('Reef Bloom', 'Maren Pearlheart', 'skill'), ('Riptide Crash', 'Maren Pearlheart', 'skill'), ('Rimefall', 'Maren Pearlheart', 'skill'), ('Backwash', 'Maren Pearlheart', 'passive'), ('Tidecaller', 'Maren Pearlheart', 'passive'), ('Salt the Reef', 'Maren Pearlheart', 'skill'), ('Undertow Grasp', 'Maren Pearlheart', 'skill'), ('Spring Tide', 'Maren Pearlheart', 'passive'),
        ('Ink Lash', 'Ink Illusion (summon)', 'skill'),
    ]),
    'crimson': ('The Crimson Court', [
        ('Tear Apart', 'Gorehound', 'passive'),
        ('Noble Blood', 'Vesper · Nature', 'passive'), ('Pit-Forged', 'Malgrath · Nature', 'passive'),
        ('Slips the Line', 'Gorehound · Nature', 'passive'), ('Overflowing Cup', 'Morwenna · Nature', 'passive'),
        ('Crimson Lunge', 'Vesper Nightshade', 'skill'), ('Night Waltz', 'Vesper Nightshade', 'skill'), ('Execute', 'Vesper Nightshade', 'sig'), ('Exsanguinate', 'Vesper Nightshade', 'skill'), ('Throat Tear', 'Vesper Nightshade', 'skill'), ('Mist Form', 'Vesper Nightshade', 'skill'), ('Riposte', 'Vesper Nightshade', 'passive'), ('Scarlet Veil', 'Vesper Nightshade', 'skill'), ('Gaze of the Count', 'Vesper Nightshade', 'skill'), ('Taste for It', 'Vesper Nightshade', 'passive'),
        ('Hellfire Slam', 'Malgrath the Unbound', 'skill'), ('Demonic Roar', 'Malgrath the Unbound', 'skill'), ('Infernal Wrath', 'Malgrath the Unbound', 'sig'), ('Pit Chains', 'Malgrath the Unbound', 'skill'), ('Sulphur Breath', 'Malgrath the Unbound', 'skill'), ('Blood Pact', 'Malgrath the Unbound', 'skill'), ('Brimstone Hide', 'Malgrath the Unbound', 'passive'), ('Brand', 'Malgrath the Unbound', 'skill'), ('Hellmouth', 'Malgrath the Unbound', 'skill'), ('Hell Answers', 'Malgrath the Unbound', 'passive'),
        ('Kiss of Ruin', 'Seraxa Thornwing', 'skill'), ('Shadowstep', 'Seraxa Thornwing', 'skill'), ('Dance of Knives', 'Seraxa Thornwing', 'sig'), ('Wing Carve', 'Seraxa Thornwing', 'skill'), ("Predator's Grace", 'Seraxa Thornwing', 'skill'), ('Flurry', 'Seraxa Thornwing', 'passive'), ('Stoop', 'Seraxa Thornwing', 'skill'), ('Razor Gale', 'Seraxa Thornwing', 'skill'), ('Blood Rush', 'Seraxa Thornwing', 'passive'),
        ('Rend', 'Gorehound', 'skill'), ('Savage Maul', 'Gorehound', 'skill'), ('Hellhound Howl', 'Gorehound', 'sig'), ('Hamstring', 'Gorehound', 'skill'), ('Feral Lunge', 'Gorehound', 'skill'), ('Come Apart', 'Gorehound', 'skill'), ('Throat Lock', 'Gorehound', 'skill'), ('Worry the Wound', 'Gorehound', 'skill'), ('Gorge', 'Gorehound', 'passive'),
        ('Blight Hex', 'Morwenna Bloodweaver', 'skill'), ('Blood Siphon', 'Morwenna Bloodweaver', 'skill'), ('Blood Communion', 'Morwenna Bloodweaver', 'sig'), ('Crimson Mend', 'Morwenna Bloodweaver', 'skill'), ('Wither', 'Morwenna Bloodweaver', 'skill'), ('Blood Ward', 'Morwenna Bloodweaver', 'skill'), ('Quickened Blood', 'Morwenna Bloodweaver', 'skill'), ('Withering Curse', 'Morwenna Bloodweaver', 'passive'), ('Open the Vein', 'Morwenna Bloodweaver', 'skill'), ('Blood Fog', 'Morwenna Bloodweaver', 'skill'), ('Blood Price', 'Morwenna Bloodweaver', 'passive'),
    ]),
    'undead': ('The Pale Host', [
        ('The Slow March', 'Mordrek · Nature', 'passive'), ('Lord of the Mound', 'Barrow · Nature', 'passive'),
        ('Bone-Thrift', 'Cadris · Nature', 'passive'), ('Breathless', 'Vaun · Nature', 'passive'),
        ('The Dead Listen', 'Mortessa · Nature', 'passive'),
        ('Grave Cross', 'Mordrek the Interred', 'skill'), ('Graveside Chill', 'Mordrek the Interred', 'skill'), ('Last Rites', 'Mordrek the Interred', 'sig'), ('Plant the Marker', 'Mordrek the Interred', 'skill'), ('Second Grave', 'Mordrek the Interred', 'passive'),
        ('Tomb Slab', 'Barrow', 'skill'), ('Grasping Hands', 'Barrow', 'skill'), ('Barrow Wall', 'Barrow', 'sig'), ('Crypt Breaker', 'Barrow', 'skill'), ('Hold the Grave', 'Barrow', 'skill'), ('Graveyard Fence', 'Barrow', 'skill'), ('Burrow', 'Barrow', 'skill'), ('Feast of the Fallen', 'Barrow', 'passive'),
        ('Bone Dart', 'Cadris Gravecall', 'skill'), ('Shambling Rise', 'Cadris Gravecall', 'skill'), ('Charnel Volley', 'Cadris Gravecall', 'sig'), ('Rot Shot', 'Cadris Gravecall', 'skill'), ('Marrow Pierce', 'Cadris Gravecall', 'skill'), ('Toll of the Dead', 'Cadris Gravecall', 'passive'),
        ('Shroudcast', 'Vaun Shroudfletch', 'skill'), ('Withering Shot', 'Vaun Shroudfletch', 'skill'), ('Pall of Bones', 'Vaun Shroudfletch', 'sig'), ('Graveshot', 'Vaun Shroudfletch', 'skill'), ('Scatter of Bones', 'Vaun Shroudfletch', 'skill'), ('Deathmark', 'Vaun Shroudfletch', 'passive'),
        ('Grave Mend', 'Mortessa', 'skill'), ('Coffin', 'Mortessa', 'skill'), ('Second Burial', 'Mortessa', 'sig'), ('Hex of Ruin', 'Mortessa', 'skill'), ('Soul Siphon', 'Mortessa', 'skill'), ('Stolen Hours', 'Mortessa', 'skill'), ('Keeper of the Coffin', 'Mortessa', 'passive'),
        ("Grave's Reach", 'Mordrek the Interred', 'skill'), ('Dead March', 'Mordrek the Interred', 'skill'), ('Grave-Patient', 'Mordrek the Interred', 'passive'),
        ('Weight of the Mound', 'Barrow', 'skill'), ("The Lord's Due", 'Barrow', 'skill'), ('First Out of the Ground', 'Barrow', 'passive'),
        ('Grip of the Grave', 'Cadris Gravecall', 'skill'), ('Charnel Tide', 'Cadris Gravecall', 'skill'), ('Grave-Debt', 'Cadris Gravecall', 'passive'),
        ('Rib-Splitter', 'Vaun Shroudfletch', 'skill'), ('Hold the Shot', 'Vaun Shroudfletch', 'skill'), ('Scattercast', 'Vaun Shroudfletch', 'passive'),
        ('Chorus of the Interred', 'Mortessa', 'skill'), ('Pall of Silence', 'Mortessa', 'skill'), ('The Dead Are Tended', 'Mortessa', 'passive'),
        ('Clawing Grasp', 'Shambler (summon)', 'skill'),
    ]),
    'riftborn': ('The Riftborn', [
        ('Fixed Point', 'Thurgan · Nature', 'passive'),
        ('Finisher', 'Nyx · Nature', 'passive'),
        ('Dead Weight', 'Thurgan', 'skill'), ('Deadfall', 'Thurgan', 'sig'), ('Event Horizon', 'Thurgan', 'skill'),
        ('Collapsing Fist', 'Thurgan', 'skill'), ('Graviton Guard', 'Thurgan', 'skill'), ('Singularity', 'Thurgan', 'skill'),
        ('Crushing Field', 'Thurgan', 'passive'),
        # Vharo's and Orin's Riftborn-era kits. Both champions are Cogbound now (see the 'cog'
        # section) and these skills are gone from the ROSTER; the glyphs are kept against the day
        # the faction is brought back, and are listed here so the coverage check stays honest.
        ('Ray', 'Vharo (retired)', 'skill'), ('Prism Lance', 'Vharo (retired)', 'skill'),
        ('Glare', 'Vharo (retired)', 'skill'), ('Focus', 'Vharo (retired)', 'skill'),
        ('Recall', 'Vharo (retired)', 'skill'),
        ('Clarion', 'Resh', 'skill'), ('Quickening Chord', 'Resh', 'skill'), ('Thrum', 'Resh', 'skill'),
        ('Discord', 'Resh', 'skill'), ('Steady Tone', 'Resh', 'skill'),
        ('Null Bolt', 'Nyx', 'skill'), ('Unmake', 'Nyx', 'sig'), ('Silencing Gyre', 'Nyx', 'skill'),
        ('Phase', 'Nyx', 'skill'), ('Collapse Point', 'Nyx', 'skill'),
        ('Attune: Gravity', 'Orin (retired)', 'skill'), ('Grand Chord', 'Orin (retired)', 'skill'),
        ('Attune: Light', 'Orin (retired)', 'skill'), ('Attune: Void', 'Orin (retired)', 'skill'),
        ('Conduct', 'Orin (retired)', 'skill'),
    ]),
    'stray': ('The Stray Banner', [
        ('Invulnerable Clone', 'Ryuunosuke · Nature', 'passive'),
        ('Shadow Matrix', 'Ryuunosuke', 'skill'), ('Iaijutsu', 'Ryuunosuke', 'sig'), ('Mark of Death', 'Ryuunosuke', 'skill'),
        ('Smoke Veil', 'Ryuunosuke', 'skill'), ('Twin Slash', 'Ryuunosuke', 'skill'), ('Blade Dance', 'Ryuunosuke', 'skill'),
        ('Shadow Step', 'Ryuunosuke', 'passive'), ('Killing Intent', 'Ryuunosuke', 'passive'),
        ('Unblinking', 'Riven · Nature', 'passive'), ('Dead Aim', 'Riven', 'passive'),
        ('Sighted Throw', 'Riven', 'skill'), ('Emptied Hands', 'Riven', 'sig'),
        ('Fan of Blades', 'Riven', 'skill'), ('Recall Swords', 'Riven', 'skill'),
        ('Barrier', 'Riven', 'skill'),
        ('Red Blood', "Zul'kan · Nature", 'passive'), ('Retaliatory Bash', "Zul'kan", 'passive'),
        ('Ground Slam', "Zul'kan", 'skill'), ('Skyward Smash', "Zul'kan", 'sig'),
        ('War Cry', "Zul'kan", 'skill'), ('Seismic Toss', "Zul'kan", 'skill'),
        ('Iron Stance', "Zul'kan", 'skill'), ('Tremor', "Zul'kan", 'skill'),
        ('Command the Fallen', 'Riven', 'skill'), ('Blade Harvest', 'Riven', 'skill'), ('Never There', 'Riven', 'passive'),
        ('Blow the Valve', 'Orin', 'skill'), ('Plate Rig', 'Orin', 'skill'), ('Tap the Line', 'Orin', 'passive'),
        ('Dissonance', 'Fin-Keeper Shazrak', 'skill'), ('Hold the Note', 'Fin-Keeper Shazrak', 'skill'), ('Keeping Time', 'Fin-Keeper Shazrak', 'passive'),
        ('Shockwave', "Zul'kan", 'skill'), ('Haymaker', "Zul'kan", 'skill'), ('Skullcracker', "Zul'kan", 'passive'),
        ('Severance', 'Ryuunosuke', 'skill'), ('Lingering Cut', 'Ryuunosuke', 'skill'),
    ]),
    'cog': ('The Cogbound', [
        ('Foundry-Cast', 'Orin', 'passive'),
        ('Spanner Swing', 'Orin', 'skill'), ('Piggyback Rig', 'Orin', 'sig'),
        ('Seize the Arm', 'Orin', 'skill'), ('Rush Bot', 'Orin', 'skill'),
        ('Overclock', 'Orin', 'skill'), ('Hammer Weld', 'Orin', 'skill'),
    ]),
    'monster': ('Monsters of Ashfall Road', [
        ('Hardened Crust', 'Magma Slime', 'passive'), ('Reassemble', 'Bone Rattler', 'passive'),
        ('Troll Blood', 'Cave Troll', 'passive'), ('Grave Hunger', 'Crypt Ghoul', 'passive'),
        ('Incorporeal', 'Banshee', 'passive'), ('Iron Plating', 'Rust Golem', 'passive'),
        ('Second Intention', 'Disgraced Duelist', 'passive'), ('Fading', 'Pale Phantom', 'passive'),
        ('Pack Hunter', 'Grave Hound', 'passive'), ('Dread Armor', 'Fallen Knight', 'passive'),
        ('Stone Skin', 'Stone Gargoyle', 'passive'),
    ]),
}


# ---------------------------------------------------------------- second-wave skills
# `bolt` above is the crossbow bolt (it shadows the lightning one), so lightning gets its own helper.
def zap(fill='url(#bolt)'):
    return f'<path d="M3 -22 L-9 3 L-1.5 3 L-5 22 L10 -5 L2.5 -5 L8.5 -22 Z" fill="{fill}"/>'


def rock(fill='url(#clay)'):
    return f'<path d="M-13 6 L-9 -8 L2 -13 L12 -5 L11 8 L-2 13 Z" fill="{fill}"/><path d="M-9 -8 L0 -2 L11 -5 M0 -2 L-2 13" stroke-width="1.4" fill="none"/>'


def wing(fill='#3d1f4a'):
    return f'<path d="M0 -14 Q16 -12 22 2 Q14 -2 10 2 Q12 8 6 12 Q4 4 -1 0 Z" fill="{fill}"/>'


def claw(color='#e9e4d8'):
    return poly('M-12 -14 Q-4 2 -8 16', color, 2.6) + poly('M0 -16 Q4 2 2 18', color, 2.6) + poly('M12 -14 Q14 2 10 16', color, 2.6)


# ---- Ironclad Union
@icon('Piledriver')
def _():
    # A driven ram, not a fist: Hydraulic Slam already owns the mech-fist-on-an-anvil read.
    return ('<rect x="7" y="48" width="50" height="7" rx="2" fill="#5a4a3a"/>'
            + '<path d="M32 48 L26 56 M32 48 L38 56" stroke-width="1.4"/>'
            + '<rect x="23" y="7" width="18" height="9" rx="2" fill="url(#iron)"/>'
            + '<rect x="28.5" y="15" width="7" height="13" fill="#5d6780"/>'
            + '<rect x="18" y="26" width="28" height="16" rx="2.4" fill="url(#steel)"/>'
            + '<path d="M23 31 H41 M23 37 H41" stroke-width="1.4"/>'
            + burst(32, 47, 4, 11, 9, '#ffd166')
            + speed_lines(9, 20, 3, 9, 6, '#f0a73a') + speed_lines(47, 20, 3, 9, 6, '#f0a73a'))


# Bunker's own gradients, carried over from the hand-drawn icon this glyph replaces.
# Glyph-local defs are fine — frame() drops the glyph inside the same <svg> (cf. RV_DEFS).
BK_DEFS = ('<defs>'
           '<linearGradient id="bkSteel" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#b9c4d8"/><stop offset="1" stop-color="#6b7792"/></linearGradient>'
           '<linearGradient id="bkGround" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#5a4a36"/><stop offset="1" stop-color="#3a2f22"/></linearGradient>'
           '</defs>')


@icon('Bunker')
def _():
    """PORTED FROM THE HAND-DRAWN skills/bunker.svg — do not "simplify" back to a shield.

    That file was bespoke art (the hull driven into the ground, anchors bitten in, two rounds
    glancing off the plating) and it was NOT produced by this script, so every run quietly
    overwrote it with a generic heater-shield glyph. The art is the better read — it draws the
    actual skill rather than a shield that could be any ward in the game — but it was missing
    the faction frame every other icon wears, which made it the one odd tile in the set.
    Keeping it here gets both: the original drawing, inside the house frame, reproducible.

    The paths are the originals in absolute 0-64 coordinates, scaled about their own centre so
    they sit inside the frame's safe area (~8..56) instead of running to the tile edge.
    """
    art = (
        # the ground it is driven into
        '<path d="M4 48 h56 v10 H4 z" fill="url(#bkGround)"/>'
        '<path d="M4 48 h56" stroke="#7d6a4e" stroke-width="2" fill="none"/>'
        # the hull: a squat, braced block
        '<path d="M14 26 h36 a4 4 0 0 1 4 4 v18 H10 V30 a4 4 0 0 1 4 -4 z" fill="url(#bkSteel)"/>'
        # the vision slit
        '<rect x="18" y="33" width="28" height="6" rx="2" fill="#1b2130"/>'
        '<rect x="18" y="33" width="28" height="2.5" rx="1.2" fill="#f0a73a" opacity=".55"/>'
        # anchors, bitten into the earth
        '<path d="M14 48 l-4 8 M50 48 l4 8" stroke="#2b3243" stroke-width="3.4" fill="none"/>'
        '<path d="M22 48 v7 M42 48 v7" stroke="#2b3243" stroke-width="2.6" fill="none"/>'
        # two rounds glancing off the plating
        '<path d="M30 10 l0 9" stroke="#f0a73a" stroke-width="2.6" fill="none"/>'
        '<path d="M30 22 q6 2 11 -5" stroke="#f0a73a" stroke-width="2.6" fill="none"/>'
        '<path d="M46 12 l-3 7" stroke="#f0a73a" stroke-width="2.2" opacity=".7" fill="none"/>'
        '<path d="M44 21 q5 2 9 -3" stroke="#f0a73a" stroke-width="2.2" opacity=".7" fill="none"/>'
    )
    return BK_DEFS + f'<g transform="translate(32 34) scale(.84) translate(-32 -34)">{art}</g>'


@icon('Limb Shear')
def _():
    return (g(sawblade(13, 12), 27, 29)
            + speed_lines(40, 18, 3, 10, 5, '#ffd166')
            + g(drop(), 45, 41, 0, 1.3) + g(drop(), 38, 51, 0, .95))


@icon('Rev Up')
def _():
    return (g(gear(11, 9, '#f0a73a'), 32, 36, 0, 1.45)
            + arc_lines(32, 36, 21, 3, 120, '#ffd166', -90, 2.2)
            + poly('M32 18 L32 8', '#8be28b', 2.6) + poly('M26 13 L32 7 L38 13', '#8be28b', 2.6))


@icon('Overload Coil')
def _():
    return (arc_lines(32, 34, 15, 3, 300, '#4d6a8f', -90, 2.4)
            + g(zap(), 32, 32, 0, 1.12) + glow(g(zap('#a6ecff'), 32, 32, 0, 1.12), .55)
            + twinkle(13, 20, .9, '#7fe3ff') + twinkle(51, 44, .9, '#7fe3ff'))


@icon('Static Field')
def _():
    return (arc_lines(32, 38, 10, 4, 200, '#7fe3ff', -90, 2.2, 6)
            + g(zap(), 20, 28, 0, .62) + g(zap(), 32, 24, 0, .72) + g(zap(), 44, 28, 0, .62)
            + twinkle(32, 50, .8, '#a6ecff'))


@icon('Mortar Walk')
def _():
    return (poly('M8 46 Q24 10 40 40', '#c9b28a', 2.2)
            + burst(14, 47, 3, 8, 8, '#ffd166') + burst(32, 47, 3.4, 9.5, 9)
            + burst(50, 45, 3.6, 10, 9, '#ffd166')
            + '<rect x="6" y="52" width="52" height="5" rx="2" fill="#5a4a3a"/>')


@icon('Shell Shock')
def _():
    return (burst(32, 36, 5, 15, 11, 'url(#fireR)')
            + g(gear(6, 7, '#9aa3b5'), 32, 36, 0, 1.1)
            + stun_stars(32, 15, 24))


@icon('Jury Rig')
def _():
    return (g(wrench(), 24, 34, -28, 1.05)
            + g(plus(), 44, 24, 0, .95)
            + twinkle(45, 44, .8, '#8be28b') + twinkle(16, 18, .7, '#8be28b'))


@icon('Coolant Flush')
def _():
    return (g(gear(8, 8, '#7a8296'), 32, 18, 0, 1.0)
            + g(drop('url(#water)'), 22, 38, 0, 1.5) + g(drop('url(#water)'), 34, 46, 0, 1.2)
            + g(drop('url(#water)'), 44, 36, 0, 1.0)
            + arc_lines(32, 20, 14, 2, 150, '#b4f4ff', 90, 2.0))


# ---- Ironclad Union, third wave
@icon('Tow Chain')
def _():
    # Reach and drag: the hook out at the end of a heavy chain, and an arrow hauling it all back.
    links = ''.join(g('<ellipse rx="4.6" ry="3" fill="url(#iron)" stroke-width="1.2"/>'
                      '<ellipse rx="2.2" ry="1.2" fill="#2a2e3a" stroke="none"/>', x, y, -38)
                    for x, y in ((11, 51), (17, 46), (23, 41), (29, 36), (35, 31)))
    hook = (poly('M0 -12 L0 -4 A7 7 0 1 0 -8 2', '#c9ccd8', 3.2)
            + '<rect x="-2.8" y="-16" width="5.6" height="5.5" rx="1.6" fill="url(#gold)"/>')
    return (links + g(hook, 45, 27, 20)
            + line(14, 20, 32, 20, '#ffd166', 2.4)
            + poly('M22 13 L13 20 L22 27', '#ffd166', 2.6))


@icon('Bulkhead')
def _():
    # Buttoned up: two slabs of plate driven shut on a sealed seam, half of everything stops here.
    rivets = ''.join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#f0a73a" stroke-width="1"/>'
                     for x, y in ((13, 24), (13, 44), (51, 24), (51, 44)))
    return ('<rect x="8" y="18" width="21" height="31" rx="2.5" fill="url(#iron)"/>'
            + '<rect x="35" y="18" width="21" height="31" rx="2.5" fill="url(#iron)"/>'
            + '<path d="M11 31 H26 M11 38 H26 M38 31 H53 M38 38 H53" stroke-width="1.4"/>'
            + rivets
            + '<rect x="28" y="15" width="8" height="37" rx="2" fill="url(#steel)"/>'
            + '<path d="M32 19 V48" stroke="#5d6780" stroke-width="1.2" fill="none"/>'
            + line(16, 11, 26, 11, '#ffd166', 2.2) + poly('M22 7 L27 11 L22 15', '#ffd166', 2.2)
            + line(48, 11, 38, 11, '#ffd166', 2.2) + poly('M42 7 L37 11 L42 15', '#ffd166', 2.2))


@icon('Counterweight')
def _():
    # The hit is answered: all that mass on its pivot swings back through whoever walked up.
    weight = ('<path d="M-11 -9 L11 -9 L14 11 L-14 11 Z" fill="url(#iron)"/>'
              '<path d="M-9 -2 H9 M-10 5 H10" stroke-width="1.4"/>'
              '<rect x="-3.4" y="-15" width="6.8" height="6.5" rx="1.6" fill="url(#steel)"/>')
    return ('<circle cx="44" cy="12" r="3.8" fill="url(#steel)"/>'
            + line(44, 12, 31, 26, '#9aa3b5', 3.0)
            + '<path d="M53 29 Q52 47 37 51" fill="none" stroke="#ffd166" stroke-width="2.2" stroke-dasharray="4 4" opacity=".9"/>'
            + poly('M43 45 L36 51 L44 55', '#ffd166', 2.2)
            + g(weight, 26, 37, 0, 1.15)
            + stun_stars(19, 13, 18))


@icon('Tooth Breaker')
def _():
    # Armour peeled back off a cracked plate, and the tooth it cost him to do it.
    plate = ('<path d="M12 18 L30 11 L48 18 L46 40 Q40 50 30 54 Q20 50 14 40 Z" fill="url(#iron)"/>'
             '<path d="M16 22 L30 16 L44 22 L42.5 39 Q38 46 30 49 Q22 46 17.5 39 Z" fill="url(#steel)" stroke-width="1.2"/>')
    peel = '<path d="M44 21 L57 15 L53 29 L42.5 31 Z" fill="url(#steel)" stroke-width="1.2"/>'
    return (plate + peel
            + poly('M30 14 L25 24 L33 30 L26 38 L31 50', '#c81e2a', 2.2)
            + g('<path d="M-6 7 L0 -7 L6 7 Z" fill="url(#steel)"/>', 15, 48, 22, .9)
            + g('<path d="M-3.5 3 L1 -4 L4 3 Z" fill="#c9ccd8" stroke-width="1"/>', 9, 36, -35)
            + twinkle(52, 44, .7, '#ffd166'))


@icon('Buzz Lash')
def _():
    # Five thin cuts in one pass, blades still spinning at either end of the flurry.
    cuts = ''.join(poly(f'M{x} 11 Q{x - 4} 32 {x - 9} 53', '#f4f7fc', 1.6) for x in (17, 26, 35, 44, 53))
    return (glow('<circle cx="46" cy="15" r="10" fill="#ff9a2e"/>'
                 '<circle cx="18" cy="47" r="9" fill="#ff9a2e"/>', .55)
            + cuts
            + g(sawblade(8, 10), 46, 15, 20, .8) + g(sawblade(8, 10), 18, 47, -15, .8)
            + twinkle(54, 42, .7, '#ffd166'))


@icon('Ragged Edge')
def _():
    # Not a clean saw edge — a torn one, and the wound under it runs deeper for it.
    return (glow('<path d="M12 30 H52 V41 H12 Z" fill="#9a0f1c"/>', .5)
            + '<path d="M10 14 H54 V30 L49 43 L45 29 L39 41 L35 28 L29 42 L24 27 L19 39 L14 28 L10 36 Z" fill="url(#steel)"/>'
            + '<path d="M13 20 H51" stroke-width="1.2" fill="none"/>'
            + poly('M10 36 L14 28 L19 39 L24 27 L29 42 L35 28 L39 41 L45 29 L49 43 L54 30', '#c9ccd8', 1.6)
            + g(drop(), 48, 51, 0, .9) + g(drop(), 34, 52, 0, .7) + g(drop(), 20, 47, 0, .55)
            + twinkle(16, 18, .6, '#ffd166'))


@icon('Condenser Burst')
def _():
    # Soaking the field: the condensers blowing off, all water and mist. The lightning comes later.
    tank = ('<rect x="23" y="38" width="18" height="18" rx="4" fill="url(#iron)"/>'
            '<rect x="19" y="33" width="26" height="5.5" rx="2" fill="#f0a73a"/>'
            '<path d="M27 44 H37 M27 50 H37" stroke-width="1.4"/>'
            '<rect x="13" y="41" width="7" height="5.5" rx="1.6" fill="url(#steel)"/>'
            '<rect x="44" y="41" width="7" height="5.5" rx="1.6" fill="url(#steel)"/>')
    return (arc_lines(32, 33, 12, 3, 190, '#b4f4ff', -90, 2.2, 6)
            + g(drop('url(#water)'), 32, 13, 0, 1.2)
            + g(drop('url(#water)'), 17, 22, 0, .9) + g(drop('url(#water)'), 47, 22, 0, .9)
            + g(drop('url(#water)'), 12, 33, 0, .7) + g(drop('url(#water)'), 52, 33, 0, .7)
            + tank)


@icon('Brownout')
def _():
    # The lights going out: a coil dimming from the top down, the mana running off the bottom of it.
    coil = ''.join(f'<ellipse cx="32" cy="{y}" rx="13" ry="4.4" fill="none" stroke="#5d6780" stroke-width="3" opacity="{o}"/>'
                   for y, o in ((17, .95), (25, .7), (33, .5), (41, .3)))
    return ('<rect x="28" y="9" width="8" height="8" rx="2" fill="url(#iron)"/>'
            + coil
            + line(13, 26, 13, 40, '#4d7ec0', 2.2) + poly('M8 35 L13 42 L18 35', '#4d7ec0', 2.2)
            + line(51, 26, 51, 40, '#4d7ec0', 2.2) + poly('M46 35 L51 42 L56 35', '#4d7ec0', 2.2)
            + g(drop('url(#mana)'), 24, 50, 0, .85) + g(drop('url(#mana)'), 34, 54, 0, .65)
            + twinkle(44, 14, .6, '#9aa3b5'))


@icon('Storm Caller')
def _():
    # Lightning and water in the same picture: her bolt going into ground that is already soaked.
    return (glow(g(zap('#a6ecff'), 32, 23, 0, .95), .55) + g(zap(), 32, 23, 0, .9)
            + burst(32, 43, 3, 8, 8, '#eaffff')
            + poly('M8 46 Q20 40 32 46 T56 46', '#b4f4ff', 2.6)
            + poly('M10 54 Q22 48 34 54 T58 54', '#2a86b8', 2.4)
            + g(drop('url(#water)'), 15, 36, 0, .7) + g(drop('url(#water)'), 49, 36, 0, .7))


@icon('Incendiary Shell')
def _():
    # Fire over an area: the shell coming apart nose-first and the ground still burning after.
    shell = ('<path d="M0 -14 C4 -9 5 -5 5 -1 V10 H-5 V-1 C-5 -5 -4 -9 0 -14 Z" fill="url(#steel)"/>'
             '<rect x="-5" y="4" width="10" height="7" fill="url(#gold)"/>'
             '<rect x="-5" y="-2" width="10" height="3" fill="#e0455a"/>')
    return ('<rect x="6" y="51" width="52" height="6" rx="2" fill="#5a4a3a"/>'
            + glow(burst(32, 40, 8, 20, 11, '#ff7a2f'), .6)
            + burst(32, 40, 6, 15, 11, 'url(#fireR)')
            + g(flame(), 15, 45, 0, .55) + g(flame(), 49, 45, 0, .55)
            + g(shell, 32, 20, 180, .95)
            + twinkle(13, 23, .7, '#ffd166') + twinkle(51, 23, .7, '#ffd166'))


@icon('Creeping Barrage')
def _():
    # The barrage walking across the ground, each blast bigger than the last, shoving the line along.
    craters = ''.join(f'<ellipse cx="{x}" cy="51" rx="{r}" ry="2.6" fill="#15121d" stroke="none" opacity=".55"/>'
                      for x, r in ((12, 4), (25, 5), (40, 6.5)))
    return ('<rect x="6" y="51" width="52" height="6" rx="2" fill="#5a4a3a"/>' + craters
            + burst(12, 44, 2.6, 7, 8, '#ffd166')
            + burst(25, 42, 3.2, 9.5, 9, '#ffd166')
            + burst(40, 38, 4, 12, 10, 'url(#fireR)')
            + '<path d="M9 21 H41" stroke="#f0a73a" stroke-width="2.4" stroke-dasharray="5 4" fill="none"/>'
            + poly('M42 15 L50 21 L42 27', '#ffd166', 2.4))


@icon('Ranging Shot')
def _():
    # The range is found: the sight settled on a mark that is already off its feet.
    mark = ('<rect x="-5" y="-8" width="10" height="17" rx="3" fill="url(#iron)"/>'
            '<circle cx="0" cy="-13" r="5" fill="url(#steel)"/>'
            '<path d="M-5 9 L-8 16 M5 9 L8 16" stroke-width="2.2"/>')
    return (g(mark, 31, 36, 16, .95)
            + '<circle cx="32" cy="32" r="18" fill="none" stroke="#f0a73a" stroke-width="2.4"/>'
            + '<path d="M32 46 V57 M7 32 H18 M46 32 H57" fill="none" stroke="#ffd166" stroke-width="2.4"/>'
            + '<circle cx="32" cy="32" r="2.6" fill="#ffd166"/>'
            + stun_stars(45, 13, 16))


@icon('Plate Patch')
def _():
    # Steel, not medicine: a scrap plate riveted straight over the hole. Deliberately no cross.
    rivets = ''.join(f'<circle cx="{x}" cy="{y}" r="2" fill="url(#gold)" stroke-width="1"/>'
                     for x, y in ((-10, -7), (10, -7), (-10, 7), (10, 7)))
    patch = ('<rect x="-14" y="-11" width="28" height="22" rx="2" fill="url(#steel)"/>'
             '<path d="M-14 0 H14" stroke-width="1.2" fill="none"/>' + rivets)
    return ('<rect x="8" y="14" width="48" height="36" rx="4" fill="url(#iron)"/>'
            + '<path d="M8 24 H56 M8 40 H56" stroke-width="1.2" fill="none"/>'
            + '<path d="M15 21 L27 18 L35 26 L32 40 L19 41 L11 31 Z" fill="#15121d" stroke="none"/>'
            + poly('M15 21 L11 31 L19 41', '#6a7180', 1.4)
            + g(patch, 38, 34, -8)
            + twinkle(16, 46, .7, '#ffd166') + twinkle(52, 19, .6, '#f0a73a'))


@icon('Throw a Wrench')
def _():
    # The works jammed: a wrench tumbling in head-first and the gear stopping on it.
    return (g(gear(13, 9, '#7a8296'), 38, 38, 0, 1.1)
            + arc_lines(38, 38, 20, 2, 80, '#9aa3b5', -40, 2.0, 4)
            + g(wrench(), 24, 24, 140)
            + burst(32, 31, 3, 8, 8, '#ffd166')
            + speed_lines(7, 13, 3, 10, 5, '#f0a73a'))


@icon('Well Oiled')
def _():
    # Everything runs quicker: one drop of oil and a gear that no longer fights its own teeth.
    return (g(gear(12, 9, '#9aa3b5'), 32, 38, 0, 1.3)
            + '<circle cx="32" cy="38" r="5" fill="url(#gold)"/><circle cx="32" cy="38" r="1.8" fill="#2a2a33"/>'
            + glow(g(drop('#f0a73a'), 32, 18, 0, 1.5), .35)
            + g(drop('url(#wood)'), 32, 18, 0, 1.5)
            + speed_lines(45, 26, 3, 9, 5, '#ffd166')
            + twinkle(14, 24, .7, '#ffd166'))


# ---- Bloodtusk Horde
@icon('Twin Axes')
def _():
    return (g(axe(), 22, 34, -24, .88) + g(axe(), 42, 34, 24, .88)
            + g(drop(), 32, 50, 0, 1.0))


@icon("Warchief's Fury")
def _():
    return (glow(burst(32, 32, 10, 26, 12, '#e0645a'), .5)
            + burst(32, 32, 8, 20, 11, '#9a0f1c')
            + g(skull('#d8c8a8'), 32, 33, 0, 1.15)
            + twinkle(13, 15, .9, '#ff7a45') + twinkle(51, 17, .8, '#ff7a45'))


@icon('Bonebreaker')
def _():
    return (g(hammer(), 24, 30, -30, .95)
            + '<path d="M38 40 q5 -4 10 0 q-3 4 0 8 q-5 3 -10 0 q3 -4 0 -8 Z" fill="url(#bone)"/>'
            + poly('M40 38 L50 50', '#e0645a', 2.2)
            + twinkle(47, 34, .8, '#fbf4e2'))


@icon('Hold the Line')
def _():
    return (g(heater('url(#hide)', '#b07d3e'), 32, 33, 0, 1.12)
            + burst(32, 33, 4, 9, 7, '#d48c3c')
            + poly('M9 20 L4 14 M55 20 L60 14', '#9aa3b5', 2.2)
            + twinkle(11, 44, .8, '#d48c3c') + twinkle(53, 44, .8, '#d48c3c'))


@icon('Pinning Throw')
def _():
    return (g(spear(), 30, 32, 28, .92)
            + '<circle cx="42" cy="44" r="9" fill="none" stroke="#e0645a" stroke-width="2.4"/>'
            + '<circle cx="42" cy="44" r="3" fill="#e0645a"/>'
            + speed_lines(8, 14, 3, 11, 5, '#c9b28a', 28))


@icon('Volley of Spears')
def _():
    return (g(spear(), 16, 34, 16, .78) + g(spear(), 32, 30, 0, .86) + g(spear(), 48, 34, -16, .78)
            + g(drop(), 32, 54, 0, .9))


@icon('Cinder Spray')
def _():
    return (g(flame(), 32, 38, 0, 1.0)
            + burst(16, 22, 2.5, 6, 7, '#ff8a3d') + burst(32, 15, 2.5, 6.5, 7, '#ffd166')
            + burst(48, 22, 2.5, 6, 7, '#ff8a3d')
            + twinkle(22, 30, .7, '#ffe680') + twinkle(43, 29, .7, '#ffe680'))


@icon('Sticky Tar')
def _():
    return ('<path d="M14 22 Q32 16 50 22 Q48 34 50 44 Q32 52 14 44 Q16 34 14 22 Z" fill="#2a2029"/>'
            + '<path d="M22 44 q2 7 0 10 M32 47 q2 8 0 11 M42 44 q2 7 0 10" stroke="#2a2029" stroke-width="4" fill="none"/>'
            + g(flame(), 32, 26, 0, .68)
            + twinkle(18, 18, .7, '#ff8a3d'))


@icon("Ancestor's Balm")
def _():
    return (glow(f'<circle cx="32" cy="32" r="17" fill="url(#holy)"/>', .9)
            + g(plus('url(#heal)'), 32, 33, 0, 1.05)
            + arc_lines(32, 33, 20, 2, 300, '#d8c8a8', -90, 1.8)
            + twinkle(14, 18, .8, '#d8c8a8') + twinkle(50, 18, .8, '#d8c8a8'))


@icon('Totem of Stone')
def _():
    return ('<rect x="24" y="16" width="16" height="36" rx="3" fill="url(#clay)"/>'
            + '<path d="M24 28 H40 M24 40 H40" stroke-width="1.6"/>'
            + g(skull('#d8c8a8'), 32, 22, 0, .62)
            + '<rect x="19" y="50" width="26" height="6" rx="2" fill="#6b4f32"/>'
            + arc_lines(32, 34, 20, 2, 110, '#9aa3b5', 0, 2.0) + arc_lines(32, 34, 20, 2, 110, '#9aa3b5', 180, 2.0))


# ---- Bloodtusk Horde, second rank: the skills and passives added after the first pass.
# House rules these follow: the orc accent is #d48c3c, hide/clay/bone/wood for gear, #e0242f and
# url(#blood) for blood, #bff0ff for anything the ancestors touch, #c89eff for a curse.

# Krug Skullsplitter --------------------------------------------------------
@icon('Headtaker')
def _():
    """The committed swing: armour-piercing and paid for in his own blood.

    Deliberately not a clean cut — the helm is drawn as two halves already knocked apart and
    tipped off each other, so the blow reads as finished and ruinous rather than mid-parry.

    THE AXE HEAD MUST NOT SIT ON THE HELM. Both were steel/iron greys in the first pass and
    at 140px they fused into one silver bowl with red inside — no axe left in the tile at all.
    The head is now kept clear of the halves against the dark ground, carries a white edge
    highlight, and the halves are pushed down into the corners and darkened to bronze so the
    two never share a value.
    """
    def half(s):
        return (f'<path d="M{-13*s} 7 C{-13*s} -8 {-8*s} -16 {-1*s} -16 L{-2*s} 7 Z" fill="#8a6a44"/>'
                f'<path d="M{-15*s} 7 H{-1*s} V11 H{-15*s} Z" fill="#4a3422"/>'
                f'<path d="M{-11.5*s} -4 H{-2.5*s} V-0.5 H{-11.5*s} Z" fill="#15121d" stroke-width="1"/>')
    # A bespoke head rather than axe(): it needs a white edge highlight to stay off the helm.
    bigaxe = ('<rect x="-2.2" y="-21" width="4.4" height="42" rx="1.8" fill="url(#wood)"/>'
              '<path d="M-3 -19 L-8.5 -17 L-8.5 -9 L-3 -8 Z" fill="url(#iron)"/>'
              '<path d="M-2 -18 L7 -22 Q22 -14 19 2 Q13 -3 7 -4 L-2 -7 Z" fill="url(#steel)"/>'
              '<path d="M7 -21.5 Q21 -14 18.5 1" fill="none" stroke="#fff6e0" stroke-width="2"/>'
              '<rect x="-3.2" y="-21.5" width="6.4" height="4" rx="1.2" fill="url(#iron)"/>')
    return (glow('<circle cx="32" cy="40" r="11" fill="#e0242f"/>', .45)
            + '<path d="M8 12 Q34 12 54 34 Q33 19 8 12 Z" fill="#ffd9b0" opacity=".8" stroke="none"/>'
            + '<path d="M8 12 Q34 12 54 34" fill="none" stroke="#ff8a6a" stroke-width="1.4"/>'
            + g(half(1), 19, 49, -26, .8) + g(half(-1), 45, 50, 28, .8)
            + g(bigaxe, 32, 20, 135, 1.05)
            + g(drop(), 12, 30, 0, .7) + g(drop(), 54, 18, 0, .55) + g(drop(), 32, 57, 0, .45))


@icon('Red Charge')
def _():
    """Shoulder first, speed lines behind, and the mark shoved back down the bar.

    A bare pauldron is not enough: on its own the plate read as a brown dome, closer to a
    tent than to anything running. The tusked head tucked in over the top of it is what
    turns the shape into an orc with his shoulder down.
    """
    pauldron = ('<path d="M-13 14 Q-16 -5 -4 -12 Q9 -17 13 -3 Q15 8 11 14 Z" fill="url(#hide)"/>'
                '<path d="M-9 11 Q-10 -3 -2 -8 Q6 -11 10 -1" fill="none" stroke="#b07d3e" stroke-width="1.8"/>'
                + burst(4, -13, 2, 6, 6, 'url(#iron)'))
    head = ('<circle cx="0" cy="0" r="7" fill="#7a9a5e"/>'
            '<path d="M-3 4 Q-5 9 -3 11 Q-1 7 -0.5 5 Z M3 4 Q5 9 3 11 Q1 7 .5 5 Z" fill="url(#bone)" stroke-width="1"/>'
            '<circle cx="3" cy="-1.5" r="1.7" fill="#2a1a1a" stroke="none"/>'
            '<path d="M-6 -4 Q0 -7 6 -5" fill="none" stroke="#4a6238" stroke-width="1.6"/>')
    return (g(speed_lines(0, 0, 3, 13, 7, '#ff8a6a', 0, .85), 5, 36)
            + g(pauldron, 22, 40, 14, .98)
            + g(head, 35, 26, 18, 1.0)
            + glow(burst(48, 32, 4, 12, 9, '#e0242f'), .6)
            + burst(48, 32, 4, 10, 9, '#ff8a3d')
            + poly('M47 18 L55 29 L47 40', '#ffd166', 2.4)
            + g(drop(), 50, 50, 0, .6))


@icon('Splitting Blow')
def _():
    """Not a bleed: a plate cracked open, so the four swinging after him all collect.

    Bone-gold fractures on iron on purpose — nothing red anywhere, or it reads as Bleed.
    """
    def crack(a, r0=7.5, r1=20.5):
        ar = math.radians(a)
        dx, dy = math.cos(ar), math.sin(ar)
        px, py = -dy, dx
        pts = []
        for i, off in enumerate((0, 2.6, -2.6, 0)):
            t = r0 + (r1 - r0) * i / 3
            pts.append(f'{32 + t * dx + off * px:.1f} {32 + t * dy + off * py:.1f}')
        return poly('M' + ' L'.join(pts), '#ffd166', 2.0)
    plate = 'M32 10 L50 20 L50 42 L32 53 L14 42 L14 20 Z'
    return (f'<path d="{plate}" fill="url(#iron)"/>'
            + f'<path d="{plate}" fill="none" stroke="#9aa3b5" stroke-width="1.4"/>'
            + ''.join(crack(a) for a in (-90, -38, 18, 66, 126, 182, 236))
            + glow(burst(32, 32, 3.5, 11, 8, '#ffd166'), .75)
            + burst(32, 32, 3.5, 9.5, 8, '#ffd166')
            + '<circle cx="32" cy="32" r="3.2" fill="#2a1a1a"/>')


# Mogra Ironhide -----------------------------------------------------------
@icon('Shield Crush')
def _():
    """The boss of the shield driven forward, and what it hits buckling away from it.

    The bent-away brackets on the right are the Weaken: the shape is crumpling, not stunned.
    """
    return (g(speed_lines(0, 0, 3, 11, 7, '#d8c8a8', 0, .7), 7, 33)
            + g(heater('url(#hide)', '#b07d3e'), 27, 33, 16, 1.06)
            + burst(28, 32, 4, 9.5, 7, '#d48c3c')
            + glow(burst(46, 30, 4, 11, 9, '#ffd166'), .6)
            + burst(46, 30, 3.5, 9, 9, '#ffd166')
            + poly('M49 17 Q42 25 50 33', '#9aa3b5', 2.4)
            + poly('M50 38 Q43 44 51 50', '#9aa3b5', 2.0)
            + poly('M55 42 V52 M51.5 48.5 L55 53 L58.5 48.5', '#8a9a7a', 2.0))


@icon('Gore and Pin')
def _():
    """Rooted, not stunned: it is still awake under there, it simply cannot leave.

    The stake goes through into the ground and the tusks keep it there — no stun stars, which
    is the whole distinction the skill text draws.
    """
    tusk = ('<path d="M0 0 Q1 -14 16 -18 Q4 -11 5.5 0 Z" fill="url(#bone)"/>'
            '<path d="M2 -3 Q3 -11 12 -15" fill="none" stroke="#fbf4e2" stroke-width="1.2"/>')
    held = ('<path d="M24 50 Q23 37 33 34 Q45 32 49 50 Z" fill="#6a4f68"/>'
            '<circle cx="32" cy="29" r="6" fill="#6a4f68"/>'
            '<path d="M27 40 L17 45 M45 41 L53 47" stroke="#6a4f68" stroke-width="4"/>'
            '<path d="M28 27 L25 21 M36 27 L39 21" stroke="#3a2a3a" stroke-width="2.4"/>')
    return ('<rect x="8" y="48" width="48" height="8" rx="2" fill="#5a4636"/>'
            + '<path d="M20 48 L15 56 M34 48 L29 56 M47 48 L42 56" stroke-width="1.4"/>'
            + held
            + '<path d="M38 11 H44 V40 L41 49 L38 40 Z" fill="url(#iron)"/>'
            + '<rect x="35.5" y="9" width="11" height="4" rx="1.6" fill="#8a5a32"/>'
            + '<path d="M41 15 V38" stroke="#dfe6f2" stroke-width="1"/>'
            + g(tusk, 8, 47, -2, 1.0) + g(tusk, 11, 34, 18, .82)
            + burst(27, 33, 3, 7.5, 8, '#e0242f')
            + g(drop(), 52, 38, 0, .55))


@icon('Hidebound')
def _():
    """Hitting her takes the strength out of YOU: the blade comes off the hide drooping.

    Plain brown bands read as stacked planks, so each layer carries a stitch run along its
    trailing edge — that is the one cue that says cured hide rather than wood. The weapon
    needs its hilt and pommel too, or the bent blade reads as a hook instead of a sword.
    """
    layer = 'M0 -23 Q-11 0 0 23 L9 23 Q-2 0 9 -23 Z'
    stitch = ('<path d="M7 -18 Q-3 0 7 18" fill="none" stroke="#d8bf96" stroke-width="1.3"'
              ' stroke-dasharray="2.4 3.2"/>')
    return (f'<path d="{layer}" fill="#3a2b20" transform="{T(14, 32)}"/>'
            + f'<g transform="{T(14, 32)}">{stitch}</g>'
            + f'<path d="{layer}" fill="#5e4836" transform="{T(23, 32)}"/>'
            + f'<g transform="{T(23, 32)}">{stitch}</g>'
            + f'<path d="{layer}" fill="url(#hide)" transform="{T(32, 32)}"/>'
            + f'<g transform="{T(32, 32)}">{stitch}</g>'
            + poly('M57 12 L46 22 Q39 28 41 37 Q43 44 37 48', '#aab4c7', 3.0)
            + g('<rect x="-7" y="-2" width="14" height="4" rx="1.6" fill="url(#gold)"/>'
                '<rect x="-1.8" y="1.5" width="3.6" height="7" fill="#5a3520"/>'
                '<circle cy="10" r="2.6" fill="url(#gold)"/>', 58, 9, 135, 1.0)
            + twinkle(45, 19, .85, '#fff1c0') + twinkle(38, 43, .6, '#fff1c0')
            + poly('M48 44 V53 M44.5 49.5 L48 54 L51.5 49.5', '#8a9a7a', 2.0))


# Vashka Spearthrower ------------------------------------------------------
@icon('Cull the Weak')
def _():
    """The finishing throw: the javelin goes into a mark that is already leaking."""
    return ('<circle cx="42" cy="41" r="11.5" fill="#e0242f" fill-opacity=".14" stroke="none"/>'
            + '<circle cx="42" cy="41" r="11.5" fill="none" stroke="#e0242f" stroke-width="2.4"/>'
            + '<path d="M42 25 V30 M42 52 V57 M26 41 H31 M53 41 H58" stroke="#e0242f" stroke-width="2.2"/>'
            + g(speed_lines(0, 0, 3, 10, 5, '#c9b28a', 0, .7), 9, 11, 45)
            + g(spear(), 26, 25, 135, 1.0)
            + g(drop(), 34, 54, 0, .8) + g(drop(), 50, 52, 0, .6) + g(drop(), 22, 44, 0, .5))


@icon('Hobbling Cast')
def _():
    """A bola out of her hand and the whole line tangled and marked behind it."""
    weights = ('<circle cx="-14" cy="-7" r="4.2" fill="url(#clay)"/>'
               '<circle cx="14" cy="-9" r="4.2" fill="url(#clay)"/>'
               '<circle cx="2" cy="13" r="4.2" fill="url(#clay)"/>')
    bola = (poly('M0 0 L-12 -6 M0 0 L12 -8 M0 0 L1.6 11', '#c9b28a', 2.0) + weights)
    marks = ''.join('<circle cx="%d" cy="46" r="5.4" fill="none" stroke="#e0242f" stroke-width="2.2"/>'
                    '<circle cx="%d" cy="46" r="1.8" fill="#e0242f"/>' % (x, x) for x in (16, 32, 48))
    return (arc_lines(32, 22, 17, 2, 150, '#d8c8a8', -90, 1.6)
            + g(bola, 32, 21, -12, 1.0)
            + poly('M8 50 Q16 40 24 50 Q32 60 40 50 Q48 40 56 50', '#c9b28a', 2.4)
            + marks
            + twinkle(13, 28, .6, '#ffd166') + twinkle(52, 30, .6, '#ffd166'))


@icon('Marked for the Pot')
def _():
    """Singled out for later: her brand painted straight onto the mark, still wet.

    The silhouette needs a rim light. Pure #2a1f1a on the Horde's brown ground is only a
    shade darker than the tile and the figure dissolves at small sizes, so it is lifted to
    #3a2b22 and edged in #6b5240 to hold its shape.
    """
    return ('<path d="M14 54 Q15 37 32 33 Q49 37 50 54 Z" fill="#3a2b22" stroke="#6b5240"/>'
            + '<circle cx="32" cy="23" r="8.4" fill="#3a2b22" stroke="#6b5240"/>'
            + '<path d="M24 16 L21 8 L28 13 Z M40 16 L43 8 L36 13 Z" fill="#3a2b22" stroke="#6b5240"/>'
            + poly('M23 38 L32 48 L41 38', '#e0242f', 3.0)
            + '<circle cx="32" cy="36" r="2.8" fill="#e0242f"/>'
            + g(drop(), 23, 45, 0, .45) + g(drop(), 41, 45, 0, .45)
            + '<path d="M9 18 V32 M13 16 V30 M17 18 V30" stroke="#c9b28a" stroke-width="2"/>'
            + twinkle(51, 20, .65, '#d48c3c'))


# Drekka Firegut -----------------------------------------------------------
@icon('Shrapnel Bomb')
def _():
    """THE POT WITH NO FIRE IN IT — keep it that way.

    No flame(), no url(#fire)/url(#fireR), no warm glow: the entire point of the skill is that
    it is the one thing she throws that a Downpour cannot put out. Steel, clay and blood only.
    """
    def nail(x, y, rot, sc=1.0):
        return g('<path d="M0 -13 L1.5 -9 L1.5 7 L0 11 L-1.5 7 L-1.5 -9 Z" fill="url(#steel)"/>'
                 '<rect x="-3.4" y="-14" width="6.8" height="3" rx="1.2" fill="url(#iron)"/>', x, y, rot, sc)
    def shard(x, y, rot, sc=1.0):
        return g('<path d="M0 -8 L4.5 1 L-1 8 L-3.5 0 Z" fill="url(#iron)"/>', x, y, rot, sc)
    return ('<path d="M20 36 Q18 50 24 55 H40 Q46 50 44 36 Z" fill="url(#clay)"/>'
            + '<path d="M20 42 Q32 47 44 42" fill="none" stroke="#7a3a1e" stroke-width="1.8"/>'
            + '<path d="M22 34 L19 44 Q27 38 30 32 Z M42 34 L45 44 Q37 38 34 32 Z" fill="#8a4a28"/>'
            + burst(32, 30, 5, 13, 10, '#9aa3b5')
            + burst(32, 30, 3, 8, 8, '#dfe6f2')
            + nail(32, 11, 0, 1.0) + nail(14, 20, -48, .9) + nail(50, 20, 48, .9)
            + nail(8, 36, -84, .8) + nail(56, 36, 84, .8)
            + shard(21, 14, -30, .95) + shard(44, 13, 26, .95) + shard(52, 30, 70, .8)
            + g(drop(), 12, 50, 0, .55) + g(drop(), 52, 48, 0, .5))


@icon('Blastcap')
def _():
    """One target takes the blast; the shock carries into a second for a share of it."""
    return (glow(burst(25, 28, 8, 22, 11, 'url(#fireR)'), .65)
            + burst(25, 28, 8, 20, 11, '#d9361a')
            + burst(25, 28, 5, 13, 10, 'url(#fireR)')
            + g(flame(), 25, 28, 0, .62)
            + arc_lines(25, 28, 24, 2, 56, '#ff8a3d', 30, 1.8)
            + glow(burst(50, 45, 4, 12, 9, 'url(#fireR)'), .6)
            + burst(50, 45, 4, 10.5, 9, '#ff8a3d')
            + burst(50, 45, 2, 5.5, 7, '#fff6c2')
            + twinkle(13, 48, .6, '#ffd166'))


@icon('Wide Spread')
def _():
    """Coverage, not heat: she packs them to scatter, so the fan is wide and the shards cold."""
    frags = ''
    for i, a in enumerate((-162, -138, -114, -90, -66, -42, -18)):
        ar = math.radians(a)
        r = 25 if i % 2 else 21
        frags += g('<path d="M0 -6 L3.6 .8 L-.8 6 L-3 0 Z" fill="url(#iron)"/>',
                   32 + r * math.cos(ar), 50 + r * math.sin(ar), a + 90, .95 if i % 2 else .8)
    return (arc_lines(32, 50, 17, 2, 168, '#d48c3c', -90, 1.8, 9)
            + poly('M8 44 L4 36 M56 44 L60 36', '#d48c3c', 1.8)
            + '<path d="M24 50 Q23 42 32 40 Q41 42 40 50 Z" fill="url(#clay)"/>'
            + '<rect x="26" y="37" width="12" height="4" rx="1.6" fill="#8a4a28"/>'
            + frags
            + '<rect x="8" y="50" width="48" height="6" rx="2" fill="#5a4636"/>')


# Old Mother Hesk ----------------------------------------------------------
@icon("Ancestors' Rebuke")
def _():
    """The dead lean over the whole line at once and halve every mend they take."""
    skulls = (g(skull('#d8c8a8'), 16, 22, -14, .6)
              + g(skull('#e8dcc4'), 32, 16, 0, .72)
              + g(skull('#d8c8a8'), 48, 22, 14, .6))
    marks = ''
    for x in (16, 32, 48):
        pts = ' '.join(f'{x + 6 * math.cos(math.radians(a)):.1f},{46 + 6 * math.sin(math.radians(a)):.1f}'
                       for a in range(-90, 270, 60))
        marks += (f'<polygon points="{pts}" fill="#2a1030" stroke="#c89eff" stroke-width="2"/>'
                  f'<path d="M{x - 3.4} {49.4} L{x + 3.4} {42.6}" stroke="#c89eff" stroke-width="1.8"/>')
    return (glow('<ellipse cx="32" cy="24" rx="22" ry="14" fill="#bff0ff"/>', .4)
            + skulls
            + poly('M16 31 Q14 36 16 39 M32 26 Q34 33 32 38 M48 31 Q50 36 48 39', '#c89eff', 1.8)
            + marks
            + twinkle(9, 12, .6, '#bff0ff') + twinkle(55, 13, .55, '#bff0ff'))


@icon('Bind the Breath')
def _():
    """Silenced: the spirit-cord goes round the jaw and nothing but a grunt gets out.

    LEATHER AND GOLD, not spirit-blue, and no disc over the mouth. The first version drew the
    binding in pale cyan with a bright circle at the centre: at 140px it read as a mask with a
    single big eye (closer to a dragonfly than a gagged jaw), at 32px it was unreadable mush,
    and the colour sat outside the Horde's palette altogether — it looked like another
    faction's icon on the shelf. The cord is the subject of this skill, so it is the brightest
    thing in the tile, and it is wrapped and knotted rather than crossed.
    """
    cord, knot, lip = '#d9a85c', '#8a5a28', '#f0cf90'
    # The muzzle: orc green, two tusks in bone, the mouth line shut underneath the binding.
    jaw = ('<path d="M17 20 Q32 14 47 20 Q47 43 32 51 Q17 43 17 20 Z" fill="#8a9d6a"/>'
           '<path d="M23 35 Q32 38 41 35" fill="none" stroke="#2a1a1a" stroke-width="2.2"/>'
           '<path d="M24 35 Q22 26 25 22 Q26 28 28 33 Z" fill="url(#bone)" stroke-width="1.2"/>'
           '<path d="M40 35 Q42 26 39 22 Q38 28 36 33 Z" fill="url(#bone)" stroke-width="1.2"/>')
    # Two turns of cord drawn right across the mouth, running off both edges of the tile.
    cords = poly('M9 30 Q32 25 55 30', cord, 3.6) + poly('M9 41 Q32 46 55 41', cord, 3.6)
    # ...and the wrap that holds them: a short band bound across both turns, with its tie.
    wrap = ('<rect x="26.5" y="28" width="11" height="15" rx="3.2" fill="' + knot + '"/>'
            '<path d="M29 32.5 h6 M29 38.5 h6" stroke="' + lip + '" stroke-width="1.5" fill="none"/>')
    return jaw + cords + wrap + twinkle(12, 17, .55, cord) + twinkle(52, 18, .5, cord)


@icon('Long Memory')
def _():
    """The ancestors do not let go: a closed cord of bound beads, knotted and knotted again.

    RING GLOW, NEVER A FILLED DISC, and no loose cord ends above the top knot. The first pass
    put a blurred filled circle behind the loop and two tails curling off the knot: at 140px
    the disc read as a flat grey coin behind the beads and the tails read as antennae, so the
    whole tile looked like a bug rather than a cord. The centre is left empty for the hex
    sigil — the curse is the thing being held on to, so it belongs inside the loop.
    """
    beads = ''
    for i in range(10):
        a = math.radians(-90 + i * 36)
        x, y = 32 + 16 * math.cos(a), 34 + 16 * math.sin(a)
        fill = '#e0645a' if i % 5 == 0 else 'url(#bone)'
        beads += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.4 if i % 5 == 0 else 2.8}" fill="{fill}"/>'
    # An overhand knot: two mirrored loops pulled through each other, not a ring with a cross.
    knot = (poly('M-8 5 Q-11 -6 -2 -5 Q6 -4 4 6', '#c9b28a', 2.4)
            + poly('M8 5 Q11 -6 2 -5 Q-6 -4 -4 6', '#c9b28a', 2.4))
    hexpts = ' '.join(f'{32 + 7 * math.cos(math.radians(a)):.1f},{34 + 7 * math.sin(math.radians(a)):.1f}'
                      for a in range(-90, 270, 60))
    return (glow('<circle cx="32" cy="34" r="16" fill="none" stroke="#bff0ff" stroke-width="6"/>', .45)
            + '<circle cx="32" cy="34" r="16" fill="none" stroke="#8a5a32" stroke-width="4.4"/>'
            + '<circle cx="32" cy="34" r="16" fill="none" stroke="#c9b28a" stroke-width="2.4"/>'
            + f'<polygon points="{hexpts}" fill="#2a1030" stroke="#c89eff" stroke-width="2"/>'
            + '<path d="M28.2 37.8 L35.8 30.2" stroke="#c89eff" stroke-width="1.8"/>'
            + beads
            + g(knot, 32, 14, 0, .95)
            + twinkle(13, 47, .6, '#bff0ff') + twinkle(51, 48, .55, '#bff0ff'))


# ---- Kingdom of Aldmere
@icon('Mageslayer')
def _():
    return (g(sword(), 26, 32, -16, .98)
            + '<circle cx="45" cy="42" r="8" fill="url(#mana)" opacity=".85"/>'
            + poly('M39 36 L51 48 M51 36 L39 48', '#e0645a', 2.4)
            + twinkle(49, 20, .8, '#bfe6ff'))


@icon('Runed Thrust')
def _():
    return (g(sword(), 32, 32, 0, 1.0)
            + arc_lines(32, 32, 19, 2, 300, '#bfe6ff', -90, 1.8)
            + twinkle(14, 24, .8, '#bfe6ff') + twinkle(50, 24, .8, '#bfe6ff') + twinkle(32, 55, .7, '#bfe6ff'))


@icon('Hammer of Judgement')
def _():
    return (glow(f'<circle cx="32" cy="24" r="16" fill="url(#holy)"/>', 1)
            + g(hammer('url(#gold)'), 32, 32, 0, 1.02)
            + burst(32, 14, 3, 9, 8, '#fff1b8')
            + twinkle(13, 40, .8) + twinkle(51, 40, .8))


@icon('Lionheart')
def _():
    return (g(heater('url(#steel)', 'url(#gold)'), 32, 32, 0, 1.15)
            + g(heart('url(#blood)'), 32, 31, 0, 1.05)
            + burst(32, 31, 5, 13, 9, '#d9b44a', extra=' opacity=".35"'))


@icon('Pistol Whip')
def _():
    return ('<path d="M14 26 H44 V33 H34 L30 44 H20 L23 33 H14 Z" fill="url(#iron)"/>'
            + '<rect x="40" y="27" width="10" height="4" rx="1.4" fill="#5d6780"/>'
            + stun_stars(40, 48, 22))


@icon('Volley Fire')
def _():
    return (burst(16, 24, 3, 8, 8, '#ffd166') + burst(32, 18, 3.4, 9, 9, 'url(#fireR)')
            + burst(48, 24, 3, 8, 8, '#ffd166')
            + speed_lines(12, 40, 3, 12, 6, '#e9e4d8')
            + speed_lines(34, 46, 3, 12, 6, '#e9e4d8'))


@icon('Flame Lance')
def _():
    return (g(spear('url(#fire)'), 32, 32, 0, 1.0)
            + glow(g(flame(), 32, 16, 0, .6), .8)
            + speed_lines(10, 44, 3, 12, 5, '#ff8a3d', -20))


@icon('Mantle of Flame')
def _():
    return (arc_lines(32, 34, 19, 2, 320, '#ff8a3d', -90, 2.4)
            + g(flame(), 32, 34, 0, 1.12)
            + twinkle(12, 22, .8, '#ffe680') + twinkle(52, 22, .8, '#ffe680'))


@icon('Benediction')
def _():
    return (glow(f'<circle cx="32" cy="32" r="19" fill="url(#holy)"/>', 1)
            + g(heater('#e9e4d8', 'url(#gold)'), 32, 33, 0, 1.0)
            + g(plus('url(#gold)'), 32, 31, 0, .7)
            + twinkle(13, 16, .9) + twinkle(51, 16, .9))


@icon('Censure')
def _():
    return (burst(32, 20, 4, 12, 10, '#fff1b8')
            + poly('M32 26 L32 50', '#d9b44a', 3.0)
            + poly('M24 44 L32 52 L40 44', '#d9b44a', 2.6)
            + twinkle(16, 36, .8) + twinkle(48, 36, .8))


# ---- Stoneleaf Accord
@icon('Forge Strike')
def _():
    # Two crossed hammers for the two blows. Anvil Strike already owns hammer-on-anvil.
    return (g(hammer(), 22, 34, -28, .88) + g(hammer(), 42, 34, 28, .88)
            + burst(32, 30, 4, 10, 9, '#ffd166')
            + twinkle(13, 50, .8, '#ffd166') + twinkle(51, 50, .8, '#ffd166'))


@icon('Quake Hammer')
def _():
    return (g(hammer(), 32, 24, 0, .92)
            + poly('M8 46 L18 42 L26 50 L36 42 L44 50 L56 44', '#a8d06b', 2.6)
            + twinkle(13, 54, .7, '#a8d06b') + twinkle(51, 54, .7, '#a8d06b'))


@icon('Boulder Toss')
def _():
    return (g(rock(), 36, 34, 0, 1.5)
            + speed_lines(6, 16, 3, 12, 6, '#c9b28a', 24)
            + arc_lines(36, 34, 24, 2, 90, '#a8d06b', 160, 2.0))


@icon('Bulwark of the Accord')
def _():
    return (g(heater('url(#steel)', '#a8d06b'), 32, 34, 0, 1.0)
            + g(heater('url(#iron)', '#a8d06b'), 14, 40, -18, .52)
            + g(heater('url(#iron)', '#a8d06b'), 50, 40, 18, .52)
            + twinkle(32, 12, .8, '#a8d06b'))


@icon('Piercing Shot')
def _():
    return (g(heater('url(#iron)', '#5d6780'), 40, 36, 0, .92)
            + g(arrow(length=52), 30, 32, 28, 1.0)
            + speed_lines(6, 12, 3, 12, 5, '#d9c58a', 28)
            + burst(44, 40, 3, 7, 7, '#a8d06b'))


@icon('Steady Aim')
def _():
    return ('<circle cx="32" cy="32" r="17" fill="none" stroke="#a8d06b" stroke-width="2.2"/>'
            + '<path d="M32 10 V18 M32 46 V54 M10 32 H18 M46 32 H54" stroke="#a8d06b" stroke-width="2.2"/>'
            + g(arrow(length=30), 32, 32, 0, .95)
            + twinkle(47, 17, .8, '#d9c58a'))


@icon('Crippling Bolt')
def _():
    return (g(bolt(vane='#9ac46b'), 30, 30, 20, 1.0)
            + g(drop('url(#poison)'), 44, 44, 0, 1.4)
            + arc_lines(44, 44, 11, 2, 160, '#9ac46b', 90, 1.8))


@icon('Toxic Barrage')
def _():
    return (g(bolt(vane='#9ac46b'), 16, 34, 14, .8) + g(bolt(vane='#9ac46b'), 32, 30, 0, .88)
            + g(bolt(vane='#9ac46b'), 48, 34, -14, .8)
            + g(drop('url(#poison)'), 32, 54, 0, 1.1))


@icon('Barkskin')
def _():
    return (g(heater('url(#wood)', '#a8d06b'), 32, 33, 0, 1.12)
            + '<path d="M26 22 V46 M32 20 V48 M38 22 V46" stroke="#4a2f16" stroke-width="1.8" fill="none"/>'
            + '<path d="M44 18 q7 -2 9 4 q-7 3 -9 -4 Z" fill="url(#leaf)"/>')


@icon('Thornlash')
def _():
    return (poly('M10 50 Q22 30 32 34 Q46 40 52 16', '#3a8a38', 3.0)
            + '<path d="M22 36 l-5 -3 l5 -1 Z M32 34 l-3 -5 l4 1 Z M42 30 l5 -3 l-4 -2 Z" fill="#c4f58a"/>'
            + g(drop(), 16, 24, 0, .9))


# ---- The Tideborn
@icon('Feeding Frenzy')
def _():
    return (g(jaws(), 32, 34, 0, 1.25)
            + g(drop(), 14, 16, 0, 1.0) + g(drop(), 50, 18, 0, .85) + g(drop(), 32, 10, 0, .7)
            + speed_lines(6, 50, 3, 10, 5, '#7fe3d8'))


@icon('Undertow')
def _():
    return (arc_lines(32, 44, 12, 4, 210, '#7fe3d8', -90, 2.6, 6)
            + poly('M10 24 Q20 16 30 24 Q40 32 50 24', '#b4f4ff', 2.6)
            + poly('M12 36 Q22 28 32 36 Q42 44 52 36', '#2a86b8', 2.4)
            + speed_lines(42, 14, 3, 11, 5, '#b4f4ff', 180))


@icon('Barnacle Bite')
def _():
    return (g(jaws(), 28, 32, 0, 1.05)
            + '<circle cx="48" cy="44" r="7" fill="#9aa3b5"/><circle cx="48" cy="44" r="3.4" fill="#3a3f4c"/>'
            + '<circle cx="42" cy="22" r="5" fill="#9aa3b5"/><circle cx="42" cy="22" r="2.4" fill="#3a3f4c"/>'
            + g(drop(), 16, 50, 0, .85))


@icon('Tail Whip')
def _():
    return (poly('M8 20 Q30 26 24 42 Q20 52 40 52', '#2f6f8f', 3.2)
            + '<path d="M40 52 L56 44 L52 54 L58 60 Z" fill="#5fa38a"/>'
            + speed_lines(10, 34, 3, 12, 6, '#b4f4ff', 20))


@icon('Choking Bite')
def _():
    bubbles = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#bff3ff" fill-opacity=".3" stroke="#bff3ff" stroke-width="1.3"/>'
                      for x, y, r in ((44, 30, 4.2), (50, 20, 3), (42, 13, 2.2)))
    return (g(jaws(), 24, 38, -12, 1.0) + bubbles
            + '<circle cx="48" cy="44" r="8" fill="none" stroke="#15121d" stroke-width="4.4"/>'
            + '<circle cx="48" cy="44" r="8" fill="none" stroke="#e0455a" stroke-width="2.4"/>'
            + '<line x1="42.3" y1="38.3" x2="53.7" y2="49.7" stroke="#15121d" stroke-width="4.4"/>'
            + '<line x1="42.3" y1="38.3" x2="53.7" y2="49.7" stroke="#e0455a" stroke-width="2.4"/>')


@icon('Drowning Chorus')
def _():
    return (g(note('#b4f4ff'), 22, 30, 0, 1.0) + g(note('#7fe3d8'), 42, 38, 0, .8)
            + arc_lines(32, 34, 22, 2, 260, '#2a86b8', -90, 2.0)
            + g(drop('url(#water)'), 32, 54, 0, 1.0))


@icon('Song of the Depths')
def _():
    return (g(heater('#2a7f8f', '#7fe3d8'), 32, 34, 0, 1.08)
            + g(note('#e9e4d8'), 32, 32, 0, .85)
            + arc_lines(32, 34, 23, 2, 300, '#7fe3d8', -90, 1.8))


@icon('Ink Whip')
def _():
    return (poly('M8 46 Q22 36 28 24 Q34 12 50 14', '#5a4a8a', 3.4)
            + '<circle cx="14" cy="44" r="3.2" fill="#4b3d6e"/><circle cx="22" cy="34" r="2.4" fill="#4b3d6e"/>'
            + glow(f'<circle cx="18" cy="46" r="11" fill="#2a1d40"/>', .7)
            + twinkle(48, 20, .8, '#e3d27a'))


@icon('Crushing Grip')
def _():
    return (poly('M12 16 Q30 22 32 34 Q34 46 20 50', '#5a4a8a', 3.4)
            + poly('M52 16 Q34 22 32 34 Q30 46 44 50', '#4b3d6e', 3.4)
            + '<circle cx="32" cy="34" r="7" fill="#9b6aa8"/>'
            + burst(32, 34, 3, 8, 8, '#2a1d40', extra=' opacity=".6"'))


@icon('Reef Bloom')
def _():
    return (glow(f'<circle cx="32" cy="34" r="16" fill="url(#pearl)"/>', .9)
            + g(plus('url(#heal)'), 32, 34, 0, .95)
            + '<path d="M12 50 q4 -12 10 -14 M52 50 q-4 -12 -10 -14" stroke="#f2c6d8" stroke-width="2.4" fill="none"/>'
            + twinkle(48, 18, .8, '#fff7e6'))


@icon('Riptide Crash')
def _():
    return (poly('M6 38 Q18 22 30 34 Q42 46 58 28', '#2a86b8', 3.0)
            + poly('M8 50 Q22 38 34 48 Q46 56 58 44', '#b4f4ff', 2.6)
            + burst(44, 20, 3.4, 9, 9, '#e9e4d8')
            + g(drop('url(#water)'), 16, 18, 0, 1.0))

@icon('Rimefall')
def _():
    # Splinters of frozen spray coming down, and the ground breaking white where they land.
    def shard(x, y, sc, rot):
        return g('<path d="M0 -12 L5 2 L0 12 L-5 2 Z" fill="#aee4f5" stroke="#15121d" stroke-width="1.7"/>'
                 '<path d="M0 -12 L5 2 L0 2 Z" fill="#eafaff"/>', x, y, rot, sc)
    return (speed_lines(30, 6, 3, 9, 11, '#cdf3ff', 8, .55)
            + shard(17, 24, .82, 12)
            + shard(33, 17, 1.0, -7)
            + shard(49, 27, .76, 19)
            + poly('M9 52 Q32 43 55 52', '#b4f4ff', 2.6)
            + burst(32, 50, 2.6, 7.5, 8, '#ffffff')
            + twinkle(22, 10, .72, '#eafaff')
            + twinkle(53, 12, .62, '#eafaff'))



# ---- The Crimson Court
@icon('Quickstep Drums')
def _():
    # The war drum, and the beat running out ahead of it.
    return ('<path d="M20 28 h20 v14 q-10 3 -20 0 z" fill="#8a5a32" stroke="#15121d" stroke-width="2"/>'
            + '<ellipse cx="30" cy="28" rx="10" ry="3.4" fill="#e8d8b8" stroke="#15121d" stroke-width="2"/>'
            + '<path d="M24 30.5 l5 8 M36 30.5 l-5 8" stroke="#15121d" stroke-width="1.4"/>'
            + g('<rect x="-1" y="-9" width="2.2" height="10" rx="1" fill="#d8c8a8" stroke="#15121d"/>', 22, 22, -28, 1)
            + g('<rect x="-1" y="-9" width="2.2" height="10" rx="1" fill="#d8c8a8" stroke="#15121d"/>', 38, 22, 28, 1)
            + speed_lines(46, 34, 3, 9, 5, '#ffd166', 0, .85)
            + twinkle(50, 16, .7, '#ffd166'))


@icon('First Light')
def _():
    # Dawn on the line, and the one it comes early for already moving.
    return ('<path d="M8 42 h48" stroke="#15121d" stroke-width="2.6"/>'
            + '<path d="M18 42 a14 14 0 0 1 28 0 z" fill="#f6d365" stroke="#15121d" stroke-width="2"/>'
            + poly('M32 20 v-6 M20 24 l-4 -4 M44 24 l4 -4', '#f6d365', 2.2)
            + poly('M14 50 h22', '#ffd166', 2.6)
            + '<path d="M36 46.5 l9 3.5 l-9 3.5 z" fill="#ffd166" stroke="#15121d" stroke-width="1.4"/>')


@icon('Wind at the Back')
def _():
    # Three gusts and a leaf carried on them.
    return (poly('M8 24 Q26 18 44 24', '#bfeee6', 3)
            + poly('M6 34 Q28 28 50 34', '#9fdcd0', 3)
            + poly('M10 44 Q30 39 48 44', '#bfeee6', 2.4)
            + g('<path d="M0 6 C3 1 9 1 12 6 C9 11 3 11 0 6 Z" fill="#7ac74f" stroke="#15121d" stroke-width="1.6"/>'
                + '<path d="M1 6 H11" stroke="#3f7a2a" stroke-width=".8"/>', 42, 16, -18, 1)
            + twinkle(54, 40, .6, '#d6fff4'))


@icon('Stolen Hours')
def _():
    # An upright hourglass with the sand held in the top bulb — the grave has pocketed its hours,
    # so nothing runs down. A drag-back arrow sweeps left beneath it.
    frame = ('<path d="M-9 -13 h18 M-9 13 h18" stroke="#d8c8a8" stroke-width="2.6" stroke-linecap="round"/>'
             + '<path d="M-7 -12 Q-7 -2 0 0 Q7 -2 7 -12 Z" fill="#1a1a24" stroke="#d8c8a8" stroke-width="2"/>'
             + '<path d="M-7 12 Q-7 2 0 0 Q7 2 7 12 Z" fill="#1a1a24" stroke="#d8c8a8" stroke-width="2"/>'
             # the sand, all of it still in the TOP bulb (stuck, not falling)
             + '<path d="M-5 -11 Q-5 -3 0 -1 Q5 -3 5 -11 Z" fill="#8ee696"/>')
    return (g(frame, 36, 26, 0, 1.15)
            + poly('M46 50 L14 50', '#8ee696', 3)
            + '<path d="M18 46 l-6 4 l6 4 z" fill="#8ee696" stroke="#15121d" stroke-width="1.4"/>'
            + twinkle(52, 12, .7, '#bdf2c4'))


@icon('Quickened Blood')
def _():
    # Her drop, already running.
    return (g(drop('#e0455a'), 30, 26, 0, 1.6)
            + speed_lines(10, 26, 3, 10, 6, '#e0455a', 0, .8)
            + poly('M26 46 Q36 50 46 44', '#ff8a96', 2.4)
            + twinkle(49, 40, .6, '#ffd0d6'))


@icon('Quick Hands')
def _():
    # One thrown flask up top, trailing a little speed; below it the speed bar, with the marker
    # already landed three-quarters along — the hand never really stopped.
    flask = ('<path d="M-3.5 -9 h7 v4.5 l4.5 9 a8 8 0 0 1 -16 0 l4.5 -9 z" fill="#5b97e6" stroke="#15121d" stroke-width="2"/>'
             + '<path d="M-4.5 -10 h9" stroke="#d8c8a8" stroke-width="2.4"/>'
             + '<path d="M-4 3 h8" stroke="#bcdcff" stroke-width="2" opacity=".7"/>')
    return (g(flask, 30, 22, 16, 1.15)
            + speed_lines(8, 22, 3, 9, 6, '#cdf3ff', 0, .75)
            # the speed bar, with its track, and the glowing marker 3/4 along
            + poly('M10 48 h44', '#5a6070', 3)
            + '<circle cx="43" cy="48" r="5.5" fill="url(#bolt)" stroke="#15121d" stroke-width="1.8"/>'
            + poly('M30 48 L41 48', '#ffd166', 3)
            + '<path d="M38 44.5 l6 3.5 l-6 3.5 z" fill="#ffd166" stroke="#15121d" stroke-width="1.4"/>')


@icon('Throat Tear')
def _():
    return (g(rapier(), 30, 32, -18, 1.0)
            + poly('M40 20 Q46 30 44 44', '#c0303f', 2.6)
            + g(drop(), 47, 48, 0, 1.3) + g(drop(), 40, 54, 0, .9))


@icon('Mist Form')
def _():
    return (glow(f'<ellipse cx="32" cy="36" rx="22" ry="15" fill="#6b5a7a"/>', .85)
            + '<path d="M12 30 Q24 24 32 30 Q40 36 52 30" stroke="#b8a8c4" stroke-width="2.6" fill="none" opacity=".9"/>'
            + '<path d="M10 42 Q22 36 32 42 Q42 48 54 42" stroke="#9c8aa8" stroke-width="2.4" fill="none" opacity=".75"/>'
            + '<circle cx="26" cy="20" r="2.2" fill="#c0303f"/><circle cx="38" cy="20" r="2.2" fill="#c0303f"/>')


@icon('Pit Chains')
def _():
    links = ''
    for i, (x, y) in enumerate([(14, 16), (24, 26), (34, 36), (44, 46)]):
        links += f'<ellipse cx="{x}" cy="{y}" rx="7" ry="4.6" fill="none" stroke="url(#iron)" stroke-width="3.2" transform="rotate({45 if i % 2 else -45} {x} {y})"/>'
    return (links + '<path d="M48 50 L56 58" stroke="url(#iron)" stroke-width="3"/>'
            + burst(52, 18, 3, 8, 8, '#e0455a'))


@icon('Sulphur Breath')
def _():
    return (g(skull('#c8b06a', '#3a1a1a'), 20, 24, 0, .95)
            + '<path d="M28 30 Q44 26 56 34 Q44 40 56 48 Q40 50 30 42 Z" fill="url(#fire)" opacity=".9"/>'
            + twinkle(50, 22, .8, '#ffe680') + twinkle(44, 54, .7, '#ff8a3d'))


@icon('Wing Carve')
def _():
    return (g(wing('#3d1f4a'), 18, 26, -8, 1.0)
            + g(dagger(), 42, 36, 24, 1.15)
            + poly('M22 44 L40 28 M28 50 L46 34', '#e05a9a', 2.2)
            + g(drop(), 16, 50, 0, .9))


@icon("Predator's Grace")
def _():
    return (g(wing('#3d1f4a'), 20, 30, -14, 1.05) + g(wing('#2a1430'), 44, 30, 194, 1.05)
            + g(dagger(), 32, 36, 0, .9)
            + speed_lines(8, 50, 3, 11, 5, '#e05a9a') + speed_lines(42, 50, 3, 11, 5, '#e05a9a'))


@icon('Hamstring')
def _():
    return (g(claw('#e9e4d8'), 30, 30, 0, 1.0)
            + poly('M14 48 Q32 54 50 46', '#c0303f', 2.6)
            + g(drop(), 44, 52, 0, 1.1) + g(drop(), 20, 54, 0, .8))


@icon('Feral Lunge')
def _():
    return (g(jaws('#8a3030'), 36, 30, 0, 1.2)
            + speed_lines(6, 22, 4, 14, 6, '#ff7a2f')
            + speed_lines(6, 44, 3, 11, 6, '#ff7a2f')
            + g(drop(), 52, 50, 0, 1.0))


@icon('Crimson Mend')
def _():
    return (glow(f'<circle cx="32" cy="32" r="16" fill="#c0303f"/>', .55)
            + g(heart('url(#blood)'), 32, 32, 0, 1.3)
            + g(plus('#ffd9d9'), 32, 32, 0, .5)
            + twinkle(14, 18, .8, '#e0455a') + twinkle(50, 18, .8, '#e0455a'))


@icon('Blood Pact')
def _():
    """One blow, split four ways: a heart at the centre feeding four drops on a ring."""
    spokes = ''.join(line(32, 32,
                          32 + 19 * math.cos(math.radians(a)),
                          32 + 19 * math.sin(math.radians(a)), '#c0303f', 2.2, False)
                     for a in (45, 135, 225, 315))
    drops = ''.join(g(drop(), 32 + 21 * math.cos(math.radians(a)), 32 + 21 * math.sin(math.radians(a)), 0, .72)
                    for a in (45, 135, 225, 315))
    return (glow(f'<circle cx="32" cy="32" r="20" fill="#5c1a2d"/>', .5)
            + '<circle cx="32" cy="32" r="20" fill="none" stroke="#c0303f" stroke-width="1.8" opacity=".85"/>'
            + spokes + drops
            + g(heart('url(#blood)'), 32, 32, 0, 1.15))


@icon('Blood Ward')
def _():
    """Her veins spread over a shield: half of every blow stops here."""
    return (glow(g(heater('#5c1a2d', 'url(#blood)'), 32, 32, 0, 1.0), .5)
            + g(heater('#5c1a2d', 'url(#blood)'), 32, 32, 0, 1.0)
            + '<path d="M32 18 V44 M32 26 L24 32 M32 26 L40 32 M32 35 L25 40 M32 35 L39 40" '
              'stroke="#e0455a" stroke-width="2" fill="none" stroke-linecap="round"/>'
            + g(drop(), 32, 24, 0, .8)
            + twinkle(16, 22, .7, '#e0455a') + twinkle(48, 22, .7, '#e0455a'))


@icon('Wither')
def _():
    return (g(skull('#b8a684', '#2a1a1a'), 32, 28, 0, 1.15)
            + '<path d="M18 44 q6 6 14 4 q8 -2 14 -6" stroke="#6b5a4a" stroke-width="2.4" fill="none"/>'
            + arc_lines(32, 30, 22, 2, 240, '#9474c4', -90, 1.8)
            + twinkle(14, 46, .7, '#9474c4') + twinkle(50, 46, .7, '#9474c4'))


def slug(name):
    """Must match skillSlug() in index.html."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower().replace("'", '')).strip('-')




# ---- The Pale Host
def headstone(fill='url(#iron)', s=1):
    """A round-topped grave marker, origin at its foot."""
    return g(f'<path d="M-9 0 V-16 Q-9 -26 0 -26 Q9 -26 9 -16 V0 Z" fill="{fill}"/>'
             '<path d="M-5 -14 H5 M-5 -9 H5" stroke-width="1.2"/>', 0, 0, 0, s)


def gravecross(fill='url(#iron)'):
    """Mordrek's iron grave marker, origin at its center, point at the foot."""
    return (f'<path d="M-3 -22 H3 V-12 H13 V-6 H3 V14 L0 22 L-3 14 V-6 H-13 V-12 H-3 Z" fill="{fill}"/>'
            '<circle cx="0" cy="-9" r="2.2" fill="#2a2e3a"/>')


def bone_shard(length=18, fill='url(#bone)'):
    """A splintered bone, lobes at the back, point at the front. Points along +x."""
    h = length / 2
    return (f'<path d="M{-h} -3.4 Q{-h - 4} -5.6 {-h - 2.6} -1.4 Q{-h - 5.4} -.4 {-h - 2.6} 1.8 Q{-h - 4} 5.6 {-h} 3.4 L{h} 1 L{h + 4} 0 L{h} -1 Z" fill="{fill}"/>')


def coffin_shape(fill='url(#wood)', w=1):
    """A shouldered coffin, upright, origin at center."""
    return (f'<path d="M-{7 * w} -20 L{7 * w} -20 L{10 * w} -8 L{6 * w} 20 L-{6 * w} 20 L-{10 * w} -8 Z" fill="{fill}"/>'
            f'<path d="M-{9 * w} -8 H{9 * w}" stroke-width="1.2"/>')


def mound():
    """A fresh grave mound with a few stones."""
    return ('<path d="M-16 8 Q0 -2 16 8 L16 10 H-16 Z" fill="url(#hide)"/>'
            '<circle cx="-7" cy="7" r="1.6" fill="#8a7a62" stroke-width="1"/>'
            '<circle cx="5" cy="6.4" r="1.3" fill="#8a7a62" stroke-width="1"/>')


def bonehand(fill='url(#bone)'):
    """A skeletal hand reaching up, wrist at the origin."""
    return (f'<path d="M-5 10 L-4 -2 L-6 -12 L-3.4 -12 L-1.6 -3 L-1 -14 L1.6 -14 L2 -3 L4 -11 L6.4 -10 L4.6 -1 L5 10 Z" fill="{fill}"/>')


@icon('Grave Cross')
def _():
    return (speed_lines(8, 20, 3, 9, 6, '#9fe8b4', -30)
            + g(gravecross(), 34, 33, -38, 1.05)
            + twinkle(51, 13, .8, '#dcffe6'))


@icon('Last Rites')
def _():
    # The marker driven straight down, point-first, through the glow of the pact.
    return ('<ellipse cx="32" cy="52" rx="15" ry="4" fill="url(#graveR)" stroke="none"/>'
            + burst(32, 50, 3.4, 8, 8, '#9fe8b4')
            + g(gravecross('url(#steel)'), 32, 27, 180, 1.1))


@icon('Graveside Chill')
def _():
    return (g(headstone(), 44, 50, 0, .8)
            + poly('M8 30 Q16 24 24 30 T40 30', '#bfeccb', 2.6)
            + poly('M6 40 Q14 34 22 40 T38 40 T52 40', '#9fe8b4', 2.6)
            + poly('M10 50 Q18 44 26 50 T42 50', '#7ec898', 2.6)
            + twinkle(14, 18, .7, '#dcffe6'))


@icon('Plant the Marker')
def _():
    return ('<ellipse cx="32" cy="50" rx="17" ry="5" fill="url(#graveR)" stroke="none"/>'
            + g(mound(), 32, 44)
            + g(gravecross(), 32, 27, 0, 1.0)
            + arc_lines(32, 30, 24, 3, 50, '#9fe8b4', 0, 2))


@icon('Tomb Slab')
def _():
    # The grave slab mid-slam, corner-first.
    return (burst(42, 50, 3, 7.5, 8, '#c9ccd8')
            + g('<rect x="-13" y="-19" width="26" height="38" rx="3" fill="url(#iron)"/>'
                '<path d="M-6 -12 H6 M-8 -6 H8 M-8 0 H8" stroke-width="1.3"/>'
                '<path d="M0 -12 V-4 M-4 -8 H4" stroke="#c9ccd8" stroke-width="2"/>', 30, 29, -34))


@icon('Graveyard Fence')
def _():
    # A stretch of iron graveyard railing raised before an ally: spear-topped bars lit grave-green,
    # two rails and an iron scroll, standing on fresh dirt.
    bars = ''.join(
        f'<rect x="{x - 2}" y="{top}" width="4" height="{50 - top}" fill="#3b414b"/>'
        f'<path d="M{x} {top - 8} l4 7 h-8 Z" fill="#3b414b"/>'
        f'<path d="M{x} {top - 6} l1.8 4 h-3.6 Z" fill="#8ee696" stroke="none"/>'
        for x, top in ((14, 22), (25, 18), (36, 18), (47, 18), (54, 22)))
    return ('<circle cx="32" cy="30" r="20" fill="url(#graveR)" stroke="none" opacity=".7"/>'
            + '<path d="M6 52 Q32 44 58 52 L58 56 H6 Z" fill="url(#clay)"/>'
            + bars
            + '<rect x="9" y="26" width="49" height="4" rx="1" fill="#3b414b"/>'
            + '<rect x="9" y="42" width="49" height="4" rx="1" fill="#3b414b"/>'
            + '<path d="M26 36 q5 -6 10 0 q-5 6 -10 0 Z" fill="none" stroke="#6d7684" stroke-width="2.2"/>')


@icon('Burrow')
def _():
    # Barrow goes under: his grave slab half sunk in a fresh mound, clods thrown up, the way down.
    slab = ('<rect x="-11" y="-17" width="22" height="34" rx="9" fill="url(#iron)"/>'
            '<path d="M0 -10 V-2 M-4 -6 H4" stroke="#8ee696" stroke-width="2"/>')
    clod = '<circle r="2.6" fill="url(#clay)" stroke-width="1"/>'
    return (g(slab, 33, 38, 10)
            + '<path d="M6 54 Q12 38 32 37 Q52 38 58 54 Z" fill="url(#clay)"/>'
            + '<path d="M14 46 Q22 41 30 44 M36 43 Q44 41 50 47" stroke="#4a2410" stroke-width="1.4" fill="none"/>'
            + g(clod, 13, 33) + g(clod, 51, 31, 0, .9) + g(clod, 18, 25, 0, .7) + g(clod, 46, 23, 0, .65)
            + '<path d="M24 9 L32 16 L40 9 M24 16 L32 23 L40 16" fill="none" stroke="#8ee696" stroke-width="2.6"/>')


@icon('Barrow Wall')
def _():
    return ('<circle cx="32" cy="32" r="21" fill="url(#graveR)" stroke="none"/>'
            + g(heater('url(#iron)', '#8ee696'), 32, 32, 0, 1.1)
            + '<path d="M32 22 V42 M24 29 H40" stroke="#8ee696" stroke-width="2.6"/>')


@icon('Grasping Hands')
def _():
    return ('<path d="M8 52 H56" stroke="#4a4036" stroke-width="3"/>'
            + g(bonehand(), 18, 46, -8, .9)
            + g(bonehand(), 32, 44, 0, 1.05)
            + g(bonehand(), 46, 46, 8, .9))


@icon('Crypt Breaker')
def _():
    return (g('<rect x="-14" y="-6" width="28" height="12" rx="2" fill="url(#iron)"/>'
              '<path d="M-3 -6 L1 0 L-2 6 M1 0 L6 -2" stroke="#15121d" stroke-width="1.6" fill="none"/>', 32, 46)
            + burst(32, 40, 3, 7, 8, '#ffd166')
            + g(hammer('url(#steel)'), 33, 22, 42, 1.05))


@icon('Hold the Grave')
def _():
    spikes = ''.join(f'<g transform="rotate({a} 32 32)"><path d="M32 9 L29.6 15 L34.4 15 Z" fill="url(#bone)"/></g>'
                     for a in (0, 45, 90, 135, 180, 225, 270, 315))
    return spikes + g(heater('url(#iron)', '#8ee696'), 32, 32, 0, .82)


@icon('Bone Dart')
def _():
    return (speed_lines(7, 38, 3, 10, 6, '#e9e4d8', -12)
            + g(bone_shard(22), 33, 31, -12, 1.15)
            + twinkle(52, 16, .8, '#ffffff'))


@icon('Charnel Volley')
def _():
    return (g(bone_shard(16), 26, 20, -24)
            + g(bone_shard(18), 32, 34, -12, 1.1)
            + g(bone_shard(15), 26, 47, 2)
            + speed_lines(6, 34, 3, 8, 7, '#bfeccb', -12))


@icon('Shambling Rise')
def _():
    return (g(headstone('url(#iron)', .85), 45, 50)
            + g(mound(), 26, 48)
            + g(bonehand('url(#grave)'), 26, 40, -4, 1.2)
            + '<circle cx="14" cy="30" r="1.6" fill="#8a7a62" stroke-width="1"/>'
            + '<circle cx="36" cy="26" r="1.4" fill="#8a7a62" stroke-width="1"/>'
            + arc_lines(26, 36, 17, 3, 60, '#9fe8b4', 0, 1.8))


@icon('Rot Shot')
def _():
    return (g(arrow('url(#bone)', '#6a7055'), 31, 31, -32)
            + g(drop('url(#poison)'), 46, 44, 0, .85)
            + speed_lines(8, 46, 2, 8, 6, '#9ac46b', -32))


@icon('Marrow Pierce')
def _():
    # A long bone spike punched clean through a plate.
    return (g('<rect x="-9" y="-13" width="18" height="26" rx="3" fill="url(#iron)"/>', 38, 36, 12)
            + g(bone_shard(34), 30, 32, 18, 1.1)
            + burst(44, 41, 2.4, 5.5, 8, '#e9e4d8'))


@icon('Shroudcast')
def _():
    # Off the staff and up the arc: the shaft in the low corner, a cord still swinging, and the
    # skull at the top of its throw.
    return (line(12, 56, 23, 31, '#6b4422', 3.4)
            + poly('M23 31 Q28 37 26 42', '#8a5a32', 1.8)
            + poly('M25 29 Q38 14 55 23', '#8a9a8c', 2.4)
            + g(skull(), 50, 25, 16, .6)
            + twinkle(35, 17, .6, '#bfeccb'))


@icon('Pall of Bones')
def _():
    # The same pall overhead as before, raining broken bone instead of arrows.
    return ('<path d="M10 16 Q16 8 26 12 Q32 4 42 10 Q52 8 54 17 Q58 24 48 25 L14 25 Q6 23 10 16 Z" fill="url(#shroud)"/>'
            + g(bone_shard(15), 20, 38, 80)
            + g(bone_shard(17), 32, 43, 100)
            + g(bone_shard(14), 45, 38, 75))


@icon('Withering Shot')
def _():
    return (g(skull(), 27, 26, -12, .72)
            + poly('M42 40 L47 46 L52 40', '#d6a0ff', 2.4)
            + poly('M42 48 L47 54 L52 48', '#a860e0', 2.4))


@icon('Graveshot')
def _():
    # Harder on the rotting: the skull comes in trailing grave-green, poison pooling under it.
    return (g(skull(), 42, 31, 14, .78)
            + speed_lines(10, 33, 3, 11, 6, '#bfeccb', -18)
            + g(drop('url(#poison)'), 45, 52, 0, .7)
            + twinkle(23, 18, .6, '#d6ff86'))


@icon('Scatter of Bones')
def _():
    return (g(bone_shard(15), 20, 22, 20)
            + g(bone_shard(13), 42, 20, -35)
            + g(bone_shard(16), 30, 38, 65)
            + g(bone_shard(12), 46, 42, 10)
            + g(drop(), 16, 44, 0, .7)
            + twinkle(33, 12, .7, '#e9e4d8'))


@icon('Grave Mend')
def _():
    return ('<circle cx="32" cy="32" r="18" fill="url(#graveR)" stroke="none"/>'
            + g(plus('url(#grave)'), 32, 32, 0, 1.1)
            + twinkle(16, 18, .8, '#dcffe6') + twinkle(48, 44, .7, '#dcffe6'))


@icon('Second Burial')
def _():
    # The lid off, and the pale light standing up out of the box.
    return ('<ellipse cx="30" cy="20" rx="10" ry="14" fill="url(#graveR)" stroke="none"/>'
            + '<path d="M30 10 V26 M24 17 L30 10 L36 17" stroke="#dcffe6" stroke-width="2.6" fill="none"/>'
            + g(coffin_shape(), 30, 40, 0, .9)
            + g('<path d="M-6 -18 L6 -18 L9 -7 L5 18 L-1 18 Z" fill="url(#wood)"/>', 49, 38, 18, .8))


@icon('Coffin')
def _():
    return ('<circle cx="32" cy="32" r="21" fill="url(#graveR)" stroke="none"/>'
            + g(coffin_shape(), 32, 32, 0, 1.15)
            + '<path d="M32 18 V28 M27 23 H37" stroke="#8ee696" stroke-width="2.2"/>')


@icon('Hex of Ruin')
def _():
    return ('<ellipse cx="32" cy="32" rx="22" ry="14" fill="url(#hex)"/>'
            + '<circle cx="32" cy="32" r="8.5" fill="#f4f0ff"/>'
            + '<circle cx="32" cy="32" r="4.4" fill="#2a1d40"/>'
            + '<path d="M46 14 L52 20 M52 14 L46 20" stroke="#8ee696" stroke-width="2.4"/>'
            + g(plus('url(#heal)'), 16, 48, 0, .5)
            + '<path d="M9 41 L23 55" stroke="#e0455a" stroke-width="2.8"/>')


@icon('Soul Siphon')
def _():
    return (g(skull('url(#bone)', '#1a241c'), 18, 40, 0, .85)
            + poly('M24 32 Q32 20 42 24 Q36 28 38 34 Q44 30 48 22', '#9fe8b4', 2.6)
            + '<circle cx="49" cy="18" r="5" fill="url(#graveR)" stroke="none"/>'
            + '<circle cx="49" cy="18" r="2.6" fill="#dcffe6"/>')


@icon('Clawing Grasp')
def _():
    return g(claw('#b9c0a6'), 32, 32, -12, .95) + speed_lines(10, 18, 2, 8, 6, '#9fe8b4', -12)


@icon('Second Grave')
def _():
    return ('<path d="M8 52 H56" stroke="#4a4036" stroke-width="3"/>'
            + g(headstone('url(#iron)', .95), 23, 52)
            + g(headstone('url(#steel)', .8), 43, 52)
            + twinkle(43, 20, .8, '#dcffe6'))


@icon('Feast of the Fallen')
def _():
    return (g(skull(), 32, 26, 0, 1.0)
            + poly('M20 44 Q26 50 32 44 Q38 50 44 44', '#9fe8b4', 2.4)
            + g(drop('url(#grave)'), 32, 48, 0, .8))


@icon('Toll of the Dead')
def _():
    # The charnel bell, cracked, with a bone for a clapper.
    return (g('<path d="M-11 8 Q-11 -12 0 -14 Q11 -12 11 8 L14 12 H-14 Z" fill="url(#iron)"/>'
              '<path d="M-2 -14 Q0 -17 2 -14" fill="none" stroke-width="2"/>'
              '<path d="M2 -6 L5 2 L3 8" fill="none" stroke-width="1.4"/>', 32, 28)
            + g(bone_shard(8), 32, 44, 90, .8)
            + arc_lines(32, 30, 22, 2, 40, '#9fe8b4', 90, 2)
            + arc_lines(32, 30, 22, 2, 40, '#9fe8b4', -90, 2))


@icon('Deathmark')
def _():
    return ('<circle cx="32" cy="32" r="17" fill="none" stroke="#e0455a" stroke-width="2.6"/>'
            + '<path d="M32 10 V20 M32 44 V54 M10 32 H20 M44 32 H54" stroke="#e0455a" stroke-width="2.6"/>'
            + g(skull(), 32, 33, 0, .85))


@icon('Keeper of the Coffin')
def _():
    return (g(coffin_shape(), 32, 32, 0, 1.05)
            + '<circle cx="32" cy="26" r="6.5" fill="url(#graveR)" stroke="none"/>'
            + g(plus('url(#heal)'), 32, 26, 0, .55))


# ---- The Pale Host, second wave ------------------------------------------
# The older Pale Host tiles above use their colours as literals; these name them, which is how the
# newer faction blocks (TD_*, CR_*) are written. Same values, so the two waves sit together.
UD_PALE = '#8ee696'     # the pact's pale green, from PAL['undead']
UD_PALE_HI = '#dcffe6'
UD_MOSS = '#9fe8b4'
UD_BONE = '#e2dcc4'
UD_DIRT = '#4a2410'     # the churned grave-dirt Burrow already digs
UD_GRAVITY = '#6b74c8'  # the engine's own gravity ring (burst-gravity), for Grave's Reach alone


@icon("Grave's Reach")
def _():
    # The one tile in the game that draws what `gravpull` draws: a ring COLLAPSING inward (the
    # engine runs its ring animation in reverse), with a hand coming up through it and the mark's
    # foot held fast. Two rings, the outer one faint, to read as inward motion at 32px.
    return ('<circle cx="32" cy="34" r="20" fill="none" stroke="' + UD_GRAVITY + '" stroke-width="2" opacity=".45"/>'
            + '<circle cx="32" cy="34" r="13.5" fill="none" stroke="' + INK + '" stroke-width="4.4"/>'
            + '<circle cx="32" cy="34" r="13.5" fill="none" stroke="' + UD_GRAVITY + '" stroke-width="2.8"/>'
            + '<path d="M8 52 Q20 42 32 41 Q44 42 56 52 Z" fill="url(#clay)"/>'
            + '<path d="M16 49 Q24 45 31 47 M36 46 Q45 45 50 50" stroke="' + UD_DIRT + '" stroke-width="1.4" fill="none"/>'
            + g(bonehand('url(#bone)'), 32, 36, 0, 1.15)
            + twinkle(49, 17, .75, UD_PALE_HI))


@icon('Dead March')
def _():
    # He does not charge. The marker goes down UPRIGHT — rotating it put the crossbar where a
    # sword's hilt sits and the whole tile read as a stabbed dagger — and the weight goes into the
    # floor, running out both ways along the line he walked into.
    return (g(gravecross('url(#iron)'), 32, 22, 0, .92)
            + '<path d="M5 44 H59" stroke="' + INK + '" stroke-width="6.4"/>'
            + '<path d="M5 44 H59" stroke="' + UD_MOSS + '" stroke-width="3"/>'
            + burst(32, 44, 3, 8.5, 8, UD_PALE)
            + poly('M10 53 Q18 47 25 52', UD_MOSS, 2.2)
            + poly('M39 52 Q46 47 54 53', UD_MOSS, 2.2))


@icon('Weight of the Mound')
def _():
    # All that mass, landed: the slab down flat, the mark shoved back off its feet (the house's
    # drag-back arrow sweeping left) and seeing stars.
    return (g(headstone('url(#iron)', 1.1), 30, 40, 14)
            + '<path d="M8 48 H56" stroke="' + INK + '" stroke-width="5.6"/>'
            + '<path d="M8 48 H56" stroke="#6b6054" stroke-width="2.6"/>'
            + poly('M50 57 L18 57', UD_PALE, 3)
            + '<path d="M22 53 l-6 4 l6 4 z" fill="' + UD_PALE + '" stroke="' + INK + '" stroke-width="1.4"/>'
            + stun_stars(38, 14, 22))


@icon("The Lord's Due")
def _():
    # The wight steps in front: his grave-plate filling the tile, the one he covers tucked small
    # behind it, and a shot glancing off the face rather than reaching them.
    return (g(husk(0, 0, .8, '#5c6350'), 45, 30)
            + g(heater('url(#iron)', 'url(#steel)'), 28, 32, 0, 1.12)
            + g(plus('url(#graveR)'), 28, 31, 0, .42)
            + poly('M58 10 L44 20', UD_PALE, 2.6)
            + poly('M44 20 L56 27', UD_PALE_HI, 2.2)
            + twinkle(44, 20, .7, UD_PALE_HI))


@icon('Grip of the Grave')
def _():
    # A bone hand closed round a throat, and it took three passes to read as one. Drawn in the same
    # pale as the mark it became the figure's LEGS; drawn as a matched pair reaching in from both
    # sides it became a bowtie. So: one hand, big, coming up across the throat from below-right
    # with the fingers plainly over it, and the mark behind it as a flat dark silhouette.
    return (g(husk(0, 0, 1.1, '#2b352e'), 30, 26)
            + arc_lines(30, 19, 5, 2, 44, UD_MOSS, -90, 1.8)   # kept clear of the rim: at y=10 the outer arc clipped the frame
            + g(bonehand('url(#bone)'), 41, 48, -46, 1.45)
            + twinkle(14, 46, .65, UD_PALE))


@icon('Charnel Tide')
def _():
    # A wave with bones in it, rolling across the whole line, and the back-arrow underneath: the
    # payload is everyone losing their place, not the damage.
    bones = ''.join(g(bone_shard(13, 'url(#bone)'), x, y, r, s)
                    for x, y, r, s in ((20, 26, -24, .95), (34, 20, 8, 1.0), (47, 27, 32, .85)))
    return ('<path d="M4 40 Q14 28 24 36 Q34 44 44 34 Q54 24 60 36 L60 48 H4 Z" fill="url(#grave)"/>'
            + '<path d="M4 40 Q14 28 24 36 Q34 44 44 34 Q54 24 60 36" fill="none" stroke="' + UD_PALE + '" stroke-width="2.4"/>'
            + bones
            + poly('M48 55 L16 55', UD_PALE_HI, 2.8)
            + '<path d="M20 51 l-6 4 l6 4 z" fill="' + UD_PALE_HI + '" stroke="' + INK + '" stroke-width="1.4"/>')


@icon('Rib-Splitter')
def _():
    # His own rib, thrown, and the kink where it carries on into a second body. The bend is the
    # whole skill, so it gets the brightest line.
    return (poly('M10 18 L34 30 L54 20', UD_MOSS, 2.4)
            + g(bone_shard(19, 'url(#bone)'), 24, 24, 27, 1.05)
            + g(bone_shard(14, 'url(#bone)'), 46, 24, -28, .85)
            + twinkle(34, 30, 1.0, UD_PALE_HI)
            + twinkle(56, 17, .7, UD_PALE))


@icon('Hold the Shot')
def _():
    # No breath to run out of, so he simply keeps holding it: the sling drawn and STILL, the mark
    # ringed, and the pale pips counting the Revs it waits.
    return ('<path d="M18 12 Q10 32 18 52" fill="none" stroke="' + INK + '" stroke-width="6"/>'
            + '<path d="M18 12 Q10 32 18 52" fill="none" stroke="#8a7a62" stroke-width="3"/>'
            + '<path d="M18 12 L30 32 L18 52" fill="none" stroke="' + UD_BONE + '" stroke-width="2"/>'
            + g(bone_shard(15, 'url(#bone)'), 36, 32, 0, .95)
            + crosshair(50, 32, 7, UD_PALE, 2)
            + twinkle(24, 15, .6, UD_PALE_HI) + twinkle(24, 49, .6, UD_PALE_HI))


@icon('Chorus of the Interred')
def _():
    # Three of them singing at once, and the mend coming back up over all three — her Nature means
    # it reaches grave-flesh whole, so the glow is drawn FULL rather than guttering.
    return (g(skull(), 18, 36, -8, .72) + g(skull(), 32, 32, 0, .82) + g(skull(), 46, 36, 8, .72)
            + arc_lines(32, 20, 9, 3, 58, UD_MOSS, -90, 2.2)
            + glow(f'<circle cx="32" cy="22" r="11" fill="url(#heal)"/>', .5)
            + g(plus('url(#heal)'), 32, 15, 0, .45))


@icon('Pall of Silence')
def _():
    # The song stopped. Drawn on a DRAPE rather than the heater shape the first pass used — that
    # silhouette is a shield, and it collided with Barrow's The Lord's Due two tiles away. Wide,
    # soft-hemmed cloth behind, the note struck through in front, and no damage anywhere on it.
    return ('<path d="M7 16 Q32 7 57 16 L57 40 Q50 48 43 42 Q36 36 29 43 Q22 50 15 42 L7 36 Z" fill="url(#shroud)"/>'
            + '<path d="M7 16 Q32 7 57 16" fill="none" stroke="' + UD_BONE + '" stroke-width="2" opacity=".55"/>'
            + g(note(UD_BONE), 30, 30, 0, 1.0)
            + poly('M14 47 L50 13', UD_PALE, 3.4))


@icon('Grave-Patient')
def _():
    # Every curse he lays holds a turn longer. A headstone with a hex on it read as a crossed-out
    # pill and said nothing about duration, so this is the curse sigil with the house's "goes round
    # again" ring sweeping it — open at the head, arrowhead coming back round to close the loop.
    return ('<path d="M32 10 A22 22 0 1 1 15.4 17.5" fill="none" stroke="' + INK + '" stroke-width="5.6"/>'
            + '<path d="M32 10 A22 22 0 1 1 15.4 17.5" fill="none" stroke="' + UD_PALE + '" stroke-width="2.8"/>'
            + '<path d="M26 5 L33 10.5 L26 15.5 Z" fill="' + UD_PALE + '" stroke="' + INK + '" stroke-width="1.4"/>'
            + hex_mark(32, 34, 11, '#241233', '#c89eff')
            + twinkle(49, 48, .7, UD_PALE_HI))


@icon('First Out of the Ground')
def _():
    # Up before the rest of them, and wanting to be seen: the marker breaking the mound with the
    # taunt flaring off it. The lines are the game's draw-every-eye flare, not damage.
    return (g(mound(), 32, 44, 0, 1.25)
            + g(headstone('url(#iron)', .95), 32, 44, -8)
            + speed_lines(10, 14, 3, 9, 7, UD_PALE, -90)
            + burst(32, 22, 4, 11, 9, 'url(#graveR)')
            + twinkle(32, 22, .8, UD_PALE_HI))


@icon('Grave-Debt')
def _():
    # He collects only from the enemy, so the tally is enemy skulls — three of them struck through
    # as paid, and the bar that is the 40% ceiling.
    return (g(skull(), 18, 28, 0, .62) + g(skull(), 32, 28, 0, .62) + g(skull(), 46, 28, 0, .62)
            + '<path d="M10 44 H54" stroke="' + INK + '" stroke-width="5"/>'
            + '<path d="M10 44 H54" stroke="' + UD_PALE + '" stroke-width="2.4"/>'
            + poly('M12 20 L52 20', UD_MOSS, 2)
            + twinkle(54, 48, .7, UD_PALE_HI))


@icon('Scattercast')
def _():
    # Loose bones read as Scatter of Bones, which he already owns. The passive is about area shots
    # landing HARDER, so the tile is three marks taking one each — the spread AND the impact.
    marks = ''.join(g(husk(0, 0, .62, '#2f3a33'), x, y) for x, y in ((15, 24), (32, 44), (49, 24)))
    hits = ''.join(g(bone_shard(11, 'url(#bone)'), x, y, r, .85)
                   for x, y, r in ((17, 14, -62), (32, 32, 0), (47, 14, 62)))
    return (marks + hits
            + twinkle(15, 22, .8, UD_PALE_HI) + twinkle(32, 42, .8, UD_PALE_HI)
            + twinkle(49, 22, .8, UD_PALE_HI))


@icon('The Dead Are Tended')
def _():
    # She keeps at it whether or not she spends the turn on it: the coffin open and the mend
    # falling in, drop by drop, and whole rather than halved because it is hers.
    return (g(coffin_shape('url(#wood)'), 32, 34, 0, 1.0)
            + '<path d="M22 22 Q32 16 42 22" fill="none" stroke="' + UD_BONE + '" stroke-width="2.4"/>'
            + glow(f'<circle cx="32" cy="32" r="10" fill="url(#heal)"/>', .55)
            + g(plus('url(#heal)'), 32, 32, 0, .5)
            + g(drop('url(#heal)'), 32, 12, 0, .66))

# ---- The Stray Banner, second wave ---------------------------------------
SB_STONE = '#8d93a8'    # Shazrak's raised stone, from his own cairn tiles
SB_SOUND = '#5fcad1'    # his aqua, from PAL['stray'] and the sound_wave default
SB_HEAT = '#e8a548'     # Orin's foundry orange, from his look.trim
SB_PLATE = '#6d7482'    # and the plate he rivets on


@icon('Command the Fallen')
def _():
    # Centred, because at x=44 the blades ran off the right edge of the tile. Three blades turning
    # in on one ring in the middle, with room round all of it.
    return (RV_DEFS
            + glow(f'<circle cx="32" cy="32" r="11" fill="{RV_GREEN}"/>', .7)
            + ''.join(rv_at(32, 32, a, .6, 3) for a in (150, 210, 30))
            + f'<circle cx="32" cy="32" r="8.5" fill="none" stroke="{INK}" stroke-width="3.6"/>'
            + f'<circle cx="32" cy="32" r="8.5" fill="none" stroke="#f2fff8" stroke-width="2"/>'
            + twinkle(32, 32, .85, '#ffffff'))


@icon('Blade Harvest')
def _():
    # The other direction: blades coming OUT of one body and home to an open hand. The body stays
    # standing — this takes his ammunition back, not its life.
    return (RV_DEFS
            + g(husk(0, 0, 1.05, '#3f3a46'), 44, 32)
            + ''.join(rv_at(16, 30 + dy, 180, .5, 2) for dy in (-9, 0, 9))
            + f'<circle cx="9" cy="30" r="4.6" fill="{RV_GREEN}" stroke="{INK}" stroke-width="1.6"/>'
            + twinkle(44, 14, .65, '#f2fff8'))


@icon('Never There')
def _():
    # Both figures were near-black on a near-black tile. The after-image is an OUTLINE now and the
    # blade is bright and going through where he used to be — he is the solid one, already clear.
    return (RV_DEFS
            + g('<path d="M-10 13 Q-10 2 -5 -.5 Q-7.5 -3.5 -7 -7.5 Q-6 -13 0 -13 Q6 -13 7 -7.5 Q7.5 -3.5 5 -.5 Q10 2 10 13 Z" '
                f'fill="none" stroke="{RV_GREEN}" stroke-width="2" opacity=".55" stroke-dasharray="4 3"/>', 22, 34, 0, 1.15)
            + g(husk(0, 0, 1.15, '#4a5560'), 45, 32)
            + rv_at(22, 32, 15, .62, 0)
            + speed_lines(9, 20, 3, 9, 7, RV_GREEN, 180)
            + twinkle(45, 15, .7, '#f2fff8'))


@icon('Blow the Valve')
def _():
    # He opens himself up and lets the whole bar go into the line. Vent plate at the bottom, three
    # hard jets, and the heat colour doing the work so it does not read as Shazrak's sound.
    return (f'<rect x="20" y="42" width="24" height="10" rx="3" fill="{SB_PLATE}" stroke="{INK}" stroke-width="2"/>'
            + f'<path d="M24 46 H40" stroke="#3a3f4a" stroke-width="2"/>'
            + ''.join(poly(f'M{x} 40 Q{x + dx} 26 {x + dx * 2} 12', SB_HEAT, 3.2)
                      for x, dx in ((24, -4), (32, 0), (40, 4)))
            + glow(f'<ellipse cx="32" cy="22" rx="16" ry="12" fill="{SB_HEAT}"/>', .4)
            + twinkle(16, 16, .7, '#ffd9a0') + twinkle(50, 15, .6, '#ffd9a0'))


@icon('Plate Rig')
def _():
    # Spare plate riveted onto somebody. The first pass drew the panel alone and it read as a
    # basket, so the ALLY is in the tile now — dark, back turned — with the plate strapped across
    # them, the rivets holding it and the spikes standing off it. Mend glow behind.
    return (glow('<circle cx="32" cy="32" r="15" fill="url(#heal)"/>', .45)
            + g(husk(0, 0, 1.5, '#333b47'), 32, 30)
            + f'<path d="M19 26 H45 L43 43 Q32 48 21 43 Z" fill="{SB_PLATE}" stroke="{INK}" stroke-width="2.2"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="1.9" fill="{SB_HEAT}" stroke="{INK}" stroke-width="1"/>'
                      for x, y in ((24, 30), (40, 30), (25, 39), (39, 39)))
            + ''.join(poly(f'M{x} 26 L{x + dx} 15', '#cfd6e2', 2.6) for x, dx in ((23, -4), (32, 0), (41, 4))))


@icon('Dissonance')
def _():
    # The note that takes something away. Two waves out of phase, crossing, and the mana coming
    # loose where they meet — his aqua for the sound, the game's blue for what it tears out.
    return (sound_wave(10, 32, 3, 7, 120, 0, SB_SOUND)
            + sound_wave(54, 32, 3, 7, 120, 180, SB_SOUND)
            + ''.join(g(drop('url(#mana)'), x, y, 0, s)
                      for x, y, s in ((32, 20, .75), (27, 36, .6), (38, 38, .55)))
            + twinkle(32, 50, .7, '#bfe9ff'))


@icon('Hold the Note')
def _():
    # One long note held over the whole warband: the note itself, and the dome it keeps up. Three
    # heads under it, so it reads as the warband rather than one ally.
    return (f'<path d="M10 40 A22 22 0 0 1 54 40" fill="none" stroke="{INK}" stroke-width="5.4"/>'
            + f'<path d="M10 40 A22 22 0 0 1 54 40" fill="none" stroke="{SB_SOUND}" stroke-width="2.8"/>'
            + glow(f'<path d="M10 40 A22 22 0 0 1 54 40 Z" fill="{SB_SOUND}"/>', .22)
            + ''.join(g(husk(0, 0, .5, '#3a4450'), x, 42) for x in (20, 32, 44))
            + g(note(SB_SOUND), 32, 24, 0, .78))


@icon('Keeping Time')
def _():
    # He sets the tempo. A metronome rather than another clock face: the game already has an
    # hourglass for the grave and a ring for Grave-Patient, and this is a beat, not a duration.
    return (f'<path d="M32 10 L46 50 H18 Z" fill="{SB_STONE}" stroke="{INK}" stroke-width="2.2"/>'
            + f'<path d="M32 14 L32 46" stroke="{INK}" stroke-width="3.6"/>'
            + f'<path d="M32 14 L32 46" stroke="{SB_SOUND}" stroke-width="1.8"/>'
            + f'<rect x="26" y="26" width="12" height="5" rx="1.6" fill="{SB_SOUND}" stroke="{INK}" stroke-width="1.6"/>'
            + arc_lines(32, 14, 7, 2, 70, SB_SOUND, -90, 2)
            + twinkle(48, 18, .6, '#bff0f4'))


@icon('Shockwave')
def _():
    # One blow into the ground and it rolls out from him, nearest first. The hammer head is DOWN
    # and already landed — the tile is the ring leaving, not the swing arriving.
    return (f'<rect x="24" y="8" width="16" height="13" rx="3" fill="{SB_PLATE}" stroke="{INK}" stroke-width="2"/>'
            + f'<rect x="30" y="18" width="4" height="16" fill="#6b4a2a" stroke="{INK}" stroke-width="1.6"/>'
            + burst(32, 38, 4, 11, 10, ZK_RED)
            + zk_floor(44)
            + ''.join(poly(d, ZK_RED, 2.4) for d in ('M8 52 Q18 44 26 50', 'M38 50 Q46 44 56 52')))


@icon('Haymaker')
def _():
    # Third pass. A round mass with knuckle LINES on it reads as a ball however the lines are
    # drawn, so the fist is squared off now: flat striking face on the right, four knuckle ridges
    # standing proud of it, thumb across the front. Impact where it lands, and the dashed red ring
    # round the whole tile for the Exposed he wears afterwards.
    fist = ('<path d="M-13 -10 L4 -11 Q12 -11 12 -4 L12 5 Q12 12 4 12 L-13 11 Q-16 0 -13 -10 Z" fill="#7ea04e" stroke="#2f3d1c" stroke-width="1.8"/>'
            '<path d="M12 -7 q4 0 4 3.4 q0 3.4 -4 3.4 Z" fill="#7ea04e" stroke="#2f3d1c" stroke-width="1.5"/>'
            '<path d="M12 0 q4 0 4 3.4 q0 3.4 -4 3.4 Z" fill="#7ea04e" stroke="#2f3d1c" stroke-width="1.5"/>'
            '<path d="M-6 -10 V11 M1 -10.5 V11.5" stroke="#2f3d1c" stroke-width="1.6"/>'
            '<path d="M-13 3 Q-5 5 0 9" stroke="#2f3d1c" stroke-width="1.8" fill="none"/>')
    return (f'<circle cx="32" cy="32" r="23" fill="none" stroke="{ZK_RED}" stroke-width="2.2" opacity=".5" stroke-dasharray="5 4"/>'
            + speed_lines(10, 34, 3, 10, 8, ZK_RED, 0)
            + g(fist, 26, 34, -8, 1.15)
            + burst(49, 30, 3, 8, 9, ZK_RED)
            + twinkle(49, 14, .75, '#ffd166'))


@icon('Skullcracker')
def _():
    # The crit that splits it. The orc head was too small to read under the crack, so the head
    # fills the tile now and the split is a single heavy bone-white line straight down through it.
    return (g(zk_head(), 32, 32, 0, 1.75)
            + poly('M26 8 L36 26 L28 34 L38 52', '#f7f1e0', 3.6)
            + stun_stars(32, 11, 24)
            + twinkle(52, 46, .8, ZK_RED))


@icon('Severance')
def _():
    # The follow-up to his own mark: the mark still hanging there, and one cut straight through it.
    return (f'<circle cx="34" cy="30" r="12" fill="none" stroke="{CRIMSON}" stroke-width="2.6" opacity=".75"/>'
            + f'<path d="M26 22 L42 38 M42 22 L26 38" stroke="{CRIMSON}" stroke-width="2.2" opacity=".75"/>'
            + slash(10, 48, 54, 12, 3.6)
            + twinkle(52, 14, .8, '#ffffff'))


@icon('Lingering Cut')
def _():
    # A cut that will not close. One clean stroke and the bleeding under it, drawn with the
    # game's bleed red so it reads as the status rather than as more blade.
    return (poly('M12 16 Q32 30 52 46', '#e8eaf2', 3.4)
            + ''.join(g(drop('url(#blood)'), x, y, 0, s)
                      for x, y, s in ((24, 34, .7), (34, 44, .6), (44, 52, .5)))
            + twinkle(14, 14, .7, '#ffffff'))


@icon('Tap the Line')
def _():
    # Whatever he mends he also tops up: the weld bead, and the mana running back down the line
    # into the ally. Heat colour going in, mana colour coming out.
    return (f'<path d="M12 44 Q32 34 52 44" fill="none" stroke="{INK}" stroke-width="5.4"/>'
            + f'<path d="M12 44 Q32 34 52 44" fill="none" stroke="{SB_PLATE}" stroke-width="2.8"/>'
            + glow(f'<circle cx="32" cy="38" r="9" fill="{SB_HEAT}"/>', .5)
            + g(plus('url(#heal)'), 32, 38, 0, .5)
            + ''.join(g(drop('url(#mana)'), x, y, 0, s) for x, y, s in ((20, 22, .7), (32, 14, .8), (44, 22, .7)))
            + twinkle(52, 30, .6, '#bfe9ff'))

# ---- The Riftborn --------------------------------------------------------

# Riftborn helpers
def grav_chevron(y, w=28, h=8, fill='url(#gravity)'):
    x0 = 32 - w / 2
    return f'<path d="M{x0} {y} L32 {y + h} L{x0 + w} {y} L{x0 + w} {y + 3} L32 {y + h + 3} L{x0} {y + 3} Z" fill="{fill}"/>'


def light_ray(cx, cy, length=20, angle=0, fill='url(#lightG)'):
    import math as m
    a = m.radians(angle)
    dx, dy = m.cos(a), m.sin(a)
    px, py = -dy, dx
    return (f'<path d="M{cx + dx * 3:.1f} {cy + dy * 3:.1f} '
            f'L{cx + dx * length:.1f} {cy + dy * length:.1f} '
            f'L{cx + dx * (length - 3) + px * 2:.1f} {cy + dy * (length - 3) + py * 2:.1f} Z" fill="{fill}"/>')


def void_shard(cx, cy, r=10, fill='url(#void)'):
    return (f'<path d="M{cx} {cy - r} L{cx + r * .6:.1f} {cy} L{cx} {cy + r} L{cx - r * .6:.1f} {cy} Z" fill="{fill}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .3:.1f}" fill="#15121d" stroke="none"/>')


def sound_wave(cx, cy, n=3, r0=8, spread=120, rot=0, color='#5fcad1'):
    return arc_lines(cx, cy, r0, n, spread, color, rot, 2.4, 6)


# --- Thurgan (gravity melee) ---
@icon('Fixed Point')
def _():
    # An anchor driven into the ground: Thurgan cannot be moved.
    return ('<rect x="29" y="10" width="6" height="36" rx="2" fill="url(#gravity)"/>'
            '<path d="M22 38 L32 48 L42 38" fill="none" stroke="url(#gravity)" stroke-width="4"/>'
            '<circle cx="32" cy="12" r="5" fill="url(#gravity)"/>'
            '<circle cx="32" cy="12" r="2.5" fill="#2a2440" stroke="none"/>'
            '<rect x="20" y="20" width="24" height="4" rx="2" fill="url(#gravity)"/>')


@icon('Dead Weight')
def _():
    # A heavy fist slamming down with gravity chevrons.
    return (grav_chevron(12) + grav_chevron(20, 22, 6)
            + '<path d="M22 30 L22 48 L42 48 L42 30 L38 28 L26 28 Z" fill="url(#iron)"/>'
            + '<rect x="24" y="28" width="16" height="4" rx="1.5" fill="url(#gravity)"/>'
            + speed_lines(10, 40, 3, 8, 5, '#6b74c8'))


@icon('Deadfall')
def _():
    # An enemy lifted high then smashed: upward arrow becoming a downward impact.
    return ('<path d="M32 10 L24 22 L28 22 L28 38 L36 38 L36 22 L40 22 Z" fill="url(#gravity)"/>'
            + grav_chevron(40, 30, 8)
            + burst(32, 50, 5, 11, 8, 'url(#gravR)')
            + '<path d="M18 48 L46 48" stroke="#6b74c8" stroke-width="2.5"/>')


@icon('Event Horizon')
def _():
    # A spiral pulling inward: the gravity well that drags targets back.
    return ('<circle cx="32" cy="32" r="18" fill="url(#gravR)" stroke="none"/>'
            + '<path d="M32 14 A18 18 0 0 1 50 32" fill="none" stroke="url(#gravity)" stroke-width="3"/>'
            + '<path d="M50 32 A18 18 0 0 1 32 50" fill="none" stroke="#9da6e0" stroke-width="2.5"/>'
            + '<path d="M32 50 A18 18 0 0 1 14 32" fill="none" stroke="#6b74c8" stroke-width="2"/>'
            + '<circle cx="32" cy="32" r="5" fill="#2a2440"/>'
            + '<circle cx="32" cy="32" r="2.5" fill="#d0d4ff" stroke="none"/>'
            + speed_lines(42, 20, 2, 7, 4, '#d0d4ff', -135))


@icon('Collapsing Fist')
def _():
    # A fist with gravity lines converging on it.
    return ('<path d="M24 26 L24 46 L44 46 L44 26 L40 24 L28 24 Z" fill="url(#iron)"/>'
            + '<rect x="26" y="24" width="16" height="4" rx="1.5" fill="url(#gravity)"/>'
            + '<path d="M18 24 L24 32 M46 24 L40 32 M32 14 L32 24" stroke="url(#gravity)" stroke-width="2.5"/>'
            + twinkle(32, 38, .8, '#d0d4ff'))


@icon('Graviton Guard')
def _():
    # A heater shield with a gravity orb in the centre.
    return (g(heater('url(#gravity)', 'url(#cosmic)'), 32, 32, 0, 1.05)
            + '<circle cx="32" cy="30" r="7" fill="url(#gravR)" stroke="none"/>'
            + '<circle cx="32" cy="30" r="3" fill="#d0d4ff" stroke="none"/>')


@icon('Singularity')
def _():
    # A black hole with rings and matter spiraling in: AoE gravity.
    return ('<circle cx="32" cy="32" r="20" fill="url(#gravR)" stroke="none"/>'
            + '<ellipse cx="32" cy="32" rx="20" ry="8" fill="none" stroke="url(#gravity)" stroke-width="2.5" transform="rotate(-20 32 32)"/>'
            + '<ellipse cx="32" cy="32" rx="16" ry="5" fill="none" stroke="#9da6e0" stroke-width="1.5" transform="rotate(15 32 32)"/>'
            + '<circle cx="32" cy="32" r="6" fill="#15121d"/>'
            + '<circle cx="32" cy="32" r="3" fill="#6b74c8" stroke="none"/>'
            + twinkle(16, 18, .6, '#d0d4ff') + twinkle(48, 44, .5, '#d0d4ff'))


@icon('Crushing Field')
def _():
    # Pressure waves radiating from a central gravity point: passive AoE bash.
    return ('<circle cx="32" cy="32" r="8" fill="url(#gravR)" stroke="none"/>'
            + '<circle cx="32" cy="32" r="4" fill="#d0d4ff" stroke="none"/>'
            + '<circle cx="32" cy="32" r="14" fill="none" stroke="url(#gravity)" stroke-width="2" stroke-dasharray="4 3"/>'
            + '<circle cx="32" cy="32" r="21" fill="none" stroke="#9da6e0" stroke-width="1.5" stroke-dasharray="3 4"/>'
            + grav_chevron(10, 16, 5) + grav_chevron(47, 16, 5, '#9da6e0'))


@icon('Ray')
def _():
    # A horizontal beam of light.
    return ('<rect x="10" y="28" width="44" height="8" rx="3" fill="url(#lightG)"/>'
            + '<rect x="12" y="30" width="40" height="4" rx="2" fill="#fffef0" stroke="none"/>'
            + glow('<rect x="8" y="26" width="48" height="12" rx="4" fill="#ffe680"/>', .3)
            + twinkle(50, 32, .6, '#fffef0'))


@icon('Prism Lance')
def _():
    # A pointed lance of light splitting into a prism rainbow.
    return ('<path d="M10 32 L42 24 L42 40 Z" fill="url(#lightG)"/>'
            + '<path d="M12 32 L40 26 L40 38 Z" fill="#fffef0" stroke="none"/>'
            + '<path d="M42 24 L54 18 L54 22 L42 28 Z" fill="#ff6060" stroke="none"/>'
            + '<path d="M42 28 L54 22 L54 30 L42 32 Z" fill="#ffe680" stroke="none"/>'
            + '<path d="M42 32 L54 30 L54 38 L42 36 Z" fill="#5fcad1" stroke="none"/>'
            + '<path d="M42 36 L54 38 L54 46 L42 40 Z" fill="#8a5ad6" stroke="none"/>')


@icon('Glare')
def _():
    # A blinding flash: bright centre with rays that can blind.
    return ('<circle cx="32" cy="32" r="14" fill="url(#lightR)" stroke="none"/>'
            + glow('<circle cx="32" cy="32" r="10" fill="#ffe680"/>', .5)
            + '<circle cx="32" cy="32" r="5" fill="#fffef0" stroke="none"/>'
            + ''.join(f'<line x1="32" y1="32" x2="{32 + 22 * math.cos(math.radians(a)):.0f}" y2="{32 + 22 * math.sin(math.radians(a)):.0f}" stroke="#ffe680" stroke-width="2"/>'
                      for a in range(0, 360, 45)))


@icon('Focus')
def _():
    # A lens focusing light into a point: empower self.
    return ('<path d="M20 14 Q32 20 44 14 Q46 32 44 50 Q32 44 20 50 Q18 32 20 14 Z" fill="url(#lightG)" opacity=".6"/>'
            + '<path d="M22 16 Q32 22 42 16 Q44 32 42 48 Q32 42 22 48 Q20 32 22 16 Z" fill="none" stroke="#e8d26a" stroke-width="1.5"/>'
            + '<circle cx="32" cy="32" r="4" fill="#fffef0"/>'
            + glow('<circle cx="32" cy="32" r="8" fill="#ffe680"/>', .3)
            + '<path d="M32 10 L32 20 M32 44 L32 54" stroke="#e8d26a" stroke-width="1.5"/>')


@icon('Recall')
def _():
    # Swords flying back to the hand: a hand with blades converging.
    return ('<circle cx="32" cy="32" r="8" fill="url(#lightG)"/>'
            + g(sword('url(#lightG)'), 18, 18, -135, .45)
            + g(sword('url(#lightG)'), 46, 18, 135, .45)
            + g(sword('url(#lightG)'), 18, 46, -45, .45)
            + g(sword('url(#lightG)'), 46, 46, 45, .45)
            + '<path d="M22 22 L28 28 M42 22 L36 28 M22 42 L28 36 M42 42 L36 36" stroke="#e8d26a" stroke-width="1.5" stroke-dasharray="2 2"/>')


# --- Resh (sound support) ---
@icon('Clarion')
def _():
    # A bell struck, radiating sound waves.
    return ('<path d="M26 18 Q26 12 32 10 Q38 12 38 18 L40 38 L24 38 Z" fill="url(#sound)"/>'
            + '<rect x="23" y="38" width="18" height="4" rx="1.5" fill="#2a7a8a"/>'
            + '<circle cx="32" cy="42" r="3" fill="url(#sound)"/>'
            + sound_wave(48, 26, 3, 6, 90, -20))


@icon('Quickening Chord')
def _():
    # A musical note with speed lines: haste buff.
    return ('<circle cx="28" cy="42" r="7" fill="url(#sound)"/>'
            + '<rect x="34" y="14" width="4" height="30" rx="1.5" fill="url(#sound)"/>'
            + '<path d="M38 14 L50 18 L50 24 L38 20 Z" fill="#5fcad1"/>'
            + speed_lines(8, 36, 3, 10, 5, '#5fcad1')
            + twinkle(46, 40, .6, '#a8eef4'))


@icon('Thrum')
def _():
    # A heavy bass wave pushing outward: knockback sonic.
    return (sound_wave(14, 32, 4, 8, 140, 0, '#5fcad1')
            + '<circle cx="14" cy="32" r="5" fill="url(#sound)"/>'
            + speed_lines(36, 32, 3, 14, 6, '#a8eef4', 0, .5))


@icon('Discord')
def _():
    # Jagged broken sound waves: AoE stagger.
    return ('<path d="M10 28 L18 22 L26 30 L34 18 L42 28 L50 20 L54 26" fill="none" stroke="url(#sound)" stroke-width="3.5"/>'
            + '<path d="M10 38 L18 44 L26 36 L34 48 L42 38 L50 46 L54 40" fill="none" stroke="#2a7a8a" stroke-width="3"/>'
            + twinkle(32, 32, .7, '#a8eef4')
            + stun_stars(32, 52))


@icon('Steady Tone')
def _():
    # A tuning fork with a healing glow: sustaining heal.
    return ('<rect x="30" y="32" width="4" height="20" rx="1.5" fill="url(#sound)"/>'
            + '<path d="M24 12 L24 34 Q24 38 28 38 L28 34 Z" fill="url(#sound)"/>'
            + '<path d="M40 12 L40 34 Q40 38 36 38 L36 34 Z" fill="url(#sound)"/>'
            + sound_wave(32, 16, 2, 5, 160, -90, '#a8eef4')
            + glow(g(plus('url(#heal)'), 32, 46, 0, .55), .4))


# --- Nyx (void ranged) ---
@icon('Finisher')
def _():
    # A crosshair on a cracked target: +dmg below half HP.
    return ('<circle cx="32" cy="32" r="14" fill="none" stroke="url(#void)" stroke-width="2.5"/>'
            + '<circle cx="32" cy="32" r="6" fill="none" stroke="#c89eff" stroke-width="1.5"/>'
            + '<line x1="32" y1="10" x2="32" y2="24" stroke="url(#void)" stroke-width="2"/>'
            + '<line x1="32" y1="40" x2="32" y2="54" stroke="url(#void)" stroke-width="2"/>'
            + '<line x1="10" y1="32" x2="24" y2="32" stroke="url(#void)" stroke-width="2"/>'
            + '<line x1="40" y1="32" x2="54" y2="32" stroke="url(#void)" stroke-width="2"/>'
            + '<path d="M28 32 L36 32 M32 28 L32 36" stroke="#c89eff" stroke-width="1.5"/>')


@icon('Null Bolt')
def _():
    # A void shard hurtling forward: never misses.
    return (void_shard(32, 30, 14)
            + glow(f'<circle cx="32" cy="30" r="8" fill="#8a5ad6"/>', .3)
            + speed_lines(8, 30, 3, 10, 5, '#c89eff')
            + twinkle(48, 44, .5, '#c89eff'))


@icon('Unmake')
def _():
    # A target being torn apart by void energy: the ultimate damage skill.
    return ('<circle cx="32" cy="32" r="16" fill="url(#voidR)" stroke="none"/>'
            + '<path d="M24 24 L18 14 M40 24 L46 14 M24 40 L18 50 M40 40 L46 50" stroke="url(#void)" stroke-width="2.5"/>'
            + '<circle cx="32" cy="32" r="6" fill="#15121d"/>'
            + '<circle cx="32" cy="32" r="2.5" fill="#c89eff" stroke="none"/>'
            + twinkle(32, 16, .6, '#c89eff') + twinkle(32, 48, .6, '#c89eff'))


@icon('Silencing Gyre')
def _():
    # A spinning void disc with a silence symbol.
    return ('<circle cx="32" cy="32" r="16" fill="url(#voidR)" stroke="none"/>'
            + '<ellipse cx="32" cy="32" rx="18" ry="6" fill="none" stroke="url(#void)" stroke-width="2.5" transform="rotate(25 32 32)"/>'
            + '<line x1="24" y1="28" x2="40" y2="36" stroke="#c89eff" stroke-width="3"/>'
            + '<circle cx="32" cy="32" r="4" fill="#15121d" stroke="none"/>')


@icon('Phase')
def _():
    # A figure half-faded into the void: evade buff.
    return ('<path d="M28 16 L28 48 L36 48 L36 16 Z" fill="url(#void)" opacity=".5"/>'
            + '<circle cx="32" cy="20" r="6" fill="url(#void)" opacity=".7"/>'
            + '<path d="M36 16 L36 48 L44 48 L44 16 Z" fill="none" stroke="url(#void)" stroke-width="1.5" stroke-dasharray="3 3"/>'
            + '<path d="M20 16 L20 48 L28 48 L28 16 Z" fill="url(#void)" opacity=".3"/>'
            + twinkle(46, 24, .5, '#c89eff') + twinkle(18, 40, .5, '#c89eff'))


@icon('Collapse Point')
def _():
    # A void implosion: AoE damage. Multiple shards converging on a centre.
    return ('<circle cx="32" cy="32" r="8" fill="url(#voidR)" stroke="none"/>'
            + void_shard(32, 14, 6)
            + void_shard(16, 42, 6)
            + void_shard(48, 42, 6)
            + '<path d="M32 20 L32 24 M20 40 L26 36 M44 40 L38 36" stroke="#c89eff" stroke-width="1.5" stroke-dasharray="2 2"/>'
            + '<circle cx="32" cy="32" r="3" fill="#15121d" stroke="none"/>')


# --- Orin (conductor support) ---
@icon('Attune: Gravity')
def _():
    # A hand placing a gravity charge on a target.
    return ('<circle cx="32" cy="32" r="14" fill="url(#gravR)" stroke="none"/>'
            + grav_chevron(20, 18, 6)
            + '<circle cx="32" cy="38" r="6" fill="url(#gravity)"/>'
            + '<circle cx="32" cy="38" r="3" fill="#d0d4ff" stroke="none"/>'
            + twinkle(18, 18, .5, '#d0d4ff'))


@icon('Attune: Light')
def _():
    # A hand placing a light charge on a target.
    return ('<circle cx="32" cy="32" r="14" fill="url(#lightR)" stroke="none"/>'
            + '<circle cx="32" cy="32" r="8" fill="url(#lightG)"/>'
            + '<circle cx="32" cy="32" r="3.5" fill="#fffef0" stroke="none"/>'
            + ''.join(f'<line x1="32" y1="32" x2="{32 + 16 * math.cos(math.radians(a)):.0f}" y2="{32 + 16 * math.sin(math.radians(a)):.0f}" stroke="#e8d26a" stroke-width="1.5"/>'
                      for a in range(0, 360, 60)))


@icon('Attune: Void')
def _():
    # A hand placing a void charge on a target.
    return ('<circle cx="32" cy="32" r="14" fill="url(#voidR)" stroke="none"/>'
            + void_shard(32, 32, 12)
            + glow('<circle cx="32" cy="32" r="6" fill="#8a5ad6"/>', .3)
            + twinkle(18, 18, .5, '#c89eff') + twinkle(46, 46, .5, '#c89eff'))


@icon('Grand Chord')
def _():
    # A massive sound wave radiating outward: AoE sound charge.
    return (sound_wave(32, 32, 4, 6, 360, 0, '#5fcad1')
            + '<circle cx="32" cy="32" r="7" fill="url(#sound)"/>'
            + '<circle cx="32" cy="32" r="3.5" fill="#a8eef4" stroke="none"/>'
            + twinkle(14, 14, .5, '#a8eef4') + twinkle(50, 50, .5, '#a8eef4'))


@icon('Conduct')
def _():
    # A conductor's baton with an empowering glow: ally buff.
    return ('<path d="M20 48 L44 16" stroke="url(#cosmic)" stroke-width="4" stroke-linecap="round"/>'
            + '<circle cx="44" cy="16" r="4" fill="url(#cosmic)"/>'
            + glow('<circle cx="44" cy="16" r="8" fill="#b9c0e0"/>', .3)
            + twinkle(30, 28, .7, '#d0d4ff')
            + twinkle(16, 38, .5, '#9da6e0')
            + '<path d="M40 20 Q50 24 48 34" fill="none" stroke="#b9c0e0" stroke-width="1.5"/>')


# ---- The Stray Banner -----------------------------------------------------

# Ryuunosuke helpers: his katana, his shadow, and a crimson brush stroke.
SHADOW = '#5a5280'   # dusk violet: dark enough to read as a shadow, light enough to see on the night frame
CRIMSON = '#c04848'


def katana(length=40, blade='url(#steel)'):
    """A katana on its back, edge down: hilt at the origin, a gently curved blade running to +x."""
    L = length
    return (f'<path d="M4 -1.6 Q{L * .55:.1f} -4.4 {L} -6.2 Q{L * .6:.1f} -1.2 4 2 Z" fill="{blade}"/>'
            f'<path d="M6 -.6 Q{L * .55:.1f} -3.2 {L - 2:.1f} -5.4" fill="none" stroke="#ffffff" stroke-width=".9" opacity=".8"/>'
            '<ellipse cx="3" cy=".2" rx="1.6" ry="4.6" fill="url(#gold)"/>'
            '<rect x="-11" y="-1.8" width="13" height="3.8" rx="1.4" fill="#2a1a1a"/>'
            '<path d="M-10 -1.8 l2 3.8 M-7 -1.8 l2 3.8 M-4 -1.8 l2 3.8" stroke="' + CRIMSON + '" stroke-width="1"/>')


def shade(x, y, s=1, fill=SHADOW, eye=CRIMSON):
    """A shadow figure (head and shoulders) with one red eye: his clone."""
    return g('<path d="M-9 12 Q-9 2 -4.6 -.4 Q-7 -3 -6.4 -7 Q-5.4 -12.6 0 -12.6 Q5.4 -12.6 6.4 -7 Q7 -3 4.6 -.4 Q9 2 9 12 Z" '
             f'fill="{fill}"/>'
             f'<path d="M1 -7 L5 -6.4" stroke="{eye}" stroke-width="1.8"/>', x, y, 0, s)


def slash(x1, y1, x2, y2, w=3.2, color='#ffffff', glow_color=CRIMSON):
    """A clean blade stroke with a crimson after-glow."""
    return (f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{glow_color}" stroke-width="{w + 3:.1f}" opacity=".45" filter="url(#blur)"/>'
            f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="{w:.1f}"/>')


def enso(cx, cy, r, color=CRIMSON, w=4):
    """A brushed red circle left open at the top right."""
    return (f'<path d="M{cx + r * .55:.1f} {cy - r * .83:.1f} A{r} {r} 0 1 0 {cx + r * .93:.1f} {cy - r * .3:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"/>')


@icon('Shadow Matrix')
def _():
    # Replicas of him rise behind every enemy, around a marked centre, blades out.
    return (shade(15, 24, .78) + shade(49, 24, .78) + shade(32, 47, .78)
            + '<circle cx="32" cy="30" r="5.4" fill="none" stroke="' + CRIMSON + '" stroke-width="2.4"/>'
            + '<circle cx="32" cy="30" r="1.8" fill="' + CRIMSON + '"/>'
            + slash(10, 44, 26, 34, 2.2) + slash(54, 44, 38, 34, 2.2) + slash(32, 10, 32, 21, 2.2))


@icon('Iaijutsu')
def _():
    # The lightning draw: half out of the scabbard, and a white cut already across the frame.
    return ('<path d="M8 44 L30 36 L31 40 L9 48 Z" fill="#2a1a1a"/>'
            '<path d="M10 45 l2 2.6 M15 43.2 l2 2.6 M20 41.4 l2 2.6" stroke="' + CRIMSON + '" stroke-width="1"/>'
            + g(katana(32), 22, 39, -20, 1.25)
            + slash(6, 22, 58, 22, 3.4)
            + '<path d="M34 16 L38 22 L33 22 L37 28" fill="none" stroke="#ffe680" stroke-width="2"/>'
            + twinkle(56, 22, .9, '#ffffff'))


@icon('Mark of Death')
def _():
    # A crimson brushed circle around the marked one, a cross cut through it.
    return (enso(32, 32, 19)
            + skull().replace('url(#bone)', '#e8e0d0').join(['<g transform="translate(32 33) scale(.7)">', '</g>'])
            + slash(17, 17, 47, 47, 2.4, '#ffffff') + slash(47, 17, 17, 47, 2.4, '#ffffff'))


@icon('Smoke Veil')
def _():
    # He is gone into the smoke - only the one red eye still shows.
    puffs = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#iron)" opacity="{o}"/>'
                    for x, y, r, o in ((20, 40, 11, .95), (36, 42, 12, .95), (47, 34, 9, .9), (28, 28, 10, .85),
                                       (42, 22, 7.5, .8), (16, 26, 6, .75)))
    return (shade(32, 32, 1.05, '#3a3650') + puffs
            + '<path d="M33 25.4 L38 26.2" stroke="' + CRIMSON + '" stroke-width="2.4"/>'
            + '<circle cx="35.5" cy="25.8" r="3.4" fill="' + CRIMSON + '" opacity=".35" filter="url(#blur)" stroke="none"/>')


@icon('Twin Slash')
def _():
    # His cut and the clone's, landing as one: steel and shadow crossing in an X, a flash where they meet.
    return (g(katana(40), 11, 51, -45, 1.12) + g(katana(40, '#8a80b8'), 53, 51, -135, 1.12)
            + burst(32, 30, 4, 10, 10, '#ffffff')
            + '<circle cx="32" cy="30" r="3" fill="' + CRIMSON + '"/>')


@icon('Blade Dance')
def _():
    # A whirl of cuts through the whole warband: arcs all round, the blade at their heart.
    arcs = ''.join(f'<path d="M{32 + 22 * math.cos(math.radians(a)):.1f} {32 + 22 * math.sin(math.radians(a)):.1f} '
                   f'A22 22 0 0 1 {32 + 22 * math.cos(math.radians(a + 70)):.1f} {32 + 22 * math.sin(math.radians(a + 70)):.1f}" '
                   f'fill="none" stroke="{c}" stroke-width="3"/>'
                   for a, c in ((-80, '#ffffff'), (40, CRIMSON), (160, '#ffffff')))
    return arcs + g(katana(30), 17, 42, -35, 1.2) + speed_lines(40, 46, 3, 8, 4, CRIMSON, 0)


@icon('Invulnerable Clone')
def _():
    # His shadow walks a step behind him, wrapped in a ring nothing gets through.
    return ('<circle cx="38" cy="30" r="17" fill="none" stroke="#9aa0d0" stroke-width="1.6" stroke-dasharray="3 3"/>'
            + shade(38, 30, 1.2) + shade(26, 34, 1.15, 'url(#steel)', CRIMSON))


@icon('Shadow Step')
def _():
    # One kill and he is already further down the line: afterimages streaming behind him.
    return (shade(16, 32, .95, SHADOW, CRIMSON).replace('<g ', '<g opacity=".35" ', 1)
            + shade(26, 32, .95, SHADOW, CRIMSON).replace('<g ', '<g opacity=".65" ', 1)
            + shade(38, 32, .95)
            + '<path d="M44 46 L56 46 M52 42 L56 46 L52 50" fill="none" stroke="' + CRIMSON + '" stroke-width="2.6"/>')


@icon('Killing Intent')
def _():
    # The pressure of a blade that has already decided: two red eyes in the dark, a ragged red aura.
    spikes = ''.join(f'<path d="M{32 + 14 * math.cos(math.radians(a)):.1f} {32 + 14 * math.sin(math.radians(a)):.1f} '
                     f'L{32 + 24 * math.cos(math.radians(a + 6)):.1f} {32 + 24 * math.sin(math.radians(a + 6)):.1f}" '
                     f'stroke="{CRIMSON}" stroke-width="2.4"/>' for a in range(-90, 270, 30))
    return (spikes + '<circle cx="32" cy="32" r="15" fill="#0b0a12"/>'
            + '<path d="M22 30 L29 32 L22 33 Z M42 30 L35 32 L42 33 Z" fill="#ff5a5a" stroke="none"/>'
            + '<circle cx="26" cy="31.6" r="4" fill="#ff5a5a" opacity=".45" filter="url(#blur)" stroke="none"/>'
            + '<circle cx="38" cy="31.6" r="4" fill="#ff5a5a" opacity=".45" filter="url(#blur)" stroke="none"/>')


# ---- Riven (The Stray Banner) -------------------------------------------
# He throws real swords and has only five, so every icon is one of HIS blades - grave-green, a
# white edge, a gold guard and grip, exactly as his art draws them - going somewhere: out to a
# mark, into one body, out of a body, or home. No suns: that was the old light-channeler.

RV_DEFS = ('<defs><linearGradient id="rvB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eafff2"/>'
           '<stop offset=".5" stop-color="#6ef0a8"/><stop offset="1" stop-color="#1f9e62"/></linearGradient></defs>')
RV_GREEN = '#6ef0a8'


def rvblade():
    """One of Riven's blades, point to the right, centred on its own origin; the tip sits at x=+20."""
    return g('<path d="M-5 0 Q1 -3.6 16 -2.8 L30 0 L16 2.8 Q1 3.6 -5 0 Z" fill="#6ef0a8" opacity=".45" filter="url(#blur)" stroke="none"/>'
             '<path d="M-4 0 Q1 -2.4 16 -1.9 L29 0 L16 1.9 Q1 2.4 -4 0 Z" fill="url(#rvB)" stroke-width="1.1"/>'
             '<path d="M-1.5 0 L25 0" stroke="#f2fff8" stroke-width=".8" opacity=".9"/>'
             '<path d="M-5.2 -3.6 Q-3.1 0 -5.2 3.6 Q-7.5 0 -5.2 -3.6 Z" fill="#ffd166" stroke-width=".9"/>'
             '<rect x="-11.5" y="-1.2" width="5.6" height="2.4" rx="1.1" fill="#b9872a" stroke-width=".8"/>', -9)


def rv_at(tx, ty, ang, s, gap=0):
    """A blade whose TIP lands `gap` short of (tx, ty), flying in at angle `ang` (degrees, 0 = rightward)."""
    r = math.radians(ang)
    d = 20 * s + gap
    return g(rvblade(), round(tx - d * math.cos(r), 1), round(ty - d * math.sin(r), 1), ang, s)


def crosshair(x, y, r=6, color=RV_GREEN, w=1.6):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{color}" stroke-width="{w}"/>'
            f'<path d="M{x - r - 3} {y} L{x - r + 2.5} {y} M{x + r - 2.5} {y} L{x + r + 3} {y} '
            f'M{x} {y - r - 3} L{x} {y - r + 2.5} M{x} {y + r - 2.5} L{x} {y + r + 3}" stroke="{color}" stroke-width="{w}"/>'
            f'<circle cx="{x}" cy="{y}" r="1.2" fill="{color}" stroke="none"/>')


def husk(x, y, s=1, fill='#4a3f3a'):
    """A body to stick blades into: head and shoulders, no face - the mark, not a champion."""
    return g('<path d="M-10 13 Q-10 2 -5 -.5 Q-7.5 -3.5 -7 -7.5 Q-6 -13 0 -13 Q6 -13 7 -7.5 Q7.5 -3.5 5 -.5 Q10 2 10 13 Z" '
             f'fill="{fill}"/>', x, y, 0, s)


@icon('Sighted Throw')
def _():
    # Two blades, levelled at the mark he picked a Rev ago: a sight laid on the target, both on its line.
    return (RV_DEFS + crosshair(51, 32, 7.5)
            + rv_at(51, 27, 4, .92, 10) + rv_at(51, 37, -4, .92, 10))


@icon('Recall Swords')
def _():
    # Every blade on the field turning for home: four of his, points in, closing on the open hand.
    return (RV_DEFS + glow(f'<circle cx="32" cy="32" r="8" fill="{RV_GREEN}"/>', .7)
            + ''.join(rv_at(32, 32, a, .6, 6) for a in (45, 135, 225, 315))
            + twinkle(32, 32, .95, '#f2fff8'))


@icon('Fan of Blades')
def _():
    # The fan off his shoulder let go at once: one blade to the mark, one more for every blade still held.
    fan = ''.join(g(rvblade(), round(10 + 24 * math.cos(math.radians(a)), 1), round(50 + 24 * math.sin(math.radians(a)), 1), a, .78)
                  for a in (-64, -38, -12))
    return (RV_DEFS + fan
            + twinkle(51, 12, .6, '#f2fff8') + twinkle(56, 40, .5, '#f2fff8'))


@icon('Emptied Hands')
def _():
    # Every blade he is holding, into one body at once: five points closing on a single mark.
    return (RV_DEFS + husk(50, 33, .95)
            + burst(48, 30, 2.5, 7, 8, '#f2fff8')
            + ''.join(rv_at(47, 30, a, .6, 3) for a in (-28, -14, 0, 14, 28)))


@icon('Barrier')
def _():
    # Three of his swords hung point-down in a row in front of him, and a straight shot glancing off them.
    wall = ''.join(g(rvblade(), x, 31, 90, .78) for x in (22, 32, 42))
    return (RV_DEFS + glow(f'<rect x="16" y="14" width="32" height="36" rx="8" fill="{RV_GREEN}"/>', .28) + wall
            + '<path d="M58 22 L50 27" stroke="#ffffff" stroke-width="2"/>'
            + '<path d="M50 27 L57 33" stroke="#ffffff" stroke-width="1.4" opacity=".6"/>'
            + burst(50, 27, 1.8, 5, 8, '#f2fff8'))


@icon('Unblinking')
def _():
    # His nature: the hood, and the two grave-green eyes that do not close.
    return ('<path d="M12 52 Q8 22 32 12 Q56 22 52 52 Q42 45 32 45 Q22 45 12 52 Z" fill="#3a3326"/>'
            + '<ellipse cx="32" cy="34" rx="12.5" ry="10" fill="#14110b"/>'
            + '<path d="M19 25 Q32 18 45 25" fill="none" stroke="#d6a84a" stroke-width="1.6"/>'
            + '<path d="M32 21 l1.8 2.4 l-1.8 2.4 l-1.8 -2.4 Z" fill="#ffd166" stroke-width=".8"/>'
            + glow(f'<circle cx="26.5" cy="34" r="5" fill="{RV_GREEN}"/><circle cx="38" cy="34.5" r="5.5" fill="{RV_GREEN}"/>', .75)
            + f'<ellipse cx="26.5" cy="34" rx="2.4" ry="1.8" fill="{RV_GREEN}" stroke="none"/>'
            + f'<ellipse cx="38" cy="34.5" rx="2.8" ry="2.1" fill="{RV_GREEN}" stroke="none"/>'
            + '<circle cx="26.6" cy="33.8" r=".8" fill="#f2fff8" stroke="none"/><circle cx="38.2" cy="34.2" r="1" fill="#f2fff8" stroke="none"/>')


@icon('Dead Aim')
def _():
    # His passive (+crit): a blade driven dead centre through the sight, and the flash of the clean hit.
    return (RV_DEFS + crosshair(36, 34, 13, RV_GREEN, 1.8)
            + '<circle cx="36" cy="34" r="6.5" fill="none" stroke="#6ef0a8" stroke-width="1.2" opacity=".7"/>'
            + rv_at(36, 34, 40, .8, 0)
            + burst(36, 34, 2.4, 8, 8, '#f2fff8'))


# ── Zul'kan ──────────────────────────────────────────────────────────────────
# The red orc holds the field by knocking people off their feet, so the kit is
# a hammer, the floor, and what the floor does back. One red runs through all
# six so they read as one hand, and the ripple-and-crack pair recurs wherever
# the ground takes the blow (Ground Slam, Seismic Toss, Tremor) — the same
# visual grammar Mogra's Ground Pound already uses for a shockwave.
ZK_RED = '#d9433a'


def zk_floor(y, cracks='M25 0 L21 8 M33 0 L34 8 M41 0 L45 8'):
    """The ground, and the splits he keeps putting in it."""
    return (f'<rect x="6" y="{y}" width="52" height="7" rx="2" fill="#5a4636"/>'
            + g(poly(cracks, '#3a2c22', 1.3), 0, y + 6))


def zk_head():
    """A tusked orc head, mouth open. Drawn here rather than borrowing skull():
       a skull reads undead, and this one is very much shouting."""
    return ('<path d="M-10 -8 Q-12 6 -4 12 Q4 15 10 8 Q13 -4 8 -10 Q0 -14 -10 -8 Z" fill="#6e8a44"/>'
            '<path d="M-5 1 Q0 10 7 2 Q1 -1 -5 1 Z" fill="#3a1410"/>'
            '<path d="M-3.5 2.5 L-4.5 8 M5 2 L6 7.5" stroke="#f2e8d0" stroke-width="2.2"/>'
            f'<circle cx="-4" cy="-4" r="1.8" fill="{ZK_RED}" stroke="none"/>'
            f'<circle cx="5" cy="-5" r="1.8" fill="{ZK_RED}" stroke="none"/>')


@icon('Ground Slam')
def _():
    # The hammer already through the floor, the shock going out both ways.
    return (arc_lines(32, 47, 15, 2, 58, ZK_RED, 180, 2.2, 6)
            + arc_lines(32, 47, 15, 2, 58, ZK_RED, 0, 2.2, 6)
            + zk_floor(47)
            + burst(32, 45, 4, 10, 9, '#ffd166')
            + g(hammer(), 32, 25, 180, .95)
            + twinkle(14, 23, .7) + twinkle(50, 23, .7))


@icon('Skyward Smash')
def _():
    # The signature: the uppercut, and whoever took it leaving the frame.
    return (speed_lines(32, 46, 3, 13, 7, ZK_RED, -90, .7)
            + g(hammer(), 26, 42, 28, .92)
            + glow(burst(40, 17, 3, 10, 8, '#ffd166'), .65)
            + burst(40, 17, 3, 9, 8, '#ffd166')
            + stun_stars(40, 11, 18))


@icon('War Cry')
def _():
    # The taunt: he shouts, and the sound is what reaches them.
    return (arc_lines(28, 32, 14, 3, 72, ZK_RED, 0, 2.4, 6)
            + g(zk_head(), 22, 32, 0, 1.15)
            + twinkle(50, 18, .65) + twinkle(52, 45, .55))


@icon('Seismic Toss')
def _():
    # Picked up, thrown across the field, landed on.
    return (poly('M11 46 Q24 6 46 32', ZK_RED, 2.0)
            + g(rock('url(#hide)'), 26, 19, -20, .72)
            + zk_floor(48, 'M20 0 L16 8 M28 0 L29 8')
            + burst(46, 40, 3, 9, 8, '#ffd166')
            + twinkle(13, 22, .65))


@icon('Iron Stance')
def _():
    # Braced: the shield planted, the blows coming in off both edges.
    return (glow(g(heater('url(#iron)', ZK_RED), 32, 29, 0, 1.0), .45)
            + g(heater('url(#iron)', ZK_RED), 32, 29, 0, 1.0)
            + zk_floor(51, 'M28 0 L26 7 M38 0 L40 7')
            + speed_lines(11, 28, 2, 9, 9, ZK_RED, 0, .55)
            + speed_lines(53, 28, 2, 9, 9, ZK_RED, 180, .55))


@icon('Tremor')
def _():
    # No hammer in this one: the floor itself is the attack, and it reaches all of them.
    return (arc_lines(32, 44, 12, 3, 66, ZK_RED, 180, 2.2, 6)
            + arc_lines(32, 44, 12, 3, 66, ZK_RED, 0, 2.2, 6)
            + zk_floor(44, 'M22 0 L18 9 M32 0 L33 9 M43 0 L47 9')
            + g(rock('url(#hide)'), 15, 37, -18, .5)
            + g(rock('url(#hide)'), 49, 35, 22, .45)
            + twinkle(32, 20, .7))


@icon('Retaliatory Bash')
def _():
    # The passive: you hit the shield, the shield hits back and you lose your feet.
    return (g(heater('url(#iron)', ZK_RED), 27, 35, 0, .95)
            + poly('M53 13 L43 24', '#c9ccd8', 2.0)
            + burst(42, 25, 3, 9, 9, '#ffd166')
            + stun_stars(43, 14, 16))


@icon('Red Blood')
def _():
    # His nature: the lower he goes, the harder he swings. A drop, and the climb out of it.
    return (glow(g(drop('url(#blood)'), 32, 34, 0, 1.7), .55)
            + g(drop('url(#blood)'), 32, 34, 0, 1.6)
            + poly('M32 47 L32 21 M25 28 L32 20 L39 28', '#ffd166', 2.0)
            + twinkle(18, 22, .65) + twinkle(47, 44, .55))


# ================================================================ third-wave Kingdom of Aldmere
# Wren taking a caster's mana off them, Garrick spending himself to hold the line, Mara ignoring
# armour, Aldous working in areas instead of bolts, Liesl trading the healing for light.
# Everything here stays on the Aldmere ground - deep blue with the gold accent - and mana blue
# appears only where magic is actually being moved, so it never reads as part of the tile.
ALD_GOLD = '#e0bb55'
ALD_LIGHT = '#fff3c4'
ALD_MANA = '#7fc6ff'
ALD_MARK = '#4d6188'    # a faceless mark, light enough to hold against both ends of the blue tile
ALD_SELF = '#3e5a8c'    # one of theirs: the same blue as Garrick's shield face
ALD_CURSE = '#b07ae0'


def ald_shard(x, y, rot, s=1.0, fill=ALD_MANA):
    """A splinter of something broken coming apart off the edge."""
    return g(f'<path d="M0 -5 L3.4 1 L-2.4 4 Z" fill="{fill}"/>', x, y, rot, s)


# Wren ---------------------------------------------------------------------
@icon('Spellbreak Arc')
def _():
    # One stroke along the whole line, and the blue going out of every one of them. The sweep is
    # the subject, so it is a tapered blade-crescent rather than a swoosh behind a sword: Power
    # Slash already owns sword-plus-arc, and a second sword here only crowded the three marks.
    #
    # The crescent arches UP over the marks, and the mana comes off the underside of the blade.
    # Two earlier cuts both failed on the drops: sagging arc with drops beneath it is a mouth
    # with tears under it (three sad faces), and loose drops ABOVE the arc is just rain falling
    # on a hill. Hung off the blade's inner edge, they are what the stroke took off them.
    marks = ''.join(husk(x, 48, .46, ALD_MARK) for x in (14, 32, 50))
    sweep = f'<path d="M8 46 Q33 10 58 32 L52 38 Q32 33 8 46 Z" fill="{ALD_LIGHT}" opacity=".92"/>'
    return (marks + glow(sweep, .5) + sweep
            + poly('M8 46 Q33 10 58 32', ALD_GOLD, 1.4)
            + poly('M52 38 Q32 33 9 45', ALD_MANA, 1.6)
            + g(drop('url(#mana)'), 16, 45, 0, .55) + g(drop('url(#mana)'), 31, 41, 0, .68)
            + g(drop('url(#mana)'), 45, 40, 0, .5)
            + twinkle(9, 29, .55, ALD_MANA) + twinkle(56, 18, .5, ALD_MANA))


@icon('Null Edge')
def _():
    # The negation sigil cut into the blade, and a mark whose mouth is already tied shut.
    # The gag is leather and gold (Bind the Breath's grammar for silence), not a second sigil.
    sigil = (f'<circle r="6.6" fill="none" stroke="{ALD_MANA}" stroke-width="2.6"/>'
             f'<line x1="-4.7" y1="4.7" x2="4.7" y2="-4.7" stroke="{ALD_MANA}" stroke-width="2.6"/>')
    return (husk(46, 38, .8, ALD_MARK)
            + poly('M40 32 H52', ALD_GOLD, 2.4)
            + '<circle cx="46" cy="32" r="2.4" fill="#8a5a28"/>'
            + g(sword(), 23, 34, 22, 1.0)
            + glow(g(sigil, 26, 26, 0, 1.0), .65) + g(sigil, 26, 26, 0, 1.0)
            + burst(36, 32, 3, 9, 8, '#ffd166')
            + twinkle(13, 51, .6, ALD_MANA))


@icon('Disrupting Edge')
def _():
    # The crit lands and the word breaks: the ring of the spell comes apart off the edge.
    ring = (f'<path d="M34.6 14.6 A10 10 0 0 1 49 9.3" fill="none" stroke="{ALD_MANA}" stroke-width="2.8"/>'
            f'<path d="M53.4 14.6 A10 10 0 0 1 39 26.7" fill="none" stroke="{ALD_MANA}" stroke-width="2.8"/>')
    return (g(sword(), 26, 38, 40, .9) + ring
            + ald_shard(54, 7, 25, .9) + ald_shard(36, 32, 200, .8) + ald_shard(56, 25, 70, .7)
            + glow(burst(41, 22, 3, 11, 9, '#ffd166'), .8) + burst(41, 22, 3, 10, 9, '#ffd166')
            + twinkle(14, 24, .7, ALD_LIGHT))


# Garrick ------------------------------------------------------------------
@icon('Castigate')
def _():
    # The hammer already in the plate, inside the shaft of light that sent it. The armour is
    # the point of the skill (it sunders), so it is a curved plate that is visibly split.
    #
    # The hammer comes down on the diagonal. Straight down (rotate 180) puts a long thin shaft
    # above a wide flat head and the whole thing reads as a broom standing in a doorway; the
    # tilt is what makes it a hammer, which is why Smite and Hammerfall both use one.
    shaft = '<path d="M23 4 H42 L52 44 H14 Z" fill="#ffe08a" opacity=".3" stroke="none"/>'
    plate = ('<path d="M11 47 Q32 38 53 47 L51 56 H13 Z" fill="url(#iron)"/>'
             '<path d="M16 51 Q32 44 48 51" fill="none" stroke="#5d6780" stroke-width="1.4"/>'
             '<circle cx="17" cy="53" r="1.4" fill="#2a2a33"/><circle cx="47" cy="53" r="1.4" fill="#2a2a33"/>')
    crack = ('<path d="M39 42 L34 49 L39 56 M30 45 L25 51 L28 56" fill="none"'
             ' stroke="#15121d" stroke-width="2.6"/>')
    return (glow(shaft, .8) + shaft + plate + crack
            + g(hammer('url(#gold)'), 33, 25, 158, 1.05)
            + ald_shard(52, 38, 50, .9, '#6b7489')
            + glow(burst(40, 46, 4, 12, 9, '#fff1b8'), .7) + burst(40, 46, 4, 11, 9, '#fff1b8')
            + twinkle(14, 16, .8) + twinkle(52, 14, .7))


@icon('Shield Charge')
def _():
    # Shield first, then the impact, then whoever was standing there going backwards.
    return (speed_lines(5, 34, 3, 12, 7, '#ffffff', 0, .75)
            + g(heater(ALD_SELF, 'url(#gold)'), 24, 34, -12, 1.05)
            + '<circle cx="24" cy="33" r="4.6" fill="url(#gold)"/>'
            + burst(40, 32, 4, 10, 9, '#ffd166')
            + g(husk(0, 0, .64, ALD_MARK), 47, 37, 22)
            + stun_stars(46, 17, 15))


@icon('Last Oath')
def _():
    # A shield that has already lost pieces of itself and is still up, with one spark of him
    # left on the boss. Deliberately NOT a clean shield: the bite out of the rim and the chips
    # leaving the frame are what say "one hit from gone".
    bite = '<path d="M36 10 L49 13 L44 26 L34 19 Z" fill="#15121d" opacity=".9" stroke="none"/>'
    cracks = ('<path d="M41 24 L34 32 L38 44 M37 27 L26 31 L21 43" fill="none"'
              ' stroke="#15121d" stroke-width="2.8"/>')
    return (g(heater(ALD_SELF, 'url(#gold)'), 31, 31, -12, 1.12) + bite + cracks
            + ald_shard(55, 12, 25, .95, '#2a3a5c') + ald_shard(13, 16, -150, .8, '#2a3a5c')
            + ald_shard(50, 48, 160, .7, '#2a3a5c')
            + glow('<circle cx="29" cy="34" r="6" fill="#ffd060"/>', .95)
            + twinkle(29, 34, .95, ALD_LIGHT))


# Mara ---------------------------------------------------------------------
@icon('Punch-Through')
def _():
    # In one side of the plate and out the far side, with the hole it left behind. The ball is
    # round and the line through the tile is straight: armour did not change its mind for it.
    plate = ('<rect x="-12" y="-17" width="24" height="34" rx="3.5" fill="url(#iron)"/>'
             '<path d="M-12 -6 H12 M-12 6 H12" stroke-width="1"/>'
             '<circle cx="-8" cy="-13" r="1.3" fill="#2a2a33"/><circle cx="8" cy="13" r="1.3" fill="#2a2a33"/>')
    hole = ('<circle cx="28" cy="30" r="5.4" fill="#0b1020"/>'
            '<circle cx="28" cy="30" r="7.6" fill="none" stroke="#ffd166" stroke-width="1.8"/>'
            '<path d="M28 21 L28 17 M19 30 L15 31 M28 39 L28 43 M36.5 31 L41 32" fill="none"'
            ' stroke="#ffd166" stroke-width="1.6"/>')
    return ('<path d="M6 36 L56 25" fill="none" stroke="#ffd166" stroke-width="1.6"'
            ' stroke-dasharray="4 3" opacity=".8"/>'
            + g(plate, 27, 32, -8) + hole
            + speed_lines(37, 27, 3, 9, 5, '#ffd166', 0, .85)
            + '<circle cx="51" cy="26" r="4.4" fill="url(#steel)"/>'
            + '<circle cx="49.6" cy="24.6" r="1.4" fill="#ffffff" stroke="none" opacity=".9"/>'
            + twinkle(14, 49, .6, '#e9e4d8'))


@icon('Called Shot')
def _():
    # Aimed Shot is the crosshair on its own; this one is the crosshair already locked on a body,
    # one line in with no spread, and a tick: it is not a gamble.
    return (husk(32, 36, .92, ALD_MARK)
            + '<path d="M8 53 L23 42" fill="none" stroke="#ffd166" stroke-width="1.8"'
              ' stroke-dasharray="4 3"/>'
            + crosshair(32, 33, 11, ALD_GOLD, 2.2)
            + '<circle cx="32" cy="33" r="2.6" fill="#e0455a"/>'
            + poly('M42 14 L47 20 L56 8', ALD_GOLD, 2.6)
            + twinkle(13, 17, .7, ALD_LIGHT))


@icon('Finishing Round')
def _():
    # The round she keeps for the one that is nearly down: the cartridge, the chevron, the
    # sliver of health left under it.
    cart = ('<path d="M-5 -7 Q0 -17 5 -7 Z" fill="url(#steel)"/>'
            '<rect x="-5" y="-7" width="10" height="17" rx="1.4" fill="url(#gold)"/>'
            '<rect x="-6.4" y="8" width="12.8" height="4.4" rx="1.4" fill="#8a5a14"/>'
            '<path d="M-5 -1 H5" stroke-width="1"/>')
    return (g(cart, 32, 22, 0, 1.0)
            + poly('M20 36 L32 46 L44 36', ALD_GOLD, 3.2)
            + '<rect x="11" y="50" width="42" height="7" rx="3.5" fill="#1b2438"/>'
            + '<rect x="13" y="52" width="9" height="3" rx="1.5" fill="#e0455a" stroke="none"/>'
            + twinkle(50, 17, .7, ALD_LIGHT))


# Aldous -------------------------------------------------------------------
@icon('Backdraft')
def _():
    # A wall of fire going out sideways across the whole line, not a bolt at one of them: the
    # crenellated front is wide, and the arcs behind it are the roll.
    marks = ''.join(husk(x, 19, .46, ALD_MARK) for x in (14, 32, 50))
    wall = ('<path d="M5 56 Q8 36 14 45 Q18 26 25 41 Q32 22 39 41 Q46 26 50 45 Q56 36 59 56 Z"'
            ' fill="url(#fire)"/>')
    core = ('<path d="M14 56 Q17 44 22 50 Q27 38 32 48 Q37 38 42 50 Q47 44 50 56 Z"'
            ' fill="#ffe680" opacity=".85"/>')
    return (marks + arc_lines(32, 58, 24, 3, 116, '#ffb347', -90, 2.0, 4.5)
            + glow(wall, .7) + wall + core
            + twinkle(9, 23, .7, '#ffd166') + twinkle(55, 23, .65, '#ffd166'))


@icon('Draw the Ember')
def _():
    # THE WHOLE POINT IS THE COLOUR CHANGE. Mana comes out of the mark blue and arrives at him
    # orange, so the stream is drawn in two halves and both ends are present in the tile: blue
    # drops on the right, his flame on the left, the hand-over in the middle.
    return (husk(49, 38, .66, ALD_MARK)
            + poly('M44 30 Q38 17 29 20', ALD_MANA, 3.4)
            + poly('M29 20 Q19 23 16 33', '#ff8a3d', 3.4)
            + g(drop('url(#mana)'), 40, 22, 0, .7) + g(drop('url(#mana)'), 47, 29, 0, .55)
            + g(flame(), 22, 21, -28, .36)
            + glow(g(flame(), 17, 42, 0, .82), .75) + g(flame(), 17, 42, 0, .78)
            + twinkle(54, 20, .65, ALD_MANA) + twinkle(33, 50, .6, '#ffd166'))


@icon('Kindled')
def _():
    # He turns up already alight. A figure standing in the fire, not a fireball being thrown:
    # no bolt, no arm, no target - just him and the wreath.
    return (glow('<circle cx="32" cy="34" r="18" fill="#ff8a3d"/>', .45)
            + arc_lines(32, 36, 20, 2, 300, '#ff8a3d', -90, 2.2, 5)
            + husk(32, 38, .95, ALD_SELF)
            + g(flame(), 14, 38, -14, .58) + g(flame(), 50, 38, 14, .58)
            + g(flame(), 32, 16, 0, .46)
            + twinkle(13, 19, .7, '#ffd166') + twinkle(51, 19, .7, '#ffd166'))


# Liesl --------------------------------------------------------------------
@icon('Dawnbreak')
def _():
    # Dawn over the whole field: the rays run right over the marks, and both of them have their
    # arms up over their eyes.
    def shielding(x, y, s):
        return g(husk(0, 0, 1, ALD_MARK)
                 + poly('M-9 -1 L-14 -12', ALD_MARK, 2.6) + poly('M9 -1 L14 -12', ALD_MARK, 2.6),
                 x, y, 0, s)
    rays = ''.join(g('<path d="M-2.2 0 L0 -27 L2.2 0 Z" fill="#ffe08a" opacity=".55" stroke="none"/>', 32, 26, a)
                   for a in range(0, 360, 30))
    return (rays + glow('<circle cx="32" cy="26" r="13" fill="#ffd060"/>', .9)
            + burst(32, 26, 7, 17, 12, '#ffe08a')
            + '<circle cx="32" cy="26" r="8.5" fill="#fffbe6"/>'
            + shielding(14, 46, .56) + shielding(50, 46, .56)
            + twinkle(10, 22, .6, ALD_LIGHT) + twinkle(54, 20, .55, ALD_LIGHT))


@icon('Absolution')
def _():
    # NOT A HEAL. No cross, no plus(), no url(#heal) anywhere near it: the subject is the curse
    # leaving. Three of theirs standing in a pool of dawn, the hexes lifting off them and coming
    # apart into dust before they reach the top of the tile.
    marks = ''.join(husk(x, 42, .52, ALD_MARK) for x in (14, 32, 50))
    wisps = (poly('M14 32 q-5 -6 0 -11 q5 -5 0 -10', ALD_CURSE, 2.4)
             + poly('M32 30 q5 -6 0 -11 q-5 -5 0 -10', ALD_CURSE, 2.4)
             + poly('M50 32 q-5 -6 0 -11 q5 -5 0 -10', ALD_CURSE, 2.4))
    dust = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#c89eff" opacity="{o}" stroke="none"/>'
                   for x, y, r, o in ((14, 7, 1.7, .5), (19, 11, 1.1, .35), (32, 5, 1.7, .5),
                                      (26, 9, 1.1, .35), (50, 7, 1.7, .5), (44, 11, 1.1, .35)))
    return (glow('<ellipse cx="32" cy="50" rx="24" ry="7" fill="#ffd060"/>', .75)
            + f'<ellipse cx="32" cy="50" rx="23" ry="6.5" fill="#ffd060" fill-opacity=".28"'
              f' stroke="{ALD_GOLD}" stroke-width="2.2"/>'
            + marks + wisps + dust
            + twinkle(8, 20, .65, ALD_LIGHT) + twinkle(56, 20, .6, ALD_LIGHT))


@icon('Dawnward March')
def _():
    # The chapel bell setting the pace, and the pace running out ahead of it.
    bell = ('<rect x="-2.4" y="-19" width="4.8" height="4.5" rx="1.6" fill="#8a5a14"/>'
            '<path d="M-13 8 Q-13 -9 0 -15 Q13 -9 13 8 Z" fill="url(#gold)"/>'
            '<path d="M-16 8 H16 L13.5 13 H-13.5 Z" fill="#f0d08a"/>'
            '<path d="M-7 -4 Q0 -8 7 -4" fill="none" stroke="#8a5a14" stroke-width="1.4"/>'
            '<circle cx="0" cy="16.5" r="3.2" fill="#8a5a14"/>')
    return (arc_lines(28, 28, 16, 3, 86, ALD_GOLD, 0, 2.2, 4.5)
            + g(bell, 28, 28, -12, 1.0)
            + speed_lines(41, 48, 3, 11, 6, ALD_LIGHT, 0, .8)
            + twinkle(14, 13, .7, ALD_LIGHT))


# ================================================================ Stoneleaf Accord, third wave
# The Accord is two peoples under one banner and the icons keep them apart on sight:
# Durgan's and Hilda's read as stone, iron and anvil work; Aelira's, Faelan's and Elowen's
# as wood, leaf and arrow work. Nothing in this block crosses that line.
STL_ACC = '#a8d06b'     # the Accord's pale green, from PAL['stone']
STL_SPARK = '#ffd166'   # the forge spark the dwarf icons already use
STL_ROOT = '#6b4422'    # root / haft brown
STL_GREEN = '#4c9a28'   # living green for vines and rot


def anvil(fill='url(#iron)', face='#9aa3b5'):
    """A blacksmith's anvil, origin at the centre of its face. Anvil Strike's silhouette,
    which is the one the Accord's dwarf icons have already taught: wide face, waist, horn."""
    return (f'<path d="M-17 0 H17 Q17 6 11 7 L9 12 H15 V18 H-11 V12 H-5 L-7 7 Q-15 6 -17 0 Z" fill="{fill}"/>'
            f'<path d="M17 0 Q25 0 27 -3 Q25 4 17 4 Z" fill="{fill}"/>'
            f'<path d="M-17 0 H17" stroke="{face}" stroke-width="1.2"/>')


def dwarf(x, y, s=1, plate='url(#iron)', beard='#d8c8a8'):
    """A squat braced dwarf of the Accord: brimmed helm, a beard over the breastplate.
    Origin at his chest; he spans roughly 26 wide and 35 tall at s=1."""
    return g(f'<path d="M-13 17 Q-13 2 -7 -1 H7 Q13 2 13 17 Z" fill="{plate}"/>'
             '<rect x="-7" y="-6.4" width="14" height="6.6" fill="#d2a87c"/>'
             f'<path d="M-7 -1.5 Q-9 10 0 14 Q9 10 7 -1.5 Z" fill="{beard}"/>'
             f'<path d="M-9 -9 Q-9 -18 0 -18 Q9 -18 9 -9 Z" fill="{plate}"/>'
             '<rect x="-10.5" y="-10" width="21" height="4.4" rx="1.6" fill="#5d6780"/>'
             '<circle cx="-3.6" cy="-3.6" r="1.4" fill="#15121d" stroke="none"/>'
             '<circle cx="3.6" cy="-3.6" r="1.4" fill="#15121d" stroke="none"/>', x, y, 0, s)


def longbow(wood='#8a5a32', string='#d8ca9e'):
    """An elven longbow, target to the right: the stave bows toward the target, the string
    runs straight down the near side, so an arrow laid on it points right. Origin at the grip."""
    return (f'<path d="M-3 -21 Q10 0 -3 21" fill="none" stroke="{INK}" stroke-width="6.4"/>'
            f'<path d="M-3 -21 Q10 0 -3 21" fill="none" stroke="{wood}" stroke-width="3.4"/>'
            f'<path d="M-3 -21 L-3 21" stroke="{string}" stroke-width="1.3"/>'
            '<path d="M6 -4 Q9 0 6 4" fill="none" stroke="#5e3a1c" stroke-width="2.6"/>')


def prybar(fill='url(#steel)'):
    """A prying tool: chisel tip at the origin, shaft running out along -x to a thin bent heel.
    Kept skinny on purpose - any thickness at the far end and it starts to read as a hammer."""
    return (f'<path d="M4 4.5 L-3.5 -4.5 L-16 -2.4 L-20 -8 L-23 -5 L-19 0.6 L-16 2.2 Z" fill="{fill}"/>'
            '<path d="M-19.5 -6.6 L-21.6 -5" stroke="#5d6780" stroke-width="1.2"/>')


# ---- Durgan Anvilbeard (dwarf)
@icon('Anvil Drop')
def _():
    # The heaviest thing in the Accord, dropped: the anvil is already down and the target is
    # still in the air. Falling streaks above, impact burst at the foot, the body flung clear.
    return ('<path d="M13 4 V15 M23 2 V13" stroke="' + STL_SPARK + '" stroke-width="2.6" opacity=".6"/>'
            + '<rect x="4" y="52" width="56" height="6" rx="2" fill="#4a3a2e"/>'
            + '<path d="M16 52 L12 58 M30 52 L26 58" stroke-width="1.4"/>'
            + g(anvil(), 23, 27, -8, .86)
            + glow(burst(31, 46, 5, 13, 10, STL_SPARK), .6)
            + burst(31, 46, 4, 10, 10, STL_SPARK)
            + speed_lines(36, 37, 3, 8, 7, '#d8c8a8', 0, .55)
            + g(husk(0, 0, .78, '#6a6054'), 52, 37, 26))


@icon('Hold the Pass')
def _():
    # He plants himself in the gap and everything on the field turns to him: the two cliff walls
    # pinch in, the attention comes from both sides, and he is already set in the middle of it.
    cliff = ('<path d="M0 52 V-28 L10 -18 L13 2 L11 52 Z" fill="#474e5b"/>'
             '<path d="M0 -28 L6 -8 L11 52 M6 -8 L13 2" fill="none" stroke="#32373f" stroke-width="1.8"/>')
    aim = ('<path d="M0 0 H11 M6 -5 L11 0 L6 5" fill="none" stroke="' + INK + '" stroke-width="5"/>'
           '<path d="M0 0 H11 M6 -5 L11 0 L6 5" fill="none" stroke="#d8c8a8" stroke-width="2.4"/>')
    # Four arrows all levelled at him and none of them near the helm: anything drawn up by his
    # head reads as antlers growing out of it.
    return (g(cliff, 1, 8) + g('<g transform="scale(-1 1)">' + cliff + '</g>', 63, 8)
            + '<rect x="13" y="50" width="38" height="6" rx="2" fill="#4a3a2e"/>'
            + dwarf(32, 33, .95)
            + g(aim, 14, 31, 0, .85) + g('<g transform="scale(-1 1)">' + aim + '</g>', 50, 31, 0, .85)
            + g(aim, 14, 13, 22, .75) + g('<g transform="scale(-1 1)">' + aim + '</g>', 50, 13, -22, .75))


@icon('Hammer and Anvil')
def _():
    # Hitting him costs you your edge. His plate is the anvil: the sword comes down on it and
    # stops as a stump, and every shard in the air is sword, not armour. A heater-shaped plate
    # just read as a shield, so the armour here is a riveted band - unmistakably worn, not held.
    band = ('<path d="M9 44 Q32 37 55 44 L54 52 Q32 59 10 52 Z" fill="url(#iron)"/>'
            '<path d="M12 45.5 Q32 39.5 52 45.5 L51.5 50 Q32 55.5 12.5 50 Z" fill="url(#steel)" stroke-width="1.2"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#5d6780" stroke="none"/>'
                      for x, y in ((15, 48), (23, 45.6), (32, 44.7), (41, 45.6), (49, 48))))
    broken = ('<path d="M-4 -24 H4 L3.8 -9 L2.4 -1 L1.2 -7.5 L-0.4 -2 L-1.6 -8.5 L-3 -2.5 L-3.8 -9.5 Z" fill="url(#steel)"/>'
              '<line x1="0" y1="-22" x2="0" y2="-11" stroke="#5d6780" stroke-width="1"/>'
              '<rect x="-10" y="-28.4" width="20" height="4.4" rx="1.6" fill="url(#gold)"/>'
              '<rect x="-2.2" y="-36" width="4.4" height="8" fill="#5a3520"/>'
              '<circle cx="0" cy="-38" r="3" fill="url(#gold)"/>')
    tip = '<path d="M0 -8 L2.8 -2 L2.4 6 L-2.4 6 L-2.8 -2 Z" fill="#dfe6f2"/>'
    chip = '<path d="M0 0 L7 2.6 L2 6 Z" fill="#dfe6f2"/>'
    return (band
            + g(broken, 29, 42, 6, 1.0)
            + glow(burst(30, 41, 3.4, 10, 9, STL_SPARK), .5)
            + burst(30, 41, 2.8, 7.5, 9, STL_SPARK)
            + g(tip, 44, 32, 115, 1.1)
            + g(chip, 14, 31, 160, .95) + g(chip, 42, 15, -35, .85) + g(chip, 18, 16, -150, .7))


# ---- Hilda Stonewall (dwarf)
@icon('Mountainside')
def _():
    # Not a thrown rock: a slab of the mountain itself, swung through, and what it caught is
    # still coming apart about it. Moss on the top face so it reads as mountain, not rubble.
    slab = ('<path d="M-17 -6 L-6 -18 L10 -15 L18 -2 L12 14 L-5 18 L-16 8 Z" fill="#7a8290"/>'
            '<path d="M-6 -18 L-2 -3 L12 14 M-2 -3 L-16 8 M-2 -3 L18 -2" fill="none" stroke="#4e5560" stroke-width="1.6"/>'
            '<path d="M-6 -18 L10 -15 L18 -2" fill="none" stroke="#7d9b52" stroke-width="2.6"/>')
    return (speed_lines(4, 32, 3, 12, 7, '#c9b28a', 0, .65)
            + g(slab, 23, 33, -8, 1.0)
            + glow(burst(44, 31, 4, 11, 9, STL_SPARK), .55)
            + burst(44, 31, 3.4, 9, 9, STL_SPARK)
            + g(husk(0, 0, .76, '#6a6054'), 50, 39, 24)
            + stun_stars(48, 13, 16))


@icon('Set in Stone')
def _():
    # She stops moving on purpose: heels together, toes out, and the stone coming up the greave
    # from the foot along a jagged line. The two hexes thrown at her break on the way in.
    # Both boots facing the same way just read as a pair of suitcases, hence the mirrored stance.
    boot = ('<path d="M-7 -20 H7 L6 -14 H-6 Z" fill="#5d6780"/>'
            '<path d="M-5.6 -14 H5.6 L6.6 -2 L15 3 L16 10 H-6.6 L-6 -2 Z" fill="url(#iron)"/>'
            '<path d="M-6 -8 H6.2" stroke="#5d6780" stroke-width="1.8"/>')
    stone = ('<path d="M-6.3 -3 L-2.5 -6 L1.5 -3 L6 -5.5 L6.6 -2 L15 3 L16 10 H-6.6 Z" fill="#8b93a1"/>'
             '<path d="M-1.5 -2.5 L0 5 M6 1 L9 6" fill="none" stroke="#5a616e" stroke-width="1.4"/>')
    hexin = ('<path d="M0 0 L8 9" fill="none" stroke="#b07ae0" stroke-width="3.2"/>'
             '<path d="M-3 9 L3 15" fill="none" stroke="#b07ae0" stroke-width="2.6" opacity=".75"/>'
             '<path d="M12 4 l4 2.4 l-4 2.4 l-2.4 -2.4 Z" fill="#e2c4f6" stroke-width="1"/>')
    return ('<path d="M7 45 H57 L53 57 H11 Z" fill="#5a606c"/>'
            + '<path d="M19 45 L16 57 M33 45 L31 57 M45 45 L47 57" fill="none" stroke="#3e444f" stroke-width="1.6"/>'
            + g('<g transform="scale(-1 1)">' + boot + stone + '</g>', 22, 37, 0, .88)
            + g(boot + stone, 42, 37, 0, .88)
            + g(hexin, 8, 5) + g('<g transform="scale(-1 1)">' + hexin + '</g>', 56, 5)
            + burst(18, 16, 2.6, 7.5, 8, '#c79aec') + burst(46, 16, 2.6, 7.5, 8, '#c79aec'))


@icon('Seamless Plate')
def _():
    # There is no gap to exploit: the panels lap over one another with a BRIGHT edge instead of
    # a dark join, and the pry bar has nothing to catch - it is skidding off the shoulder.
    # The notched neckline matters: without it the lapped bands read as a bell, not a cuirass.
    laps = ''.join(f'<path d="M{a} {b} Q32 {c} {64 - a} {b} L{63 - a} {d} Q32 {e} {a + 1} {d} Z" fill="url(#steel)"/>'
                   f'<path d="M{a} {b} Q32 {c} {64 - a} {b}" fill="none" stroke="#eaf1f8" stroke-width="1.8"/>'
                   for a, b, c, d, e in ((17, 28, 21, 36, 31), (18, 36, 30, 44, 39), (21, 44, 38, 51, 47)))
    rivets = ''.join(f'<circle cx="{x}" cy="{y}" r="1.3" fill="#5d6780" stroke="none"/>'
                     for x, y in ((21, 31), (43, 31), (22, 39), (42, 39), (25, 47), (39, 47)))
    return ('<path d="M14 26 L22 17 L27 21 H37 L42 17 L50 26 L48 44 Q40 55 32 58 Q24 55 16 44 Z" fill="url(#iron)"/>'
            + laps + rivets
            + g(prybar(), 45, 31, 112)
            + '<path d="M50 25 L56 22 M49 19 L53 14" fill="none" stroke="#d8c8a8" stroke-width="2.2" opacity=".8"/>')


# ---- Aelira Swiftwind (elf)
@icon('Threadneedle')
def _():
    # Three shots, one needle's eye. The ring is small on purpose - the whole read is that the
    # group is tighter than the gap it goes through.
    sh = ('url(#steel)', STL_ACC, 34)
    return ('<ellipse cx="44" cy="32" rx="8" ry="10.5" fill="none" stroke="' + INK + '" stroke-width="6"/>'
            '<ellipse cx="44" cy="32" rx="8" ry="10.5" fill="none" stroke="url(#gold)" stroke-width="3"/>'
            + g(arrow(*sh), 33.8, 27.5, 100, .85)
            + g(arrow(*sh), 32.4, 32, 90, .92)
            + g(arrow(*sh), 33.8, 36.5, 80, .85)
            + twinkle(53, 15, .85, '#ffffff'))


@icon('Loose and Move')
def _():
    # Shoot, then slip. She is on the right now with two of herself fading out behind her; the
    # shot has gone, and the arrow coming back for her is through the space she left.
    return (g(longbow('#6b4422', '#b3a584'), 16, 33, 0, .76, ' opacity=".26"')
            + g(longbow('#7a4f2c', '#c6b891'), 26, 33, 0, .88, ' opacity=".5"')
            + g(longbow(), 38, 34, 0, 1.0)
            + g(arrow('url(#steel)', STL_ACC, 24), 44, 18, 90, .8)
            + g(arrow('url(#iron)', '#9aa3b5', 26), 18, 46, 215, .75)
            + speed_lines(8, 12, 3, 10, 6, '#d4ffb0', 0, .55))


@icon('Second Nock')
def _():
    # One string, two nocks, two arrows away together: one more arrow in every volley.
    return (g(longbow(), 24, 32, 0, 1.0)
            + g(arrow('url(#steel)', STL_ACC, 34), 35.5, 26, 90, .85)
            + g(arrow('url(#steel)', STL_ACC, 34), 35.5, 38, 90, .85)
            + twinkle(51, 15, .8, STL_ACC))


# ---- Faelan Thornshot (elf)
@icon('Blinding Toxin')
def _():
    # Venom across the eyes: the splash lands on the face and both eyes are struck out under it.
    # The head gets a jaw and a neck - a bare oval reads as a stone, not as somebody blinded.
    head = ('<path d="M19 30 Q19 14 32 14 Q45 14 45 30 Q45 42 39 47 L39 52 H25 L25 47 Q19 42 19 30 Z" fill="#6a6054"/>'
            '<path d="M26 43 Q32 47 38 43" fill="none" stroke="#443e36" stroke-width="2"/>')
    splat = ('<path d="M11 25 Q19 17 27 23 Q33 16 40 21 Q48 15 53 26 Q48 34 40 30 '
             'Q33 36 26 31 Q18 36 11 25 Z" fill="url(#poison)"/>')
    return (glow('<ellipse cx="32" cy="26" rx="21" ry="11" fill="#b8ff6a"/>', .5)
            + head + splat
            + '<path d="M21 22 L29 30 M29 22 L21 30 M35 23 L43 31 M43 23 L35 31" fill="none" stroke="' + INK + '" stroke-width="3.2"/>'
            + '<circle cx="14" cy="16" r="2.2" fill="#b8ff6a"/><circle cx="51" cy="14" r="1.8" fill="#b8ff6a"/>'
            + '<circle cx="47" cy="37" r="1.6" fill="#b8ff6a"/>'
            + g(drop('url(#poison)'), 21, 40, 0, .62) + g(drop('url(#poison)'), 44, 43, 0, .5))


@icon('Marrowrot')
def _():
    # Not a splash on the outside: the bolt is in past the head and the rot is travelling the
    # bone from the wound outward. The bone is drawn over the bolt's tip so the depth shows.
    bone = ('<path d="M-21 -5 Q-27 -9 -26 -2.5 Q-30 0 -26 3 Q-27 9 -21 5.5 L21 5.5 Q27 9 26 3 '
            'Q30 0 26 -2.5 Q27 -9 21 -5 Z" fill="url(#bone)"/>')
    return (glow('<circle cx="33" cy="36" r="13" fill="#8adc4a"/>', .45)
            + g(bolt('url(#poison)', '#9ac46b', 32), 23.2, 27.1, 140, 1.05)
            + g(bone, 32, 36, -22, 1.05)
            # Branching, not a stripe: a single green line along the bone reads as decoration.
            + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#5e7a2a" stroke="none"'
                      f' transform="rotate(-22 {x} {y})"/>'
                      for x, y, rx, ry in ((39, 30, 3.4, 2.2), (45, 28, 2.4, 1.6), (23, 39, 2.8, 1.8)))
            + poly('M30 34 Q39 30 47 26', STL_GREEN, 2.2)
            + poly('M36 32 L38 37 M42 29 L45 33 M33 33 L32 28', STL_GREEN, 1.4)
            + poly('M30 35 Q24 39 18 42', STL_GREEN, 1.8)
            + poly('M25 38 L24 43 M21 40 L20 36', STL_GREEN, 1.2)
            + '<ellipse cx="29.5" cy="33" rx="4.2" ry="2.6" fill="#2b3a1c" transform="rotate(-22 29.5 33)"/>'
            + g(drop('url(#poison)'), 45, 49, 0, .6))


@icon('Rotgut')
def _():
    # The same venom, run down thicker: one drop with a dark concentrate sitting in the middle
    # of it, and the green arrow the Accord uses for "more".
    return (glow('<circle cx="32" cy="30" r="14" fill="#b8ff6a"/>', .45)
            + g(drop('url(#poison)'), 30, 30, 0, 2.4)
            + g(drop('#2a5a16'), 30, 32, 0, 1.25)
            + '<ellipse cx="25" cy="22" rx="2.6" ry="3.6" fill="#eaffc0" stroke="none" opacity=".75" transform="rotate(-25 25 22)"/>'
            + '<path d="M50 48 V34 M44.5 39.5 L50 33 L55.5 39.5" fill="none" stroke="' + STL_ACC + '" stroke-width="2.6"/>')


# ---- Elowen Greenmantle (elf)
@icon('Grasping Roots')
def _():
    # The whole line held at once: the ground splits and the briars come up through it with
    # three of them already caught.
    held = (husk(15, 34, .62, '#6a6054') + husk(32, 29, .72, '#6a6054') + husk(49, 34, .62, '#6a6054'))
    roots = (poly('M11 52 C11 42 19 44 16 36', STL_ROOT, 2.8)
             + poly('M32 50 C28 40 37 40 33 27', STL_ROOT, 3.0)
             + poly('M53 52 C53 42 45 44 48 36', STL_ROOT, 2.8))
    wraps = (poly('M9 37 Q15 33 21 37', STL_GREEN, 2.2)
             + poly('M25 32 Q32 28 39 32', STL_GREEN, 2.4)
             + poly('M43 37 Q49 33 55 37', STL_GREEN, 2.2))
    thorns = ''.join(f'<path d="M{x} {y} l{dx} {dy} l2 1.6 Z" fill="#9ac46b" stroke-width="1"/>'
                     for x, y, dx, dy in ((15, 42, -4, -3), (34, 37, 4, -3), (49, 42, 4, -3)))
    return ('<path d="M4 50 Q32 44 60 50 L60 58 H4 Z" fill="#4a3a2e"/>'
            + '<path d="M14 49 L11 58 M32 47 L29 58 M48 49 L45 58" fill="none" stroke="#2f251c" stroke-width="1.6"/>'
            + held + roots + wraps + thorns)


@icon('Oaken Vigil')
def _():
    # The warband armoured in thorns, not healed: a closed ring of bark grown round all three
    # of them, thorns out, and the blow that came for them skidding off into one.
    ring = ('<circle cx="32" cy="35" r="19" fill="none" stroke="' + INK + '" stroke-width="9.6"/>'
            '<circle cx="32" cy="35" r="19" fill="none" stroke="url(#wood)" stroke-width="6"/>'
            + ''.join(f'<path d="M{32 + 19 * math.cos(math.radians(a)):.1f} {35 + 19 * math.sin(math.radians(a)):.1f} '
                      f'l{2.6 * math.cos(math.radians(a)):.1f} {2.6 * math.sin(math.radians(a)):.1f}" '
                      f'stroke="#5a3a1c" stroke-width="2" fill="none"/>' for a in range(15, 360, 30)))
    thorns = ''.join(g('<path d="M-3.2 0 L0 -7.5 L3.2 0 Z" fill="#9ac46b"/>',
                       round(32 + 22.4 * math.cos(math.radians(a)), 1),
                       round(35 + 22.4 * math.sin(math.radians(a)), 1), a + 90)
                     for a in range(0, 360, 45))
    blade = ('<path d="M0 0 L5 -14 L10.5 -11 L4.5 2 Z" fill="url(#steel)"/>'
             '<path d="M7 -14 L13.5 -10.5" stroke="url(#gold)" stroke-width="3"/>')
    return (thorns + ring
            + husk(24, 38, .46, '#6f7f5e') + husk(40, 38, .46, '#6f7f5e') + husk(32, 32, .5, '#8a9a74')
            + g(blade, 47, 22, 0, 1.0)
            + glow(burst(45.5, 23.5, 3, 8.5, 8, STL_SPARK), .5)
            + burst(45.5, 23.5, 2.6, 7, 8, STL_SPARK)
            + '<path d="M52 29 Q57 32 55 38" fill="none" stroke="#d8c8a8" stroke-width="2" opacity=".75"/>')


@icon('Deeproot')
def _():
    # It holds longer because it is holding onto something: the taproot is down past the soil
    # with its fingers closed over the stone, and it is not letting go.
    sprout = ('<path d="M32 25 V10" fill="none" stroke="#3f7a4f" stroke-width="3.6"/>'
              '<path d="M32 18 C25 18 20 13 19 7 C26 6 31 11 32 18 Z" fill="url(#leaf)"/>'
              '<path d="M32 22 C39 22 44 18 45 12 C38 11 33 15 32 22 Z" fill="url(#leaf)"/>')
    # A solid bar of soil read as a plank across the middle and rock()'s default clay read as a
    # crate: the soil is a crumbling layer now and the stone is stone-grey.
    return (sprout
            + '<path d="M4 23 Q32 19 60 23 L60 28 Q51 33 45 28 Q37 33 30 28 Q22 33 15 28 Q8 32 4 27 Z" fill="#52402f"/>'
            + '<circle cx="12" cy="35" r="1.4" fill="#6b5641" stroke="none"/>'
            + '<circle cx="54" cy="33" r="1.2" fill="#6b5641" stroke="none"/>'
            + g(rock('#7a8290'), 32, 44, 0, 1.45)
            + poly('M32 25 C34 34 30 41 33 53', STL_ROOT, 5.0)
            + poly('M32 32 C25 34 19 33 15 39', STL_ROOT, 2.8)
            + poly('M33 36 C41 38 46 35 51 41', STL_ROOT, 2.8)
            + poly('M33 51 C38 56 29 58 26 52', STL_ROOT, 2.4)
            + twinkle(51, 14, .7, STL_ACC))


# ================================================================ The Tideborn, third wave
# One faction, five bodies, and the icons have to keep them apart on sight. The rule the
# existing Tideborn set already set down, and which nothing in this block crosses:
#   Tharos   - teeth, trident, blood in the water
#   Grubble  - rime, ice-blue, biting back
#   Seraphine- the note, sound rings, the voice
#   Octavia  - ink, tentacles, suckers
#   Maren    - pearl, reef pink, water
TD_ACC = '#7fe3d8'      # the faction's pale aqua, from PAL['tide']
TD_DEEP = '#14485a'     # the deep-water fill Dirge of the Deep and Tide Pool already use
TD_ICE = '#bff3ff'      # Grubblefin's rime
TD_ICE_HI = '#eafaff'
TD_STEEL_ICE = '#dff4ff'
TD_RED = '#b8202e'      # the blood Blood in the Water leaves behind
TD_RED_HI = '#ff8a8a'
TD_INK = '#5a4a8a'      # Octavia's ink, mid tone
TD_INK_DK = '#2a1d40'
TD_PEARL = '#f2c6d8'    # Maren's reef pink
TD_HEX = '#c89eff'      # the house's "mend halved" purple (cf. Ancestors' Rebuke)
TD_BODY = '#6a6054'     # the faceless mark husk() is drawn in


def fin(fill='#53687a'):
    """A dorsal fin, origin at its base, swept back to the right. The silhouette is Blood in
    the Water's, scaled down: a rounded triangle reads as a tent, the swept tip reads as shark."""
    return f'<path d="M-11 7 Q-5 -15 11 -24 Q6 -9 11 7 Z" fill="{fill}"/>'


def shark(fill='#0d2a34', eye='#ff6a7a'):
    """A shark from the side, NOSE UP, origin at the body centre: the thing coming up from
    underneath. A silhouette on purpose - a face would make it a portrait, not a shadow.
    Body, dorsal, pectoral and tail are separate pieces so the ink outline draws the shape."""
    return (f'<path d="M0 -21 C6 -13 7 -4 6 4 C5 11 3 15 0 18 C-3 15 -5 11 -6 4 C-7 -4 -6 -13 0 -21 Z" fill="{fill}"/>'
            f'<path d="M4 -4 L13 6 L3 5 Z" fill="{fill}"/>'
            f'<path d="M-4 1 L-12 8 L-3 7 Z" fill="{fill}"/>'
            f'<path d="M0 12 L8 23 L0 17 L-8 23 Z" fill="{fill}"/>'
            f'<path d="M-4.6 -8 L-1.2 -6.6 M-4.2 -11 L-.8 -9.6" stroke="#9fb8c2" stroke-width="1" fill="none" opacity=".75"/>'
            f'<circle cx="-2.8" cy="-13" r="1.5" fill="{eye}" stroke="none"/>')


def tentacle(fill=TD_INK):
    """One of Octavia's arms: base at the origin, reaching out along +x, tapering to a hook.
    Tapered on purpose - a constant-width stroke reads as a strap, not an arm."""
    return (f'<path d="M0 -6 C12 -6 20 -2.4 27 4 C19 1.2 10 2.2 0 6 Z" fill="{fill}"/>'
            '<circle cx="7" cy="-1.6" r="1.3" fill="#e8dcff" stroke="none"/>'
            '<circle cx="13" cy=".4" r="1.1" fill="#e8dcff" stroke="none"/>'
            '<circle cx="18.5" cy="2.4" r="1" fill="#e8dcff" stroke="none"/>')


def throat(x, y, s=1, fill=TD_BODY):
    """A mark with the song being drawn out of it: husk(), clean, with the mana leaving just
    clear of the head. Marking the figure itself only ever defaces it - a patch on the chest
    reads as a pendant and a flare on the crown turns the whole thing into a tied sack."""
    return husk(x, y, s, fill) + g(drop('url(#mana)'), x, y - 14.5 * s, 0, .5 * s)


def down_arrow(x, y, h=11, color='#b07ae0', w=2.6):
    """The house's "less of it" arrow (Dirge of the Deep, Withering Curse)."""
    return (f'<path d="M{x} {y - h / 2} V{y + h / 2} M{x - 4.4} {y + h / 2 - 4.6} L{x} {y + h / 2 + 1} '
            f'L{x + 4.4} {y + h / 2 - 4.6}" fill="none" stroke="{color}" stroke-width="{w}"/>')


def hex_mark(x, y, r=7, fill='#2a1030', edge=TD_HEX):
    """A hex sigil with the bar through it: the game's mark for a mend that will not pay."""
    pts = ' '.join(f'{x + r * math.cos(math.radians(a)):.1f},{y + r * math.sin(math.radians(a)):.1f}'
                   for a in range(-90, 270, 60))
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            f'<path d="M{x - r * .55:.1f} {y + r * .55:.1f} L{x + r * .55:.1f} {y - r * .55:.1f}" '
            f'stroke="{edge}" stroke-width="1.8"/>')


# ---- Tharos Razorfin (shark-folk)
@icon('Chum the Water')
def _():
    # The whole line opened at once. The stain is drawn FLAT - no ink outline and no highlight
    # curves on it, because an outlined lobed blob with folds in it reads as a brain - and the
    # three fins cut the surface above it, with the waterline laid over their bases.
    # NOTHING SYMMETRICAL AND NOTHING HANGING OFF THE BOTTOM. A tidy red mass with three
    # tendrils under it reads as an animal with legs, every time; a plume has to be lopsided,
    # with loose clots drifting off it, and no two edges alike.
    plume = ('<path d="M11 39 C8 33 15 28 22 31 C27 26 37 28 39 34 C45 31 52 35 50 40 '
             'C52 46 43 50 37 46 C31 50 21 49 18 44 C12 45 10 42 11 39 Z" fill="#a81a26" stroke="none"/>')
    clots = ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#9a1420" stroke="none"'
                    f' transform="rotate({r} {x} {y})"/>'
                    for x, y, rx, ry, r in ((52, 47, 4.4, 3, 20), (15, 48, 3.4, 2.4, -25),
                                            (44, 26, 2.8, 2, 35), (25, 52, 2.4, 1.6, 10)))
    return (glow('<ellipse cx="31" cy="39" rx="26" ry="12" fill="#d8303c"/>', .55)
            + plume + clots
            # The far fin is mirrored so the two outer ones lean INTO the middle: three fins all
            # swept the same way read as a shoal going past, not as a ring closing.
            + g(fin('#5b7183'), 14, 25, 12, .58) + g(fin('#6b8496'), 31, 24, 0, .72)
            + g('<g transform="scale(-1 1)">' + fin('#5b7183') + '</g>', 50, 25, 12, .52)
            + f'<path d="M3 24 Q13 20 23 24 T43 24 T61 23" fill="none" stroke="{TD_ACC}" stroke-width="2.2" opacity=".85"/>'
            + '<path d="M3 15 H10 M4 19 H9 M54 15 H61 M55 19 H60" stroke="#b4f4ff" stroke-width="1.8" opacity=".55"/>')


@icon('Gutter')
def _():
    # Straight through the plate and it drinks on the way out: the middle prong is clear of the
    # far face, and the blood is tracking BACK down the shaft to the hand, not dripping off it.
    plate = ('<path d="M38 11 H50 Q53 11 53 15 V49 Q53 53 50 53 H38 Z" fill="url(#steel)"/>'
             '<path d="M41.5 11 V53" stroke="#5d6780" stroke-width="1.4" fill="none"/>'
             + ''.join(f'<circle cx="47" cy="{y}" r="1.4" fill="#5d6780" stroke="none"/>' for y in (16, 25, 39, 48)))
    return (plate
            + '<ellipse cx="45" cy="32" rx="6" ry="4.4" fill="#15121d" stroke="none"/>'
            + g(trident(), 28, 32, 90, 1.0)
            + glow(burst(41, 32, 3, 9, 9, '#ff6a7a'), .55)
            + burst(41, 32, 2.6, 7, 9, '#ff8a8a')
            # Back along the shaft, not dripping off it - and said with the arrow the Tideborn
            # already use for "pulled back" (Backwash, Riptide). Drops strung along the shaft
            # only ever read as a red sausage, however they are spaced.
            + f'<path d="M41 35 Q26 37 12 36" fill="none" stroke="{TD_RED_HI}" stroke-width="2" opacity=".85"/>'
            + '<path d="M34 45 H16 M16 45 L21 40 M16 45 L21 50" fill="none" stroke="#15121d" stroke-width="4.8"/>'
            + '<path d="M34 45 H16 M16 45 L21 40 M16 45 L21 50" fill="none" stroke="#e8545e" stroke-width="2.4"/>'
            + g(drop(), 36, 23, 0, .55))


@icon('Red Water')
def _():
    # Not a fresh cut: the mark is already tipping over and sinking, and the shadow underneath
    # is on its way up to finish it. Reddened water, bubbles going the other way.
    return (glow('<ellipse cx="32" cy="36" rx="25" ry="19" fill="#a81825"/>', .5)
            + f'<path d="M5 16 Q13 12 21 16 T37 16 T59 15" fill="none" stroke="{TD_ACC}" stroke-width="2" opacity=".6"/>'
            # Slumped and going down, NOT rolled over: past about 30 degrees husk() stops being
            # head-and-shoulders and becomes a brown lump. The sinking is said by the bubbles
            # going up past it and by the shadow coming the other way.
            + g(husk(0, 0, .8, TD_BODY), 21, 25, 24)
            + g(drop(), 13, 14, 0, .55) + '<path d="M15 20 Q13 18 13.5 16" fill="none" stroke="#e8545e" stroke-width="2"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{TD_ICE}" stroke-width="1.2" opacity=".7"/>'
                      for x, y, r in ((31, 15, 2.6), (37, 9, 1.8), (10, 33, 1.6)))
            + g(shark(), 38, 38, -20, .88))


# ---- Grubblefin (rime-plated brawler)
@icon('Bait the Hook')
def _():
    # Come and try. The bait is the thing on offer, the jaws are the thing on offer's bill -
    # drawn BEHIND the hook and already open, so the order of events reads left to right.
    # Clear water between the bait and the jaws: set close they fuse and the bait reads as a
    # tongue hanging out of the mouth.
    jaw = g(jaws('#5fb2dc'), 45, 42, -12, .7)
    bait = ('<path d="M20 35 C14 35 13 42 18 45 C24 48 31 45 30 39 C29 36 25 35 20 35 Z" fill="#c0505e"/>'
            '<path d="M19 38 Q23 39 26 42" fill="none" stroke="#f2a0a8" stroke-width="1.4"/>')
    hook = (poly('M21 12 V30 C21 41 32 41 32.5 30', '#cfe8f5', 3.0)
            + '<path d="M32.5 30.5 L27.5 25.5" fill="none" stroke="#cfe8f5" stroke-width="2.4"/>'
            + '<circle cx="21" cy="11" r="3.2" fill="none" stroke="#cfe8f5" stroke-width="2.2"/>')
    return (jaw + bait + hook
            + twinkle(14, 16, .8, TD_ICE_HI) + twinkle(53, 20, .6, TD_ICE_HI)
            + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{TD_ICE}" stroke-width="1.2" opacity=".7"/>'
                      for x, y, r in ((13, 45, 2.6), (18, 52, 1.8), (50, 15, 1.6))))


@icon('Icebreaker')
def _():
    # Four thin cuts, and plate is no answer to them: each sliver is edged like an icicle and
    # goes clean past both edges of the plate instead of stopping at it.
    plate = ('<path d="M11 18 H53 Q56 18 56 22 V42 Q56 46 53 46 H11 Q8 46 8 42 V22 Q8 18 11 18 Z" fill="url(#steel)"/>'
             '<path d="M8 32 H56" stroke="#8d97aa" stroke-width="1.2" fill="none"/>'
             + ''.join(f'<circle cx="{x}" cy="{y}" r="1.3" fill="#5d6780" stroke="none"/>'
                       for x, y in ((13, 22), (13, 42), (51, 22), (51, 42))))
    sliver = ('<path d="M-2 -23 L2.2 -21.5 L3.4 -8 L1.4 -3 L3.4 4 L1.2 10 L2.6 21.5 L-2.6 23 '
              'L-1.2 10 L-3.4 4 L-1.4 -3 L-3.4 -8 Z" fill="' + TD_STEEL_ICE + '"/>'
              '<path d="M-1 -19 L1.4 -8 L-.4 -3 L1.4 4 L-.4 10 L.6 19" fill="none" stroke="#9fd8ee" stroke-width="1"/>')
    return (plate
            + ''.join(g(sliver, x, 32, 20, 1.0) for x in (15, 26, 37, 48))
            + twinkle(11, 11, .7, TD_ICE_HI) + twinkle(54, 53, .6, TD_ICE_HI))


@icon('Gnashing')
def _():
    # Land a blow and the blow is what he bites. The sword is already in the mouth and chipping,
    # and the cold comes off the bite - not off him.
    chip = '<path d="M0 0 L6.4 2.4 L1.6 5.6 Z" fill="#dfe6f2"/>'
    return (g(sword('url(#steel)'), 46, 20, 212, .8)
            + g(jaws('#5fb2dc'), 29, 38, -8, 1.12)
            + glow(burst(35, 32, 3.4, 10, 9, TD_ICE_HI), .5)
            + burst(35, 32, 2.8, 7.5, 9, '#ffffff')
            + g(chip, 46, 36, 25, .95) + g(chip, 19, 22, -150, .8)
            + twinkle(13, 16, .8, TD_ICE_HI) + twinkle(50, 51, .6, TD_ICE_HI))


# ---- Seraphine Wavecaller (siren)
@icon('Abyssal Note')
def _():
    # ONE note, and it is the heaviest thing she has: a single thick ring driven down into the
    # dark, with what it landed on already under the water and out of air.
    return ('<path d="M6 32 Q32 26 58 32 V56 H6 Z" fill="#0b2b36"/>'
            + f'<path d="M6 32 Q32 26 58 32" fill="none" stroke="{TD_ACC}" stroke-width="1.6" opacity=".7"/>'
            + g(note('#ffffff'), 32, 19, 0, 1.05)
            # Three thinning rings, not one fat one: a single heavy white arc under the note
            # stops being a sound wave and becomes a bowl with the note sitting in it.
            + arc_lines(32, 22, 15, 3, 140, TD_ICE_HI, 90, 3.0, 5)
            + g(husk(0, 0, .56, '#417080'), 32, 50, 10)
            + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{TD_ICE}" stroke-width="1.2" opacity=".65"/>'
                      for x, y, r in ((19, 48, 2.4), (46, 46, 2), (14, 54, 1.6))))


@icon('Hollow the Throat')
def _():
    # The siren's actual legend: she takes the voice, and the voice is the mana. Three throats
    # paying up at once, her sigil holding what comes out of them.
    sigil = (glow('<circle cx="32" cy="17" r="11" fill="#6fb0ff"/>', .5)
             + f'<circle cx="32" cy="17" r="9.6" fill="#123a52" stroke="{TD_PEARL}" stroke-width="2.4"/>'
             + g(note('#ffffff'), 31, 17, 0, .6))
    marks = (throat(13, 47, .68) + throat(32, 50, .68) + throat(51, 47, .68))
    streams = (poly('M14 35 Q17 30 25 24', 'url(#mana)', 2.6)
               + poly('M32 38 Q33 33 32 28', 'url(#mana)', 2.8)
               + poly('M50 35 Q47 30 39 24', 'url(#mana)', 2.6))
    motes = (g(drop('url(#mana)'), 18, 30, 30, .5) + g(drop('url(#mana)'), 46, 30, -30, .5))
    return marks + streams + motes + sigil


@icon('Hush the Deep')
def _():
    # A voice she has already taken cannot ward itself. The mouth is sealed shut and the seal
    # is splitting - the crack is the brightest thing in the tile, because the crack is the skill.
    # Two false starts worth recording: a teal band over the lips buried them (dark on dark,
    # with the ties reading as barrel staves), and a thin mouth under big stitches read as a
    # row of X's. The mouth has to be LARGE and bright, the stitching small and only on one
    # side - and the break comes through the other side, which is the whole point of the skill.
    # Cupid's bow on the top lip and a fuller bottom one: a plain symmetrical almond with a
    # line through it is an eye, not a mouth.
    lips = ('<path d="M9 32 Q17 20 24 24 Q28 17 32 23 Q36 17 40 24 Q47 20 55 32 Z" fill="#f2c6d8"/>'
            '<path d="M9 32 Q21 50 32 50 Q43 50 55 32 Z" fill="#c9849f"/>'
            '<path d="M9 32 H55" stroke="#6e3f52" stroke-width="2.4" fill="none"/>')
    stitches = ''.join(f'<path d="M{x - 3} 27 L{x + 3} 37 M{x + 3} 27 L{x - 3} 37" fill="none" '
                       f'stroke="#8fd0e6" stroke-width="2"/>' for x in (17, 26))
    return (glow('<ellipse cx="32" cy="32" rx="24" ry="14" fill="#2a7f8f"/>', .4)
            + lips + stitches
            + poly('M41 12 L36 22 L44 31 L37 41 L42 52', TD_ICE_HI, 2.8)
            + glow(burst(40, 31, 3, 9, 9, '#ffffff'), .5)
            + burst(40, 31, 2.4, 6.5, 9, '#ffffff')
            + f'<path d="M47 24 L52 21 M32 43 L27 47" fill="none" stroke="{TD_ICE}" stroke-width="1.8" opacity=".75"/>')


# ---- Octavia Inkveil (octopus-folk)
@icon('Eight Arms')
def _():
    # Four arms in at once from four sides, four separate little hits. The middle is left to
    # the ink on purpose: one burst in the centre would read as a single heavy cast.
    arms = (g(tentacle(TD_INK), 7, 10, 42) + g(tentacle(TD_INK_DK), 57, 10, 138)
            + g(tentacle(TD_INK_DK), 7, 54, -42) + g(tentacle(TD_INK), 57, 54, -138))
    hits = ''.join(burst(x, y, 2, 4.8, 8, '#fff6dc') for x, y in ((26, 26), (38, 26), (26, 38), (38, 38)))
    return (glow('<circle cx="32" cy="32" r="10" fill="' + TD_INK_DK + '"/>', .6)
            + arms + hits)


@icon('Abyssal Ink')
def _():
    # Both halves of what she is for: the ink is over its face so it cannot see, and the arms
    # have gone out of it so what it swings is worth less.
    # The ink has to stop ABOVE the chin and the arms have to hang clear of the body, or the
    # silhouette is a dome with a cloud on it - a tree, not somebody who has been blinded.
    head = ('<path d="M25 30 Q25 16 32 16 Q39 16 39 30 Q39 37 36 40 L28 40 Q25 37 25 30 Z" fill="' + TD_BODY + '"/>'
            '<path d="M28 36 Q32 38 36 36" fill="none" stroke="#443e36" stroke-width="2"/>')
    torso = ('<path d="M21 44 Q32 40 43 44 L42 48 H22 Z" fill="#584f46"/>'
             '<path d="M24 48 H40 L41 56 H23 Z" fill="#584f46"/>')
    # Hanging, not curved back in: a pair of arms that bow out and round reads as handles.
    arms = (poly('M22 46 Q18 50 19 56', TD_BODY, 3.4) + poly('M42 46 Q46 50 45 56', TD_BODY, 3.4))
    splat = ('<path d="M11 22 Q18 13 26 19 Q32 10 39 16 Q48 10 53 21 Q49 30 40 27 Q33 34 26 28 '
             'Q18 33 11 22 Z" fill="url(#ink)"/>')
    drips = ('<path d="M18 28 Q17 33 19 37 M31 31 Q32 36 30 40 M45 27 Q47 32 45 35" fill="none" '
             'stroke="' + TD_INK_DK + '" stroke-width="2.6"/>')
    return (arms + head + torso
            + glow('<ellipse cx="32" cy="22" rx="22" ry="12" fill="' + TD_INK + '"/>', .5)
            + splat + drips
            + down_arrow(55, 44, 11))


@icon('Clouded Eyes')
def _():
    # It cannot see what is hitting it: both eyes still open behind the ink, and the blow coming
    # in low on the other side of the veil where they are not looking.
    eyes = ''.join(f'<ellipse cx="{x}" cy="28" rx="7.6" ry="5.6" fill="#fff6dc"/>'
                   f'<circle cx="{x}" cy="28" r="2.8" fill="#15121d" stroke="none"/>'
                   f'<path d="M{x - 7} 24 Q{x} 20.5 {x + 7} 24" fill="none" stroke="#9a86a8" stroke-width="1.4"/>'
                   for x in (21, 43))
    veil = ('<path d="M5 18 Q32 12 59 18 L59 31 Q52 38 45 34 Q38 30 32 35 Q25 40 18 35 Q11 30 5 36 Z" '
            'fill="url(#ink)" opacity=".76"/>')
    blade = ('<path d="M0 -12 L3 -3 L2.6 7 L-2.6 7 L-3 -3 Z" fill="url(#steel)"/>'
             '<rect x="-5.6" y="6.5" width="11.2" height="3" rx="1.2" fill="#9aa3b5"/>')
    return (eyes + veil
            + g(blade, 48, 54, 208, 1.0)
            + glow(burst(40, 46, 3.2, 9.5, 9, '#ffffff'), .5)
            + burst(40, 46, 2.6, 7, 9, '#ffffff')
            + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{TD_INK_DK}" stroke="none" opacity=".8"/>'
                      for x, y, r in ((11, 44, 2.4), (20, 49, 1.8))))


# ---- Maren Pearlheart (reef priestess)
@icon('Salt the Reef')
def _():
    # The healer's own weapon turned round. NO CROSS ANYWHERE IN THIS TILE: salt going down
    # over the coral, the coral curling up grey, and her glow broken into a guttering ring
    # with the game's "mend halved" hex sitting in it.
    # Antler coral, drawn as STRAIGHT forked segments - curved strokes at several angles come
    # out as a tangle of worms every time. The living stock is reef pink, the tips are bleached
    # bone-grey and drooping, which is what dying coral actually looks like and is the one cue
    # that still works at 32px.
    stock = (poly('M29 56 V44', '#b07a95', 5.0)
             + poly('M29 46 L19 38', '#b07a95', 4.0)
             + poly('M29 46 L39 38', '#b07a95', 4.0)
             + poly('M29 45 V35', '#b07a95', 3.6))
    # Bare tapered ends, no round caps: a blob on the end of every limb reads as a knuckle,
    # and five limbs with knuckles on them read as a little man.
    tips = (poly('M19 38 L16 44', '#bdb4ba', 3.2)
            + poly('M39 38 L42 44', '#bdb4ba', 3.2)
            + poly('M29 36 L27 30', '#bdb4ba', 3.0))
    # A second, smaller head of coral: one stand on its own reads as a figure with its arms
    # out, two read as a reef.
    stock += poly('M13 56 V48', '#a06d87', 3.6) + poly('M13 50 L8 44', '#a06d87', 2.8)
    tips += poly('M8 44 L6 49', '#b3aab0', 2.4)
    salt = ''.join(g('<path d="M0 -4.4 L3.4 0 L0 4.4 L-3.4 0 Z" fill="#eef7fb"/>', x, y, r, s)
                   for x, y, r, s in ((14, 14, 14, 1.0), (27, 10, -18, .88), (41, 14, 24, .96),
                                      (51, 22, -12, .8), (20, 25, 32, .7), (36, 24, -26, .62)))
    grains = ''.join(f'<circle cx="{x}" cy="{y}" r="1.1" fill="#eef7fb" stroke="none"/>'
                     for x, y in ((22, 18), (33, 17), (46, 20), (10, 24), (54, 14), (30, 28)))
    # The glow going out, drawn as a glow and not as a ring: a dashed halo round the coral
    # only put more pink stubs beside the limbs and made the whole thing read as a scarecrow.
    return (glow('<ellipse cx="29" cy="47" rx="15" ry="9" fill="' + TD_PEARL + '"/>', .3)
            + g(twinkle(0, 0, .7, TD_PEARL), 12, 42, 0, 1, ' opacity=".45"')
            + g(twinkle(0, 0, .5, TD_PEARL), 46, 32, 0, 1, ' opacity=".25"')
            + stock + tips + salt + grains
            + hex_mark(48, 48, 7.4))


@icon('Undertow Grasp')
def _():
    # The whole line taken off its feet and set down slower. One current hooking back on itself,
    # three marks going over with it, each tipped further than the one before.
    # Three of them, stood well apart, each tipped further than the one before it - shoulder to
    # shoulder they merge into one caterpillar, and past about 45 degrees a husk stops being a
    # body. The current runs BEHIND them at waist height; carried high it reads as a rainbow.
    return (f'<path d="M6 50 Q19 45 32 50 T58 49 V56 H6 Z" fill="{TD_DEEP}"/>'
            + poly('M58 24 Q42 18 31 25 Q22 31 23 39', 'url(#water)', 3.8)
            + poly('M53 29 Q43 25 36 29', TD_ACC, 1.8)
            + '<path d="M23 40 L10 35 L13 49 Z" fill="#b4f4ff"/>'
            + g(husk(0, 0, .62, TD_BODY), 50, 41, -22)
            + g(husk(0, 0, .62, TD_BODY), 36, 43, -36)
            + g(husk(0, 0, .62, TD_BODY), 22, 45, -50)
            # Foam closing over their feet, drawn in front: it is the water that has them.
            + f'<path d="M8 50 Q16 45 24 50 T40 50 T58 49" fill="none" stroke="#b4f4ff" stroke-width="2.4" opacity=".9"/>'
            + g(drop('url(#water)'), 54, 13, 0, .55)
            + g(drop('url(#water)'), 44, 9, 0, .4))


@icon('Spring Tide')
def _():
    # Everything at once, right across the field: one crest carried the full width of the tile,
    # foam running off both edges, with a pearl riding in the trough so it stays hers.
    # Passive, so the tile is a ROUND medallion: the sea has to be a shape that stays inside
    # the rim. A full-width rectangle of water hangs out of the circle at both bottom corners.
    return (f'<path d="M2 44 Q32 38 62 44 Q51 58 32 58 Q13 58 2 44 Z" fill="{TD_DEEP}"/>'
            + '<path d="M4 47 C5 26 17 13 34 14 C49 15 59 26 54 36 C51 42 42 42 41 35 '
              'C40 29 34 28 31 32 C26 38 29 45 36 49 Z" fill="url(#water)"/>'
            + '<path d="M11 43 C12 27 21 18 33 18 C44 18 52 25 52 32" fill="none" stroke="#ffffff" '
              'stroke-width="1.8" opacity=".85"/>'
            + f'<path d="M2 50 Q13 45 24 50 T46 49 T62 50" fill="none" stroke="{TD_ICE}" stroke-width="2.2" opacity=".8"/>'
            + '<circle cx="46" cy="45" r="4" fill="url(#pearl)"/>'
            + twinkle(20, 10, .72, TD_ICE_HI) + twinkle(48, 11, .6, TD_ICE_HI)
            + f'<circle cx="11" cy="16" r="2" fill="none" stroke="{TD_ICE}" stroke-width="1.2" opacity=".7"/>')


# ================================================================ The Crimson Court, third wave
# One faction, two bloodlines, and the icons have to keep them apart on sight. The split the
# existing Court set already set down, and which nothing in this block crosses:
#   Vesper   - blood, the rapier, pale dark elegance
#   Malgrath - hellfire, horns, chains, scorched ground
#   Seraxa   - wings, pink blades, speed
#   Gorehound- teeth, jaws, paws, feral orange
#   Morwenna - the hex purple laid over the blood red
# The trap this faction sets is that nearly everything in it is red on a dark wine ground, so a
# tile can collapse into one indistinct red smear. The rule used throughout below: separate by
# VALUE, not hue - bone cream, steel, gold and the grey-brown of a faceless mark carry the
# silhouettes, and the reds are only ever the thing being done to them.
CR_ACC = '#e0455a'       # PAL['crimson'] accent
CR_RED = '#b8202e'
CR_RED_DK = '#8e1420'
CR_RED_HI = '#ff6a7a'
CR_BONE = '#fbf4e2'
CR_BONE_D = '#d6c6a6'
CR_BODY = '#5f574a'      # the faceless mark: a cool grey-brown, well off the wine ground
CR_BODY_D = '#4a4338'
CR_BODY_HI = '#736a5b'
CR_PLUM = '#3d1f4a'      # Seraxa's wing, from Wing Carve
CR_PLUM_D = '#2a1430'
CR_PINK = '#e05a9a'
CR_PINK_HI = '#ff9ad0'
CR_HEX = '#d07aff'       # Morwenna's hex, from Blight Hex
CR_HEX_D = '#2a0f30'
CR_HOUND = '#8a3a3a'     # the Gorehound's lip, from Tear Apart
CR_EMBER = '#ff7a2f'
CR_GOLD = '#ffd166'
CR_FLESH = '#c8a096'
CR_LIP = '#e8bac6'
CR_LIP_D = '#bd7e90'


def cr_mark(x, y, s=1, fill=CR_BODY, lean=0, stride=0):
    """A faceless mark WITH LEGS - husk() is head and shoulders only, and half this wave needs
    somebody standing in a line or caught mid-step. Head clear of the shoulders, arms hanging
    and tapered, legs as two separate strokes: a single blocky trunk reads as a bollard.
    Spans roughly 20 x 36 at s=1, so s=.55 puts three of them across a tile with air between."""
    legs = (poly(f'M-3 2 L{-3.5 - stride * .45:.1f} 14', fill, 3.0)
            + poly(f'M3 2 Q{3 + stride * .6:.1f} 8 {3 + stride:.1f} 13', fill, 3.0))
    arms = poly('M-6.5 -10 Q-10 -4.5 -9 3', fill, 2.6) + poly('M6.5 -10 Q10 -4.5 9 3', fill, 2.6)
    body = (f'<circle cx="0" cy="-17" r="5" fill="{fill}"/>'
            f'<path d="M-7 -12 Q0 -14.5 7 -12 L5 2 H-5 Z" fill="{fill}"/>')
    return g(arms + legs + body, x, y, lean, s)


def cr_fallen(x, y, s=1, fill=CR_BODY):
    """A body that is already down, drawn LYING: head out clear at one end, one arm flung and
    one leg trailing. A rotated husk() past about 30 degrees stops being a body and becomes a
    brown lump (the Tideborn wave learned this the hard way), so the prone pose is drawn."""
    return g(f'<circle cx="-15" cy="-3" r="5.6" fill="{fill}"/>'
             f'<path d="M-11 -7 Q-1 -9.5 9 -5.5 L14 3 H-10 Z" fill="{fill}"/>'
             + poly('M-4 -8 Q2 -14 10 -13', fill, 3.0)
             + poly('M12 -1 Q18 2 21 -4', fill, 3.0), x, y, 0, s)


def cr_crescent(x, y, rot=0, s=1, fill='#fff0f6', edge=CR_PINK):
    """One wind-blade: a crescent with two sharp points. Thin on purpose - a fat crescent reads
    as a moon, and six moons in a tile read as nothing at all."""
    return g(f'<path d="M-13 3 Q0 -10 13 3 Q0 -3.5 -13 3 Z" fill="{fill}"/>'
             f'<path d="M-10 1.6 Q0 -6.5 10 1.6" fill="none" stroke="{edge}" stroke-width="1.2" opacity=".8"/>',
             x, y, rot, s)


def cr_bite(x, y, rot=0, s=1, color=CR_BONE):
    """One bite mark: two OPPOSED rows of teeth with a clear gap between them, drawn as two
    zigzag strips (the same construction jaws() uses for its teeth). Punctures scattered
    individually round an ellipse came out as broken glass every single time, and three of
    those on one spot came out as a smashed window."""
    up = (f'<path d="M-12 -5 Q0 -13 12 -5 L9.5 .5 L7 -4.5 L4.5 1 L2 -5 L-.5 1 L-3 -5 L-5.5 1 '
          f'L-8 -4.5 L-10.5 .5 Z" fill="{color}" stroke-width="1.2"/>')
    lo = (f'<path d="M-11 6 Q0 13 11 6 L8.5 .5 L6 5.5 L3.5 0 L1 6 L-1.5 0 L-4 5.5 L-6.5 0 '
          f'L-9 5 Z" fill="{color}" stroke-width="1.2"/>')
    return g(up + lo, x, y, rot, s)


def cr_sigil(fill=CR_GOLD, core='#fff1a0'):
    """Malgrath's brand: a horned downward triangle with the bar through it. Origin at centre,
    spans about 28 x 26."""
    return (f'<path d="M-10 -8 H10 L0 11 Z" fill="none" stroke="{fill}" stroke-width="3"/>'
            f'<path d="M-6.5 -1 H6.5" stroke="{fill}" stroke-width="2.6" fill="none"/>'
            f'<path d="M-10 -8 L-14 -14 M10 -8 L14 -14" stroke="{fill}" stroke-width="2.6" fill="none"/>'
            f'<circle cx="0" cy="3" r="2.2" fill="{core}" stroke="none"/>')


def cr_horned(x, y, s=1, fill='url(#demon)', horn='#2a1a1f'):
    """A horned head, the Court's demon read (cf. Demonic Roar, Infernal Wrath)."""
    return g(f'<path d="M-8 -11 C-15 -15 -17 -22 -13 -28 C-12 -22 -8 -19 -4 -15 Z" fill="{horn}"/>'
             f'<path d="M8 -11 C15 -15 17 -22 13 -28 C12 -22 8 -19 4 -15 Z" fill="{horn}"/>'
             f'<path d="M-10 -2 C-10 -11 -5 -15 0 -15 C5 -15 10 -11 10 -2 C10 3 7 5 6 6 L6 11 H-6 V6 C-7 5 -10 3 -10 -2 Z" fill="{fill}"/>'
             f'<path d="M-6.5 -4.5 L-2 -3 M6.5 -4.5 L2 -3" stroke-width="1.4"/>'
             f'<circle cx="-4.2" cy="-2" r="2" fill="{CR_GOLD}" stroke="none"/>'
             f'<circle cx="4.2" cy="-2" r="2" fill="{CR_GOLD}" stroke="none"/>', x, y, s=s)


def cr_droop(x, y, rot=0, s=1):
    """A blade hanging point-down out of a hand: the Court's "swings for less" cue, small enough
    to put one in each of three marks' fists."""
    return g('<path d="M0 0 L2.4 4 L1.9 18 L-1.9 18 L-2.4 4 Z" fill="url(#steel)"/>'
             '<rect x="-5.4" y="-2.4" width="10.8" height="3.2" rx="1.4" fill="#8d97aa"/>', x, y, rot, s)


def cr_plate(x, y, s=1, pits=True):
    """A small breastplate for a mark to be wearing, so a line skill can show armour coming
    apart. Shaped, not a rectangle: shoulders, a waist and a centre seam."""
    out = (f'<path d="M-7 -8 Q0 -11 7 -8 L6 6 Q3 9.5 0 10 Q-3 9.5 -6 6 Z" fill="url(#iron)"/>'
           f'<path d="M-5.6 -6 Q0 -8.4 5.6 -6" fill="none" stroke="#b6c0d0" stroke-width="1.2"/>'
           f'<path d="M0 -8 V9" fill="none" stroke="#5d6780" stroke-width="1"/>')
    if pits:
        out += ''.join(f'<circle cx="{cx}" cy="{cy}" r="1.4" fill="#2a1016" stroke="none"/>'
                       for cx, cy in ((-3.2, -3), (2.6, 0), (-1.4, 4)))
    return g(out, x, y, 0, s)


# ---- Vesper Nightshade (vampire lord)
@icon('Scarlet Veil')
def _():
    # Both halves of what it does: one sheet of it over the whole line, and every thread of it
    # running back out of them to one point off the left edge, where he is.
    # The curtain is drawn FLAT - no ink outline, no highlight curves - because an outlined
    # lobed sheet with folds in it reads as an organ. The hem is ragged and uneven; a scalloped
    # hem of equal lobes reads as bunting. The marks stand clear below it with daylight between
    # their heads and the hem, or the whole top half fuses into one red mass.
    curtain = ('<path d="M3 5 H61 V22 Q56 31 51 24 Q46 17 40 26 Q34 33 29 24 Q24 16 18 26 '
               'Q12 33 8 25 Q6 21 3 23 Z" fill="#a81a26" stroke="none"/>')
    folds = ('<path d="M12 7 V24 M20 7 V25 M29 7 V23 M38 7 V25 M46 7 V23 M54 7 V24" fill="none" '
             'stroke="#78101c" stroke-width="1.6" opacity=".75"/>')
    marks = cr_mark(26, 48, .58) + cr_mark(40, 50, .62) + cr_mark(53, 47, .54)
    # Thin, bright, and all three ending in the SAME place: three red curves that merely wander
    # look like spilt blood, three that converge look like a draw.
    threads = (poly('M24 42 Q17 40 13 36', '#ff9aa4', 2.0)
               + poly('M37 43 Q25 42 14 37', '#ff9aa4', 2.0)
               + poly('M51 41 Q31 46 15 38', '#ff9aa4', 2.0))
    hits = ''.join(burst(x, y, 1.3, 4, 8, CR_RED_HI, extra=' stroke-width="1"')
                   for x, y in ((26, 42), (40, 43), (53, 41)))
    return (glow('<rect x="4" y="6" width="56" height="20" fill="#d8303c"/>', .45)
            + curtain + folds + threads + hits + marks
            + glow(f'<circle cx="11" cy="33" r="7" fill="{CR_RED_HI}"/>', .7)
            + g(drop(), 11, 33, 0, 1.15)
            + f'<path d="M21 30 L15 34 L21 38" fill="none" stroke="{CR_BONE}" stroke-width="2.2"/>')


@icon('Gaze of the Count')
def _():
    # Held by a look and nothing else: no weapon anywhere in the tile. The eyes are drawn with
    # a cream sclera and a red iris - two glowing red lozenges on a wine ground are just two
    # red lozenges, it is the almond lid and the pale white that make them eyes.
    eye = (f'<path d="M-11 0 Q0 -8.5 11 0 Q0 8.5 -11 0 Z" fill="#f6efdc"/>'
           f'<circle cx="0" cy="0" r="4.6" fill="#c0303f"/>'
           f'<circle cx="0" cy="0" r="1.9" fill="#15121d" stroke="none"/>'
           f'<path d="M-11 0 Q0 -8.5 11 0" fill="none" stroke="#3a1018" stroke-width="1.6"/>')
    return (glow('<ellipse cx="19" cy="18" rx="12" ry="8" fill="#ff3a4a"/>'
                 '<ellipse cx="45" cy="18" rx="12" ry="8" fill="#ff3a4a"/>', .75)
            + g(eye, 19, 18, -7, .96) + g(eye, 45, 18, 7, .96)
            # Two lines of sight landing on the ONE mark, so the skill cannot be read as an aura
            + f'<path d="M21 26 Q27 33 31 38 M43 26 Q37 33 33 38" fill="none" stroke="{CR_ACC}" '
              f'stroke-width="1.6" opacity=".7"/>'
            # Caught mid-stride, trailing foot still off the floor, and pinned there
            + cr_mark(32, 45, .74, CR_BODY, 0, 8)
            + f'<path d="M13 44 H19 M45 44 H51" fill="none" stroke="{CR_ACC}" stroke-width="2.6"/>'
            + f'<path d="M13 40 V48 M51 40 V48" fill="none" stroke="{CR_ACC}" stroke-width="2"/>'
            + '<path d="M36 57 Q40 55 44 57" fill="none" stroke="#6b5f52" stroke-width="1.6" opacity=".7"/>'
            + twinkle(22, 32, .7, CR_GOLD) + twinkle(43, 31, .6, CR_GOLD))


@icon('Taste for It')
def _():
    # The smell of it is the trigger, so the drop is still in the air and the mouth is already
    # open under it. Two things learned the hard way here: a red drop with a red GLOW behind it
    # stops being a drop and becomes a flame, so the drop gets a white highlight and no halo;
    # and two symmetrical wisps rising above a mouth read as horns, so the scenting is said
    # with flat squiggles either side of the drop instead.
    gape = '<path d="M11 32 Q32 19 53 32 Q32 51 11 32 Z" fill="#2a0a12"/>'
    upper = ('<path d="M9 32 Q18 17 26 23 Q29 16 32 22 Q35 16 38 23 Q46 17 55 32 Q32 22 9 32 Z" '
             f'fill="{CR_LIP}"/>')
    lower = f'<path d="M11 33 Q32 55 53 33 Q32 42 11 33 Z" fill="{CR_LIP_D}"/>'
    fangs = ''.join(f'<path d="M{x - 3.2} 28 L{x + 3.2} 28 L{x + .6} 44 Z" fill="{CR_BONE}"/>'
                    for x in (23, 41))
    tongue = '<path d="M24 40 Q32 48 40 40 Q32 44 24 40 Z" fill="#9a1420" stroke="none"/>'
    return (glow(f'<ellipse cx="32" cy="34" rx="22" ry="12" fill="{CR_RED_DK}"/>', .4)
            + gape + tongue + upper + lower + fangs
            + f'<path d="M32 4 V8" fill="none" stroke="{CR_RED_HI}" stroke-width="2" opacity=".8"/>'
            + g(drop(), 32, 14, 0, 1.05)
            + '<ellipse cx="30.2" cy="14" rx="1.4" ry="2.2" fill="#ffd9d9" stroke="none"/>'
            + f'<path d="M9 15 Q13 11 17 15 Q21 19 25 15 M55 15 Q51 11 47 15 Q43 19 39 15" '
              f'fill="none" stroke="{CR_ACC}" stroke-width="1.8" opacity=".55"/>')


# ---- Malgrath the Unbound (demon brute)
@icon('Brand')
def _():
    # ONE of them, seared. The tile is a single figure filling it, so it can never be mistaken
    # for a line skill: no second mark anywhere, and the sigil is dead centre on its chest.
    # The plate is what says "ignores armor" - it is scorched through round the sigil and three
    # flakes of it have curled off, which is a thing only heat does. An earlier pass put a tidy
    # orange ellipse round the brand and the whole tile read as a speaker grille; the scorch is
    # now an irregular patch with no two edges alike.
    mark = husk(32, 28, 1.5, CR_BODY_D)
    plate = ('<path d="M16 32 Q32 27 48 32 L46 50 Q40 57 32 58 Q24 57 18 50 Z" fill="url(#steel)"/>'
             '<path d="M20 35 Q32 31 44 35" fill="none" stroke="#8d97aa" stroke-width="1.4"/>'
             + ''.join(f'<circle cx="{x}" cy="37" r="1.3" fill="#5d6780" stroke="none"/>'
                       for x in (21, 43)))
    scorch = ('<path d="M18 42 C19 34 27 30 34 33 C42 29 49 36 47 44 C48 52 38 57 32 53 '
              'C24 56 17 50 18 42 Z" fill="#1d0c05" stroke="none"/>'
              '<path d="M18 42 C19 34 27 30 34 33 C42 29 49 36 47 44 C48 52 38 57 32 53 '
              'C24 56 17 50 18 42 Z" fill="none" stroke="#a84a18" stroke-width="2"/>')
    flakes = ('<path d="M17 31 Q10 27 12 20 Q16 27 22 29 Z" fill="#c9d2e0"/>'
              '<path d="M47 31 Q54 28 53 21 Q48 28 42 29 Z" fill="#aeb8c8"/>'
              '<path d="M25 57 Q22 61 16 60 Q22 57 24 53 Z" fill="#c9d2e0"/>')
    return (mark + plate + flakes + scorch
            + glow(g(cr_sigil('#ff6a1a'), 32, 43, 0, .92), .85)
            + g(cr_sigil(CR_GOLD, '#ffffff'), 32, 43, 0, .76)
            + g(flame(), 51, 18, 22, .44) + g(flame(), 12, 16, -20, .38)
            + twinkle(54, 42, .7, CR_GOLD) + twinkle(10, 42, .6, CR_EMBER))


@icon('Hellmouth')
def _():
    # The ground itself, right across the width, and it stays open. The crust is a lit EARTH
    # brown so the fissure can be near-black inside it: crust and crack both drawn dark made
    # one coal heap with a campfire on it. Five flames of five different heights - a row of
    # matching flames reads as a fence.
    crust = ('<path d="M2 45 Q11 42 19 46 Q27 50 35 45 Q44 41 52 46 Q57 49 62 45 V60 H2 Z" '
             'fill="#44210f"/>'
             '<path d="M2 45 Q11 42 19 46 Q27 50 35 45 Q44 41 52 46 Q57 49 62 45" fill="none" '
             'stroke="#6b3418" stroke-width="1.6"/>')
    fissure = ('<path d="M5 48 L14 44 L22 49 L31 43 L40 48 L49 43 L59 48 L51 55 L41 50 L32 56 '
               'L22 51 L13 55 Z" fill="#0a0404" stroke="none"/>'
               '<path d="M5 48 L14 44 L22 49 L31 43 L40 48 L49 43 L59 48" fill="none" '
               'stroke="#ffae4d" stroke-width="2.2"/>')
    cracks = ('<path d="M10 57 L14 53 M27 58 L29 54 M45 57 L43 53 M55 56 L53 52" fill="none" '
              'stroke="#ff7a2f" stroke-width="1.8" opacity=".9"/>')
    fires = (g(flame(), 32, 31, 0, .98) + g(flame(), 19, 35, -12, .74)
             + g(flame(), 45, 34, 11, .8) + g(flame(), 10, 39, -20, .5)
             + g(flame(), 55, 39, 18, .54))
    return (glow('<ellipse cx="32" cy="40" rx="28" ry="16" fill="#ff5a1a"/>', .7)
            + fires + crust + fissure + cracks
            + twinkle(13, 14, .8, CR_GOLD) + twinkle(50, 12, .65, CR_EMBER)
            + f'<circle cx="24" cy="16" r="1.6" fill="{CR_EMBER}" stroke="none" opacity=".85"/>'
            + f'<circle cx="41" cy="19" r="1.3" fill="{CR_GOLD}" stroke="none" opacity=".85"/>')


@icon('Hell Answers')
def _():
    # Hit him and all of them pay. The order of events has to be legible: the blow comes in on
    # ONE side, the burst is where it lands, and the fire goes OUT from him to three marks on
    # the other three sides. Streaks with a flame at the far end, not flames on their own -
    # loose flames in a ring read as a campfire. The marks are cr_mark and not husk: at this
    # size a husk is a headstone, and three headstones round a demon is a graveyard.
    marks = (cr_mark(14, 46, .48) + cr_mark(49, 47, .48) + cr_mark(50, 17, .44))
    streaks = (poly('M26 40 Q20 43 16 43', CR_EMBER, 2.4)
               + poly('M38 40 Q44 43 48 44', CR_EMBER, 2.4)
               + poly('M39 27 Q46 21 50 19', CR_EMBER, 2.4))
    return (glow(f'<circle cx="32" cy="33" r="15" fill="{CR_EMBER}"/>', .5)
            + streaks + marks
            + g(flame(), 14, 40, -8, .38) + g(flame(), 49, 41, 8, .38) + g(flame(), 51, 11, 14, .34)
            + cr_horned(32, 36, .92)
            + g(mace(), 14, 15, 140, .72)
            + glow(burst(24, 25, 3, 9, 9, '#ffffff'), .6)
            + burst(24, 25, 2.4, 6.5, 9, '#ffffff'))


# ---- Seraxa Thornwing (winged blade dancer)
@icon('Stoop')
def _():
    # From the sky, and the tile has to say sky: the diver is at the TOP with clear air under
    # it, the mark is on a ground line at the very bottom, and the only thing between them is
    # the dive. Wings swept UP and back and held close - wings spread level read as a glide,
    # and a glide is not a stoop. The thing underneath is a standing figure, not a mound: a
    # hunched silhouette on a baseline is a hill, whatever it is meant to be.
    diver = (g(wing(CR_PLUM), 27, 17, 228, 1.0)
             + g('<g transform="scale(-1 1)">' + wing(CR_PLUM_D) + '</g>', 37, 17, 132, .95)
             + f'<path d="M27.5 26 Q32 29.5 36.5 26 L34.5 7 H29.5 Z" fill="{CR_PLUM}"/>'
             + f'<circle cx="32" cy="30" r="4.8" fill="{CR_PLUM}"/>'
             + poly('M28.5 23 Q26 16 27.5 9', CR_PLUM, 2.2) + poly('M35.5 23 Q38 16 36.5 9', CR_PLUM, 2.2)
             + f'<circle cx="30.1" cy="30" r="1.3" fill="{CR_PINK_HI}" stroke="none"/>'
             + f'<circle cx="33.9" cy="30" r="1.3" fill="{CR_PINK_HI}" stroke="none"/>')
    streak = f'<path d="M28.8 33 H35.2 L32 45 Z" fill="{CR_PINK_HI}"/>'
    chevrons = ''.join(f'<path d="M{x - 5} {y} L{x} {y + 5} L{x + 5} {y}" fill="none" '
                       f'stroke="{CR_PINK}" stroke-width="2.2" opacity="{o}"/>'
                       for x, y, o in ((12, 20, .9), (12, 28, .65), (12, 36, .4),
                                       (52, 20, .9), (52, 28, .65), (52, 36, .4)))
    return (chevrons
            + '<path d="M9 58 H55" fill="none" stroke="#4a4038" stroke-width="2.6"/>'
            + cr_mark(32, 49, .52)
            + glow(streak, .8) + streak + diver
            + glow(burst(32, 41, 3, 9.5, 9, '#ffffff'), .6)
            + burst(32, 41, 2.4, 6.8, 9, '#ffffff'))


@icon('Razor Gale')
def _():
    # Many thin cuts over a line, in TWO passes. The two passes are said by two bands at two
    # heights going opposite ways, each with its own long guide arc behind it: six crescents
    # scattered at random would just be confetti.
    passA = (cr_crescent(15, 15, 16, .8) + cr_crescent(33, 12, 14, .92) + cr_crescent(50, 16, 18, .8))
    passB = (cr_crescent(18, 31, -16, .74, '#f4bdd6') + cr_crescent(36, 33, -14, .86, '#f4bdd6')
             + cr_crescent(53, 29, -18, .72, '#f4bdd6'))
    guides = (f'<path d="M4 23 Q32 10 60 22" fill="none" stroke="{CR_PINK_HI}" stroke-width="1.4" opacity=".55"/>'
              f'<path d="M60 38 Q32 28 4 37" fill="none" stroke="{CR_PINK}" stroke-width="1.4" opacity=".45"/>')
    marks = cr_mark(14, 50, .5) + cr_mark(32, 52, .54) + cr_mark(50, 50, .5)
    cuts = ''.join(f'<path d="M{x - 3} {y - 2} L{x + 3} {y + 2}" fill="none" stroke="{CR_RED_HI}" '
                   f'stroke-width="1.8"/>' for x, y in ((14, 44), (32, 45), (50, 44)))
    return (guides + marks + cuts + passB + passA
            + twinkle(7, 44, .6, CR_PINK_HI) + twinkle(57, 45, .5, CR_PINK_HI))


@icon('Blood Rush')
def _():
    # A kill carries her ONWARD. Speed, not mending: no cross, no plus(), no url(#heal) - the
    # whole tile is a trail, a lean and two forward chevrons. The body she left is already down
    # and BEHIND her, which is what makes this a kill trigger rather than a sprint. Her torso
    # carries a pink edge so it does not disappear into its own wings.
    flier = ('<path d="M-5 10 Q0 12 5 10 L3.5 -8 H-3.5 Z" fill="#6b3f80"/>'
             + '<circle cx="0" cy="-12" r="4.8" fill="#6b3f80"/>'
             + poly('M-5 4 Q-9 9 -8 14', '#5a3570', 2.4) + poly('M5 4 Q9 9 8 14', '#5a3570', 2.4)
             + f'<circle cx="-1.6" cy="-12.5" r="1.4" fill="{CR_PINK_HI}" stroke="none"/>')
    wings = (g(wing(CR_PLUM_D), -5, -5, 172, 1.05) + g(wing(CR_PLUM), -4, 3, 202, .95))
    return (speed_lines(8, 22, 3, 15, 6, CR_PINK_HI, 0, .9)
            + speed_lines(10, 36, 3, 12, 5, CR_PINK, 0, .6)
            + cr_fallen(22, 49, .72) + g(drop(), 10, 45, 0, .5) + g(drop(), 35, 54, 0, .42)
            + g(wings + flier, 41, 28, 14, 1.0)
            + f'<path d="M47 19 L53 28 L47 37 M53 19 L58 28 L53 37" fill="none" '
              f'stroke="{CR_PINK_HI}" stroke-width="2.6"/>')


# ---- Gorehound (two-headed hellhound)
@icon('Throat Lock')
def _():
    # The finishing bite: the thing is ALREADY opened - head wrenched back off the shoulders,
    # the throat bare and running, the gorget on it already split - and the jaws have closed
    # over the gorget, not over clean plate. The jaws are deliberately held to about half the
    # tile; at full size they swallow the victim and all that is left is a toothy oval.
    throat = (f'<path d="M15 22 L29 20 L33 44 L19 46 Z" fill="{CR_BODY_HI}"/>'
              f'<path d="M20 22 L23 45" fill="none" stroke="#8a8071" stroke-width="1.4" opacity=".7"/>')
    head = (f'<circle cx="19" cy="15" r="9.4" fill="{CR_BODY}"/>'
            f'<path d="M10 12 L13 20 L20 22 Z" fill="{CR_BODY}"/>')
    shoulders = f'<path d="M10 58 Q12 48 24 45 Q36 48 38 58 Z" fill="{CR_BODY_D}"/>'
    gorget = g('<path d="M-13 -5.5 H13 L11 5.5 H-11 Z" fill="url(#steel)"/>'
               '<path d="M-11.5 0 H11.5" fill="none" stroke="#8d97aa" stroke-width="1.2"/>'
               '<path d="M-5 -5.5 L-3 -1 L-6 1.5 L-4 5.5" fill="none" stroke="#1d1a24" stroke-width="1.6"/>'
               '<path d="M2 -5.5 L3.4 -2 L1.6 1" fill="none" stroke="#1d1a24" stroke-width="1.2" opacity=".8"/>'
               '<path d="M7 -5.5 L4.5 -1.5 L9 1 L7 5.5" fill="none" stroke="#1d1a24" stroke-width="1.6"/>'
               '<path d="M-13 -2 L-18 1 L-13 4.5 Z" fill="#1d1a24" stroke-width="1"/>', 26, 34, 6, 1.0)
    return (head + throat + shoulders
            + f'<path d="M24 24 Q28 34 26 44" fill="none" stroke="{CR_RED}" stroke-width="3.2"/>'
            + gorget
            + g(jaws(CR_HOUND), 44, 33, -28, .92)
            + glow(burst(36, 33, 3, 9, 9, CR_RED_HI), .55)
            + burst(36, 33, 2.4, 6.4, 9, '#ffd9d9')
            + g(drop(), 22, 53, 0, .85) + g(drop(), 31, 57, 0, .6) + g(drop(), 46, 51, 0, .5)
            + f'<path d="M11 36 L7 40 M15 44 L11 48" fill="none" stroke="{CR_EMBER}" '
              f'stroke-width="2" opacity=".7"/>')


@icon('Worry the Wound')
def _():
    # Not one big bite: the same spot taken THREE times, fast. The last bite is bright and
    # square on, the two before it are dimmer and half behind it, so the count is readable in
    # one look without the three of them turning into a pile of shards. The jaws are already
    # coming back in, and the motion arcs behind them say it is going to happen again.
    patch = ('<path d="M19 26 C25 19 38 20 44 27 C50 34 46 45 38 47 C29 50 20 45 18 38 '
             'C16 33 17 29 19 26 Z" fill="#7e1020" stroke="none"/>')
    return (glow('<ellipse cx="31" cy="35" rx="17" ry="14" fill="#c01e2c"/>', .45)
            + patch
            + cr_bite(26, 27, -40, .52, CR_BONE_D) + cr_bite(39, 43, 34, .5, CR_BONE_D)
            + cr_bite(32, 35, -8, .74)
            + arc_lines(14, 14, 11, 3, 66, CR_EMBER, 42, 1.8, 4)
            + g(jaws(CR_HOUND), 16, 16, 40, .76)
            + g(drop(), 24, 55, 0, .8) + g(drop(), 44, 53, 0, .6) + g(drop(), 52, 43, 0, .45))


@icon('Gorge')
def _():
    # A kill feeds him: the maw is down ON the body and the red is running UP into it, which is
    # the whole passive. The flow TAPERS - wide where it leaves the body, narrow where it goes
    # in - because a constant-width red band between a body and a mouth is a drinking straw
    # and reads either way; the arrowhead at the mouth end fixes the direction for good.
    flow = ('<path d="M38 27 L42 29 L31 46 L19 48 Z" fill="#c01e2c"/>'
            '<path d="M24 46 L39 29" fill="none" stroke="#ff8a8a" stroke-width="1.8" opacity=".9"/>'
            + ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ff8a8a" stroke="none" opacity=".8"/>'
                      for cx, cy, r in ((33, 37, 1.6), (28, 43, 1.3))))
    return (glow('<ellipse cx="30" cy="40" rx="20" ry="14" fill="#a81825"/>', .4)
            + cr_fallen(24, 48, .9)
            + flow
            + f'<path d="M32 36 L39 29 L41 37" fill="none" stroke="{CR_BONE}" stroke-width="2.4"/>'
            + g(jaws(CR_HOUND), 44, 21, -38, .95)
            + g(drop(), 13, 37, 0, .55) + g(drop(), 32, 56, 0, .45)
            + f'<path d="M52 36 L56 40 M47 43 L50 47" fill="none" stroke="{CR_EMBER}" '
              f'stroke-width="2" opacity=".65"/>')


# ---- Morwenna Bloodweaver (blood witch)
@icon('Open the Vein')
def _():
    # Two things at once and both have to show: the vein is open (a gash across a bared forearm,
    # blood leaving it) AND it is hexed (her sigil on the wound, with two hooks holding the lips
    # apart so it cannot close). Three corrections from the first pass: the limb has a FIST and
    # a sleeve cuff, because a plain tapered bar with a highlight down its length is a log; the
    # gash is big and bright, because the wound is the skill; and the hex ring is dashed, which
    # is what keeps a hexagon laid over an arm from reading as a bangle.
    arm = g(f'<path d="M-26 -8 L13 -6.5 Q19 -5.5 19 0 Q19 5.5 13 6.5 L-26 8 Z" fill="{CR_FLESH}"/>'
            f'<circle cx="19" cy="0" r="8" fill="{CR_FLESH}"/>'
            '<path d="M14 -4.5 L22 -3.5 M14 0 L23 0 M14 4.5 L22 3.5" fill="none" stroke="#9a6a66" stroke-width="1.3"/>'
            '<path d="M-28 -9 H-19 V9 H-28 Z" fill="#3a2234"/>'
            '<path d="M-19 -9 V9" fill="none" stroke="#5a3850" stroke-width="1.4"/>', 30, 32, 30, 1.0)
    vein = g(f'<path d="M-17 3 Q-6 1 6 3" fill="none" stroke="#7a3a5e" stroke-width="2" opacity=".8"/>', 30, 32, 30, 1.0)
    # Lopsided on purpose, and with the pale lip on ONE side only: a symmetrical lens with a
    # bright middle and a pale rim top and bottom is an eye, which is exactly what the first
    # pass of this tile drew.
    gash = g('<path d="M-13 1.5 C-9 -2.5 -4 -1.5 0 -4 C5 -2 9 -3.5 13 -.5 C9 3.5 4 2 0 4.5 '
             'C-5 2.5 -9 4.5 -13 1.5 Z" fill="#280810"/>'
             '<path d="M-10 .8 C-6 -1.4 -2 -.6 1 -1.8 C5 -.6 8 -1.4 10.5 0 C8 1.8 4 1 1 2.2 '
             'C-3 1 -7 2.4 -10 .8 Z" fill="#cf1f2b" stroke="none"/>'
             f'<path d="M-13 1.5 C-9 -2.5 -4 -1.5 0 -4 C5 -2 9 -3.5 13 -.5" fill="none" '
             f'stroke="{CR_LIP}" stroke-width="1.8"/>',
             24, 28, 120, 1.0)
    ring = ' '.join(f'{24 + 12.5 * math.cos(math.radians(a)):.1f},{28 + 12.5 * math.sin(math.radians(a)):.1f}'
                    for a in range(-90, 270, 60))
    return (arm
            + f'<path d="M27 33 Q24 42 26 50" fill="none" stroke="{CR_RED}" stroke-width="3"/>'
            + vein + gash
            + glow(f'<circle cx="24" cy="28" r="13" fill="{CR_HEX}"/>', .22)
            + f'<polygon points="{ring}" fill="none" stroke="{CR_HEX}" stroke-width="1.8" '
              f'stroke-dasharray="4.5 3.2" opacity=".95"/>'
            + f'<path d="M16 21 Q12 25 15 29 M32 35 Q36 31 33 27" fill="none" stroke="{CR_HEX}" '
              f'stroke-width="2.2"/>'
            + g(drop(), 22, 50, 0, .9) + g(drop(), 33, 55, 0, .6) + g(drop(), 13, 48, 0, .5)
            + twinkle(45, 13, .7, CR_HEX) + twinkle(11, 16, .55, CR_HEX))


@icon('Blood Fog')
def _():
    # The whole line worn down at once. Three marks stood well apart, each with its blade
    # hanging point-down out of its fist and its breastplate pitted through, standing in a low
    # red mist. The mist is LOBES at partial opacity, not a filled band: a solid slab of red
    # across the bottom third reads as a pool of blood, which is a different skill entirely.
    def worn(x, y, s):
        return (cr_mark(x, y, s) + cr_plate(x, y - 5.5 * s, s * 1.05)
                + cr_droop(x + 9.6 * s, y + 2 * s, 12, s * .95))
    lobes = (f'<path d="M2 47 Q9 39 17 45 Q24 50 31 43 Q39 37 46 44 Q53 50 62 43 V60 H2 Z" '
             f'fill="{CR_RED_DK}" stroke="none" opacity=".52"/>'
             f'<path d="M2 53 Q11 47 21 52 Q30 57 39 51 Q49 46 62 52 V60 H2 Z" '
             f'fill="{CR_RED}" stroke="none" opacity=".34"/>'
             + ''.join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{CR_RED}" '
                       f'stroke="none" opacity=".26"/>'
                       for cx, cy, rx, ry in ((16, 42, 11, 5), (38, 40, 12, 5.5), (55, 43, 8, 4)))
             + f'<path d="M2 47 Q9 39 17 45 Q24 50 31 43 Q39 37 46 44 Q53 50 62 43" fill="none" '
               f'stroke="{CR_RED_HI}" stroke-width="1.6" opacity=".5"/>')
    wisps = (f'<path d="M12 44 Q16 38 13 33 M38 43 Q42 37 39 32 M54 45 Q58 40 55 36" fill="none" '
             f'stroke="{CR_RED_HI}" stroke-width="1.8" opacity=".5"/>')
    return (glow(f'<ellipse cx="32" cy="48" rx="29" ry="12" fill="{CR_RED}"/>', .45)
            + worn(14, 33, .6) + worn(32, 31, .66) + worn(50, 34, .6)
            + lobes + wisps
            + down_arrow(54, 15, 12, CR_HEX, 2.6)
            + twinkle(9, 13, .6, CR_HEX))


@icon('Blood Price')
def _():
    # Her law, laid on everybody: a cast weighed against blood, and the blood is the heavier
    # pan. The beam is GOLD, not red - a red balance on a wine ground disappears, and the whole
    # point of this tile is the shape of the scales. The drop sits clear ABOVE its pan so the
    # bowl still reads; sat in the bowl it just covers it up.
    def pan(x, y):
        return (f'<path d="M{x - 8.5} {y} Q{x} {y + 8} {x + 8.5} {y} Z" fill="url(#gold)"/>'
                f'<path d="M{x - 8.5} {y} H{x + 8.5}" fill="none" stroke="#8a5a14" stroke-width="1.4"/>')
    beam = '<path d="M14 24 L49 15 L50 19.5 L15 28.5 Z" fill="url(#gold)"/>'
    strings = ('<path d="M14.6 26.5 L7.5 38 M14.6 26.5 L21.5 38 M49.2 17.5 L42.5 29 M49.2 17.5 L56 29" '
               'fill="none" stroke="#c9a04a" stroke-width="1.6"/>')
    post = ('<rect x="29.6" y="18" width="5" height="32" fill="url(#gold)"/>'
            '<path d="M22 50 H42 L45 57 H19 Z" fill="url(#gold)"/>'
            '<path d="M32 13 L37 21 H27 Z" fill="url(#gold)"/>')
    hexpan = ' '.join(f'{49 + 6.6 * math.cos(math.radians(a)):.1f},{22.5 + 6.6 * math.sin(math.radians(a)):.1f}'
                      for a in range(-90, 270, 60))
    return (post + beam + strings + pan(14.5, 38) + pan(49, 29)
            + glow(f'<circle cx="14.5" cy="31" r="7" fill="{CR_RED_HI}"/>', .55)
            + g(drop(), 14.5, 31, 0, 1.0)
            + f'<polygon points="{hexpan}" fill="{CR_HEX_D}" stroke="{CR_HEX}" stroke-width="2.2"/>'
            + twinkle(49, 22.5, .5, CR_HEX)
            + twinkle(10, 15, .6, CR_ACC) + twinkle(55, 47, .5, CR_HEX))

def frame(faction, kind, glyph, name):
    top, bot, acc = PAL[faction]
    if kind in ('passive', 'neutral'):   # neutral skills share the round frame of the hand-drawn neutral set
        return passive_frame(faction, glyph, name)
    sig = kind == 'sig'
    rim = 'url(#gold)' if sig else acc
    corner = ''
    if sig:
        corner = (f'<polygon points="{star_pts(53, 11, 6.4, 2.7)}" fill="{INK}"/>'
                  f'<polygon points="{star_pts(53, 11, 5, 2.1)}" fill="#ffd66a"/>')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Burizza skill icon: {escape(name)}{' (signature)' if sig else ''}. Generated by make_icons.py, 64x64. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="128" height="128">
<defs>{DEFS}<radialGradient id="bg" cx=".5" cy=".3" r=".85"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></radialGradient></defs>
<rect x="2" y="2" width="60" height="60" rx="11" fill="url(#bg)"/>
<rect x="5.5" y="5.5" width="53" height="53" rx="8" fill="none" stroke="{acc}" stroke-width="1" opacity="{.5 if sig else .25}"/>
<g filter="url(#ds)" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">{glyph}</g>
<rect x="2" y="2" width="60" height="60" rx="11" fill="none" stroke="{rim}" stroke-width="{3 if sig else 2}" opacity="{1 if sig else .85}"/>
{corner}
</svg>
'''


def passive_frame(faction, glyph, name):
    """Passives: a round medallion, so they never look like something you can click."""
    top, bot, acc = PAL[faction]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Burizza passive icon: {escape(name)}. Generated by make_icons.py, 64x64. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="128" height="128">
<defs>{DEFS}<radialGradient id="bg" cx=".5" cy=".3" r=".85"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></radialGradient></defs>
<circle cx="32" cy="32" r="30" fill="url(#bg)"/>
<circle cx="32" cy="32" r="26" fill="none" stroke="{acc}" stroke-width="1" stroke-dasharray="2 3" opacity=".55"/>
<g filter="url(#ds)" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round" transform="translate(32 32) scale(.86) translate(-32 -32)">{glyph}</g>
<circle cx="32" cy="32" r="30" fill="none" stroke="{acc}" stroke-width="2.2"/>
</svg>
'''


def main():
    seen = set()
    for faction, (_, skills) in CATALOG.items():
        for name, _champ, kind in skills:
            if name not in ICONS:
                raise SystemExit(f'No glyph for {name!r}')
            seen.add(name)
            (OUT / f'{slug(name)}.svg').write_text(frame(faction, kind, ICONS[name](), name), encoding='utf-8')
    extra = set(ICONS) - seen
    if extra:
        raise SystemExit(f'Glyphs not in CATALOG: {sorted(extra)}')
    write_gallery()
    print(f'Wrote {len(seen)} icons + gallery.html to {OUT}')


def write_gallery():
    sections = []
    for faction, (fname, skills) in CATALOG.items():
        acc = PAL[faction][2]
        cards = ''.join(
            f'<figure class="card {kind}"><img src="{slug(n)}.svg" alt="" width="72" height="72">'
            f'<figcaption><b>{"★ " if kind == "sig" else ""}{escape(n)}</b>'
            f'<span>{"Passive · " if kind == "passive" else ""}{escape(c)}</span></figcaption></figure>'
            for n, c, kind in skills)
        sections.append(f'<section style="--acc:{acc}"><h2>{escape(fname)}</h2><div class="grid">{cards}</div></section>')
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Burizza Skill Icons</title>
<link href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;700;800&family=Grenze+Gotisch:wght@600&display=swap" rel="stylesheet">
<style>
/* Generated by make_icons.py. Same dusk palette as the game. */
:root {{ --bg: #161925; --bg-2: #262036; --panel: #1e2232; --panel-2: #282d43; --line: #3a4058; --fg: #ece6d8; --muted: #a29fb2; --accent: #e8a548; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; color: var(--fg); font: 16px/1.4 "Alegreya Sans", "Segoe UI", sans-serif;
  background: radial-gradient(120% 70% at 50% 0%, var(--bg-2), var(--bg) 65%) fixed, var(--bg); }}
.wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; display: grid; gap: 28px; }}
h1 {{ margin: 0; font-family: "Grenze Gotisch", Georgia, serif; font-size: clamp(2rem, 5vw, 2.8rem); line-height: 1; color: var(--accent); }}
.tag {{ margin: 6px 0 0; color: var(--muted); }}
h2 {{ margin: 0 0 12px; font-family: "Grenze Gotisch", Georgia, serif; font-size: 1.7rem; color: var(--acc); }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
@media (max-width: 620px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.card {{ margin: 0; padding: 12px 10px; display: grid; justify-items: center; gap: 8px; text-align: center;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); border: 1px solid var(--line); border-radius: 12px; }}
.card.sig {{ border-color: #8a6a2a; }}
.card.passive {{ border-style: dashed; }}
.card.passive figcaption span {{ color: var(--acc); }}
.card img {{ width: 72px; height: 72px; }}
figcaption {{ display: grid; gap: 2px; font-size: .9rem; line-height: 1.2; }}
figcaption span {{ font-size: .78rem; color: var(--muted); }}
</style>
</head>
<body>
<main class="wrap">
<header><h1>Skill Icons</h1><p class="tag">Every skill and passive in Burizza, grouped by faction. Each row is one champion: skill, second skill, ★ signature (gold frame), passive (round).</p></header>
{''.join(sections)}
</main>
</body>
</html>
'''
    (OUT / 'gallery.html').write_text(html, encoding='utf-8')


if __name__ == '__main__':
    main()
