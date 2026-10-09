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


@icon('Nibble Flurry')
def _():
    return (g(jaws(), 20, 21, -15, .55) + g(jaws(), 36, 32, -15, .55) + g(jaws(), 47, 47, -15, .5)
            + '<path d="M10 40 L16 44 M24 52 L28 56" stroke="#7fe3d8" stroke-width="2" opacity=".7"/>')


@icon('Gurgle Frenzy')
def _():
    bubbles = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#bff3ff" fill-opacity=".25" stroke="#bff3ff" stroke-width="1.2"/>'
                      for x, y, r in ((12, 14, 3.5), (52, 12, 2.6), (54, 50, 3.2), (11, 50, 2.4), (47, 22, 1.8)))
    return (bubbles + glow('<ellipse cx="32" cy="33" rx="20" ry="15" fill="#ff4a4a"/>', .45)
            + g(jaws(), 32, 33, 0, 1.15)
            + '<path d="M8 30 L13 32 M56 30 L51 32 M32 10 V15" stroke="#ff7a7a" stroke-width="2.2"/>')


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
@icon('Rivet Shot')
def _():
    rivet = ('<rect x="-8" y="-3" width="16" height="6" fill="url(#steel)"/>'
             '<path d="M8 -7 Q15 -7 15 0 Q15 7 8 7 Z" fill="url(#iron)"/>')
    return speed_lines(8, 32, 3, 12, 6, '#8be28b') + g(rivet, 34, 32, 0, 1.4)


@icon('Rivet Burst')
def _():
    rivet = ('<rect x="-8" y="-3" width="16" height="6" fill="url(#steel)"/>'
             '<path d="M8 -7 Q15 -7 15 0 Q15 7 8 7 Z" fill="url(#iron)"/>')
    return (speed_lines(6, 32, 3, 9, 7, '#8be28b')
            + g(rivet, 34, 18, -18, .95) + g(rivet, 38, 32, 0, .95) + g(rivet, 34, 46, 18, .95))


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


@icon('Tiny Target')
def _():
    fish = ('<path d="M-8 0 C-4 -6 4 -6 7 0 C4 6 -4 6 -8 0 Z" fill="#5fa38a"/>'
            '<path d="M7 0 L12 -4 L11 0 L12 4 Z" fill="#2f6f8f"/>'
            '<circle cx="-4" cy="-1" r="1.3" fill="#15121d" stroke="none"/>')
    return (g(arrow(), 30, 22, 80, .9)
            + '<path d="M8 30 Q30 24 54 30" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-dasharray="3 3" opacity=".6"/>'
            + g(fish, 32, 42, 0, 1.2)
            + '<path d="M22 50 L18 54 M42 50 L46 54" stroke="#bff3ff" stroke-width="1.6"/>')


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


@icon('Bloodhound')
def _():
    paw = ('<ellipse cx="0" cy="3" rx="5" ry="4.2" fill="url(#demon)"/>'
           '<circle cx="-5" cy="-4" r="2" fill="url(#demon)"/><circle cx="-1.7" cy="-6.5" r="2" fill="url(#demon)"/>'
           '<circle cx="1.7" cy="-6.5" r="2" fill="url(#demon)"/><circle cx="5" cy="-4" r="2" fill="url(#demon)"/>')
    return (g(paw, 20, 44, -20, 1.1) + g(paw, 38, 26, -20, 1.1)
            + g(drop(), 30, 44, 0, .5) + g(drop(), 48, 40, 0, .6) + g(drop(), 46, 14, 0, .45) + g(drop(), 16, 24, 0, .4))


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


# ---------------------------------------------------------------- catalog (for the frame + gallery)
# kind: "skill", "sig" (★ signature, gold frame), "passive" or "neutral" (round frame).
# Per champion: skill, second skill, ★ signature, passive. Mirrors ROSTER / SUMMONS in index.html.
CATALOG = {
    'common': ('Everyone', [('Attack', 'All champions', 'skill'), ('Guard', 'All champions', 'skill'),
        ('Provoke', 'Neutral skill', 'neutral'),
        ('Toughness', 'Any champion', 'passive'), ('Might', 'Any champion', 'passive'), ('Swiftness', 'Any champion', 'passive'),
        ('Keen Edge', 'Any champion', 'passive'), ('Deep Well', 'Any champion', 'passive'), ('Second Wind', 'Any champion', 'passive')]),
    'mech': ('Ironclad Union', [
        ('Piston Punch', 'Bulwark-7', 'skill'), ('Steam Vent', 'Bulwark-7', 'skill'), ('Hydraulic Slam', 'Bulwark-7', 'sig'), ('Piledriver', 'Bulwark-7', 'skill'), ('Bunker Down', 'Bulwark-7', 'skill'), ('Reactive Plating', 'Bulwark-7', 'passive'),
        ('Rip Saw', 'Sawtooth', 'skill'), ('Shrapnel Spin', 'Sawtooth', 'skill'), ('Grinder', 'Sawtooth', 'sig'), ('Limb Shear', 'Sawtooth', 'skill'), ('Rev Up', 'Sawtooth', 'skill'), ('Serrated', 'Sawtooth', 'passive'),
        ('Arc Bolt', 'Arclight', 'skill'), ('Discharge', 'Arclight', 'skill'), ('Chain Surge', 'Arclight', 'sig'), ('Overload Coil', 'Arclight', 'skill'), ('Static Field', 'Arclight', 'skill'), ('Feedback Loop', 'Arclight', 'passive'),
        ('Flak Burst', 'Howitzer', 'skill'), ('AP Round', 'Howitzer', 'skill'), ('Siege Shell', 'Howitzer', 'sig'), ('Mortar Walk', 'Howitzer', 'skill'), ('Shell Shock', 'Howitzer', 'skill'), ('Big Guns', 'Howitzer', 'passive'),
        ('Field Weld', 'Patchwork', 'skill'), ('Overclock', 'Patchwork', 'skill'), ('Assemble Scrapbot', 'Patchwork', 'sig'), ('Jury Rig', 'Patchwork', 'skill'), ('Coolant Flush', 'Patchwork', 'skill'), ('Maintenance Drone', 'Patchwork', 'passive'),
        ('Rivet Shot', 'Scrapbot (summon)', 'skill'),
        ('Rivet Burst', 'Scrapbot (summon)', 'skill'),
    ]),
    'orc': ('Bloodtusk Horde', [
        ('Cleave', 'Krug Skullsplitter', 'skill'), ('Reckless Swing', 'Krug Skullsplitter', 'skill'), ('Blood Frenzy', 'Krug Skullsplitter', 'sig'), ('Twin Axes', 'Krug Skullsplitter', 'skill'), ("Warchief's Fury", 'Krug Skullsplitter', 'skill'), ('Bloodlust', 'Krug Skullsplitter', 'passive'),
        ('Skull Rattler', 'Mogra Ironhide', 'skill'), ('Ground Pound', 'Mogra Ironhide', 'skill'), ('Iron Hide', 'Mogra Ironhide', 'sig'), ('Bonebreaker', 'Mogra Ironhide', 'skill'), ('Hold the Line', 'Mogra Ironhide', 'skill'), ('Thick Skull', 'Mogra Ironhide', 'passive'),
        ('Call the War Boar', 'Vashka Spearthrower', 'skill'), ("Hunter's Mark", 'Vashka Spearthrower', 'skill'), ('Gutpiercer', 'Vashka Spearthrower', 'sig'), ('Pinning Throw', 'Vashka Spearthrower', 'skill'), ('Volley of Spears', 'Vashka Spearthrower', 'skill'), ('Steppe Hunter', 'Vashka Spearthrower', 'passive'),
        ('Firepot', 'Drekka Firegut', 'skill'), ('Napalm Jar', 'Drekka Firegut', 'skill'), ('Powder Keg', 'Drekka Firegut', 'sig'), ('Cinder Spray', 'Drekka Firegut', 'skill'), ('Sticky Tar', 'Drekka Firegut', 'skill'), ('Pyromaniac', 'Drekka Firegut', 'passive'),
        ('Spirit Ward', 'Old Mother Hesk', 'skill'), ('Bone Charm', 'Old Mother Hesk', 'skill'), ('Drums of the Horde', 'Old Mother Hesk', 'sig'), ("Ancestor's Balm", 'Old Mother Hesk', 'skill'), ('Totem of Stone', 'Old Mother Hesk', 'skill'), ('Ancestral Watch', 'Old Mother Hesk', 'passive'),
        ('Gore', 'War Boar (summon)', 'skill'),
        ('Tusk Charge', 'War Boar (summon)', 'skill'),
    ]),
    'human': ('Kingdom of Aldmere', [
        ('Power Slash', 'Wren', 'skill'), ('Arcane Edge', 'Wren', 'skill'), ('Thunderclap', 'Wren', 'sig'), ('Mageslayer', 'Wren', 'skill'), ('Runed Thrust', 'Wren', 'skill'), ('Arcane Ward', 'Wren', 'passive'),
        ('Smite', 'Sir Garrick Vane', 'skill'), ('Consecrate', 'Sir Garrick Vane', 'skill'), ('Oathguard', 'Sir Garrick Vane', 'sig'), ('Hammer of Judgement', 'Sir Garrick Vane', 'skill'), ('Lionheart', 'Sir Garrick Vane', 'skill'), ('Retribution', 'Sir Garrick Vane', 'passive'), ('Shield of the Realm', 'Sir Garrick Vane', 'passive'),
        ('Aimed Shot', 'Mara Holt', 'skill'), ('Ricochet', 'Mara Holt', 'skill'), ('Powder Shot', 'Mara Holt', 'sig'), ('Pistol Whip', 'Mara Holt', 'skill'), ('Volley Fire', 'Mara Holt', 'skill'), ('Deadeye', 'Mara Holt', 'passive'),
        ('Fireball', 'Aldous Emberfall', 'skill'), ('Ignite', 'Aldous Emberfall', 'skill'), ('Inferno', 'Aldous Emberfall', 'sig'), ('Flame Lance', 'Aldous Emberfall', 'skill'), ('Mantle of Flame', 'Aldous Emberfall', 'skill'), ('Kindling', 'Aldous Emberfall', 'passive'),
        ('Sacred Light', 'Sister Liesl', 'skill'), ('Guardian Angel', 'Sister Liesl', 'skill'), ('Prayer of Dawn', 'Sister Liesl', 'sig'), ('Benediction', 'Sister Liesl', 'skill'), ('Censure', 'Sister Liesl', 'skill'), ('Mercy', 'Sister Liesl', 'passive'),
    ]),
    'stone': ('Stoneleaf Accord', [
        ('Hammerfall', 'Durgan Anvilbeard', 'skill'), ('Anvil Strike', 'Durgan Anvilbeard', 'skill'), ('Mountain Breaker', 'Durgan Anvilbeard', 'sig'), ('Forge Strike', 'Durgan Anvilbeard', 'skill'), ('Quake Hammer', 'Durgan Anvilbeard', 'skill'), ('Grudge', 'Durgan Anvilbeard', 'passive'),
        ('Shield Bash', 'Hilda Stonewall', 'skill'), ('Shieldwall', 'Hilda Stonewall', 'skill'), ('Stand Firm', 'Hilda Stonewall', 'sig'), ('Boulder Toss', 'Hilda Stonewall', 'skill'), ('Bulwark of the Accord', 'Hilda Stonewall', 'skill'), ('Unbreakable', 'Hilda Stonewall', 'passive'),
        ('Swift Arrows', 'Aelira Swiftwind', 'skill'), ('Arrow Rain', 'Aelira Swiftwind', 'skill'), ('Hawkeye', 'Aelira Swiftwind', 'sig'), ('Piercing Shot', 'Aelira Swiftwind', 'skill'), ('Steady Aim', 'Aelira Swiftwind', 'skill'), ('Keen Eye', 'Aelira Swiftwind', 'passive'),
        ('Venom Bolt', 'Faelan Thornshot', 'skill'), ('Envenom', 'Faelan Thornshot', 'skill'), ('Thornvolley', 'Faelan Thornshot', 'sig'), ('Crippling Bolt', 'Faelan Thornshot', 'skill'), ('Toxic Barrage', 'Faelan Thornshot', 'skill'), ('Debilitating Venom', 'Faelan Thornshot', 'passive'),
        ('Regrowth', 'Elowen Greenmantle', 'skill'), ('Entangle', 'Elowen Greenmantle', 'skill'), ('Bloom of Spring', 'Elowen Greenmantle', 'sig'), ('Barkskin', 'Elowen Greenmantle', 'skill'), ('Thornlash', 'Elowen Greenmantle', 'skill'), ('Forest Stride', 'Elowen Greenmantle', 'passive'), ('Verdant Aura', 'Elowen Greenmantle', 'passive'),
    ]),
    'tide': ('The Tideborn', [
        ('Trident Lunge', 'Tharos Razorfin', 'skill'), ('Riptide', 'Tharos Razorfin', 'skill'), ('Blood in the Water', 'Tharos Razorfin', 'sig'), ('Feeding Frenzy', 'Tharos Razorfin', 'skill'), ('Undertow', 'Tharos Razorfin', 'skill'), ('Blood Scent', 'Tharos Razorfin', 'passive'),
        ('Nibble Flurry', 'Grubblefin', 'skill'), ('Slippery Scales', 'Grubblefin', 'skill'), ('Gurgle Frenzy', 'Grubblefin', 'sig'), ('Barnacle Bite', 'Grubblefin', 'skill'), ('Tail Whip', 'Grubblefin', 'skill'), ('Choking Bite', 'Grubblefin', 'skill'), ('Tiny Target', 'Grubblefin', 'passive'),
        ("Siren's Hush", 'Seraphine Wavecaller', 'skill'), ('Dirge of the Deep', 'Seraphine Wavecaller', 'skill'), ('Lure Song', 'Seraphine Wavecaller', 'sig'), ('Drowning Chorus', 'Seraphine Wavecaller', 'skill'), ('Song of the Depths', 'Seraphine Wavecaller', 'skill'), ('Echo', 'Seraphine Wavecaller', 'passive'),
        ('Ink Double', 'Octavia Inkveil', 'skill'), ('Tentacle Snare', 'Octavia Inkveil', 'skill'), ('Ink Cloud', 'Octavia Inkveil', 'sig'), ('Ink Whip', 'Octavia Inkveil', 'skill'), ('Crushing Grip', 'Octavia Inkveil', 'skill'), ('Ink Sac', 'Octavia Inkveil', 'passive'),
        ('Healing Tide', 'Maren Pearlheart', 'skill'), ('Tide Pool', 'Maren Pearlheart', 'skill'), ('Pearl Barrier', 'Maren Pearlheart', 'sig'), ('Reef Bloom', 'Maren Pearlheart', 'skill'), ('Riptide Crash', 'Maren Pearlheart', 'skill'), ('Backwash', 'Maren Pearlheart', 'passive'), ('Tidecaller', 'Maren Pearlheart', 'passive'),
        ('Ink Lash', 'Ink Illusion (summon)', 'skill'),
    ]),
    'crimson': ('The Crimson Court', [
        ('Crimson Lunge', 'Vesper Nightshade', 'skill'), ('Night Waltz', 'Vesper Nightshade', 'skill'), ('Execute', 'Vesper Nightshade', 'sig'), ('Exsanguinate', 'Vesper Nightshade', 'skill'), ('Throat Tear', 'Vesper Nightshade', 'skill'), ('Mist Form', 'Vesper Nightshade', 'skill'), ('Riposte', 'Vesper Nightshade', 'passive'),
        ('Hellfire Slam', 'Malgrath the Unbound', 'skill'), ('Demonic Roar', 'Malgrath the Unbound', 'skill'), ('Infernal Wrath', 'Malgrath the Unbound', 'sig'), ('Pit Chains', 'Malgrath the Unbound', 'skill'), ('Sulphur Breath', 'Malgrath the Unbound', 'skill'), ('Blood Pact', 'Malgrath the Unbound', 'skill'), ('Brimstone Hide', 'Malgrath the Unbound', 'passive'),
        ('Kiss of Ruin', 'Seraxa Thornwing', 'skill'), ('Shadowstep', 'Seraxa Thornwing', 'skill'), ('Dance of Knives', 'Seraxa Thornwing', 'sig'), ('Wing Carve', 'Seraxa Thornwing', 'skill'), ("Predator's Grace", 'Seraxa Thornwing', 'skill'), ('Flurry', 'Seraxa Thornwing', 'passive'),
        ('Rend', 'Gorehound', 'skill'), ('Savage Maul', 'Gorehound', 'skill'), ('Hellhound Howl', 'Gorehound', 'sig'), ('Hamstring', 'Gorehound', 'skill'), ('Feral Lunge', 'Gorehound', 'skill'), ('Bloodhound', 'Gorehound', 'passive'),
        ('Blight Hex', 'Morwenna Bloodweaver', 'skill'), ('Blood Siphon', 'Morwenna Bloodweaver', 'skill'), ('Blood Communion', 'Morwenna Bloodweaver', 'sig'), ('Crimson Mend', 'Morwenna Bloodweaver', 'skill'), ('Wither', 'Morwenna Bloodweaver', 'skill'), ('Blood Ward', 'Morwenna Bloodweaver', 'skill'), ('Withering Curse', 'Morwenna Bloodweaver', 'passive'),
    ]),
    'undead': ('The Pale Host', [
        ('Grave Cross', 'Mordrek the Interred', 'skill'), ('Graveside Chill', 'Mordrek the Interred', 'skill'), ('Last Rites', 'Mordrek the Interred', 'sig'), ('Plant the Marker', 'Mordrek the Interred', 'skill'), ('Second Grave', 'Mordrek the Interred', 'passive'),
        ('Tomb Slab', 'Barrow', 'skill'), ('Grasping Hands', 'Barrow', 'skill'), ('Barrow Wall', 'Barrow', 'sig'), ('Crypt Breaker', 'Barrow', 'skill'), ('Hold the Grave', 'Barrow', 'skill'), ('Graveyard Fence', 'Barrow', 'skill'), ('Burrow', 'Barrow', 'skill'), ('Feast of the Fallen', 'Barrow', 'passive'),
        ('Bone Dart', 'Cadris Gravecall', 'skill'), ('Shambling Rise', 'Cadris Gravecall', 'skill'), ('Charnel Volley', 'Cadris Gravecall', 'sig'), ('Rot Shot', 'Cadris Gravecall', 'skill'), ('Marrow Pierce', 'Cadris Gravecall', 'skill'), ('Toll of the Dead', 'Cadris Gravecall', 'passive'),
        ('Shroud Arrow', 'Vaun Shroudfletch', 'skill'), ('Withering Shot', 'Vaun Shroudfletch', 'skill'), ('Pall of Arrows', 'Vaun Shroudfletch', 'sig'), ('Graveshot', 'Vaun Shroudfletch', 'skill'), ('Scatter of Bones', 'Vaun Shroudfletch', 'skill'), ('Deathmark', 'Vaun Shroudfletch', 'passive'),
        ('Grave Mend', 'Mortessa', 'skill'), ('Coffin', 'Mortessa', 'skill'), ('Second Burial', 'Mortessa', 'sig'), ('Hex of Ruin', 'Mortessa', 'skill'), ('Soul Siphon', 'Mortessa', 'skill'), ('Keeper of the Coffin', 'Mortessa', 'passive'),
        ('Clawing Grasp', 'Shambler (summon)', 'skill'),
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


@icon('Bunker Down')
def _():
    return (g(heater('url(#iron)', '#f0a73a'), 32, 33, 0, 1.12)
            + poly('M23 26 L32 34 L41 26', '#ffd166', 2.6)
            + poly('M23 37 L32 45 L41 37', '#ffd166', 2.6)
            + twinkle(12, 16, .8, '#f0a73a') + twinkle(52, 16, .8, '#f0a73a'))


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


# ---- The Crimson Court
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


@icon('Shroud Arrow')
def _():
    return (poly('M10 44 Q18 36 14 26 Q22 32 20 20', '#8a9a8c', 2.4)
            + g(arrow('url(#steel)', '#44523f'), 33, 30, -28)
            + poly('M22 44 Q30 40 28 32', '#6a7a6c', 2))


@icon('Pall of Arrows')
def _():
    arr = '<path d="M0 -8 V6 M0 6 L-2.6 1.8 M0 6 L2.6 1.8 M-2 -8 L0 -5 L2 -8" stroke-width="2" fill="none"/>'
    return ('<path d="M10 16 Q16 8 26 12 Q32 4 42 10 Q52 8 54 17 Q58 24 48 25 L14 25 Q6 23 10 16 Z" fill="url(#shroud)"/>'
            + g(arr, 20, 38) + g(arr, 32, 42) + g(arr, 44, 38))


@icon('Withering Shot')
def _():
    return (g(arrow('url(#steel)', '#44523f'), 30, 28, -22)
            + poly('M42 40 L47 46 L52 40', '#d6a0ff', 2.4)
            + poly('M42 48 L47 54 L52 48', '#a860e0', 2.4))


@icon('Graveshot')
def _():
    return (g(skull(), 46, 42, 0, .6)
            + g(arrow('url(#steel)', '#44523f'), 28, 28, -30)
            + speed_lines(8, 42, 2, 9, 6, '#bfeccb', -30))


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
