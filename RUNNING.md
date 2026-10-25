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

Run these from the repository root:

```sh
pixi run build
```

Builds ponysay in `ponysay/` with the path known to work:

```sh
python3 setup.py --freedom=partial --without-info --without-man --without-shell build
```

This compiles the quote data and produces the installable `ponysay.install`
zipapp without requiring texinfo.

```sh
pixi run quotes
```

Compiles only the quote data: `ponysay/ponyquotes/*.<N>` →
`ponysay/quotes/<group>.<N>`.  Use this when you only want to regenerate the
compiled quotes.

```sh
pixi run smoke
```

Installs ponysay into `.pixi/envs/default` (passing `--without-shared-cache`
so a non-root install does not try to create `/var/cache/ponysay`) and then
runs:

```sh
ponysay -q twilight
```

A successful run prints an emo `dear diary, ...` twilight quote.

## Running the installed binary directly

After `pixi run smoke` has installed it, invoke the installed binary through
the pixi environment:

```sh
pixi run ponysay -q twilight
```

Or use the absolute path:

```sh
.pixi/envs/default/bin/ponysay -q twilight
```

For other ponies, replace `twilight` with any name listed by
`pixi run ponysay -l`.
