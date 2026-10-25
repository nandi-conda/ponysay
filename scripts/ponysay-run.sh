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

if [ "$#" -eq 0 ]; then
    exec "$PONYSAY" -q
fi

exec "$PONYSAY" "$@"
