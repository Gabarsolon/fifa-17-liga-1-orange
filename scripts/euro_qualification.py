"""Season-1 European qualification of Astra and Steaua (issue #29).

python scripts/euro_qualification.py --project <abs .fbproject> --workdir <abs dir> [--restore]

`initteams.txt` of `dlc_FootballCompEng` seeds the competition tables of the previous season at the start of a Career: node 353
(Liga 1) holds the final table (slot 0 = champion), node 335 the cup. The seed still held the Danish leftovers (Craiova first,
Steaua 4th, Astra absent), so Astra did not qualify. The seed is read once at career start, so only the first season is affected:
from then on the game uses its own tables. Real 2015-16: Astra champion, Steaua second. Other slots keep their old order.
The original file is kept in `<workdir>/orig_initteams.txt` (`--restore` writes it back).
"""
import argparse
import os
import subprocess

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
PATH = 'dlc/dlc_FootballCompEng/dlc/FootballCompEng/data/compdata/initteams.txt'
ASTRA, STEAUA = 270, 269


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
    idx = [i for i, l in enumerate(lines) if l.startswith('353,')]
    old = [int(lines[i].split(',')[2]) for i in idx]
    new = [ASTRA, STEAUA] + [t for t in old if t not in (ASTRA, STEAUA)]
    new = new[:len(old)]
    for i, team in zip(idx, new):
        lines[i] = f"353,{lines[i].split(',')[1]},{team}"
    out = os.path.join(a.workdir, 'new_initteams.txt')
    open(out, 'w', encoding='utf-8', newline='').write(nl.join(lines))
    frosty('import-legacy', a.project, PATH, out)
    print('node 353', old, '->', new)


if __name__ == '__main__':
    main()
