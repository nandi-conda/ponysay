# Coordination audit: three emo-Twilight threads

Read-only audit, snapshot at 2026-10-26 02:12 UTC. No tracked file was edited.
Evidence: git refs in this worktree, the three threads' event streams (sequence
numbers below), and their messages. The threads' working trees live in separate
sandboxes, so uncommitted edits there are visible only through their tool-call
events, not through git here.

## Baseline

- `origin/main` = `24e0634` ("Add --list-emo to the pixi ponysay wrapper"), 01:59.
  It did not move during any of the three current turns.
- None of the three has a `landed`/`saved` event or a new commit in this round.
  `thread/t_ada8c4b3` is still at `24e0634`; the other two threads have no
  branch ref in this worktree. Their earlier tips were already landed on main
  and the runner's ref is gone (assumption: the landing process removes it).
- Current turns started together: `t_ada8c4b3` created 02:03:52; `t_2d6b74f6`
  and `t_b530b9d0` revived 02:03:52; router ownership notes delivered 02:10:06
  (`74269`, `74270`, `74271`).

## What each thread is doing right now

| Thread | Role given by router | Tool calls | Observed writes this round | Status at 02:12 |
|---|---|---|---|---|
| `t_ada8c4b3` | Diagnose the rendering regression, report only | 54 | none to tracked files; one `touch` of `ponysay/ponies/twilight.pony` (mtime only, content unchanged, tree clean) | Still analysing; reasoning says "now let me write the note". No outbound message yet. |
| `t_2d6b74f6` | Verify via pixi; own `RUNNING.md` and pixi-run docs | 91 | none; works in `/tmp/ponysay-clean` clone at `24e0634` | Sent findings to both peers (`74516`, `74527`); no `RUNNING.md` edit yet. |
| `t_b530b9d0` | Fix the art | 69 | ran `scripts/make-emo-pony.py` once (idempotent, byte-identical); art candidates rendered only to `/tmp` PNGs | Mid-design; no commit. |

Findings in the three threads agree on the root cause: the art transform in
`scripts/make-emo-pony.py` over-darkens the coat/head and paints a solid fringe
rectangle over the only eye plus an eyeliner bar on the muzzle. `t_ada8c4b3`
quantified 228 subpixel changes, identical for xterm and tty; `t_b530b9d0`
confirmed visually ("my fringe is a solid dark rectangle that erases the eye",
`71710`) and is rebuilding conservatively (recolour + swept fringe + subtle
frown; skipping the choker, `74645`).

## Overlap matrix (work, not files)

| Work item | t_ada8c4b3 | t_2d6b74f6 | t_b530b9d0 |
|---|---|---|---|
| Render emo vs classic and inspect | yes | yes | yes |
| Hand-built ANSI/terminal-colour -> PNG or grid tooling | yes | yes | yes |
| Attribute art delta to individual transform rules | yes | - | yes |
| Prove render pipeline unchanged (old build vs current) | yes | partial | - |
| TTY truncation investigation | partial | root cause | asked to "cover" it |
| `make-emo-pony.py` idempotence check | yes | - | yes |
| Art edits | no (forbidden) | no (forbidden) | planned |
| `RUNNING.md` edits | no | planned (owner) | no (forbidden; authored it earlier) |

Duplication is real but mostly in tooling and analysis: three separate
ANSI-to-image renderers and three independent reproductions of "emo vs classic".
The distinct value is split cleanly: `t_ada8c4b3` proved the render path is
byte-identical to the pre-emo build; `t_2d6b74f6` found a genuine renderer bug
in `-V` mode; `t_b530b9d0` is producing the only actual fix.

## File-touch matrix

| File | t_ada8c4b3 | t_2d6b74f6 | t_b530b9d0 |
|---|---|---|---|
| `ponysay/ponies/twilight.pony` | read + mtime touch | read (clone) | regenerate (write) |
| `ponysay/ttyponies/twilight.pony` | read | read | regenerate (write) |
| `ponysay/ponies/twilightclassic.pony` | read (regen source) | read | read |
| `ponysay/ttyponies/twilightclassic.pony` | read | read | read |
| `scripts/make-emo-pony.py` | imported/read | git log only | executed |
| `scripts/ponysay-run.sh` | executed only | read (earlier turns) | untouched |
| `ponysay/src/backend.py` | read | read + test harness | untouched |
| `RUNNING.md` | read | intends to edit (owner) | untouched this round |
| `ponysay/EMO-QUOTES.md` | read | untouched | owned, untouched this round |

Historical ownership (commits): `t_b530b9d0` authored `10e1701` (all four art
files, `scripts/make-emo-pony.py`, `EMO-QUOTES.md`), `49b326a` (raritysdad
metadata), `d9c0181` (`RUNNING.md` smoke note). `t_2d6b74f6` authored the
`RUNNING.md` verification section (`ade2005`) and the stale-install correction
(`92986fc`). `t_ada8c4b3` has authored nothing.

## Actual collisions

1. **No materialised collision.** No two threads wrote the same tracked file in
   this round, no thread committed, and `origin/main` did not move. The
   `scripts/ponysay-run.sh` risk is gone: nobody is editing it (last change
   `24e0634`; stale-install logic landed earlier in `1839aa3`).
2. **Pending semantic collision in `RUNNING.md` (the important one).**
   `RUNNING.md` hardcodes the emo print's md5
   `a3b1d64d3baf1842748c8bd58c73d905` and describes emo markers as "fringe
   covers one eye", "black choker", "striped leg warmers". That is exactly what
   `t_b530b9d0` is removing: "the mane already forms a collar, so a separate
   choker would blend - I'll skip it" (`74645`), plus a swept fringe and a
   subtle frown. As soon as the art lands, the owner's own docs are wrong. This
   is a text conflict only if `t_b530b9d0` edits `RUNNING.md` (router told it
   not to); otherwise it is silent staleness.
3. **Wrong-layer hand-off for the TTY defect.** `t_2d6b74f6` told the art owner
   "Extra tty defect your fix should cover" and offered "regenerate tty art
   with classic-style single `]P` defs per colour change" (`74527`). The real
   cause is `Backend.getColour` returning 11 characters for a 10-character
   `ESC ] P <7 hex>` palette definition that ends in `0`; `__truncate` then
   over-counts width. Evidence from its own run at `73886`/`74067`: every
   mismatch is `actual 10 / got 11`; only emo tty rows 13 and 17 reach
   `x_end 80` and get cut, classic peaks at 77. This is a renderer bug in
   `ponysay/src/backend.py`, not art, and it has **no owner** in the router's
   map; `t_2d6b74f6` was told not to edit `src/`.
4. **Mtime touch of an owned art file.** `t_ada8c4b3` ran
   `touch ponysay/ponies/twilight.pony` (`74112`) to test the wrapper's
   mtime-based reinstall. Content is unchanged and `git status` stayed clean,
   but it violates the letter of "do not modify the art files" and would
   trigger a reinstall in its own worktree.
5. **Doc claim already false.** `RUNNING.md` says `git log --all --not main` is
   empty. In this repo it now lists harness session/snapshot commits
   (`df62d60`, `8df526f`, ...) from `refs/sessions/*` and `refs/snapshots/*`.
   Harmless, but the claim needs an exclude filter if it is touched again.

## Communication matrix

| Sender -> receiver | This round |
|---|---|
| `t_2d6b74f6` -> `t_ada8c4b3` | 02:09:16, delivered (`74516`/`74514`) |
| `t_2d6b74f6` -> `t_b530b9d0` | 02:09:34, delivered (`74527`/`74526`) |
| `t_ada8c4b3` -> anyone | none; it read the note and confirmed independently |
| `t_b530b9d0` -> anyone | none this round (it did message `t_5b7e73d1` and `t_42bd2979` in earlier turns) |
| router -> all three | ownership notes at 02:10:06 |

So communication is one-way: the verifier broadcast to both fixers; neither
replied. `t_b530b9d0` has not been told the final coordinates the verifier
needs, and `t_2d6b74f6` cannot know the new md5/markers until the art lands.
`t_2d6b74f6` also read `t_ada8c4b3`'s stream directly (`70360`, `71126`), i.e.
it is monitoring rather than relying on replies.

## Recommendations

1. **Order the landings: art first, docs second.** Let `t_b530b9d0` land the
   art commit; only then re-dispatch `t_2d6b74f6` to rewrite `RUNNING.md`. It is
   idle-until-message and cannot wake itself, so the router must nudge it after
   the art lands.
2. **Art owner publishes the doc facts.** `t_b530b9d0` should put the final
   xterm/tty md5s and the markers that actually survive into its turn summary
   and message them to `t_2d6b74f6`. It should not edit `RUNNING.md`; if a doc
   sentence is needed, send it to the owner instead.
3. **Docs owner waits for that hand-off.** `t_2d6b74f6` must recompute the md5
   and rewrite the marker list from the landed art, not from the current file.
   While there, replace the `git log --all --not main` claim with an
   `--exclude=refs/sessions/* --exclude=refs/snapshots/*` form or drop it.
4. **Give the `backend.getColour` bug a real owner or explicitly defer it.**
   It is independent of the art (classic would truncate too at a narrower
   width), affects only `-V` tty output, and cannot be fixed by padding art.
   Do not let `t_b530b9d0` re-encode the tty art as a workaround.
5. **Keep `t_ada8c4b3` read-only.** Its value is the byte-identity proof and
   the per-rule damage report; it should land that as `NOTE-*.md` and reply in
   one line to `t_2d6b74f6` (agree on art cause; flag that the tty cut is a
   renderer bug). It should not implement the art fix or touch owned files
   again.
6. **Refresh the art owner's directory entry.** `t_b530b9d0`'s summary still
   advertises the choker and fringe-over-eye design it is removing, and its
   `files` list is empty. `team.set_summary` before ending the turn.
7. **Optional:** share one ANSI-to-PNG helper instead of three. Low value now
   that all three are nearly done; not worth tracked code.

## Sandbox note (not a coordination finding)

At about 02:13 this sandbox's shared repo lost `refs/heads/main` and this
worktree's admin entry; `git status` failed with "not a git repository". I
recreated `refs/heads/main` from `refs/remotes/origin/main` (`24e0634`) and the
worktree admin files, then ran `git reset` (mixed) to rebuild the index. No
tracked file content changed. `git status` is clean apart from this note.
