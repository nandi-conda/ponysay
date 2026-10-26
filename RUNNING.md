# How to run

This repository is a ponysay fork with emo `dear diary, ...` quotes and
emo-styled artwork for Twilight Sparkle and Fluttershy.  The build/run
workflow is managed by [pixi](https://pixi.sh); the manifest is
[`pixi.toml`](pixi.toml) at the repo root and the pinned lockfile is
[`pixi.lock`](pixi.lock).

## Prerequisites

- **pixi** — the lockfile was generated with pixi 0.83.0 (lockfile format v7).
  Install from <https://pixi.sh> and make sure `pixi` is on `PATH`.
- **conda-forge access** — pixi resolves `python` from `conda-forge`
  (currently `python 3.13.17`).
- **No texinfo/makeinfo needed** — the optional info manual is the only part
  that needs texinfo, so texinfo is intentionally *not* declared in the
  default environment.  The default build task pins it away with
  `--without-info`.

The sandbox note still applies for bare `python3` calls outside pixi: prepend
`/.sprite/languages/python/pyenv/shims` to `PATH` if the system python shim is
broken.

## DeepSeek API balance check

[`scripts/deepseek-balance.py`](scripts/deepseek-balance.py) queries the
official DeepSeek account balance endpoint
(`GET https://api.deepseek.com/user/balance`) with the
`Authorization: Bearer <API key>` header and prints, for each currency, the
total / granted / topped-up balances and whether the balance is sufficient
for API calls.

The API key is read from the `DEEPSEEK_API_KEY` environment variable (or the
`--api-key` argument) and is never printed. Use the environment variable so
the key does not appear in the process list:

```sh
DEEPSEEK_API_KEY=sk-... python3 scripts/deepseek-balance.py
```

The script needs only the Python standard library. Run it with a working
`python3`; in this sandbox that means the same PATH note as the build tasks
above.

## Pixi tasks

Run these from the repository root.

### `pixi run build`

Builds ponysay in `ponysay/` with:

```sh
python3 setup.py --freedom=partial --without-info --without-man --without-shell build
```

This compiles the quote data and produces the installable `ponysay.install`
zipapp without requiring texinfo.

### `pixi run quotes`

Compiles only the quote data: `ponysay/ponyquotes/*.<N>` →
`ponysay/quotes/<group>.<N>`.  Use this when you only want to regenerate the
compiled quotes.

### `pixi run install`

Installs ponysay into `.pixi/envs/default`.  The command is:

```sh
python3 setup.py --freedom=partial --without-info --without-man --without-shell --without-shared-cache --prefix "$PIXI_PROJECT_ROOT/.pixi/envs/default" install
```

`setup.py install` performs the build itself, so this works from a clean
checkout.  `--prefix` bakes the pixi environment's share directory into the
generated zipapp; `--without-shared-cache` stops a non-root install from
trying to create `/var/cache/ponysay`.

### `pixi run ponysay ...`

Runs the installed ponysay.  The task installs ponysay quietly on first use,
and reinstalls quietly whenever the source tree is newer than the installed
binary (for example after a quote or pony-art change), so it works from a
clean checkout and always serves current data without printing the full
install log.  With no arguments it prints a random quote from a random pony:

```sh
pixi run ponysay
```

Any arguments after the task name are passed through to `ponysay`:

```sh
pixi run ponysay -q twilight
pixi run ponysay -f twilight
pixi run ponysay -l
```

`-q twilight` prints an emo `dear diary, ...` twilight quote and renders the
emo twilight art (lavender coat, dark navy mane, hair lock over one eye,
choker and striped leg warmers).  `-q fluttershy` does the same for the emo
fluttershy art.  `-f twilight` renders the same art: when
stdin is a terminal it picks a random twilight quote, and when stdin is piped
it uses the piped text as the message (`echo hi | pixi run ponysay -f
twilight`).  `-l` lists the installed ponies.

`pixi run ponysay -h` prints the help (`+h` forces colours when piped).  Help
and `-l` output use bold and colour for headings and option names; only the
option arguments in the help synopsis are underlined, so no stray underline
is left on the following text.

### `pixi run ponysay --emo`

Prints a random pony among those tagged `EMO: yes`, together with one of her
quotes.  The wrapper translates `--emo` (short form `-e`) into
`ponysay -r emo=yes -q`:

```sh
pixi run ponysay --emo
```

`twilight` and `fluttershy` are the emo-tagged ponies, so this picks one of
the two at random and renders her emo art with a random `dear diary, ...`
quote.  Arguments after `--emo` are still passed through to ponysay, for
example `pixi run ponysay --emo -o` renders only the pony without a quote.
Use `--list-emo` (below) to print the emo-tagged ponies.

### `pixi run ponysay --list-emo`

Prints the names of the ponies tagged `EMO: yes`, one per line, and exits 0:

```sh
pixi run ponysay --list-emo
```

Current output:

```
fluttershy
twilight
```

The wrapper reads the `EMO: yes` header from the installed pony files
(`.pixi/envs/default/share/ponysay/ponies/*.pony`), falling back to
`ponysay/ponies/*.pony` when the installed data is missing.  The output is
plain text, sorted, and deterministic; ponies without an `EMO: yes` header are
not listed, and if nothing matches the command prints nothing and still exits
0.

`--list-emo` is a wrapper-level flag because `-r` only affects random
selection in core ponysay: `ponysay -l -r emo=yes` prints the same full list as
`ponysay -l`.  `--list-emo` takes precedence over `--emo` when both are given.

### `pixi run smoke`

Installs ponysay into `.pixi/envs/default` (via the `install` task) and then
runs `ponysay -q twilight`.  A successful run prints an emo
`dear diary, ...` twilight quote with the emo twilight artwork.

## Emo pony art

The emo theme also extends to the artwork.  Two ponies have emo art, Twilight
Sparkle and Fluttershy, and each has an xterm file and a Linux-VT file:

| pony | xterm art | Linux-VT art |
| --- | --- | --- |
| Twilight Sparkle | `ponysay/ponies/twilight.pony` | `ponysay/ttyponies/twilight.pony` |
| Fluttershy | `ponysay/ponies/fluttershy.pony` | `ponysay/ttyponies/fluttershy.pony` |

All four files carry the `EMO: yes` metadata tag, so they are selectable with
`ponysay -r emo=yes`.  The transformation keeps each pony's coat colours and
changes the hair to dark navy `#00005f`, then adds emo details:

- **Twilight Sparkle**: lavender coat/face preserved; mane dark navy
  (`#00005f`) with the magenta/pink streak; tail stays blue-grey with pink; a
  swept hair lock covers the far eye; the mouth is a subtle frown; dark navy
  choker; striped leg warmers.  Except for the eye pupil, the art uses no pure
  black.
- **Fluttershy**: yellow coat/face preserved (palette 228/178, highlight 222);
  the pink mane **and** tail (palette 218/175) become dark navy `#00005f`; a
  side-swept fringe covers the near eye; dark navy choker at the base of the
  neck; two navy stripes per leg.

The original (classic) art is kept intact alongside the emo art as
`twilightclassic` and `fluttershyclassic`; render them with:

```sh
pixi run ponysay -f twilightclassic
pixi run ponysay -f fluttershyclassic
```

The classic files are byte-identical copies of the pre-emo originals, and only
the plain pony name (`twilight`, `fluttershy`) selects the emo art.

To regenerate the emo art from the classic originals:

```sh
python3 scripts/make-emo-pony.py
```

The script is spec-driven for both ponies and idempotent: a second run
produces identical files and leaves the classic copies untouched.

## Running the installed binary directly

After `pixi run install`, `pixi run ponysay ...`, or `pixi run smoke`, the
installed binary can also be invoked by its absolute path:

```sh
.pixi/envs/default/bin/ponysay -q twilight
```

The installed `ponysay` is a zipapp with a `#!/usr/bin/env python3` shebang,
so the absolute-path form needs a working `python3` on `PATH`.  If `python3`
is not on `PATH` (for example, the broken sandbox shim), either prefer the
`pixi run ponysay` task form above, or put the pixi environment's `bin` first:

```sh
PATH="$PWD/.pixi/envs/default/bin:$PATH" .pixi/envs/default/bin/ponysay -q twilight
```

For other ponies, replace `twilight` with any name listed by
`pixi run ponysay -l`.

## Checking which emo art you are seeing

Verified on a clean clone of `main` at the Fluttershy art commit (`67bb265`).
pixi is not installed in this sandbox, so the checks ran the exact commands the
pixi tasks run (`setup.py ... install`, then `sh scripts/ponysay-run.sh ...`)
with Python 3.13.17, the version the lockfile pins.  `-q twilight`,
`-q fluttershy` and `--emo` render the **emo** artwork, and the installed
copies under `.pixi/envs/default/share/ponysay/` are byte-identical to the repo
files:

| pony | art | md5 |
| --- | --- | --- |
| twilight | emo xterm | `6559f8f83b6686e0368a242facdcf511` |
| twilight | emo Linux-VT | `47aee3c2f285ad3608f733196b005bc6` |
| twilight | classic xterm | `a46179ba979b5d691c1fb1d891eb1a38` |
| twilight | classic Linux-VT | `a83ced2a590fcbfdc56c966a6bdab70a` |
| fluttershy | emo xterm | `f18a6eaf87c7702180e65fc21221293f` |
| fluttershy | emo Linux-VT | `7f4c684ff3bc61b9508c4aecdc583071` |
| fluttershy | classic xterm | `d0d56f8949e299ad5f16d3bf803f9d6a` |
| fluttershy | classic Linux-VT | `60d70a626495edbf93a5b3bcb723933f` |

All four emo files carry `EMO: yes`; neither classic file does.

Visual markers:

- **Twilight emo**: lavender coat and face (same as classic); dark navy mane
  (`#00005f`) with the magenta/pink streak; tail blue-grey with pink; a swept
  hair lock covers the far eye (only one eye visible); subtle frown; dark navy
  choker at the neck; dark navy horizontal bars across the legs (striped leg
  warmers).  The art uses no pure black except the eye pupil.
- **Twilight classic**: light lilac mane and face; both eyes and a smile
  visible; no choker; plain legs.
- **Fluttershy emo**: yellow coat and face (same as classic); pink mane and
  tail replaced by dark navy (`#00005f`); a side-swept fringe covers the near
  eye; dark navy choker; two navy stripes per leg.
- **Fluttershy classic**: pink mane and tail; both eyes visible; no choker;
  plain legs.
- Colour is a better marker than shape here: for Twilight the magenta mane
  streak is **not** useful (both art files have it), and for Fluttershy the
  pink mane/tail is the marker (the emo art has no pink).

Both emo arts render fully at 80 columns in xterm and Linux VT: Twilight is
53 columns wide and Fluttershy 54.  For both, the art-only render
(`ponysay -o -f <pony>`, plus `-V` for Linux VT) at 80 columns is
byte-identical to the `PONYSAY_FULL_WIDTH=1` render.  The emo Fluttershy TTY
art avoids `]P...0` palette definitions on its art rows; the generator nudges
the blue step (`#d7af00` → `#d7af01`, `#000000` → `#000001`), which looks the
same but does not trip `Backend.getColour`'s over-read.  Art with large
pure-black areas would still be truncated at 80 columns.

The **classic** Fluttershy TTY art still truncates at 80 columns.  It is the
untouched upstream art, which uses `]P...0` palette definitions, so this is a
pre-existing `Backend.getColour` defect and not an emo regression: at 80
columns it renders byte-identically to the pre-emo checkout (`fac2a7f`).  The
classic Twilight TTY art does not truncate.

Command-line tells:

```sh
pixi run ponysay -l          # lists twilight, fluttershy and both *classic*
                             # twins; bold = the pony has quotes
grep '^EMO' ponysay/ponies/twilight.pony ponysay/ttyponies/twilight.pony \
            ponysay/ponies/fluttershy.pony ponysay/ttyponies/fluttershy.pony
pixi run ponysay -q fluttershy        # emo fluttershy art + dear diary quote
pixi run ponysay -q twilightclassic   # classic art + fallback quote
                                      # "Zecora! Help me, I am mute!"
```

The two `*classic` ponies have no quote file, so `-q twilightclassic` and
`-q fluttershyclassic` print the built-in fallback quote.
`pixi run ponysay -f twilightclassic -q` prints the classic art with an
**empty** balloon: `-q` at the end takes no pony argument, so the message is
read from stdin (empty in a non-interactive run).

The `-r` restriction must come **before** `-q`.  `-q` takes the pony name as
its argument, so `ponysay -q -r emo=yes` treats `-r` as the pony name and
`emo=yes` as the message.  With `PONYSAY_TYPO_LIMIT=0` that fails with
`I have never heard of anypony named -r` (exit 252); with the default typo
correction it quietly renders some other pony (observed `tom`, `cow`, `joe`
and `zecora`).  Use:

```sh
pixi run ponysay -r emo=yes -q     # a random emo pony, always
pixi run ponysay --emo             # same, via the wrapper
```

### Stale installs

`scripts/ponysay-run.sh` installs ponysay when
`.pixi/envs/default/bin/ponysay` is missing, and reinstalls when any file
under `ponysay/` is newer than that binary.  A `.pixi/` created before the
emo art landed therefore refreshes on the next `pixi run ponysay` instead of
rendering the old classic art.  Verified in a clean clone: after checking
out a newer commit over an existing environment, the first
`pixi run ponysay -q twilight` rebuilt the binary (mtime changed) and
rendered the emo art; immediate repeat runs did not reinstall (mtime
unchanged).

The mtime check compares the repo tree with the installed binary only.  It
does not detect an installed copy that was changed out-of-band (for example
copying `twilightclassic.pony` over the installed `twilight.pony`): that
keeps rendering the classic art until you run `pixi run install` (or remove
`.pixi/`).  `.pixi/` is gitignored, so a fresh checkout is never stale.

### Merge status

Both emo ponies are on `main`: `67bb265` ("Add emo Fluttershy art alongside
classic original") adds the Fluttershy art and turns
`scripts/make-emo-pony.py` into a spec-driven generator for both ponies.  The
earlier emo commits are ancestors too: `10e1701` added the first emo Twilight
art and `63bff1a` redesigned it (lavender coat, dark navy mane).  All
`origin/thread/*` topic branches are contained in `main`; there is no separate
emo branch.  The only refs ahead of `main` are harness session and snapshot
refs (`origin-sessions/*`, `origin-snapshots/*`), so
`git log --all --not main` shows snapshots, not unmerged work.
The classic xterm and TTY files for both ponies are byte-identical to the
pre-emo originals.
