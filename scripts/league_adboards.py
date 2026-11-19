"""Replace the Danish text on the league's stadium ad boards (issue: "EASPORTSDANMARK" boards in Romanian stadiums).

python scripts/league_adboards.py [--project <abs .fbproject> ...] [--no-inject]

The ad boards of a league are one atlas per league: `content/worlds/adboard/textures/denmark_1/adboard_1_color`
(1024x2048, BC1 sRGB, 12 mips, 16 stripes of 128 px). Exported with `FrostyMeshCli export-texture`; stripes 0-7 are repeated in
8-15: FIFA.com, FIFA Football for Hope, FIFA 17, EA SPORTS, FIFA 17 Ultimate Team, EASPORTS.COM/FIFA, a Facebook stripe
"@EASPORTSDANMARK" (6), YouTube, ... a Snapchat stripe and an Instagram stripe "@EASPORTSDANMARK" (15). Only the two Danish
stripes (6 and 15) are redrawn, with the league logo and the league name; the generic EA/FIFA stripes stay.
The league slot is the replaced Danish league 1, so the same texture name is used.

Default source (2026-11-19): the Romanian sponsor boards of FIFA 16 FRLT, `data/sceneassets/adboard/specificadboard_0_83_0_0.rx3`
(league 83 = Liga 1). The RX3 holds one 512x1024 DXT1 texture (16 stripes of 64 px, the same 8:1 stripe shape as FIFA 17's 128 px
stripes of 1024 px): Radio Romania, SuperBet, winmasters, Ceresit, NetBet, DentalMed, City Insurance, Suzuki, Adeplast, Orange,
Bel Profile, Baumit, Kober, Shell Helix, Nike. The first mip is carved from the tail of the file (the container header is 344 bytes
before the 349544 bytes of the mip chain) and upscaled 2x to 1024x2048. `--own` keeps the older drawn version (two stripes with the
league logo and "LIGA 1 ORANGE", the rest generic EA/FIFA).
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
ORIGINAL = os.path.join(ROOT, 'assets', 'league', 'adboard_1_color_original.png')
OUT_DIR = os.path.join(ROOT, 'assets', 'league')
TEXTURE = 'content/worlds/adboard/textures/denmark_1/adboard_1_color'
STRIPE = 128
ORANGE = (255, 121, 0)
FONT = r'C:\Windows\Fonts\ariblk.ttf'


def fit_font(draw, text, max_w, max_h):
    size = max_h
    while size > 8:
        font = ImageFont.truetype(FONT, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        if r - l <= max_w and b - t <= max_h:
            return font, (l, t, r, b)
        size -= 2
    return ImageFont.truetype(FONT, 8), draw.textbbox((0, 0), text, font=ImageFont.truetype(FONT, 8))


def logo_stripe(logo):
    """White stripe: the league logo centred (replaces the Facebook stripe)."""
    img = Image.new('RGBA', (1024, STRIPE), (255, 255, 255, 255))
    h = 108
    w = int(logo.width * h / logo.height)
    img.alpha_composite(logo.resize((w, h), Image.LANCZOS), ((1024 - w) // 2, (STRIPE - h) // 2))
    return img


def text_stripe():
    """White stripe with the tricolour edge and 'LIGA 1 ORANGE' (replaces the Instagram stripe)."""
    img = Image.new('RGBA', (1024, STRIPE), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    for i, c in enumerate(((0, 43, 127), (252, 209, 22), (206, 17, 38))):
        d.rectangle([i * 1024 // 3, 0, (i + 1) * 1024 // 3, 12], fill=c)
        d.rectangle([i * 1024 // 3, STRIPE - 13, (i + 1) * 1024 // 3, STRIPE], fill=c)
    text = 'LIGA 1 ORANGE'
    font, (l, t, r, b) = fit_font(d, text, 900, 80)
    d.text(((1024 - (r - l)) / 2 - l, (STRIPE - (b - t)) / 2 - t), text, font=font, fill=ORANGE)
    return img


FRLT_RX3 = os.path.join('data', 'sceneassets', 'adboard', 'specificadboard_0_83_0_0.rx3')
FRLT_PNG = os.path.join(OUT_DIR, 'adboard_frlt_512x1024.png')


def frlt_atlas():
    """The FRLT league board (512x1024) upscaled to the FIFA 17 atlas size. Carved from the RX3 when FIFA 16 is installed, else read
    from the PNG kept in assets/league."""
    import struct
    rx3 = os.path.join(os.environ.get('FIFA16_DIR', ''), FRLT_RX3)
    if os.path.exists(rx3):
        raw = open(rx3, 'rb').read()
        mip0 = raw[-349544:-349544 + 512 * 1024 // 2]
        header = (b'DDS ' + struct.pack('<7I', 124, 0x1007 | 0x80000, 1024, 512, len(mip0), 0, 1) + bytes(44)
                  + struct.pack('<2I4s5I', 32, 4, b'DXT1', 0, 0, 0, 0, 0) + struct.pack('<5I', 0x1000, 0, 0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            dds = os.path.join(tmp, 'frlt.dds')
            open(dds, 'wb').write(header + mip0)
            subprocess.run([os.environ['TEXCONV_PATH'], '-nologo', '-y', '-ft', 'png', '-o', tmp, dds], check=True, capture_output=True)
            Image.open(os.path.join(tmp, 'frlt.png')).convert('RGB').save(FRLT_PNG)
    if not os.path.exists(FRLT_PNG):
        raise SystemExit(f'missing {rx3} and {FRLT_PNG}')
    return Image.open(FRLT_PNG).convert('RGBA').resize((1024, 2048), Image.LANCZOS)


def build(own=False):
    if not own:
        return frlt_atlas()
    if not os.path.exists(ORIGINAL):
        raise SystemExit(f'missing {ORIGINAL} (export it: FrostyMeshCli FIFA17 export-texture {TEXTURE} adboard.dds, then texconv -ft png)')
    atlas = Image.open(ORIGINAL).convert('RGBA')
    logo = Image.open(os.path.join(ROOT, 'assets', 'league', 'Liga_I_logo_hires.png')).convert('RGBA')
    atlas.paste(logo_stripe(logo), (0, 6 * STRIPE))
    atlas.paste(text_stripe(), (0, 15 * STRIPE))
    return atlas


def tiny_logos(projects):
    """data/ui/imgAssets/leagueLogos_tiny/{dark,light}/l1.dds (200x64 DXT5, one mip): the small league logo of the Career hub
    'Clasamente' tile and other small spots; it still showed 'alka SUPERLIGA'. The other league-1 images (league, 512x128,
    512x512) were replaced earlier; trophies and the online emblems are generic, not Danish."""
    logo = Image.open(os.path.join(ROOT, 'assets', 'league', 'Liga_I_logo_hires.png')).convert('RGBA')
    h = 56
    w = int(logo.width * h / logo.height)
    img = Image.new('RGBA', (200, 64), (0, 0, 0, 0))
    img.alpha_composite(logo.resize((w, h), Image.LANCZOS), ((200 - w) // 2, (64 - h) // 2))
    png = os.path.join(OUT_DIR, 'l1_tiny.png')
    img.save(png)
    subprocess.run([os.environ['TEXCONV_PATH'], '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '1', '-ft', 'dds', '-o', OUT_DIR, png],
                   check=True, capture_output=True)
    dds = os.path.join(OUT_DIR, 'l1_tiny.dds')
    frosty = os.environ['FROSTYCLI_PATH']
    for project in projects:
        for variant in ('dark', 'light'):
            subprocess.run([frosty, 'FIFA17', 'import-legacy', project, f'data/ui/imgAssets/leagueLogos_tiny/{variant}/l1.dds', dds],
                           cwd=os.path.dirname(frosty), check=True, capture_output=True)
        print('  tiny league logos injected into', os.path.basename(project))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', action='append', help='absolute path of a project to inject into (repeatable)')
    ap.add_argument('--no-inject', action='store_true')
    ap.add_argument('--own', action='store_true', help='older drawn version (league logo + LIGA 1 ORANGE stripes)')
    a = ap.parse_args()
    atlas = build(a.own)
    png = os.path.join(OUT_DIR, 'adboard_1_color.png')
    atlas.convert('RGB').save(png)
    subprocess.run([os.environ['TEXCONV_PATH'], '-nologo', '-y', '-f', 'BC1_UNORM', '-srgb', '-ft', 'dds', '-o', OUT_DIR, png],
                   check=True, capture_output=True)
    print('wrote', os.path.join(OUT_DIR, 'adboard_1_color.dds'))
    if not a.no_inject:
        frosty = os.environ['FROSTYCLI_PATH']
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(os.path.join(OUT_DIR, 'adboard_1_color.dds'), tmp)
            for project in a.project or [os.path.join(ROOT, 'Liga1Orange.test.fbproject')]:
                # import-team replaces the first argument inside the file name: use one that does not occur
                subprocess.run([frosty, 'FIFA17', 'import-team', 'zzzz', 'zzzz', tmp, project], cwd=os.path.dirname(frosty),
                               check=True, capture_output=True)
                print('  injected into', os.path.basename(project))
        tiny_logos(a.project or [os.path.join(ROOT, 'Liga1Orange.test.fbproject')])


if __name__ == '__main__':
    main()
