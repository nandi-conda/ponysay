# Pixi build/run validation (clean environment)

Validated: 2026-10-25, on branch `thread/t_6b371547`.

## Summary

The ponysay project (with the emo `dear diary, ...` quote set already landed under
`ponysay/ponyquotes/`) builds and runs in a fresh pixi-managed environment.

- `origin/main` (`ee45e81`) has **no** `pixi.toml` and **no** `pyproject.toml`
  `[tool.pixi]` section. A manifest must be added.
- A temporary, minimal manifest (below) was used for this validation only; it is
  intentionally not the canonical project manifest (that is owned by another
  thread). Its required contents are recorded here.
- From a clean state (`pixi install` from scratch), the build with
  `--freedom=partial --without-info --without-man --without-shell` succeeds and
  the quote compiler produces **490** compiled quote files under
  `ponysay/quotes/`.
- `ponysay -q twilight` (installed into the pixi env) renders an emo quote, e.g.
  `dear diary, i keep my heart in a locked book, and even the key has stopped
  believing in me.`
- A default/full build fails only at the **optional info manual** because the
  sandbox/system has no `makeinfo`/texinfo. The failure is isolated to the info
  step and is pinned away in the pixi config by passing `--without-info` in the
  default build task (do **not** declare texinfo in the default environment).

## Environment

- pixi version: **0.83.0** (`pixi --version`)
- Platform: `linux-64` (x86_64, Ubuntu 26.04.1 host)
- Conda channel: `conda-forge`
- Resolved python: `python 3.15.1` (`>=3.8` resolves to this on conda-forge as
  of this validation). The 2016-era ponysay code still builds and runs on it,
  but it emits one harmless `SyntaxWarning` about `"\-"` in
  `src/balloon.py`; a conservative upper bound (e.g. `python >=3.8,<3.14`) is
  recommended for the canonical manifest.

## Minimal working manifest

```toml
[workspace]
name = "ponysay"
version = "3.0.4"
channels = ["conda-forge"]
platforms = ["linux-64"]

[tasks]
build = "cd ponysay && python3 setup.py --freedom=partial --without-info --without-man --without-shell build"
smoke = "cd ponysay && python3 setup.py --freedom=partial --without-info --without-man --without-shell --without-shared-cache --prefix \"$PIXI_PROJECT_ROOT/.pixi/envs/default\" install && \"$PIXI_PROJECT_ROOT/.pixi/envs/default/bin/ponysay\" -q twilight"

[dependencies]
python = ">=3.8"
```

### What a working manifest must contain

1. **Python dependency.** The build and the quote compiler are pure Python once
   the optional extras are disabled. No other conda dependency is required.
2. **A build task that disables the optional extras:**
   `python3 setup.py --freedom=partial --without-info --without-man --without-shell build`.
   In particular `--without-info` is mandatory on systems without texinfo;
   otherwise the build reaches `makeinfo manuals/ponysay.texinfo` and fails.
3. **A smoke/run task** that installs into the pixi environment and runs
   `ponysay -q twilight` (or otherwise exercises the compiled quotes). Non-root
   installs must also pass `--without-shared-cache`, otherwise `setup.py install`
   tries to create `/var/cache/ponysay` and fails on read-only/unprivileged
   filesystems.
4. **Texinfo must be pinned away from the default environment/tasks.** Do not
   add `texinfo` to `[dependencies]` just to satisfy the default build; the info
   manual is optional. If info-manual support is ever wanted, put it in an
   optional pixi feature/task so the default build never requires `makeinfo`.

## Clean-state validation procedure and results

Run from the repository root (after `pixi.toml` exists):

```sh
pixi install                 # creates pixi.lock + .pixi/envs/default
pixi run build               # builds in ponysay/ and compiles quotes
pixi run smoke               # installs into the pixi env, runs ponysay -q twilight
```

Observed results:

- `pixi install` from scratch (no `.pixi/`, no `pixi.lock`) exits 0 and creates:
  - `pixi.lock` (lockfile format version **7**)
  - `.pixi/envs/default` (python 3.15.1 plus its conda run dependencies)
- `pixi run build` exits 0:
  - 478 `Generating quote files for ...` messages (one per pony mention in
    `ponyquotes/ponies`)
  - `find ponysay/quotes -type f | wc -l` → **490** compiled quote files
  - all 490 compiled quote files contain `dear diary` (emo quote content)
- `pixi run smoke` exits 0 and renders an emo twilight quote, e.g.:

  ```
  / dear diary, i keep my heart in a locked book, and even the \
  \ key has stopped believing in me.                            /
  ```

## Default/full build failure isolation

Running the same pixi environment with a *default* build
(`python3 setup.py --freedom=partial build`, i.e. without the
`--without-*` flags) exits 1. The build gets through source zipping and
manpage compression (`gzip`) and fails only in the info-manual section:

```
makeinfo manuals/ponysay.texinfo
sh: 1: makeinfo: not found
gzip -9 -f < ponysay.info > ponysay.info.gz
FileNotFoundError: [Errno 2] No such file or directory: 'ponysay.info'
```

`makeinfo`/texinfo is absent from both the pixi environment and the host
(`which makeinfo` → not found). The failure is isolated to the **optional
info manual**: passing `--without-info` (as the validated build task does)
skips that block entirely, and the validated build log contains zero
`makeinfo` references.

## Lockfile behaviour

- `pixi install` automatically creates `pixi.lock` at the manifest root when
  it is missing.
- Lockfile format version is **7** (`version: 7` at the top of `pixi.lock`).
- It pins the solved conda package URLs + hashes for the `default` environment
  (channel `conda-forge`), including the `linux-64` virtual packages
  (`__unix`, `__linux`, `__glibc`, `__archspec`).
- Changing only task definitions (no dependency changes) leaves the lockfile
  essentially unchanged; dependency changes require a re-solve/lock update.

## Missing system packages

- Declared in the manifest: **`python` only**.
- Intentionally **not** declared: **texinfo/makeinfo** (optional info manual,
  pinned away via `--without-info`).
- No other system packages had to be declared. The build/install exercises
  host `gzip` (manpage compression, only reached in the default build path)
  and `stty` (terminal size probing during dimension generation). Both are
  inherited from the host `PATH` by `pixi run` in this sandbox, so no conda
  package had to be declared for them; `stty` was present here.
