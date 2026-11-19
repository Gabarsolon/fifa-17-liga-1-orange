"""Season-1 European qualification from the real 2015-16 results (issue #29).

python scripts/euro_qualification.py --project <abs .fbproject> --workdir <abs dir> [--restore]

`initteams.txt` of `dlc_FootballCompEng` seeds the competition tables of the previous season at the start of a Career: node 353
(Liga 1) holds the final table (slot 0 = champion), node 335 the cup (winner, finalist). The seed still held Danish leftovers
(Craiova first, Steaua 4th, Astra absent), so Astra did not qualify. The seed is read once at career start, so only the first
season is affected. Now: the real 2015-16 table (`constants.LEAGUE_TABLE_2015_16`, top 6 = the slots of the seed) and the real
cup (`constants.CUP_2015_16`). The original file is kept in `<workdir>/orig_initteams.txt` (`--restore` writes it back).
"""
import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import CUP_2015_16, LEAGUE_TABLE_2015_16, liga1orange_teams  # noqa: E402
load_dotenv(os.path.join(ROOT, '.env'))
PATH = 'dlc/dlc_FootballCompEng/dlc/FootballCompEng/data/compdata/initteams.txt'


def frosty(*args):
    exe = os.environ['FROSTYCLI_PATH']
    subprocess.run([exe, 'FIFA17', *args], cwd=os.path.dirname(exe), check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--workdir', required=True)
    ap.add_argument('--restore', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.workdir, exist_ok=True)
    orig = os.path.join(a.workdir, 'orig_initteams.txt')
    if a.restore:
        frosty('import-legacy', a.project, PATH, orig)
        print('restored')
        return
    if not os.path.exists(orig):
        frosty('export-legacy', a.project, PATH, orig)
    text = open(orig, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    changed = {}
    for node, keys in (('353', LEAGUE_TABLE_2015_16), ('335', CUP_2015_16)):
        idx = [i for i, l in enumerate(lines) if l.startswith(node + ',')]
        old = [int(lines[i].split(',')[2]) for i in idx]
        new = [int(liga1orange_teams[k].teamid_fifa17) for k in keys][:len(idx)]
        for i, team in zip(idx, new):
            lines[i] = f"{node},{lines[i].split(',')[1]},{team}"
        changed[node] = (old, new)
    out = os.path.join(a.workdir, 'new_initteams.txt')
    open(out, 'w', encoding='utf-8', newline='').write(nl.join(lines))
    frosty('import-legacy', a.project, PATH, out)
    for node, (old, new) in changed.items():
        print('node', node, old, '->', new)


if __name__ == '__main__':
    main()
