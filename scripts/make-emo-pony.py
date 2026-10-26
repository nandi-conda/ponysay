#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Regenerate the emo pony art for Twilight Sparkle.

The emo theme originally only covered the quotes (ponysay/ponyquotes/).  This
script extends it to the artwork by producing, from the untouched classic
originals:

  * ponysay/ponies/twilight.pony       (xterm, 256-colour)
  * ponysay/ttyponies/twilight.pony    (Linux VT, 16-colour palette)

The classic originals are kept side by side as `twilightclassic.pony`.

The transformation is:
  * recolor the lavender mane (#d7afd7/#af87af/#875f87) to a dark plum/purple
    palette (#5f005f/#5f0087/#000000) while leaving the lavender face/coat
    highlights intact;
  * sweep a fringe over the far eye;
  * add black eyeliner, a half-lid and an under-eye shadow to the near eye;
  * add a downturned mouth and a black choker;
  * add striped leg warmers.

Run from the repository root:

    python3 scripts/make-emo-pony.py

It is idempotent: it reads the classic files, never the generated emo files.
'''
import re
import sys

ROOT = __file__ and __file__.rsplit('/', 2)[0] or '.'


def parse_xterm_art(art):
    grid = []
    for ln in art.split('\n'):
        fg = None
        bg = None
        i = 0
        n = len(ln)
        top = []
        bot = []
        while i < n:
            c = ln[i]
            if c == '\x1b':
                m = re.match(r'\x1b\[([0-9;]*)m', ln[i:])
                if m:
                    params = m.group(1).split(';') if m.group(1) else []
                    i += len(m.group(0))
                    j = 0
                    while j < len(params):
                        p = params[j]
                        if p == '':
                            j += 1
                            continue
                        if p in ('0', '00'):
                            fg = None; bg = None
                        elif p == '38':
                            j += 1
                            if params[j] == '5':
                                j += 1
                                fg = int(params[j])
                        elif p == '48':
                            j += 1
                            if params[j] == '5':
                                j += 1
                                bg = int(params[j])
                        elif p == '39':
                            fg = None
                        elif p == '49':
                            bg = None
                        j += 1
                    continue
                i += 1
                continue
            if c == '$':
                j = ln.index('$', i + 1) if '$' in ln[i + 1:] else n
                top.append('VAR'); bot.append('VAR')
                i = j + 1
                continue
            (t, b) = cell_to_subpixels(fg, bg, c)
            top.append(t); bot.append(b)
            i += 1
        grid.append(top); grid.append(bot)
    return grid


RGB_TO_256 = {
    '000000': 16, '00005F': 17, '5F005F': 53, '5F0087': 54, '5F5F87': 60,
    '5F5FAF': 61, '875F87': 96, '875FAF': 97, 'AF87AF': 139, 'D75FAF': 169,
    'D7AFD7': 182, 'FF5FAF': 205, 'FFFFFF': 231, '303030': 236, '585858': 240,
    '606060': 241, '121212': 233, '262626': 235,
}
C256_TO_RGB = {v: k for k, v in RGB_TO_256.items()}


def parse_tty_art(art):
    palette = {}
    grid = []
    for ln in art.split('\n'):
        fg_base = None
        bg_base = None
        bold = False
        i = 0
        n = len(ln)
        top = []
        bot = []
        def cur_rgb(idx):
            if idx is None:
                return None
            h = palette.get(idx)
            if h is None or h.upper() in ('AAAAAA', 'C0C0C0'):
                return None
            return RGB_TO_256.get(h.upper(), None)
        while i < n:
            c = ln[i]
            if c == '\x1b':
                if ln[i:i + 2] == '\x1b]':
                    m = re.match(r'\x1b\]P([0-9A-Fa-f])([0-9A-Fa-f]{6})', ln[i:])
                    if m:
                        palette[int(m.group(1), 16)] = m.group(2).upper()
                        i += len(m.group(0))
                        continue
                    i += 1
                    continue
                m = re.match(r'\x1b\[([0-9;]*)m', ln[i:])
                if m:
                    params = m.group(1).split(';') if m.group(1) else []
                    i += len(m.group(0))
                    for p in params:
                        if p in ('', '0', '00'):
                            fg_base = None; bg_base = None; bold = False
                        elif p in ('1', '01'):
                            bold = True
                        elif p == '22':
                            bold = False
                        elif p == '39':
                            fg_base = None
                        elif p == '49':
                            bg_base = None
                        elif p in ('30', '31', '32', '33', '34', '35', '36', '37'):
                            fg_base = int(p[1])
                        elif p in ('40', '41', '42', '43', '44', '45', '46', '47'):
                            bg_base = int(p[1])
                    continue
                i += 1
                continue
            if c == '$':
                j = ln.index('$', i + 1) if '$' in ln[i + 1:] else n
                top.append('VAR'); bot.append('VAR')
                i = j + 1
                continue
            fg_idx = (fg_base + (8 if bold else 0)) if fg_base is not None else None
            (t, b) = cell_to_subpixels(cur_rgb(fg_idx), cur_rgb(bg_base), c)
            top.append(t); bot.append(b)
            i += 1
        grid.append(top); grid.append(bot)
    return grid


def cell_to_subpixels(fg, bg, g):
    if g == '\u2588':
        return (fg, fg)
    if g == '\u2580':
        return (fg, bg)
    if g == '\u2584':
        return (bg, fg)
    if g == '\u258c':
        return (fg, bg)
    if g == '\u2590':
        return (bg, fg)
    if g == ' ':
        return (bg, bg)
    return (None, None)


def transform_emo(grid):
    '''
    Turn the classic Twilight into the emo variant.

    In the classic art the lavender tones 182/139/96 (#d7afd7/#af87af/#875f87)
    are the pony's *coat*, and the mane/tail hair is the 60/61/54/97 blue-purple
    family.  So the coat is left completely untouched and only the mane hair
    (left of the tail, which starts around column 30) is darkened.  The pink
    streak (205/169) is kept.

    The mane is recoloured to dark navy #00005f (palette 17) rather than pure
    black: that is the pony's real dark-blue mane family, it reads as a near
    black emo mane, and -- unlike #000000 -- it does not end in a '0' hex byte,
    so it does not trip backend.getColour()'s ']P...0' over-read (which would
    otherwise truncate the tty art at 80 columns).  If getColour is fixed, pure
    black (16) can be substituted here with no other changes.

    On top of the recolour: a hair lock covers the far eye (one eye covered),
    a choker band sits at the neck, and the legs get striped leg warmers.
    '''
    g = [list(r) for r in grid]

    # Darken the mane hair left of the tail; keep the lavender coat untouched.
    HAIR = {60: 17, 61: 17, 54: 17, 97: 17}
    for r in range(len(g)):
        for c in range(len(g[r])):
            v = g[r][c]
            if v in (None, 'VAR'):
                continue
            if c < 30 and v in HAIR:
                g[r][c] = HAIR[v]

    # Fringe: a hair lock over the far eye (art rows 8-10, cols 12-14).
    for ar in (8, 9, 10):
        for c in (12, 13, 14):
            for sr in (2 * ar, 2 * ar + 1):
                if 0 <= sr < len(g) and g[sr][c] not in (None, 'VAR'):
                    g[sr][c] = 17

    # Choker at the neck.
    for c in range(12, 18):
        if g[23][c] not in (None, 'VAR'):
            g[23][c] = 17

    # Striped leg warmers.
    for c in range(20, 24):
        for r in (34, 35, 38, 39):
            if g[r][c] not in (None, 'VAR'):
                g[r][c] = 17
    for c in range(29, 32):
        for r in (34, 35, 38, 39):
            if g[r][c] not in (None, 'VAR'):
                g[r][c] = 17

    return g


def xterm_sgr(fg, bg):
    params = []
    params.append('48;5;%d' % bg if bg is not None else '49')
    params.append('38;5;%d' % fg if fg is not None else '39')
    return '\x1b[%sm' % ';'.join(params)


def grid_to_xterm_lines(grid):
    lines = []
    for i in range(0, len(grid) - 1, 2):
        top = grid[i]
        bot = grid[i + 1]
        out = ''
        last = None
        for c in range(max(len(top), len(bot))):
            t = top[c] if c < len(top) else None
            b = bot[c] if c < len(bot) else None
            if t == 'VAR' or b == 'VAR':
                continue
            if t is None and b is None:
                fg = bg = None; g = ' '
            elif t == b:
                fg = bg = t; g = '\u2588'
            elif t is None:
                fg = b; bg = None; g = '\u2584'
            elif b is None:
                fg = t; bg = None; g = '\u2580'
            else:
                fg = b; bg = t; g = '\u2584'
            key = (fg, bg)
            if key != last:
                out += xterm_sgr(fg, bg)
                last = key
            out += g
        out += '\x1b[00m'
        lines.append(out)
    return lines


def grid_to_tty_lines(grid):
    lines = []
    for i in range(0, len(grid) - 1, 2):
        top = grid[i]
        bot = grid[i + 1]
        out = ''
        last = None
        for c in range(max(len(top), len(bot))):
            t = top[c] if c < len(top) else None
            b = bot[c] if c < len(bot) else None
            if t == 'VAR' or b == 'VAR':
                continue
            if t is None and b is None:
                fg = bg = None; g = ' '
            elif t == b:
                fg = bg = t; g = '\u2588'
            elif t is None:
                fg = b; bg = None; g = '\u2584'
            elif b is None:
                fg = t; bg = None; g = '\u2580'
            else:
                fg = b; bg = t; g = '\u2584'
            key = (fg, bg)
            if key != last:
                params = []
                if fg is not None:
                    out += '\x1b]P8' + C256_TO_RGB[fg]
                    params.append('30;01')
                else:
                    params.append('39')
                if bg is not None:
                    out += '\x1b]P0' + C256_TO_RGB[bg]
                    params.append('40')
                else:
                    params.append('49')
                out += '\x1b[%sm' % ';'.join(params)
                last = key
            out += g
        out += '\x1b[00m'
        lines.append(out)
    return lines


def split_pony(path):
    data = open(path).read()
    assert data.startswith('$$$\n'), path
    end = data.index('\n$$$\n')
    return data[4:end], (data[end + 5:]).split('\n')


def emo_meta(meta):
    out = []
    inserted = False
    for ln in meta.split('\n'):
        if ln.startswith('NAME:'):
            out.append('NAME: Twilight Sparkle (emo)')
        else:
            out.append(ln)
        if 'EYE:' in ln and not inserted:
            out.append('EMO: yes')
            inserted = True
    return '\n'.join(out)


def make_emo(pony='twilight'):
    classic_name = pony + 'classic'
    for kind in ('xterm', 'tty'):
        sub = 'ponies' if kind == 'xterm' else 'ttyponies'
        src = '%s/ponysay/%s/%s.pony' % (ROOT, sub, classic_name)
        meta, art_lines = split_pony(src)
        grid = (parse_xterm_art if kind == 'xterm' else parse_tty_art)('\n'.join(art_lines))
        g = transform_emo(grid)
        ser = (grid_to_xterm_lines if kind == 'xterm' else grid_to_tty_lines)(g[8:48])
        new_lines = art_lines[0:4] + ser + [art_lines[24]]
        content = '$$$\n' + emo_meta(meta) + '\n$$$\n' + '\n'.join(new_lines)
        dest = '%s/ponysay/%s/%s.pony' % (ROOT, sub, pony)
        open(dest, 'w').write(content)
        print('wrote %s (%d bytes)' % (dest, len(content)))


if __name__ == '__main__':
    make_emo()
