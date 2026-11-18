"""Flat ("plata") normal and coeff maps for the kits of an imported team.

python scripts/kit_flat_maps.py <team_key> [--project <abs path to a .fbproject>] [--no-inject]

Why: the Danish team that a Liga 1 team replaces keeps its own `_normal` (bump) and `_coeff` (material) textures,
so its sponsor/brand prints (e.g. "Hellerup Finans", "Fog", adidas/Joma logos) stay embossed in the new kit. The
colour textures are replaced by the import, these two are not. The same fix was made by hand in Photoshop for the first
six teams (FCSB's `jersey_269_0_0_normal` is one flat colour). Here every normal/coeff map of home/away/goalkeeper
jersey, shorts and socks becomes one flat colour (the means of the hand-cleaned FCSB maps), written as DXT1 DDS with
mips (the format and sizes of the originals) next to the colour textures and injected with `FrostyCmd import-team`.
Trade-off: the fine fabric weave of the original maps is lost. Tune by hand in Photoshop if needed (the DDS are plain
files in assets/teams/<key>/final).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from dotenv import load_dotenv
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SIZES = {'jersey': (1024, 1024), 'shorts': (1024, 512), 'socks': (512, 256)}
FLAT = {
    'normal': {'jersey': (127, 130, 0), 'shorts': (128, 128, 0), 'socks': (128, 127, 0)},
    'coeff': {'jersey': (116, 52, 0), 'shorts': (114, 47, 0), 'socks': (101, 18, 0)},
}
KITS = (0, 1, 2)  # home, away, goalkeeper


def build(final_dir, teamid, out_dir=None):
    """Write the 18 flat DDS files for FIFA 17 team id `teamid` into out_dir (default final_dir); returns their paths."""
    out_dir = out_dir or final_dir
    os.makedirs(out_dir, exist_ok=True)
    texconv = os.environ['TEXCONV_PATH']
    paths = []
    with tempfile.TemporaryDirectory() as tmp:
        for kit in KITS:
            for part, size in SIZES.items():
                for kind in ('normal', 'coeff'):
                    name = f'{part}_{teamid}_{kit}_0_{kind}'
                    Image.new('RGB', size, FLAT[kind][part]).save(os.path.join(tmp, name + '.png'))
        subprocess.run([texconv, '-nologo', '-y', '-f', 'BC1_UNORM', '-ft', 'dds', '-o', out_dir,
                        *[os.path.join(tmp, f) for f in sorted(os.listdir(tmp))]], check=True, capture_output=True)
    for kit in KITS:
        for part in SIZES:
            for kind in ('normal', 'coeff'):
                path = os.path.join(out_dir, f'{part}_{teamid}_{kit}_0_{kind}.dds')
                assert os.path.exists(path), path
                paths.append(path)
    return paths


def inject(team, paths, project):
    frosty = os.environ['FROSTYCLI_PATH']
    with tempfile.TemporaryDirectory() as tmp:
        for p in paths:
            shutil.copy(p, tmp)
        subprocess.run([frosty, 'FIFA17', 'import-team', str(team.teamid_fifa16), str(team.teamid_fifa17), tmp, project],
                       cwd=os.path.dirname(frosty), check=True, capture_output=True)


def main():
    from constants import liga1orange_teams
    ap = argparse.ArgumentParser()
    ap.add_argument('team', choices=sorted(liga1orange_teams))
    ap.add_argument('--project', action='append', help='absolute path of a project to inject into (repeatable); default the test project')
    ap.add_argument('--no-inject', action='store_true')
    a = ap.parse_args()
    team = liga1orange_teams[a.team]
    final = os.path.join(ROOT, 'assets', 'teams', a.team, 'final')
    paths = build(final, team.teamid_fifa17)
    print(f'{a.team}: wrote {len(paths)} flat maps to {final}')
    if not a.no_inject:
        for project in a.project or [os.path.join(ROOT, 'Liga1Orange.test.fbproject')]:
            inject(team, paths, project)
            print('  injected into', os.path.basename(project))


if __name__ == '__main__':
    main()
