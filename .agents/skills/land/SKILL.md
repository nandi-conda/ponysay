---
name: land
description: >-
  Commit, verify, rebase, and push this repository's changes to main on the
  public GitHub remote. Use only when the user has explicitly asked to land,
  merge, push, or ship changes to main, for example through the Land Changes
  action. Not for reviewing, preparing commits, or running checks alone.
disable-model-invocation: true
metadata:
  delta-action: land
---

# Land changes

Landing means the change is committed, verified with the project's own checks,
rebased onto the latest `main`, pushed to the public GitHub remote, and
confirmed to be there. Preparing commits or pushing a side branch is not
landing.

Invoke this only for an explicit landing request ("land it", "push it", the
Land Changes action). That request is the permission to land: do not stop to
ask whether the merge should happen. Stop only for a genuine blocker below.

## Destination and remotes

- `github` -> `https://github.com/nandi-conda/ponysay`: the public destination.
  Land here, on `main`.
- `origin` -> the workspace/orchestrator bare repository, and `local` -> the
  user's own checkout. Those belong to the Delta harness and sync on their own.
  Never push to `origin` or `local` from this skill.

`github/main` is public, unprotected, and has no CI workflows (the repository
has no `.github/` directory) and no open pull requests. History is linear with
no merge commits, so landing is a direct push to `main`; do not open a pull
request unless the user explicitly asks for one (then push a branch and use
`gh pr create`).

Commit subjects in this repository are sentence-case summaries such as
`Fix emo Twilight art: preserve lavender coat, darken mane only`. There are no
`Co-authored-by` or tool-attribution trailers and no conventional-commit
prefixes; keep it that way.

## 1. Preflight

Run from the repository root (`git rev-parse --show-toplevel`).

```sh
git status --short
git branch --show-current
git log --oneline -5
git fetch github main
```

- On a detached HEAD, or if the branch is not the one the requested change was
  made on: stop and report instead of guessing.
- If the working tree is clean and `git log --oneline github/main..HEAD` is
  empty, there is nothing to land: say so and stop.
- Read the working tree before staging. If it contains changes unrelated to the
  work being landed, stop and report the extra paths rather than sweeping them
  into the commit.

## 2. Commit the work

Only when the tree has uncommitted changes. The move/rename detection must be
preserved, so stage everything that was reviewed in preflight:

```sh
git add -A
git status --short
git commit -m "<Area>: <imperative summary>" -m "<what changed and why>"
```

Use `-m` flags; never open an interactive editor. The subject should read like
the existing history and describe the whole change, not one file among many.
Large moves (for example flattening a subdirectory into the repository root)
belong in the body, since `git log --stat` will show them as renames.

## 3. Rebase onto main

```sh
git rebase github/main
```

- Already up to date: continue.
- On conflict: rebase onto `main` and fix the conflicts, resolving each file to
  the intended combined result, then `git add <paths>` and
  `GIT_EDITOR=true git rebase --continue`.
- Re-check the corrected tree after resolving, then finish the rebase and re-run
  the verification step below, because a conflict resolution can change a
  build input.
- If the correct result is ambiguous, or unrelated work would be overwritten or
  lost: `git rebase --abort` and report the conflict paths as a blocker.

## 4. Verify

The repository's own checks are the pixi tasks defined in `pixi.toml`
(`[tasks]`). Run them from the repository root:

```sh
pixi run build     # python3 setup.py --freedom=partial --without-info --without-man --without-shell build
pixi run smoke     # install into .pixi/envs/default, then render `ponysay -q twilight`
```

`pixi run smoke` is the end-to-end check: it installs into the pixi environment
and must print an emo `dear diary, ...` quote with the emo Twilight artwork.
`pixi run build` must exit 0 after compiling the quote data and the pony
metadata.

Optional sanity for changes touching the pony data or the `ponysay` wrapper:

```sh
pixi run ponysay --list-emo   # prints: fluttershy, twilight
```

These are the only required checks: there is no CI to wait for, so a
representative local run is the verification. Do not weaken or skip a failing
check. If any command fails, fix the change if the fix is clearly in scope;
otherwise leave the change unlanded and report the failing command and its
output. After the checks, confirm `git status --short` is still clean (build
output under `.pixi/`, `quotes/` and the installed data is gitignored).

## 5. Land

```sh
git push github HEAD:main
```

This is a fast-forward because step 3 rebased onto `github/main`. Never use
`--force` or `--force-with-lease` on `main`. If the push is rejected because
`main` moved, `git fetch github main`, repeat step 3, re-run step 4, and retry
once; if it is rejected again, stop and report.

## 6. Confirm and report

```sh
git ls-remote github refs/heads/main
git rev-parse HEAD
git status --short
```

The SHA from `ls-remote` must equal `git rev-parse HEAD`, and the tree must be
clean. Only then report success, naming the commit SHA and subject, the
verification commands that passed, and that `github/main` now contains it.
If any check fails or the push did not happen, say plainly that the change has
not landed, and give the blocker and the exact command that failed.
