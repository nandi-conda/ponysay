#!/bin/sh
# Wrapper for `pixi run ponysay`.
#
# `pixi run ponysay` with no arguments should print a random quote from a
# random pony, i.e. behave like `ponysay -q`.  pixi appends any extra task
# arguments after this command, so when arguments are present we pass them
# through unchanged (for example `-q twilight` or `-l`).
set -eu

if [ -n "${PIXI_PROJECT_ROOT:-}" ]; then
    ROOT=$PIXI_PROJECT_ROOT
else
    ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fi

PONYSAY="$ROOT/.pixi/envs/default/bin/ponysay"

# Install quietly on first use.  The task itself deliberately does not depend
# on the `install` task, because that would run the full setup.py install
# output before every quote.  The install command is the same one used by
# `pixi run install` and `pixi run smoke`.
if [ ! -x "$PONYSAY" ]; then
    LOG="${TMPDIR:-/tmp}/ponysay-install.$$.log"
    if ! (cd "$ROOT/ponysay" && python3 setup.py \
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

if [ "$#" -eq 0 ]; then
    exec "$PONYSAY" -q
fi

exec "$PONYSAY" "$@"
