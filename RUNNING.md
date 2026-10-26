# How to run

This repository is a ponysay fork with emo `dear diary, ...` quotes and an
emo-styled Twilight Sparkle artwork.  The build/run workflow is managed by
[pixi](https://pixi.sh); the manifest is [`pixi.toml`](pixi.toml) at the repo
root and the pinned lockfile is [`pixi.lock`](pixi.lock).

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
choker and striped leg warmers).  `-f twilight` renders the same art: when
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

`twilight` is currently the only emo-tagged pony, so this renders the emo
twilight art with a random `dear diary, ...` quote.  Arguments after `--emo`
are still passed through to ponysay, for example `pixi run ponysay --emo -o`
renders only the pony without a quote.  Use `--list-emo` (below) to print the
emo-tagged ponies.

### `pixi run ponysay --list-emo`

Prints the names of the ponies tagged `EMO: yes`, one per line, and exits 0:

```sh
pixi run ponysay --list-emo
```

Current output:

```
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

## Emo pony art

The emo theme also extends to the artwork for Twilight Sparkle.  Both the
xterm art (`ponysay/ponies/twilight.pony`) and the Linux-VT art
(`ponysay/ttyponies/twilight.pony`) render an emo Twilight: the lavender
coat/face is preserved, the mane is dark navy (`#00005f`) with the
magenta/pink streak, the tail stays blue-grey with pink, a swept hair lock
covers the far eye, the mouth is a subtle frown, and a dark navy choker and
striped leg warmers are added.  Except for the eye pupil, the art uses no
pure black.  The `EMO: yes` metadata tag is set on these files, so they are
selectable with `ponysay -r emo=yes`.

The original (classic) art is kept intact alongside the emo art as
`twilightclassic`; render it with:

```sh
pixi run ponysay -f twilightclassic
```

To regenerate the emo art from the classic originals (the script is
idempotent):

```sh
python3 scripts/make-emo-pony.py
```

### `pixi run smoke`

Installs ponysay into `.pixi/envs/default` (via the `install` task) and then
runs `ponysay -q twilight`.  A successful run prints an emo
`dear diary, ...` twilight quote with the emo twilight artwork.

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

## Checking which Twilight art you are seeing

Verified on a clean clone of `main` (`63bff1a`) with pixi 0.83.0:
`pixi run ponysay -q twilight` and `pixi run ponysay --emo` render the
**emo** artwork, and the installed copies under
`.pixi/envs/default/share/ponysay/` are byte-identical to the repo files
(xterm md5 `6559f8f83b6686e0368a242facdcf511`, TTY md5
`47aee3c2f285ad3608f733196b005bc6`).  Both files carry `EMO: yes`.

Visual markers:

- **Emo**: lavender coat and face (same as classic); dark navy mane
  (`#00005f`) with the magenta/pink streak; a swept hair lock covers the far
  eye (only one eye visible); subtle frown; dark navy choker at the neck;
  dark navy horizontal bars across the legs (striped leg warmers).  The art
  uses no pure black except the eye pupil.
- **Classic**: light lilac mane and face; both eyes and a smile visible; no
  choker; plain legs.
- The magenta mane streak is **not** a useful marker: both art files have it.
- Both xterm and TTY art render fully at 80 columns.  In particular,
  `pixi run ponysay -f twilight -o -V` is identical to
  `PONYSAY_FULL_WIDTH=1`; the TTY renderer's KMS-palette width bug
  (`Backend.getColour` over-reads `]P...0` defs) does not trigger because
  the art uses black only for the eye pupil.  Art with large pure-black
  areas would still be truncated at 80 columns.

Command-line tells:

```sh
pixi run ponysay -l          # lists both `twilight` and `twilightclassic`;
                             # bold = pony has quotes, twilightclassic is plain
grep '^EMO' ponysay/ponies/twilight.pony ponysay/ttyponies/twilight.pony
pixi run ponysay -q twilightclassic   # classic art + fallback quote
                                      # "Zecora! Help me, I am mute!"
```

`twilightclassic` has no quote file, so `-q twilightclassic` prints the
built-in fallback quote.  `pixi run ponysay -f twilightclassic -q` prints the
classic art with an **empty** balloon: `-q` at the end takes no pony
argument, so the message is read from stdin (empty in a non-interactive run).

The `-r` restriction must come **before** `-q`.  `-q` takes the pony name as
its argument, so `ponysay -q -r emo=yes` treats `-r` as the pony name and
`emo=yes` as the message.  With `PONYSAY_TYPO_LIMIT=0` that fails with
`I have never heard of anypony named -r` (exit 252); with the default typo
correction it quietly renders some other pony (observed `tom`, `cow`, `joe`
and `zecora`).  Use:

```sh
pixi run ponysay -r emo=yes -q     # emo twilight, always
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

The emo art is on `main`: commit `10e1701` ("Add emo Twilight Sparkle art
alongside classic original") is an ancestor of `main`; the current art is the
`63bff1a` redesign (lavender coat, dark navy mane).  All
`origin/thread/*` topic branches are contained in `main`; there is no
separate emo branch.  The only refs ahead of `main` are harness session and
snapshot refs (`origin-sessions/*`, `origin-snapshots/*`), so
`git log --all --not main` shows snapshots, not unmerged work.
The classic xterm and TTY files are byte-identical to the pre-emo originals.
