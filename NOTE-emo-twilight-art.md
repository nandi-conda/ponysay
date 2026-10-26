# Emo Twilight renders as a dark blob — diagnosis

Diagnosis only: no art, source, wrapper, or doc files were changed. The note
records the root cause and a validated fix proposal. The art files and
`scripts/make-emo-pony.py` belong to t_b530b9d0; `RUNNING.md` belongs to
t_2d6b74f6.

Baseline: `main` = 24e0634.

## Verdict

1. **The emo art files themselves are the cause of the "terrible" look.** The
   renderer reproduces `ponysay/ponies/twilight.pony` pixel for pixel, the
   classic art renders correctly through the same pipeline, and the emo art
   renders exactly the same way at 10e1701 (the commit that landed it) — the
   art was born broken and nothing since then changed it.
2. **`scripts/make-emo-pony.py` recolors the wrong palette entries.** It treats
   the lavender *coat* colors (182/139/96) as the mane, so the body, neck,
   back and hindquarters turn dark plum/black, while the real mane (hair
   palette 60/61/54 and the 97 edge) stays purple. Its detail rectangles
   (fringe, eyeliner, "wing") also land on the wrong body parts: the eyeliner
   is painted on the flank/cutie mark, not the eyes.
3. **Secondary, TTY only:** a pre-existing `Backend.getColour` bug inflates the
   width of TTY palette escapes, so `TERM=linux` renders of the emo tty art are
   truncated at 80 columns. Classic tty art is unaffected. This is a separate
   defect from the ugly art; a one-line fix is verified below.

## Reproduction

`pixi` is not installed in this sandbox (same as t_ccaf7cde reported), so I ran
the exact commands the pixi tasks run, with python3 3.13.17:

```sh
cd ponysay
python3 setup.py --freedom=partial --without-info --without-man \
    --without-shell --without-shared-cache \
    --prefix "$PWD/../.pixi/envs/default" install          # pixi run install
cd ..
PIXI_PROJECT_ROOT=$PWD sh scripts/ponysay-run.sh -q twilight        # pixi run ponysay -q twilight
PIXI_PROJECT_ROOT=$PWD sh scripts/ponysay-run.sh --emo              # pixi run ponysay --emo
PIXI_PROJECT_ROOT=$PWD sh scripts/ponysay-run.sh -f twilightclassic # pixi run ponysay -f twilightclassic
```

All runs were done under a real pty (Python `pty.openpty`, 100x40 and 80x40),
with `TERM=xterm-256color` for the xterm pony and `TERM=linux` for the tty
pony. Every command exits 0.

| command | result |
| --- | --- |
| `-q twilight` (xterm) | emo art (dark blob) + `dear diary, ...` quote |
| `--emo` (xterm) | same emo art + emo quote |
| `-f twilightclassic` (xterm) | classic art, recognizable, unmodified |
| `-q twilight` (TERM=linux) | same emo defects in the 16-color tty art |
| `-f twilightclassic` (TERM=linux) | classic tty art, recognizable |

## The pipeline is not the culprit (evidence)

| check | result |
| --- | --- |
| installed share copy vs repo file | byte-identical: xterm `a3b1d64d3baf1842748c8bd58c73d905`, tty `582bedcf8d8b2deefb9bcba192086ed2`, classic `a46179ba979b5d691c1fb1d891eb1a38` |
| pty output vs art file, subpixel comparison | xterm: **0** differing subpixels (2650 checked); tty: only the cells explained by the 80-column truncation below |
| render at HEAD vs a build of 10e1701 (`-f twilight 'test message'`) | byte-identical for xterm emo, xterm classic and tty emo |
| art history | only 10e1701 ever changed `ponies/twilight.pony` or `ttyponies/twilight.pony`; no art commit is unmerged (`git log --all --not main -- ponysay/ponies/twilight.pony ponysay/ttyponies/twilight.pony` is empty) |
| re-run `scripts/make-emo-pony.py` on the classic files | reproduces both committed emo files byte-for-byte (the script is idempotent) |
| SGR 21 -> 22 change (3f5a2e0) | touches help/list/ponysay-tool text only; pony files contain no SGR 21 or 22 and the pony render path is untouched |
| ponysay.py quote-selection change (1839aa3/584d250) | only chooses a quote when stdin is a tty; does not touch the art |
| wrapper reinstall (`scripts/ponysay-run.sh`) | works: touching the art file made the next run reinstall (binary mtime changed) and the installed art stayed correct |
| classic art through the same build | renders correctly (both xterm and tty) |

## Root cause: the emo transform in `scripts/make-emo-pony.py`

Twilight's classic palette (subpixel counts in the 53x48 art, xterm; the tty
file has the same counts):

| index | RGB | role | classic | current emo |
| --- | --- | --- | --- | --- |
| 182 | `#d7afd7` | coat (light lavender) | 225 | 92 |
| 139 | `#af87af` | coat shade | 54 | 17 |
| 96 | `#875f87` | coat deep shade | 36 | 19 |
| 97 | `#875faf` | mane edge / neck and leg-outline accent | 124 | 104 |
| 60 | `#5f5f87` | mane + tail (gray-blue) | 143 | 143 |
| 61 | `#5f5faf` | mane + tail (blue-violet) | 27 | 22 |
| 54 | `#5f0087` | mane + tail (dark violet) | 48 | 78 |
| 205/169 | pink | mane + tail streak | 72 | 72 |
| 16 | black | pupils | 11 | 83 |
| 53 | `#5f005f` | (new) dark plum | 0 | 119 |

The script (`MANE_MAP` at line 181, `keep()` at 182) maps
`182 -> 53, 139 -> 54, 96 -> 16`. Those are the **coat**, not the mane:
133 of the 225 coat-182 subpixels are darkened (plus most of the 139/96
shades), so 59% of the light-lavender coat disappears. The `keep()` box only
protects part of the face/chest (subpixel rows 16-29 cols 13-31 and rows 30-44
cols 18-31), so the neck, back, flank and hindquarters go dark. The actual mane
palette (60/61/54 + the 97 edge) is left almost untouched.

The detail edits are blind rectangles at coordinates that do not match this
art:

| rule | script coordinates | where it actually lands |
| --- | --- | --- |
| recolor | every 182/139/96 outside `keep()` | 117 subpixels of coat (182 -> 53 x69, 139 -> 54 x31, 96 -> 16 x17); body/neck/back/legs turn dark |
| fringe | subpixel rows 17-21, cols 13-24 -> 53 | a flat 12-cell-wide plum block across the right half of the face (cells rows 8-10, cols 13-24): 31 coat, 2 coat-shade, 5 mane, 2 mane-edge, 6 outline and 9 pupil pixels (it lightens 16 -> 53), covering the far eye, cheek and outline |
| eyeliner | rows 24-25 cols 24-32; row 30 cols 25-31 -> 16 | cell row 12 (flank/back), not the eyes (eyes are cells rows 8-10): 14 coat, 4 mane-edge, 1 outline and 2 of the 5 white cutie-mark pixels (231 -> 16) |
| "wing" | rows 26-28 col 31 -> 16 | 3 coat pixels on the body outline at the flank |
| frown | (26,16), (27,16), (28,17) -> 16 | 3 mane-edge pixels at the muzzle; plausible, but it is drawn on top of the existing mouth |
| choker | row 23 cols 12-17 -> 16 | the neck (cell row 11 bottom): correct (3 coat, 1 coat-shade, 1 mane-edge, 1 dark-violet pixel) |
| leg warmers | rows 34-35, 38-39, cols 20-23 and 29-31 -> 16 | cells rows 17/19 on the legs: correct (15 coat, 3 coat-shade, 10 mane-edge pixels) |

The table lists rule writes; some cells are written twice, so the total is 236
writes but 228 net changed subpixels (xterm and tty are identical here). The result
is the dark blob in the report: dark head/face, dark neck and body, black bars
on the back and legs, and only the chest/front legs still lavender.

The grid round-trip is not the problem (re-running the script reproduces the
committed files). One latent serializer bug: `cell_to_subpixels` treats `▌`/`▐`
as top/bottom halves instead of left/right halves. Twilight's art does not use
them, so it does not affect this image, but it would corrupt other ponies if
the script were reused.

## Fix proposal

### A. Art (owner: t_b530b9d0)

Rewrite the transform to recolor the **hair**, not the coat, and drop the
misplaced rectangles:

1. Remove `MANE_MAP` (182/139/96) and `keep()` entirely. Keep the coat colors
   182/139/96 unchanged.
2. Recolor the hair colors only in the mane region: `60 -> 16`, `61 -> 16`,
   `54 -> 53`, `97 -> 16` (or `53` for a softer plum) for cells with column
   `< 30`. Excluding columns >= 30 keeps the tail's original gray-blue + pink
   (the tail shares the hair palette and starts around column 30).
3. Keep the choker (subpixel row 23, cols 12-17) and the leg warmers (rows
   34-35 and 38-39, cols 20-23 and 29-31); they are correctly placed.
4. Drop the fringe, eyeliner and "wing" rectangles. If a fringe over one eye
   is wanted, use the eye next to the mane (cells rows 8-10, cols 12-14) and
   paint a 1-2 cell-wide lock, not a 12-wide block. Reference coordinates from
   the classic art: eyes at cells rows 8-10 (pupils at col 12 and cols 17-18),
   muzzle/mouth at rows 13-14 cols 16-22, neck at row 11 bottom cols 12-17,
   front legs cols 20-23, hind legs cols 29-31 (rows 16-22).
5. Prefer doing the recolor as a direct SGR-parameter substitution on the
   classic text (`38;5;N` / `48;5;N`), and use the grid only for the hand-placed
   details. That keeps the geometry byte-exact and avoids the `▌`/`▐` bug.
6. Validate with a color-histogram assertion before committing: coat 182 must
   stay ~225 (current emo: 92), 97 must drop to near 0 (current: 104), and
   `16` should grow only by the mane pixels. Then render and look at it.

I validated this recipe in a scratch copy (not in the repo, no preview
committed): hair recolor in columns < 30 plus a one-eye fringe, the choker and
the leg warmers renders as a recognizable lavender Twilight with a black mane
and pink streak, one eye covered, striped legs, and the original gray-blue
tail. The current committed file renders as the dark blob.

**Fast fallback** if the art cannot be redone before landing: copy
`twilightclassic.pony` over `twilight.pony` in both `ponies/` and
`ttyponies/` and decide whether to keep `EMO: yes`. The emo quote set still
works; the art is the known-good classic. `RUNNING.md`'s emo-art description
would then need to change (t_2d6b74f6).

### B. TTY truncation (needs an owner; it is a `src/backend.py` fix)

`Backend.getColour` (ponysay/src/backend.py:411-419) reads the 7-character
KMS palette payload `ESC ] P <index><rrggbb>` and then falls through into the
generic OSC handling. If the payload's last hex digit is `0` (for example
`]P0000000` or `]P8000000`), the `while c == '0':` loop consumes the following
ESC. `Backend.len` and `__truncate` then count the next SGR body (e.g.
`[30;01m`) as visible text, so widths are inflated. Measured with the script's
own `Backend.len` on the tty files: emo lines reach 103 columns, classic lines
stop at 77.

Visible effect at 80 columns (`TERM=linux`, fixed message so the balloon does
not vary):

- `ponysay -f twilight 'test message'` truncates rendered lines 17 and 21
  (53 -> 30 and 46 -> 44 visible columns); `-o -V` truncates the same two
  art lines (rendered 13 and 17 there, because there is no balloon).
- `ponysay -f twilightclassic 'test message'` is unaffected.
- `PONYSAY_FULL_WIDTH=1` restores the missing columns.
- xterm (`TERM=xterm-256color`) is unaffected at 80 columns.

Minimal fix, verified on a scratch build: return immediately after the `]P`
payload loop, i.e. add `return rc` after the `while (di < 7) ...` block (before
`while c == '0':`). With that one line the emo tty output at 80 columns is
byte-identical to `PONYSAY_FULL_WIDTH=1`, and classic output is unchanged.

Why emo and not classic: the emo tty file writes two palette defs per colour
change (`ESC ] P 8 <fg>` then `ESC ] P 0 <bg>`) followed by a long combined SGR
(`ESC [30;01;40m`), while the classic file writes one def followed by a short
SGR (`ESC [45m`). Each overread therefore costs about 10 phantom columns in the
emo file and about 4 in the classic one (emo worst line: 53 visible + 50
phantom = 103; classic worst: 53 + 24 = 77). So it is the emo file's escape
layout, not just its colours, that crosses 80 columns.

This bug predates the emo work (`git log -S 'di < 7'` -> cef7f33, the initial
import), so it is not a regression from the recent commits. An art-side
workaround (classic-style single defs / avoiding `#000000` payloads) would only
move the threshold and stays fragile; fix `getColour`.

## Not to blame

- The SGR 21 -> 22 bold-off change (3f5a2e0): help/list/tool text only.
- The ponysay.py quote-selection change and the wrapper reinstall
  (1839aa3, 584d250): wrapper reinstall verified; renders are byte-identical
  to a 10e1701 build.
- Stale install: installed art is byte-identical to the repo.
- The rendering pipeline: the classic pony proves it can render a good image,
  and the emo output matches its file exactly.
