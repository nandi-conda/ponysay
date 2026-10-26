# Documentation

- [`RUNNING.md`](RUNNING.md) — build, install and run ponysay with pixi; the
  emo quote set and emo artwork, and how to regenerate them.
- [`EMO-QUOTES.md`](EMO-QUOTES.md) — what the fork changes in the quote data
  and how `setup.py` compiles it.

## `notes/`

Dated, point-in-time records (validations, audits, failure diagnoses).  Each
one describes the tree as it was when it was written and is not updated
afterwards, so the paths inside a note may predate the current layout.

- [`notes/PIXI-VALIDATION.md`](notes/PIXI-VALIDATION.md) — first clean-environment
  pixi build/run validation.
- [`notes/NOTE-emo-twilight-art.md`](notes/NOTE-emo-twilight-art.md) — diagnosis of
  the dark-blob emo Twilight render.
- [`notes/NOTE-verify-second-emo.md`](notes/NOTE-verify-second-emo.md) — clean-checkout
  verification of the second emo pony (Fluttershy).
- [`notes/NOTE-coordination-audit.md`](notes/NOTE-coordination-audit.md) — audit of
  three concurrent threads working on emo Twilight.
- [`notes/NOTE-failed-threads.md`](notes/NOTE-failed-threads.md) — why two threads
  failed (worker loss, API balance).
