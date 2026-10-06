# Ashfall Road character art

The game loads every character from this folder:

```
characters/<faction>/<id>.svg
```

| Folder      | Faction            | Characters                                   |
|-------------|--------------------|----------------------------------------------|
| `mech`      | Ironclad Union     | bulwark, sawtooth, arclight, howitzer, patchwork |
| `orc`       | Bloodtusk Horde    | krug, mogra, vashka, drekka, hesk            |
| `human`     | Kingdom of Aldmere | wren, garrick, mara, aldous, liesl           |
| `stoneleaf` | Stoneleaf Accord   | durgan, hilda, aelira, faelan, elowen        |
| `tideborn`  | The Tideborn       | tharos, grubble, seraphine, octavia, maren   |
| `crimson`   | The Crimson Court  | vesper, malgrath, seraxa, gorehound, morwenna |
| `summons`   | Summoned units     | scrapbot (Patchwork), warboar (Vashka), risen (Drowned Abbot) |
| `monsters`  | Cave and dungeon monsters | cinderbat, ashcrawler, magmaslime, bonerattler, glowcap, cavetroll, cryptghoul, wraith, clockspider, rustgolem, emberimp, ashdrake |
| `monsters`  | Dungeon bosses     | abbot (Sunken Crypt), ironjaw (Rustgut Mine), ashmaw (Ashen Spire) |
| `npcs`      | Cinderhold villagers | keepers: brann (Ironsmith), mott (Market), hesta (Tavern), ysolde (Elder's Hut), roska (Arena); townsfolk: pip, fenwick, holt, lyra, bolt, nessa |

Village NPCs are not champions and never fight. Keepers stand by their building and greet you inside it; three random townsfolk stroll the square on each visit and talk when clicked. Their names and lines are in `index.html` (`KEEPERS`, `TOWNSFOLK`). A missing NPC file shows a plain hooded villager.

Octavia's Ink Illusion has no file of its own: it reuses Octavia's art with an ink tint.

## Animation

A champion also animates on the battlefield if `animations/` has clips for them. The SVG above
stays the fallback and is what the speed bar, the champion cards and the village always use.

```
characters/animations/<id>-idle.webp     loops while the champion stands
characters/animations/<id>-attack.webp   plays once when they act
characters/animations/manifest.json      what the game needs to place and time them
```

Each manifest entry gives both clips' `w`/`h`, the `footX`/`footY` the character stands on, and
the attack's `ms` (how long the whole clip runs) and `hitMs` (when the blow lands). The game scales
each clip so its foot point sits exactly where the SVG's does, and holds the damage back until
`hitMs`, so the number appears on the frame the weapon connects. A clip that swings more than once
can list every impact in `hitsMs`; multi-hit skills use the gap between the first two to pace their
follow-up hits against the clip already playing.

Drop in a new champion's clips by adding the two files and a manifest entry. Leave the entry out
and that champion just keeps their SVG — as does everyone, if the manifest is missing or the
visitor has asked for reduced motion. `animations/battle-test.html` plays every clip against a
ground line for checking alignment and transparency.

## Rules for new art

- **Keep the file name.** The game finds art by `<id>`, e.g. `human/wren.svg`.
- **Face right.** Enemies are mirrored automatically.
- **Square canvas, transparent background.** The current files are 100×100 units, shown at up to about 170px.
- **Same footing for everyone.** Feet sit near the bottom (y = 94 of 100) so characters line up.
- **Missing or broken file?** The game falls back to its built-in placeholder, so you can replace characters one at a time.

## Switching to PNG

1. Save PNGs with the same names, e.g. `human/wren.png` (512×512 works well).
2. In `index.html`, change `const ART_EXT = 'svg';` to `const ART_EXT = 'png';`.

All characters must then have a PNG, or they will show the placeholder.

## Editing tools

SVG: Inkscape (free), Figma, Illustrator. PNG: Aseprite or LibreSprite for pixel art, Krita (free) for painted art.
