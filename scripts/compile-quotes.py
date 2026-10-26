#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Compile only the pony quote data.

This reproduces the quote-compiler step of `setup.py build`: it reads
`ponyquotes/ponies` and copies each `ponyquotes/<pony>.<N>` file to
`quotes/<group>.<N>` (the group is the `+`-joined pony line from
`ponyquotes/ponies`).  It does not build the man/info/shell extras or the
installable ponysay zipapp.

Usage:
    python3 scripts/compile-quotes.py [ponysay-checkout]

The optional argument is the ponysay checkout directory; it defaults to the
current directory.
'''

import os
import shutil
import sys


def compile_quotes(root):
    ponyquotes_dir = os.path.join(root, 'ponyquotes')
    quotes_dir = os.path.join(root, 'quotes')

    if not os.path.isdir(ponyquotes_dir):
        raise SystemExit('not a ponysay checkout: %s is missing' % ponyquotes_dir)

    # `setup.py build` recreates `quotes/` from scratch each time.
    if os.path.isdir(quotes_dir) or os.path.islink(quotes_dir):
        shutil.rmtree(quotes_dir)
    os.mkdir(quotes_dir)

    with open(os.path.join(ponyquotes_dir, 'ponies'), 'rb') as ponymap:
        groups = ponymap.read().decode('utf-8', 'replace').split('\n')

    for group in groups:
        for pony in group.split('+'):
            if len(pony) == 0:
                continue
            print('Generating quote files for \033[34m' + pony + '\033[39m')
            for name in sorted(os.listdir(ponyquotes_dir)):
                if name.startswith(pony + '.'):
                    source = os.path.join(ponyquotes_dir, name)
                    if os.path.isfile(source):
                        shutil.copy(source, os.path.join(quotes_dir, group + name[name.find('.'):]))


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    compile_quotes(root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
