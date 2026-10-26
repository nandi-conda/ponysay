#!/bin/sh
# Wrapper for `pixi run ponysay`.
#
# `pixi run ponysay` with no arguments should print a random quote from a
# random pony, i.e. behave like `ponysay -q`.  `--emo`/`-e` selects a random
# emo-tagged pony and lets her quote herself (`ponysay -r emo=yes -q`), and
# `--list-emo` prints the names of the emo-tagged ponies, one per line.  pixi
# appends any extra task arguments after this command, so when arguments are
# present we pass them through unchanged (for example `-q twilight` or `-l`).
set -eu

if [ -n "${PIXI_PROJECT_ROOT:-}" ]; then
    ROOT=$PIXI_PROJECT_ROOT
else
    ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fi

PONYSAY="$ROOT/.pixi/envs/default/bin/ponysay"

# Install quietly on first use, and again whenever the installed binary is
# older than the source tree (for example after a quote or pony-art change),
# so a pre-existing environment never serves stale data.  The task itself
# deliberately does not depend on the `install` task, because that would run
# the full setup.py install output before every quote.  The install command is
# the same one used by `pixi run install` and `pixi run smoke`.
#
# The source scan skips `.pixi/` (it holds the installed binary itself, so
# scanning it would always look stale), `.git/`, and `docs/` (documentation
# does not change the install).
needs_install=0
if [ ! -x "$PONYSAY" ]; then
    needs_install=1
elif [ -n "$(find "$ROOT" \
        \( -path "$ROOT/.pixi" -o -path "$ROOT/.git" -o -path "$ROOT/docs" \) -prune \
        -o -type f -newer "$PONYSAY" -print -quit 2>/dev/null)" ]; then
    needs_install=1
fi

if [ "$needs_install" -eq 1 ]; then
    LOG="${TMPDIR:-/tmp}/ponysay-install.$$.log"
    if ! (cd "$ROOT" && python3 setup.py \
            --freedom=partial --without-info --without-man --without-shell \
            --without-shared-cache \
            --prefix "$ROOT/.pixi/envs/default" install >"$LOG" 2>&1); then
        cat "$LOG" >&2
        rm -f "$LOG"
        exit 1
    fi
    rm -f "$LOG"
fi

# The 2016-era zipapp triggers a SyntaxWarning for `\-` in balloon.py.
# Suppress it so the quote is the only output.
export PYTHONWARNINGS=ignore

# Print the names of the ponies tagged `EMO: yes`, one per line in C order.
# Core ponysay parses `-r` but only uses it for random selection, so
# `ponysay -l -r emo=yes` still prints the full list; scan the pony headers
# directly instead.  The installed share tree is what ponysay itself reads, so
# prefer it, and fall back to the source tree if the installed data is
# missing.  No matches prints nothing and still succeeds.
list_emo_ponies() {
    for dir in "$ROOT/.pixi/envs/default/share/ponysay/ponies" "$ROOT/ponies"; do
        [ -d "$dir" ] || continue
        for pony in "$dir"/*.pony; do
            [ -f "$pony" ] || continue
            grep -qE '^EMO:[[:space:]]*yes[[:space:]]*$' "$pony" 2>/dev/null || continue
            name=${pony##*/}
            printf '%s\n' "${name%.pony}"
        done | LC_ALL=C sort
        return 0
    done
    return 0
}

# `--emo` / `-e` and `--list-emo` are wrapper-level flags, not ponysay
# options: `--emo` selects a random pony among those tagged `EMO: yes`
# (`-r emo=yes`) and lets her quote herself (`-q`), and `--list-emo` prints
# those ponies and exits.  Only leading wrapper flags are consumed, so any
# following ponysay arguments are passed through unchanged (e.g.
# `--emo -q twilight`).
emo=0
listemo=0
while [ "$#" -gt 0 ]; do
    case $1 in
        --emo|-e) emo=1; shift ;;
        --list-emo) listemo=1; shift ;;
        *) break ;;
    esac
done

if [ "$listemo" -eq 1 ]; then
    list_emo_ponies
    exit 0
fi

if [ "$emo" -eq 1 ]; then
    if [ "$#" -eq 0 ]; then
        exec "$PONYSAY" -r emo=yes -q
    fi
    exec "$PONYSAY" -r emo=yes "$@"
fi

if [ "$#" -eq 0 ]; then
    exec "$PONYSAY" -q
fi

exec "$PONYSAY" "$@"
