# Second emo pony (Fluttershy): clean-checkout verification

Verification only: no art, wrapper, pixi manifest, or source files were changed
by this thread.  The only edits are documentation (`RUNNING.md`,
`ponysay/EMO-QUOTES.md`) and this note.

Verified commit: `67bb265` ("Add emo Fluttershy art alongside classic
original"), which is on `main`.  Baseline for pre-emo comparisons: `fac2a7f`.

## Environment

`pixi` is **not installed in this sandbox** (`which pixi` prints nothing), so
the checks ran the exact commands the pixi tasks run, with Python 3.13.17 (the
version in `pixi.lock`):

```sh
# pixi run install
cd ponysay && python3 setup.py --freedom=partial --without-info \
    --without-man --without-shell --without-shared-cache \
    --prefix "$ROOT/.pixi/envs/default" install

# pixi run ponysay ...      (the wrapper installs on first use)
PIXI_PROJECT_ROOT="$ROOT" sh scripts/ponysay-run.sh --list-emo
PIXI_PROJECT_ROOT="$ROOT" sh scripts/ponysay-run.sh --emo
PIXI_PROJECT_ROOT="$ROOT" sh scripts/ponysay-run.sh -e
PIXI_PROJECT_ROOT="$ROOT" sh scripts/ponysay-run.sh
PIXI_PROJECT_ROOT="$ROOT" sh scripts/ponysay-run.sh -q fluttershy
$ROOT/.pixi/envs/default/bin/ponysay -q fluttershy
$ROOT/.pixi/envs/default/bin/ponysay -q fluttershy -V    # Linux VT

# pixi run smoke
$ROOT/.pixi/envs/default/bin/ponysay -q twilight
```

Clean checkout (no `.pixi`, no untracked files):

```sh
git clone --no-hardlinks /home/sprite/threads/t_4b2cdf70 /tmp/clean067
git -C /tmp/clean067 checkout --detach 67bb265
```

The same harness was re-run from a fresh clone of the documentation commit
(the art tree is unchanged): 40 checks, 0 failed.

Rendering was captured under a real 80x40 pty (`TERM=xterm-256color` for the
xterm art, `TERM=linux` with `-V` for the Linux-VT art).  The harness parses
the ANSI output back into top/bottom-half subpixel cells and compares those
against the same parse of the art file, so a match means the rendered art is
the stored art, not merely the same size.  Quote lines are unwrapped from the
balloon and checked against the pony's own `ponyquotes` group.  **40 checks,
0 failed.**

## Requirement results

1. **`--list-emo` lists both ponies.**  Exit 0, deterministic, output exactly
   two lines in C order:
   `fluttershy` then `twilight`.
2. **`--emo` / `-e` picks a random emo-tagged pony with an emo quote.**
   The harness ran each flag 30 times through the wrapper: all exit 0, all
   rendered art matched exactly one emo art file, and every quote started
   `dear diary, ` and was a member of that pony's quote group.  A separate
   40-run sweep per flag counted the split: `--emo` 19 twilight / 21
   fluttershy, `-e` 22 twilight / 18 fluttershy.  `--emo -o` renders an emo
   pony with no balloon; `--emo --list-emo` still prints the list
   (`--list-emo` wins).
3. **`-q fluttershy` renders the emo art in xterm and tty at 80 columns.**
   Art matched pixel for pixel (0 differing subpixels) in both terminals; all
   art rows are the full 54 columns; the 80-column art-only render is
   byte-identical to the `PONYSAY_FULL_WIDTH=1` render.  The installed share
   copy is byte-identical to the repo file (emo xterm
   `f18a6eaf87c7702180e65fc21221293f`, emo tty
   `7f4c684ff3bc61b9508c4aecdc583071`).  Twilight's emo art is unchanged and
   still renders pixel-perfect at 53 columns in both terminals.
4. **`-f fluttershyclassic` is byte-identical to the original art.**  Classic
   xterm `d0d56f8949e299ad5f16d3bf803f9d6a` and classic tty
   `60d70a626495edbf93a5b3bcb723933f` equal
   `git show fac2a7f:ponysay/{,tty}ponies/fluttershy.pony`; the classic files
   have no `EMO` header.  `-f fluttershyclassic` renders the classic art
   pixel for pixel (xterm), `-q fluttershyclassic` prints the built-in
   fallback quote `Zecora! Help me, I am mute!`, and `-l` lists `fluttershy`
   and `fluttershyclassic`.  The emo pony is still reachable by its plain
   name.
5. **Bare `pixi run ponysay` is unchanged.**  `scripts/ponysay-run.sh` is not
   touched by `67bb265` (`git diff --name-only fac2a7f 67bb265` lists only
   the four art files and `scripts/make-emo-pony.py`).  Bare runs (piped stdin
   and three real-pty runs) exit 0 and print a random pony with a
   `dear diary, ...` quote.

`ponysay -q twilight` (the smoke command) still exits 0 and renders the emo
Twilight art.

## Corroborating checks

- **Coat preserved, only hair recoloured.**  xterm palette histogram,
  fluttershy classic -> emo: the pink mane (218, 341 cells) and tail (175, 296
  cells) disappear, dark navy (17) gains 726 cells, and the yellow coat
  entries stay in place (228: 187 -> 136, 178: 146 -> 125, 222: 48 -> 34; the
  reductions are the fringe, choker and leg stripes painted over them).  No
  coat colour is recoloured.
- **Twilight untouched.**  `git diff fac2a7f 67bb265` shows no change to
  `ponysay/ponies/twilight.pony`, `ponysay/ttyponies/twilight.pony` or either
  twilight classic file; their md5s are still `6559f8f8...` / `47aee3c2...`.
- **TTY palette avoids the width bug.**  In the emo fluttershy tty art, no
  `]P...` palette definition on an art row has a hex ending in `0`; the art
  rows use `#00005f`, `#000001`, `#d7af01`, etc.  The only `]P...0`
  definitions left are in the trailing standard 16-colour palette line, which
  carries no visible cells.
- **Regeneration is idempotent.**  Running `python3 scripts/make-emo-pony.py`
  twice on a copy of the clean checkout left all four fluttershy files and
  both twilight files byte-identical (same md5s before, after run 1 and after
  run 2; `git status` clean).
- **Installed share tree matches the repo** for the emo xterm and tty files
  of both ponies.
- **Render matrix on `67bb265`** (art-only, 80 columns, real pty): twilight
  emo, twilight classic and fluttershy emo are 0-subpixel diffs from their art
  files and byte-identical to the `PONYSAY_FULL_WIDTH=1` render in **both**
  xterm and Linux VT.  Only `fluttershyclassic` in Linux VT differs (4
  subpixels, shortened rows), the pre-existing truncation described below.

## Known limitation (not a regression)

`-f fluttershyclassic` in **Linux VT** still truncates some rows at 80
columns.  `fluttershyclassic` is the untouched upstream art, whose art rows
use `]P0;000000` / `]P..;D7AF00` definitions that `Backend.getColour`
over-reads; this is the pre-existing bug, not caused by the emo change.  At 80
columns the classic tty render from `67bb265` is byte-identical (12,177 bytes)
to the render of the original pony from the pre-emo checkout `fac2a7f`.  The
emo Fluttershy art and both Twilight arts do not truncate.

## Documentation updated

- `RUNNING.md`: intro, `--emo` and `--list-emo` text/output, a two-pony
  "Emo pony art" section with markers and the classic twins, the smoke task
  moved back under "Pixi tasks", a rewritten "Checking which emo art you are
  seeing" section with the full md5 table and 80-column results, and the merge
  status.
- `ponysay/EMO-QUOTES.md`: the artwork paragraph now covers both ponies, and
  the stale "three tasks" sentence lists the five pixi tasks.

## Full harness log

```
PASS art file exists: ponysay/ponies/fluttershy.pony
PASS art file exists: ponysay/ttyponies/fluttershy.pony
PASS art file exists: ponysay/ponies/fluttershyclassic.pony
PASS art file exists: ponysay/ttyponies/fluttershyclassic.pony
PASS --list-emo exit 0: exit 0
PASS --list-emo lists exactly twilight and fluttershy: ['fluttershy', 'twilight']
PASS --list-emo deterministic
PASS EMO: yes header in ponysay/ponies/fluttershy.pony
PASS EMO: yes header in ponysay/ttyponies/fluttershy.pony
PASS --emo exits 0 with an emo art + own emo quote (30 runs)
PASS --emo selected both emo ponies: ['fluttershy', 'twilight']
PASS -e exits 0 with an emo art + own emo quote (30 runs)
PASS -e selected both emo ponies: ['fluttershy', 'twilight']
PASS -q fluttershy (xterm) exit 0: exit 0
PASS -q fluttershy (xterm) quote is fluttershy's emo quote: 'dear diary, today i was a ghost in my own story, watching the happy parts from outside.'
PASS -q fluttershy (xterm) renders the emo art exactly: diff 0 subpixels at row 14, widths [54]
PASS -q fluttershy (xterm) full art width at 80 cols: widths [54] vs art 54
PASS -q fluttershy (xterm) 80-col art render == PONYSAY_FULL_WIDTH render: 6982 vs 6982 bytes
PASS -q fluttershy (tty) exit 0: exit 0
PASS -q fluttershy (tty) quote is fluttershy's emo quote: 'dear diary, i am a note left on the fridge that nopony reads twice.'
PASS -q fluttershy (tty) renders the emo art exactly: diff 0 subpixels at row 14, widths [54]
PASS -q fluttershy (tty) full art width at 80 cols: widths [54] vs art 54
PASS -q fluttershy (tty) 80-col art render == PONYSAY_FULL_WIDTH render: 9410 vs 9410 bytes
PASS installed fluttershyclassic (xterm) == repo file
PASS -f fluttershyclassic (xterm) exit 0: exit 0
PASS -f fluttershyclassic (xterm) renders the classic art
PASS installed fluttershyclassic (tty) == repo file
PASS -f fluttershyclassic (tty) exit 0: exit 0
PASS -f fluttershyclassic (tty) render matches the pre-emo original at 80 cols (truncation is pre-existing, not a regression): 12177 vs baseline 12177 bytes, diff 4 vs art, widths [33, 36, 37, 48, 52, 54]
PASS ponysay/ponies/fluttershyclassic.pony is byte-identical to pre-emo fluttershy.pony: d0d56f8949e299ad5f16d3bf803f9d6a vs d0d56f8949e299ad5f16d3bf803f9d6a
PASS ponysay/ttyponies/fluttershyclassic.pony is byte-identical to pre-emo fluttershy.pony: 60d70a626495edbf93a5b3bcb723933f vs 60d70a626495edbf93a5b3bcb723933f
PASS pre-emo original fluttershy had no EMO header
PASS -q fluttershy still selectable
PASS installed emo ponies/fluttershy.pony == repo file
PASS installed emo ttyponies/fluttershy.pony == repo file
PASS -l exit 0 and lists fluttershy and fluttershyclassic
PASS -q fluttershyclassic uses the fallback quote: 'Zecora! Help me, I am mute!'
PASS bare wrapper (no args, piped stdin) exit 0: exit 0
PASS bare wrapper in a terminal prints a random pony + emo quote (3 runs)
PASS smoke command (installed ponysay -q twilight) exit 0

40 checks, 0 failed
```
