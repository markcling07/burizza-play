"""Status-effect icons for Burizza.

Reads glyphs.json ({ "<fx id>": "<svg child markup>" }, drawn on a 64x64 canvas inside 9..55) and
writes one SVG per status into this folder, named by its FX id:
    status/<id>.svg      e.g. FX.burn -> status/burn.svg
plus status/gallery.html, a contact sheet at chip size and at full size.

The game shows a status as a chip (see .chip .ico in index.html), so every icon is a round
medallion in the colour of its kind - bad (crimson), good (green), neutral (steel) - with the same
ink outline, drop shadow and shared gradient palette as the skill icons in ../skills/make_icons.py.

Run:  python make_status_icons.py
"""
import json
import re
import sys
from html import escape
from pathlib import Path

OUT = Path(__file__).parent
INK = '#15121d'

# Medallion colours per kind: (background top, background bottom, rim)
PAL = {
    'bad':     ('#5c1a2d', '#18060d', '#e0455a'),
    'good':    ('#355d40', '#0e1d12', '#8ee696'),
    'neutral': ('#3e4c61', '#12171f', '#9fb4cf'),
}

# The same shared palette the skill icons use, so a flame or a drop looks identical in both sets.
DEFS = '''
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
<filter id="ds" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="1.4" stdDeviation="1" flood-color="#000" flood-opacity=".55"/></filter>
'''
ALLOWED_URLS = set(re.findall(r'id="([a-zA-Z]+)"', DEFS)) - {'ds'}
FORBIDDEN_TAGS = ('svg', 'defs', 'text', 'image', 'script', 'style', 'use', 'foreignObject')


def check(fx_id, glyph):
    """Hard rules a glyph must meet before it is framed. Returns a list of problems (empty = fine)."""
    problems = []
    for tag in FORBIDDEN_TAGS:
        if re.search(rf'<\s*{tag}\b', glyph, re.I):
            problems.append(f'forbidden <{tag}>')
    if re.search(r'\bid\s*=', glyph):
        problems.append('id= attribute')
    if re.search(r'\bfilter\s*=', glyph):
        problems.append('filter= attribute')
    for ref in re.findall(r'url\(#([a-zA-Z0-9_-]+)\)', glyph):
        if ref not in ALLOWED_URLS:
            problems.append(f'unknown url(#{ref})')
    # well-formed when wrapped
    try:
        import xml.dom.minidom
        xml.dom.minidom.parseString(f'<svg xmlns="http://www.w3.org/2000/svg">{glyph}</svg>')
    except Exception as e:  # noqa: BLE001
        problems.append(f'not well-formed: {e}')
    return problems


def medallion(kind, glyph, fx_id, label):
    top, bot, rim = PAL[kind]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Burizza status icon: {escape(label)} ({fx_id}, {kind}). Generated by status/make_status_icons.py, 64x64. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="128" height="128">
<defs>{DEFS}<radialGradient id="bg" cx=".5" cy=".3" r=".85"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></radialGradient></defs>
<circle cx="32" cy="32" r="30" fill="url(#bg)"/>
<circle cx="32" cy="32" r="26" fill="none" stroke="{rim}" stroke-width="1" opacity=".35"/>
<g filter="url(#ds)" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round" transform="translate(32 32) scale(.9) translate(-32 -32)">{glyph}</g>
<circle cx="32" cy="32" r="30" fill="none" stroke="{rim}" stroke-width="2.2"/>
</svg>
'''


def gallery(rows):
    cells = ''.join(
        f'<figure class="{kind}"><img class="big" src="{fid}.svg" alt=""><img class="chip" src="{fid}.svg" alt="">'
        f'<figcaption><b>{escape(label)}</b><small>{fid}</small></figcaption></figure>'
        for fid, label, kind in rows)
    return f'''<!doctype html><meta charset="utf-8"><title>Burizza status icons</title>
<style>
body{{margin:0;padding:18px;background:#161925;color:#ece6d8;font:14px/1.3 "Segoe UI",system-ui,sans-serif}}
h1{{font-size:18px;margin:0 0 12px}} .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:10px}}
figure{{margin:0;padding:8px;border-radius:10px;background:#1e2232;border:1px solid #3a4058;display:grid;justify-items:center;gap:4px}}
figure.bad{{border-color:#5c1a2d}} figure.good{{border-color:#355d40}} figure.neutral{{border-color:#3e4c61}}
img.big{{width:64px;height:64px}} img.chip{{width:16px;height:16px;margin-top:-2px}}
figcaption{{text-align:center}} figcaption b{{display:block;font-size:12px}} figcaption small{{color:#a29fb2;font-size:10px}}
</style>
<h1>Status icons - {len(rows)} (big = 64px, small = the 16px battle chip)</h1><div class="grid">{cells}</div>'''


def main():
    src = OUT / 'glyphs.json'
    if not src.exists():
        sys.exit('status/glyphs.json not found')
    data = json.loads(src.read_text(encoding='utf-8'))
    # data: { id: { "label":..., "kind":..., "glyph":... } }
    bad = {}
    rows = []
    for fid, rec in data.items():
        probs = check(fid, rec['glyph'])
        if probs:
            bad[fid] = probs
            continue
        (OUT / f'{fid}.svg').write_text(medallion(rec['kind'], rec['glyph'], fid, rec['label']), encoding='utf-8', newline='\n')
        rows.append((fid, rec['label'], rec['kind']))
    (OUT / 'gallery.html').write_text(gallery(rows), encoding='utf-8', newline='\n')
    print(f'wrote {len(rows)} icons; rejected {len(bad)}')
    for fid, probs in bad.items():
        print(f'  REJECT {fid}: {"; ".join(probs)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
