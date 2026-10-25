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
