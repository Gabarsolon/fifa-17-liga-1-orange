"""Move the player-name hotspot of a kit off printed art (what the first five teams needed by hand).

python scripts/fix_hotspots.py <team_key> [--project <abs .fbproject>] [--dry-run]

Every kit has a `PlayerHotspotDataAsset` (`hotspots_<teamid>_<kit>_0`) whose `Jersey.Name` / `Jersey.NumberBack` are UV
rectangles (x, y, z, w) where the game draws the shirt name and number. The replaced Danish kit puts the name just BELOW the
number. In the hand-made teams the user moved the name in 15 of 15 kits: when the kit art prints something there (a back
sponsor such as "TRANSGAZ" or "NetBet") the name goes ABOVE the number instead, always with the standard size 0.182 x 0.033
and a gap of 0.004 to the number.
This script automates that: it measures how busy the colour texture is under the Danish name rectangle and under a
standard rectangle above the number, and moves the name above only when the Danish place is busy (> 10) and the new place is
clean (< 5). Nothing else is touched. Needs FrostyMeshCli (local, FROSTYMESHCLI_PATH in .env).
Result on the 8 pipeline teams: only the three Gaz Metan kits needed it (busyness 29-82 vs 0).
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from dotenv import load_dotenv
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import liga1orange_teams  # noqa: E402

NAME_W, NAME_H, GAP = 0.182, 0.033, 0.004
BUSY_OLD, CLEAN_NEW = 10.0, 5.0


def cli(*args):
    exe = os.environ['FROSTYMESHCLI_PATH']
    env = dict(os.environ)
    return subprocess.run([exe, 'FIFA17', *args], cwd=os.path.dirname(exe), capture_output=True, text=True,
                          encoding='utf-8', errors='replace', env=env)


def hotspot_names(team_id):
    """EBX names of the hotspot assets of a FIFA 17 team slot (from FrostyCmd list-assets)."""
    exe = os.environ['FROSTYCLI_PATH']
    out = subprocess.run([exe, 'FIFA17', 'list-assets', 'ebx'], cwd=os.path.dirname(exe), capture_output=True, text=True,
                         encoding='utf-8', errors='replace').stdout
    names = sorted(set(re.findall(rf'(content/character/kit/[^\s]+/hotspots_{team_id}_[012]_0)\b', out)))
    return names


def parse_dump(text):
    values, stack = {}, []
    for line in text.splitlines():
        m = re.match(r'^(\s*)([A-Za-z0-9_]+):\s*$', line)
        indent = len(line) - len(line.lstrip())
        if m:
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, m.group(2)))
            continue
        m = re.match(r'^\s*([xyzw]) = (.+)$', line)
        if m:
            values.setdefault('/'.join(n for _, n in stack), {})[m.group(1)] = float(m.group(2))
    return values


def busyness(img, x0, y0, x1, y1):
    w, h = img.size
    box = (int(min(x0, x1) * w), int(min(y0, y1) * h), int(max(x0, x1) * w) + 1, int(max(y0, y1) * h) + 1)
    a = np.array(img.crop(box).convert('RGB')).astype(float)
    if a.size == 0:
        return 0.0
    return float(np.abs(a - np.median(a.reshape(-1, 3), axis=0)).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('team', choices=sorted(liga1orange_teams))
    ap.add_argument('--project', action='append', help='absolute path of a project to modify (repeatable)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    team = liga1orange_teams[a.team]
    tid = str(team.teamid_fifa17)
    final = os.path.join(ROOT, 'assets', 'teams', a.team, 'final')
    names = hotspot_names(tid)
    if not names:
        sys.exit(f'no hotspot assets found for team {tid}')
    projects = a.project or [os.path.join(ROOT, 'Liga1Orange.test.fbproject')]
    dump = cli('dump-ebx', ','.join(names)).stdout
    blocks = dump.split('=== ')[1:]
    for block in blocks:
        name, body = block.split('\n', 1)
        name = name.strip()
        kit = re.search(r'hotspots_\d+_(\d)_0$', name).group(1)
        texture = os.path.join(final, f'jersey_{tid}_{kit}_0_color.png')
        if not os.path.exists(texture):
            print(f'{name}: no {os.path.basename(texture)} (hand-made kit?), skipped')
            continue
        values = parse_dump(body)
        n, nb = values['Jersey/Name'], values['Jersey/NumberBack']
        img = Image.open(texture).convert('RGB')
        old = busyness(img, n['x'], n['y'], n['z'], n['w'])
        cx = (nb['x'] + nb['z']) / 2
        top_number = min(nb['y'], nb['w'])
        bottom, top = top_number - GAP, top_number - GAP - NAME_H
        new = busyness(img, cx - NAME_W / 2, top, cx + NAME_W / 2, bottom)
        print(f'{name.split("/")[-1]}: name under art {old:5.1f}, above number {new:5.1f}', end=' ')
        if not (old > BUSY_OLD and new < CLEAN_NEW):
            print('-> keep')
            continue
        # keep the orientation of the original rectangle (x > z and y > w in the Danish assets)
        x, z = (cx + NAME_W / 2, cx - NAME_W / 2) if n['x'] >= n['z'] else (cx - NAME_W / 2, cx + NAME_W / 2)
        y, w = (bottom, top) if n['y'] >= n['w'] else (top, bottom)
        print(f'-> move to x={x:.4f} y={y:.4f} z={z:.4f} w={w:.4f}')
        if a.dry_run:
            continue
        for project in projects:
            r = cli('set-vec4', project, name, 'Jersey.Name', f'{x:.6f}', f'{y:.6f}', f'{z:.6f}', f'{w:.6f}')
            if r.returncode != 0:
                sys.exit(f'set-vec4 failed: {(r.stdout + r.stderr)[-300:]}')


if __name__ == '__main__':
    main()
