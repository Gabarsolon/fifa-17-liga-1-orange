"""Audit of the imported Liga 1 teams: data in the TSVs against FIFA 16, and assets inside a Frosty project.

python scripts/audit_teams.py [--project Liga1Orange.fbproject] [team_key ...]

Read-only. For every team it prints
 - squad: FIFA 17 slots, FIFA 16 players, name pairs found, unpaired slots, players with an empty/out-of-range name id
 - players: for the paired players, columns of `players` that differ from FIFA 16 (the pipeline copies every common column,
   so a difference means the slot was not imported with the current code); jersey numbers that differ
 - team: foundation year, kit colours, formation id
 - assets (from `FrostyCmd project-info`): colour/normal/coeff textures, 3D crests, hotspots, legacy crests and minikits, minifaces
"""
import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict

import pandas as pd
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import liga1orange_teams  # noqa: E402

NAMEID_MAX = 29999
IGNORED_PLAYER_COLUMNS = {'playerid', 'firstnameid', 'lastnameid', 'commonnameid', 'playerjerseynameid',
                          'headclasscode', 'hashighqualityhead'}  # set by the pipeline on purpose


def rd(path):
    return pd.read_csv(os.path.join(ROOT, path), sep='\t', encoding='utf-16-le', dtype=str, keep_default_na=False)


def project_info(project):
    exe = os.environ['FROSTYCLI_PATH']
    out = subprocess.run([exe, 'FIFA17', 'project-info', project], cwd=os.path.dirname(exe), capture_output=True,
                         text=True, encoding='utf-8', errors='replace').stdout
    return [re.sub(r'^\[[^\]]*\]:\s*', '', line).strip() for line in out.splitlines()]


def squad_names(players, links, names, teamid):
    nm = dict(zip(names.nameid, names['name']))
    rows = links[links.teamid == str(teamid)].merge(players, on='playerid')
    rows['full'] = rows.apply(lambda r: (nm.get(r.firstnameid, '') + ' ' + nm.get(r.lastnameid, '')).strip(), axis=1)
    return rows


def audit_team(key, team, tables, info):
    p17, l17, n17, p16, l16, n16, t17, t16, k17, k16 = tables
    print(f'\n=== {key} (FIFA 17 {team.teamid_fifa17} <- FIFA 16 {team.teamid_fifa16})')
    s17 = squad_names(p17, l17, n17, team.teamid_fifa17)
    s16 = squad_names(p16, l16, n16, team.teamid_fifa16)
    by16 = defaultdict(list)
    for r in s16.itertuples():
        by16[(r.firstnameid and dict(zip(n16.nameid, n16['name'])).get(r.firstnameid, ''),
              dict(zip(n16.nameid, n16['name'])).get(r.lastnameid, ''))].append(r)
    nm17 = dict(zip(n17.nameid, n17['name']))
    nm16 = dict(zip(n16.nameid, n16['name']))
    pairs, unpaired = [], []
    for r in s17.itertuples():
        key16 = (nm17.get(r.firstnameid, ''), nm17.get(r.lastnameid, ''))
        if by16.get(key16):
            pairs.append((r, by16[key16].pop(0)))
        else:
            unpaired.append(r)
    bad_ids = [r.full for r in s17.itertuples()
               if int(r.firstnameid) > NAMEID_MAX or int(r.lastnameid) > NAMEID_MAX or r.firstnameid not in nm17 and r.firstnameid != '0']
    print(f'squad: {len(s17)} slots, {len(s16)} FIFA 16 players, {len(pairs)} paired by name, '
          f'{len(unpaired)} slots not matching a FIFA 16 name, {len(bad_ids)} with empty/out-of-range name id')
    if unpaired:
        print('  unpaired slots:', ', '.join(f'{r.full}' for r in unpaired[:8]))
    # players columns vs FIFA 16
    common = [c for c in p17.columns if c in p16.columns and c not in IGNORED_PLAYER_COLUMNS]
    diff = defaultdict(int)
    jersey_diff = 0
    for r17, r16 in pairs:
        for c in common:
            if getattr(r17, c, None) != getattr(r16, c, None):
                diff[c] += 1
        if r17.jerseynumber != r16.jerseynumber:
            jersey_diff += 1
    top = sorted(diff.items(), key=lambda kv: -kv[1])[:6]
    print(f'players: {sum(1 for c in diff)} of {len(common)} columns differ in some pair; jersey numbers differ for {jersey_diff}/{len(pairs)}'
          + (f'; most: {top}' if top else ''))
    # team data
    r17t = t17[t17.teamid == str(team.teamid_fifa17)].iloc[0]
    r16t = t16[t16.teamid == str(team.teamid_fifa16)].iloc[0]
    colour_cols = [c for c in t17.columns if c.startswith('teamcolor') and c in t16.columns]
    cdiff = [c for c in colour_cols if r17t[c] != r16t[c]]
    print(f'team: foundationyear {r17t["foundationyear"]} (constants {team.foundation_year}), '
          f'team colours differing from FIFA 16: {cdiff or "none"}')
    kit17 = k17[k17.teamtechid == str(team.teamid_fifa17)] if 'teamtechid' in k17.columns else k17[k17.teamid == str(team.teamid_fifa17)]
    kit16 = k16[k16.teamtechid == str(team.teamid_fifa16)] if 'teamtechid' in k16.columns else k16[k16.teamid == str(team.teamid_fifa16)]
    print(f'kits: {len(kit17)} rows in FIFA 17, {len(kit16)} in FIFA 16')
    # assets
    tid = str(team.teamid_fifa17)
    tex = defaultdict(set)
    for line in info:
        m = re.search(rf'/(jersey|shorts|socks|crest)_{tid}_(\d)_0_(color|normal|coeff)$', line)
        if m:
            tex[m.group(3)].add((m.group(1), m.group(2)))
    hotspots = sum(1 for line in info if re.search(rf'/hotspots_{tid}_\d_0$', line))
    crests = sum(1 for line in info if re.search(rf'imgAssets/crest[^/]*/(light|dark)/l{tid}\.dds$', line, re.I))
    minikits = sum(1 for line in info if re.search(rf'imgAssets/kits/j\d_{tid}_0\.dds$', line, re.I))
    ids = set(s17.playerid)
    faces = sum(1 for line in info if (m := re.search(r'imgAssets/heads/p(\d+)\.dds$', line, re.I)) and m.group(1) in ids)
    col = tex['color']
    print(f'assets: colour textures {len(col)}/12 (jersey+shorts+socks+crest x3 kits; socks of the gk kit may be shared), '
          f'normal {len(tex["normal"])}/9, coeff {len(tex["coeff"])}/9, hotspots {hotspots}/3, legacy crests {crests}/8, '
          f'minikits {minikits}/3, minifaces {faces}/{len(ids)}')
    missing_col = sorted({(p, k) for p in ('jersey', 'shorts', 'socks') for k in '012'} - col)
    if missing_col:
        print('  missing colour textures:', missing_col)
    return len(bad_ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', default=os.path.join(ROOT, 'Liga1Orange.fbproject'))
    ap.add_argument('teams', nargs='*')
    a = ap.parse_args()
    tables = (rd('db/players.txt'), rd('db/teamplayerlinks.txt'), rd('db/playernames.txt'),
              rd('db/fifa-16/players.txt'), rd('db/fifa-16/teamplayerlinks.txt'), rd('db/fifa-16/playernames.txt'),
              rd('db/teams.txt'), rd('db/fifa-16/teams.txt'), rd('db/teamkits.txt'), rd('db/fifa-16/teamkits.txt'))
    info = project_info(os.path.abspath(a.project))
    for key in a.teams or liga1orange_teams:
        audit_team(key, liga1orange_teams[key], tables, info)


if __name__ == '__main__':
    main()
