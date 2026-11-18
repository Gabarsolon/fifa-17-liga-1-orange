"""Stadium fan flags and banners for the imported teams (issue #22).

python scripts/fan_flags.py <team_key> [--project <abs .fbproject> ...] [--no-inject]

Each team slot has 4 flag textures `content/worlds/flag/textures/flag_<id>/flag_<id>_<k>_color` (512x256, BC1 sRGB, 10 mips)
and one banner atlas `content/worlds/banner/textures/banner_<id>/banner_<id>_color` (1024x512, BC1 sRGB, 11 mips). The
replaced Danish team's art stays in the game ("Esbjerg fB" flags in a Botosani stadium) unless it is replaced. Layout of the
original atlas (exported with `FrostyMeshCli export-texture` and checked on Esbjerg): a 4x4 grid of 256x128 tiles; row 0 is
the 4 flags shrunk, rows 1-2 are 8 more designs (diagonals, stripes, hoops, checks) and row 3 holds 2 long scarves of 512x128.
This script draws the same set with the club's own crest, colours and name: plain club flags, no slogans.
FCSB has hand-made fan flags and is skipped. Output PNG + DDS go to assets/teams/<key>/final/ (git-ignored for the
pipeline teams) and are injected with `FrostyCmd import-team`.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import liga1orange_teams  # noqa: E402

FONT_BOLD = r'C:\Windows\Fonts\ariblk.ttf'
FONT_ALT = r'C:\Windows\Fonts\impact.ttf'
FLAG_W, FLAG_H = 512, 256


def rd(path):
    return pd.read_csv(os.path.join(ROOT, path), sep='\t', encoding='utf-16-le', dtype=str, keep_default_na=False)


def luminance(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def palette(team, crest):
    """(primary, secondary) from the crest, which shows the real club colours (the kit colour columns do not: CFR came out grey).
    Primary = the most frequent saturated crest colour (else the most frequent non-white); secondary = a second frequent
    saturated colour when it is clearly different, else white for dark primaries and near-black for light ones."""
    import numpy as np
    from scipy.cluster.vq import kmeans2
    a = np.array(crest.resize((96, 96), Image.LANCZOS))
    px = a[a[..., 3] > 200][:, :3].astype(float)
    np.random.seed(1)
    centers, labels = kmeans2(px, 6, minit='++', seed=1)
    counts = np.bincount(labels, minlength=len(centers))

    def sat(c):
        return (max(c) - min(c)) / 255.0

    ranked = sorted(range(len(centers)), key=lambda i: -counts[i])
    chroma = [i for i in ranked if sat(centers[i]) > 0.35 and 35 < luminance(centers[i]) < 225]
    pool = chroma or [i for i in ranked if luminance(centers[i]) < 235] or ranked
    primary = tuple(int(v) for v in centers[pool[0]])
    secondary = None
    for i in pool[1:]:
        c = tuple(int(v) for v in centers[i])
        if dist(c, primary) > 110 and counts[i] > 0.15 * counts[pool[0]]:
            secondary = c
            break
    if secondary is None:
        secondary = (255, 255, 255) if luminance(primary) < 170 else (20, 20, 20)
    return primary, secondary


def club_name(team):
    strings = rd('db/LanguageStrings.txt')
    row = strings[strings.stringid == f'TeamName_Abbr15_{team.teamid_fifa17}']
    return row.iloc[0].sourcetext.strip() if len(row) else team.name


def find_crest(key, team):
    patterns = [f'assets/teams/{key}/f16_raw/team_{team.teamid_fifa16}_crest_standard.png',
                f'assets/teams/{key}/logo_big.png', f'assets/teams/{key}/{key}_logo_big.png',
                f'assets/teams/{key}/crest_{team.teamid_fifa17}_0_0_color.png', f'assets/teams/{key}/logo.png']
    for pattern in patterns:
        for path in glob.glob(os.path.join(ROOT, pattern)):
            return Image.open(path).convert('RGBA')
    raise SystemExit(f'no crest image found for {key}')


def ink(bg, wanted):
    """Text colour on `bg`: the wanted colour when it contrasts enough, else white or near-black."""
    if abs(luminance(bg) - luminance(wanted)) >= 90:
        return wanted
    return (255, 255, 255) if luminance(bg) < 140 else (20, 20, 20)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def paste_crest(img, crest, height, center):
    w = int(crest.width * height / crest.height)
    c = crest.resize((w, height), Image.LANCZOS)
    img.alpha_composite(c, (int(center[0] - w / 2), int(center[1] - height / 2)))


def fit_text(draw, text, box, fill, font_path=FONT_BOLD, stroke=0, stroke_fill=None):
    x0, y0, x1, y1 = box
    size = int(y1 - y0)
    while size > 6:
        font = ImageFont.truetype(font_path, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
        if r - l <= (x1 - x0) and b - t <= (y1 - y0):
            break
        size -= 2
    draw.text(((x0 + x1) / 2 - (r + l) / 2, (y0 + y1) / 2 - (b + t) / 2), text, font=font, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)


def new(w, h, color):
    return Image.new('RGBA', (w, h), color + (255,))


def flag0(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    paste_crest(img, crest, 200, (FLAG_W / 2, FLAG_H / 2))
    return img


def flag1(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, s)
    d = ImageDraw.Draw(img)
    d.rectangle([14, 14, FLAG_W - 15, FLAG_H - 15], fill=p)
    fit_text(d, name, (40, 50, FLAG_W - 40, FLAG_H - 50), ink(p, s))
    return img


def flag2(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    for r in range(4):
        for c in range(8):
            if (r + c) % 2:
                d.rectangle([c * 64, r * 64, c * 64 + 63, r * 64 + 63], fill=s)
    paste_crest(img, crest, 170, (FLAG_W / 2, FLAG_H / 2))
    return img


def flag3(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, shade(p, 0.62))
    d = ImageDraw.Draw(img)
    d.rectangle([100, 0, FLAG_W - 101, FLAG_H], fill=p)
    paste_crest(img, crest, 150, (FLAG_W / 2, FLAG_H / 2))
    return img


def diagonal(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    d.polygon([(FLAG_W, 0), (FLAG_W, FLAG_H), (0, FLAG_H)], fill=s)
    paste_crest(img, crest, 170, (FLAG_W / 2, FLAG_H / 2))
    return img


def stripes_h(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    d.rectangle([0, FLAG_H // 3, FLAG_W, 2 * FLAG_H // 3], fill=s)
    paste_crest(img, crest, 170, (FLAG_W / 2, FLAG_H / 2))
    return img


def stripes_v(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    for c in range(1, 9, 2):
        d.rectangle([c * FLAG_W // 9, 0, (c + 1) * FLAG_W // 9, FLAG_H], fill=s)
    paste_crest(img, crest, 170, (FLAG_W / 2, FLAG_H / 2))
    return img


def corner_block(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    d.rectangle([0, FLAG_H // 2, FLAG_W // 2, FLAG_H], fill=s)
    d.rectangle([FLAG_W // 2, 0, FLAG_W, FLAG_H // 2], fill=shade(p, 0.7))
    paste_crest(img, crest, 150, (FLAG_W / 2, FLAG_H / 2))
    return img


def dark_field(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, shade(p, 0.6))
    paste_crest(img, crest, 190, (FLAG_W / 2, FLAG_H / 2))
    return img


def hoops(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    for r in range(1, 6, 2):
        d.rectangle([0, r * FLAG_H // 6, FLAG_W, (r + 1) * FLAG_H // 6], fill=s)
    paste_crest(img, crest, 170, (FLAG_W / 2, FLAG_H / 2))
    return img


def city_flag(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, p)
    d = ImageDraw.Draw(img)
    fit_text(d, city.upper(), (30, 70, FLAG_W - 30, FLAG_H - 70), ink(p, s), font_path=FONT_ALT)
    return img


def year_flag(p, s, crest, name, year, city):
    img = new(FLAG_W, FLAG_H, s)
    d = ImageDraw.Draw(img)
    fit_text(d, str(year), (30, 40, FLAG_W - 30, FLAG_H - 40), ink(s, p), font_path=FONT_ALT)
    return img


def scarf(p, s, crest, name, light):
    img = new(1024, 256, s if light else p)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1023, 18], fill=p if light else s)
    d.rectangle([0, 237, 1023, 255], fill=p if light else s)
    fit_text(d, name, (210, 50, 814, 206), ink(s, p) if light else ink(p, s))
    paste_crest(img, crest, 150, (110, 128))
    paste_crest(img, crest, 150, (914, 128))
    return img


def build(key, team):
    crest = find_crest(key, team)
    p, s = palette(team, crest)
    name, year, city = club_name(team), team.foundation_year, team.cityname or club_name(team)
    flags = [f(p, s, crest, name, year, city) for f in (flag0, flag1, flag2, flag3)]
    tiles = [f(p, s, crest, name, year, city) for f in (diagonal, stripes_h, stripes_v, corner_block, dark_field, hoops, city_flag, year_flag)]
    atlas = Image.new('RGBA', (1024, 512), (0, 0, 0, 255))
    small = lambda im: im.resize((256, 128), Image.LANCZOS)
    for i, im in enumerate(flags + tiles):
        atlas.alpha_composite(small(im), ((i % 4) * 256, (i // 4) * 128))
    atlas.alpha_composite(scarf(p, s, crest, name, True).resize((512, 128), Image.LANCZOS), (0, 384))
    atlas.alpha_composite(scarf(p, s, crest, name, False).resize((512, 128), Image.LANCZOS), (512, 384))
    return flags, atlas


def write_dds(png_path, out_dir):
    subprocess.run([os.environ['TEXCONV_PATH'], '-nologo', '-y', '-f', 'BC1_UNORM', '-srgb', '-ft', 'dds', '-o', out_dir, png_path],
                   check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('team', choices=sorted(liga1orange_teams))
    ap.add_argument('--project', action='append', help='absolute path of a project to inject into (repeatable)')
    ap.add_argument('--no-inject', action='store_true')
    a = ap.parse_args()
    if a.team == 'fcsb':
        sys.exit('fcsb has hand-made fan flags')
    team = liga1orange_teams[a.team]
    tid = team.teamid_fifa17
    out = os.path.join(ROOT, 'assets', 'teams', a.team, 'fan_flags')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    flags, atlas = build(a.team, team)
    for k, im in enumerate(flags):
        im.convert('RGB').save(os.path.join(out, f'flag_{tid}_{k}_color.png'))
    atlas.convert('RGB').save(os.path.join(out, f'banner_{tid}_color.png'))
    for png in glob.glob(os.path.join(out, '*.png')):
        write_dds(png, out)
    print(f'{a.team}: wrote {len(flags)} flags + banner to {out}')
    if not a.no_inject:
        frosty = os.environ['FROSTYCLI_PATH']
        with tempfile.TemporaryDirectory() as tmp:
            for dds in glob.glob(os.path.join(out, '*.dds')):
                shutil.copy(dds, tmp)
            for project in a.project or [os.path.join(ROOT, 'Liga1Orange.test.fbproject')]:
                subprocess.run([frosty, 'FIFA17', 'import-team', str(team.teamid_fifa16), str(tid), tmp, project],
                               cwd=os.path.dirname(frosty), check=True, capture_output=True)
                print('  injected into', os.path.basename(project))


if __name__ == '__main__':
    main()
