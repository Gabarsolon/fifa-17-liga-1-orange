"""Fixed real 2016-17 Champions League / Europa League group stage (experiment, issue #29).

python scripts/euro_groups.py --project <abs .fbproject> [--workdir <dir>] [--no-inject]

The game draws the groups at random from pots (`advancement.txt`: pots 146-149 -> groups 151-158 for the CL, pots 222-225 ->
groups 227-238 for the EL). This script exports `tasks.txt` and `advancement.txt` of `dlc_FootballCompEng` from the project,
removes the pot -> group rows and adds `<comp>,start,FillWithTeam,<group node>,<slot>,<team id>,0` rows (the same task the
game uses for the fixed groups of the national-team competitions) with the groups of `db/reference/euro_groups_2016_17.json`
(real clubs or the in-game stand-ins), then writes them back with `import-legacy`.
There is NO first-season-only switch in the engine: the files have no season condition, so the groups repeat every season.
Original files are kept in `<workdir>/orig_*.txt`; `--restore` writes them back.
"""
import argparse
import json
import os
import subprocess
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
BASE = 'dlc/dlc_FootballCompEng/dlc/FootballCompEng/data/compdata/'
FILES = ('tasks.txt', 'advancement.txt')
# competition node, first group node, pot nodes whose rows to groups are removed, last group node
CL = dict(comp=121, first=151, groups=range(151, 159), pots=range(146, 150))
EL = dict(comp=185, first=227, groups=range(227, 239), pots=range(222, 226))


def frosty(*args):
    exe = os.environ['FROSTYCLI_PATH']
    subprocess.run([exe, 'FIFA17', *args], cwd=os.path.dirname(exe), check=True, capture_output=True)


def read(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.read()


def patch(tasks, adv, groups, spec):
    """returns the new texts; groups = {'A': [{'game_id':..}, ...], ...}"""
    nl = '\r\n'
    adv_lines = adv.split(nl)
    drop = 0
    kept = []
    for line in adv_lines:
        p = line.split(',')
        if len(p) == 4 and int(p[0]) in spec['pots'] and int(p[2]) in spec['groups']:
            drop += 1
            continue
        kept.append(line)
    rows = []
    for i, letter in enumerate(sorted(groups)):
        node = spec['first'] + i
        assert node in spec['groups'], (letter, node)
        for slot, t in enumerate(groups[letter], start=1):
            rows.append(f"{spec['comp']},start,FillWithTeam,{node},{slot},{t['game_id']},0")
    t_lines = tasks.split(nl)
    # right after the last `start` row of this competition
    idx = max(i for i, l in enumerate(t_lines) if l.startswith(f"{spec['comp']},start,"))
    t_lines[idx + 1:idx + 1] = rows
    return nl.join(t_lines), nl.join(kept), drop, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True, help='absolute path of the project')
    ap.add_argument('--workdir', required=True, help='absolute folder for the exported originals and the patched files')
    ap.add_argument('--no-inject', action='store_true')
    ap.add_argument('--restore', action='store_true', help='write the saved originals back')
    a = ap.parse_args()
    os.makedirs(a.workdir, exist_ok=True)
    originals = {n: os.path.join(a.workdir, 'orig_' + n) for n in FILES}
    if a.restore:
        for n in FILES:
            frosty('import-legacy', a.project, BASE + n, originals[n])
        print('originals restored into', os.path.basename(a.project))
        return
    for n in FILES:
        if not os.path.exists(originals[n]):  # first run: keep the pristine file
            frosty('export-legacy', a.project, BASE + n, originals[n])
    tasks, adv = read(originals['tasks.txt']), read(originals['advancement.txt'])
    data = json.load(open(os.path.join(ROOT, 'db', 'reference', 'euro_groups_2016_17.json'), encoding='utf-8'))
    for key, spec in (('cl', CL), ('el', EL)):
        tasks, adv, dropped, added = patch(tasks, adv, data[key], spec)
        print(f'{key}: removed {dropped} pot->group rows, added {added} FillWithTeam rows')
    out = {n: os.path.join(a.workdir, 'new_' + n) for n in FILES}
    for n, text in (('tasks.txt', tasks), ('advancement.txt', adv)):
        with open(out[n], 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    if not a.no_inject:
        for n in FILES:
            frosty('import-legacy', a.project, BASE + n, out[n])
        print('injected into', os.path.basename(a.project))


if __name__ == '__main__':
    sys.exit(main())
