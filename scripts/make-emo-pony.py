#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Regenerate the emo pony art.

The emo theme originally only covered the quotes (ponysay/ponyquotes/).  This
script extends it to the artwork by producing, from the untouched classic
originals, for each pony in `PONIES`:

  * ponysay/ponies/<pony>.pony       (xterm, 256-colour)
  * ponysay/ttyponies/<pony>.pony    (Linux VT, 16-colour palette)

The classic originals are kept side by side as `<pony>classic.pony`.  Those
files are plain copies of the upstream art and are never written by this
script.

The transformation keeps the coat colours intact and:
  * recolors only the mane/hair tones to dark navy #00005f (palette 17):
    near-black, but not #000000, because Backend.getColour's `]P...0`
    over-read mismeasures pure-black KMS palette definitions and would
    truncate the TTY art at 80 columns;
  * sweeps a hair lock over one eye;
  * adds a navy choker at the neck;
  * adds two navy stripes per leg as leg warmers.

Run from the repository root:

    python3 scripts/make-emo-pony.py [pony ...]

With no arguments every pony in `PONIES` is regenerated.  It is idempotent:
it reads the classic files, never the generated emo files, and re-running it
produces byte-identical output.
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
    # Palette entries used by the 16-colour TTY art of other ponies
    # (Fluttershy's pink mane and yellow coat).
    'D787AF': 175, 'FFAFD7': 218, 'FFD787': 222, 'D7AF00': 178,
    'FFFF87': 228, '00AFAF': 37, '5FAFAF': 73,
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
            h = h.upper()
            # Undo the visually-invisible blue-nibble nudge the TTY writer
            # applies to colors whose hex ends in '0' (see kms_hex).
            if h in ('000001', 'D7AF01'):
                h = h[:-1] + '0'
            return RGB_TO_256.get(h, None)
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


# Emo palette entry: dark navy #00005f.  Deliberately not pure black: the
# TTY renderer's Backend.getColour over-reads KMS palette definitions whose
# last hex digit is '0', which mismeasures and truncates such art at 80
# columns.  #00005f ends in 'F' and is safe.
NAVY = 17

# Per-pony emo recipes.  All coordinates are subpixels (two per text row) and
# text columns, matching the parsed grids.
#
# `hair` is the set of palette entries that make up the mane/tail.  The coat
# palette is deliberately absent, so the coat colours survive untouched.
# `hair_before_col` limits the recolor to columns left of that number; it is
# used for Twilight, whose tail keeps its original blue-grey/pink colours
# while only the mane is darkened.  Fluttershy's mane and tail are the same
# pink, so all of her hair is darkened.
#
# `fringe`, `choker` and `legwarmers` are inclusive (row0, row1, col0, col1)
# rectangles painted in NAVY.  They only paint existing art pixels, never
# background, so the silhouette does not grow.
PONIES = {
    'twilight': {
        'emo_name': 'Twilight Sparkle (emo)',
        # The top art row (line 3) is left verbatim, as it always was.
        'first_line': 4,
        'hair': (60, 61, 54, 97),
        'hair_before_col': 30,
        # Hair lock over the far eye (text rows 8-10, columns 12-14).
        'fringe': [(16, 21, 12, 14)],
        'choker': [(23, 23, 12, 17)],
        'legwarmers': [
            (34, 35, 20, 23), (38, 39, 20, 23),
            (34, 35, 29, 31), (38, 39, 29, 31),
        ],
    },
    'fluttershy': {
        'emo_name': 'Fluttershy (emo)',
        # Lines 0-3 are the balloon and its three tail markers; art starts at
        # line 4.
        'first_line': 4,
        # Pink mane and tail (218 #ffafd7, 175 #d787af); the yellow coat
        # (228/178) and its pale highlight (222) are not touched.
        'hair': (218, 175),
        'hair_before_col': None,
        # The classic TTY art defines #d7af00 (coat shade) and #000000
        # (pupil); both end in '0' and trip the renderer's over-read.
        'avoid_kms_overread': True,
        # Side-swept fringe: a diagonal lock from the top of the head over the
        # right side of the face, plus a short lock over the top of the near
        # eye.  The far eye is already hidden behind the mane.
        'fringe': [
            (12, 13, 15, 17), (13, 14, 16, 18), (14, 15, 17, 19),
            (15, 16, 18, 20), (16, 17, 19, 21), (17, 18, 20, 22),
            (18, 19, 21, 23),
            (14, 15, 15, 18), (16, 16, 17, 18),
        ],
        # Navy choker across the visible base of the neck.
        'choker': [(26, 27, 25, 30)],
        # Two stripes per leg; the coat colour between them makes the banding.
        'legwarmers': [
            (38, 39, 23, 27), (42, 43, 23, 27),
            (38, 39, 31, 35), (42, 43, 31, 35),
            (42, 43, 18, 21),
        ],
    },
}


def transform_emo(grid, spec):
    '''
    Turn a classic pony into its emo variant using a `PONIES` recipe.

    Only the recipe's `hair` palette entries are recolored (to NAVY), so the
    coat colours are preserved.  The fringe, choker and leg-warmer rectangles
    are then painted over existing art pixels only.
    '''
    g = [list(r) for r in grid]
    hair = set(spec['hair'])
    limit = spec['hair_before_col']

    for r in range(len(g)):
        for c in range(len(g[r])):
            v = g[r][c]
            if v in (None, 'VAR') or v not in hair:
                continue
            if limit is None or c < limit:
                g[r][c] = NAVY

    for key in ('fringe', 'choker', 'legwarmers'):
        for (r0, r1, c0, c1) in spec[key]:
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if 0 <= r < len(g) and 0 <= c < len(g[r]):
                        if g[r][c] not in (None, 'VAR'):
                            g[r][c] = NAVY

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


def grid_to_tty_lines(grid, safe_kms=False):
    def kms_hex(idx):
        # Backend.getColour reads one character too many when the last hex
        # digit of a `]P...` palette definition is '0'.  The stray read makes
        # the renderer over-count the line and truncate it at 80 columns.
        # Nudging the blue nibble by one is visually invisible and keeps the
        # definition parseable.
        h = C256_TO_RGB[idx]
        if safe_kms and h.endswith('0'):
            h = h[:-1] + '1'
        return h

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
                    out += '\x1b]P8' + kms_hex(fg)
                    params.append('30;01')
                else:
                    params.append('39')
                if bg is not None:
                    out += '\x1b]P0' + kms_hex(bg)
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


def emo_meta(meta, emo_name):
    out = []
    inserted = False
    for ln in meta.split('\n'):
        if ln.startswith('NAME:'):
            out.append('NAME: ' + emo_name)
        else:
            out.append(ln)
        if 'EYE:' in ln and not inserted:
            out.append('EMO: yes')
            inserted = True
    return '\n'.join(out)


def make_emo(pony, spec):
    classic_name = pony + 'classic'
    first = spec['first_line']
    for kind in ('xterm', 'tty'):
        sub = 'ponies' if kind == 'xterm' else 'ttyponies'
        src = '%s/ponysay/%s/%s.pony' % (ROOT, sub, classic_name)
        meta, art_lines = split_pony(src)
        grid = (parse_xterm_art if kind == 'xterm' else parse_tty_art)('\n'.join(art_lines))
        g = transform_emo(grid, spec)
        start = 2 * first
        stop = 2 * (len(art_lines) - 1)
        if kind == 'xterm':
            ser = grid_to_xterm_lines(g[start:stop])
        else:
            ser = grid_to_tty_lines(g[start:stop], safe_kms=spec.get('avoid_kms_overread', False))
        new_lines = art_lines[0:first] + ser + [art_lines[-1]]
        content = '$$$\n' + emo_meta(meta, spec['emo_name']) + '\n$$$\n' + '\n'.join(new_lines)
        dest = '%s/ponysay/%s/%s.pony' % (ROOT, sub, pony)
        open(dest, 'w').write(content)
        print('wrote %s (%d bytes)' % (dest, len(content)))


def main(argv):
    names = argv[1:]
    if not names:
        names = list(PONIES)
    for pony in names:
        if pony not in PONIES:
            raise SystemExit('unknown pony: %s (known: %s)' % (pony, ', '.join(sorted(PONIES))))
        make_emo(pony, PONIES[pony])


if __name__ == '__main__':
    main(sys.argv)
