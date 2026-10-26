# Emo ponysay quotes

This fork of [ponysay](https://github.com/erkin/ponysay) (upstream master
`00b8c84d`) rewrites the pony quote sets in a consistent emo voice:
first-person, melancholic, black-fringe diary entries.  Every quote is a
single `dear diary, ...` sentence.

## What changed

- `ponyquotes/*.<N>` — all 409 quote files were replaced with emo diary
  entries.  Each file keeps the upstream format: one quote per file, ASCII
  (valid UTF-8), and a single trailing newline.
- `ponyquotes/ponies` — the pony → quote-group mapping is untouched, so the
  installer's quote compiler still associates the right quote files with each
  pony and `ponysay -l` / `ponysay -q` work as before.

The content was generated deterministically (one quote per file, no duplicate
entries within a pony's set) and committed as the final source data.

## How the quote data is compiled

Upstream's `setup.py build` reads `ponyquotes/ponies` and copies each
`ponyquotes/<pony>.<N>` file to `quotes/<group>.<N>` (the group is the
`+`-joined pony line from `ponyquotes/ponies`).  This is the "quote compiler";
there is no separate zip step in this version of ponysay.

To regenerate the compiled `quotes/` data:

    python3 setup.py --freedom=partial build

The optional info/man/shell extras require `makeinfo`, which is not needed by
the quote compiler.  On systems without texinfo, build with:

    python3 setup.py --freedom=partial \
        --without-info --without-man --without-shell build

## Emo artwork

The emo theme also extends to the artwork of two ponies, Twilight Sparkle and
Fluttershy.  See [`RUNNING.md`](../RUNNING.md) for the emo art files, the
preserved `twilightclassic` and `fluttershyclassic` originals, the visual
markers, and how to regenerate the art with `scripts/make-emo-pony.py`.
Both ponies keep their normal coat colours; the emo treatment changes the
hair to dark navy and adds a fringe, choker and leg stripes.

## Using pixi

The repository root has a [`pixi.toml`](../pixi.toml) manifest that declares a
conda-forge Python interpreter (`>=3.8,<3.14`) and the build/run tasks
(`build`, `quotes`, `install`, `ponysay`, `smoke`).  Texinfo is intentionally
not declared: it is only needed for the optional info manual, and the default
build task pins it away with `--without-info`.

Install [pixi](https://pixi.sh) (e.g. `curl -fsSL https://pixi.sh/install.sh
| bash`), then run the tasks from the repository root:

    pixi run build          # build without info/man/shell extras
    pixi run quotes         # compile only ponyquotes/* -> quotes/*
    pixi run install        # install into the pixi env
    pixi run ponysay        # random pony + quote (or pass ponysay arguments)
    pixi run ponysay --emo  # random emo-tagged pony + her emo quote
    pixi run smoke          # install into the pixi env and render `ponysay -q twilight`

`pixi run smoke` installs ponysay into `.pixi/envs/default` (passing
`--without-shared-cache` so a non-root install does not try to create
`/var/cache/ponysay`) and then runs the installed `ponysay -q twilight`.
`pixi run quotes` is the narrow quote-data-only step if you only need to
regenerate `quotes/`.
