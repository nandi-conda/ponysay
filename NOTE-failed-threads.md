# Note: why t_6b9734d6 and t_8470e2dc failed

Diagnosed 2026-10-26 ~01:42 UTC from the runner event log and the shared git repo.
Read-only diagnosis; no project code was changed.

## What happened

Both threads ran on the orchestrator worker `orch-p-f4b27dfa-w3`. That worker
stopped answering at **01:07:46**. Six threads on it recorded the same
`worker_lost` event (t_6b9734d6, t_8470e2dc, t_57a9a942, t_9af94c46,
t_a4f319c2, t_b530b9d0). Threads between turns went idle; the two that were
mid-turn were marked `failed`.

A second worker, `orch-p-f4b27dfa-w5`, stopped answering at **01:26:20** and
took down t_2d6b74f6, t_133245a5, t_4668f265 and t_b530b9d0 the same way.
Separately, at 01:00:36 and 01:00:49, two threads got HTTP 402 "Insufficient
Balance" from DeepSeek (t_cea00c13, t_42bd2979).

Per-thread timeline:

- t_6b9734d6 "Review current project state": created 01:07:18, lost 01:07:46 (28 s).
- t_8470e2dc "Verify emo branch merged to main": created ~01:03-01:04, lost 01:07:46
  after roughly four minutes of work.

## (a) Did they do any work before failing?

- **t_6b9734d6: no.** Its whole first life is two events: `created` and
  `worker_lost`. Zero tool calls, zero edits, zero commits. The request attached
  a 20 KB PNG; nothing came of it.
- **t_8470e2dc: yes, a read-only investigation.** It made 32 `python_repl` calls,
  all running read-only git/cat/grep/find, plus a scratch clone at
  `/tmp/verify-emo` where it ran the build, installed into
  `/tmp/verify-emo/prefix`, and ran `ponysay -q twilight` and
  `-f twilightclassic`. It proved the emo art renders from a clean build and the
  original art still renders. It never edited the repo: its final
  `git status --short` was empty and its branch still pointed at `d9c0181`.
  It streamed a complete final report, but the worker died before the turn
  finished, so no summary or reply was saved.

## (b) Does any work need recovery or recommitting?

**No code is lost and there is nothing to recommit.**

- Neither thread made a commit, and neither left uncommitted files.
- Neither has a `refs/sessions/` or `refs/snapshots/` entry: the runner creates
  those only for threads that commit. (They exist for t_cdd997c1, t_42bd2979 and
  t_b530b9d0.) At death both branches just pointed at the base commit.
- The only real loss is t_8470e2dc's undelivered report. Its conclusion, from the
  streamed transcript, was:
  - The emo artwork commits `10e1701`, `49b326a` and `d9c0181` are already on
    main; `thread/t_b530b9d0` had been fast-forwarded to main. No merge was
    needed. (Main has since advanced to `e05dbbf`, "Add --emo flag to pixi run
    ponysay".)
  - The likely reason non-emo art still showed was a stale `.pixi` install:
    `scripts/ponysay-run.sh` only installs when
    `.pixi/envs/default/bin/ponysay` is missing, and `.pixi/` is gitignored, so
    an install made before the emo merge keeps the old pony files in
    `.pixi/envs/default/share/ponysay/ponies/`. Fix: `pixi run install`, or
    delete `.pixi/` and rerun.
  - That stale-install point was a hypothesis at the time (`.pixi` was absent
    from its own worktree); the revived run was re-checking it.

Both threads have since been revived (t_8470e2dc shows `revived` at 01:37:08)
and are working again: t_6b9734d6 started fresh, t_8470e2dc replays the original
request.

## (c) Did our workers die?

**Yes, the platform workers died, not the agents' work.** `orch-p-f4b27dfa-w3`
(01:07:46) and `orch-p-f4b27dfa-w5` (01:26:20) stopped answering and every thread
on them was dropped; the harness re-runs a dropped thread on its next message.
Both target threads were casualties of w3, within one second of each other, so
their failure says nothing about the repo or their tasks. No project state was
lost beyond one undelivered report.

Two things worth watching, both infrastructure rather than repo issues: the
w3/w5 worker instability, and the DeepSeek 402 balance errors at 01:00.
