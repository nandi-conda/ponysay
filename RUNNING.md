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
so it works from a clean checkout as well as after `pixi run smoke` without
printing the full install log.  With no arguments it prints a random quote
from a random pony:

```sh
pixi run ponysay
```

Any arguments after the task name are passed through to `ponysay`:

```sh
pixi run ponysay -q twilight
pixi run ponysay -l
```

`-q twilight` prints an emo `dear diary, ...` twilight quote and renders the
emo twilight art (black mane, fringe over one eye, eyeliner, choker and
striped leg warmers); `-l` lists the installed ponies.

## Emo pony art

The emo theme also extends to the artwork for Twilight Sparkle.  Both the
xterm art (`ponysay/ponies/twilight.pony`) and the Linux-VT art
(`ponysay/ttyponies/twilight.pony`) render an emo Twilight: black mane with a
magenta streak, a fringe covering one eye, eyeliner with an under-eye shadow,
a downturned mouth, a black choker and striped leg warmers.  The `EMO: yes`
metadata tag is set on these files, so they are selectable with
`ponysay -r emo=yes`.

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
