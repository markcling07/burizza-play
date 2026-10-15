# Burizza art assets

The catalogue, standards, and provenance for every drawn asset in the game.
`node tests/assets.js` enforces the contract described here against the files on
disk and the game's own data — run it after adding or renaming any asset.

## Provenance and ownership

All art in this repository — the character SVGs under `characters/`, the skill
icons under `skills/`, and the animation clips under `characters/animations/` —
is **original work created for Burizza and owned by the project maintainer**. No
asset is licensed from or derived from a third party, so none carries an
external licence obligation. If that ever changes — a commissioned or licensed
asset enters the tree — record it per file in the table below with its source
and licence, and the blanket statement above no longer applies to that row.

## Where art lives

| Kind | Path | Format | Canvas | Named |
|------|------|--------|--------|-------|
| Champion art | `characters/<folder>/<id>.svg` | SVG | `viewBox="0 0 100 100"`, feet near y=94, faces right | `<id>.svg` |
| Champion variant | `characters/<folder>/<id>-<tag>.svg` | SVG | same | e.g. `garrick-ward.svg` |
| Monster art | `characters/monsters/<id>.svg` | SVG | `0 0 100 100` | `<id>.svg` |
| Summon art | `characters/summons/<id>.svg` | SVG | `0 0 100 100` | `<id>.svg` |
| NPC art | `characters/npcs/<id>.svg` | SVG | `0 0 100 100` | `<id>.svg` |
| Skill icon | `skills/<slug>.svg` | SVG | `viewBox="0 0 64 64"` | skill name slugged: `Siren's Hush` → `sirens-hush.svg` |
| Animation | `characters/animations/<id>-<action>.{gif,webp}` | GIF + WebP pair | — | `aelira-idle.webp` |

The faction → folder map is `ART_FOLDER` in `index.html`; `stone` lives in
`stoneleaf`, `tide` in `tideborn`, every other faction in a folder of its own
name. Two factions must never share a folder — that is how a champion would end
up wearing another faction's art.

Every filename is kebab-case: lowercase, digits and single hyphens only.

## The fallback contract — why art is optional

No champion, monster, or summon needs an art file to appear in play. Each has a
procedural `look: { body: … }` recipe (a key into `BODIES`), and a global
`error` handler in `index.html` swaps any art `<img>` that fails to load for the
built-in drawing of that recipe. So a missing or not-yet-drawn file renders as a
clean placeholder, never a broken image. Three consequences the guard test pins
down:

- **Every non-copy id must carry a valid `look.body`.** That recipe *is* the
  fallback; without it a missing file would break.
- **A copy summon (Illusion, Double) carries no `look.body` on purpose.** It is
  spawned with `art = ` its caster's id and wears the caster's appearance.
- **A missing skill icon or animation is dropped silently** — the skill still
  works, the SVG underneath an animation still shows.

This is what lets characters and animations be added or updated by dropping in a
file, with no interface change (roadmap Phase 6's completion condition).

## Adding or updating a character

1. Add the roster/monster/summon entry in `index.html` with a `look.body` that
   exists in `BODIES`. The character is now fully playable, drawn procedurally.
2. Optionally drop `characters/<folder>/<id>.svg` (a `0 0 100 100` SVG) to give
   them bespoke art. No code change — the loader finds it by id.
3. Optionally add `skills/<slug>.svg` icons and `characters/animations/` clips.
4. Run `node tests/assets.js` and `node tests/harness.js`.

## Coverage (not a requirement — the rest fall back)

Counts drift as art is drawn; `node tests/assets.js` prints the live figures.
At the time of writing: **40/40 champions** and 15/31 monsters have bespoke art —
every champion is now drawn, so none fall back to a `look` recipe in play. The
monster ids that remain still render from theirs. 206/225 champion-skill icons
are drawn — the newest skills (Shazrak's cairn kit: Mana Cairn, Quickening Stone,
Unweaving Stone, Storm Cairn, Bulwark Stone, Binding Chord, Mana Battery, and the
rest) have none yet and show without an icon until one is added.

The fallback contract above still holds and is still tested: full coverage is a
snapshot, not a new requirement. Deleting any champion SVG must still leave that
champion playable on its `look.body` recipe.
