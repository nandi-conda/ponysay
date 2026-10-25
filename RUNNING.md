# How to run

This repository is a ponysay fork with emo `dear diary, ...` quotes.  The
build/run workflow is managed by [pixi](https://pixi.sh); the manifest is
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

Runs the installed ponysay.  The task depends on `install`, so it works from a
clean checkout as well as after `pixi run smoke`; any arguments after the task
name are passed to `ponysay`:

```sh
pixi run ponysay -q twilight
pixi run ponysay -l
```

`-q twilight` prints an emo `dear diary, ...` twilight quote; `-l` lists the
installed ponies.

### `pixi run smoke`

Installs ponysay into `.pixi/envs/default` (via the `install` task) and then
runs `ponysay -q twilight`.  A successful run prints an emo
`dear diary, ...` twilight quote.

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
