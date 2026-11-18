"""Transfermarkt part of the squad report (AGENTS.md rule 10).

python scripts/tm_report.py <team_key> <tm_club_slug> <tm_club_id> [--season 2016]

Lists the FIFA 16 squad of the team (from db/fifa-16 TSVs) sorted by OVR with: matched Transfermarkt name + score,
club today (or retired / without club), current and peak market value. Marks which players are kept (a FIFA 17 slot
exists) and which are cut. Read-only; nothing is written. Low volume on purpose (one squad page, 2 requests per
matched player, 1.5 s pause): Transfermarkt does not like crawlers and its terms apply to this data.
"""
import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.request

import pandas as pd

sys.path.insert(0, __file__.rsplit('scripts', 1)[0] + 'scripts')
from constants import liga1orange_teams  # noqa: E402

ROOT = __file__.rsplit('scripts', 1)[0]
SLEEP = 1.5
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'


def get(url):
    time.sleep(SLEEP)
    headers = {'User-Agent': UA, 'Accept': '*/*'}
    if 'tmapi' not in url:  # the JSON API answers 406 when Accept-Language is sent
        headers['Accept-Language'] = 'en'
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z ]', '', s).strip()


def rd(p):
    return pd.read_csv(ROOT + p, sep='\t', encoding='utf-16-le', dtype=str, keep_default_na=False)


def fifa16_squad(teamid16):
    links, players, names = rd('db/fifa-16/teamplayerlinks.txt'), rd('db/fifa-16/players.txt'), rd('db/fifa-16/playernames.txt')
    nm = dict(zip(names.nameid, names['name']))
    sq = links[links.teamid == str(teamid16)].merge(players, on='playerid')
    sq['name'] = sq.apply(lambda p: (nm.get(p.firstnameid, '') + ' ' + nm.get(p.lastnameid, '')).strip(), axis=1)
    sq['ovr'] = sq.overallrating.astype(int)
    return sq.sort_values('ovr', ascending=False)


def tm_squad(slug, club_id, season):
    t = get(f'https://www.transfermarkt.com/{slug}/kader/verein/{club_id}/saison_id/{season}/plus/1')
    out = {}
    for _, pid, name in re.findall(r'href="/([^"/]+)/profil/spieler/(\d+)"[^>]*>\s*([^<]+?)\s*<', t):
        out.setdefault(pid, name)
    return out


def best_match(name, pool):
    n = norm(name)
    last = n.split()[-1] if n.split() else n
    scored = []
    for pid, tn in pool.items():
        m = norm(tn)
        s = difflib.SequenceMatcher(None, n, m).ratio()
        if last and last in m.split():
            s = max(s, 0.8)
        scored.append((s, pid, tn))
    scored.sort(reverse=True)
    return scored[0] if scored and scored[0][0] >= 0.75 else None


def profile(pid):
    t = get(f'https://www.transfermarkt.com/-/profil/spieler/{pid}')
    club = re.search(r'data-header__club[^>]*>\s*<a[^>]*title="([^"]+)"', t)
    club = club.group(1) if club else None
    retired = 'Retired' in t[:60000] and 'data-header__club' not in t[:60000]
    cur = re.search(r'data-header__market-value-wrapper[^>]*>\s*([^<]*?)\s*<', t)
    hist = json.loads(get(f'https://tmapi-alpha.transfermarkt.technology/player/{pid}/market-value-history'))
    vals = [h['marketValue']['value'] for h in hist.get('data', {}).get('history', [])]
    peak = max(vals) if vals else None
    last = vals[-1] if vals else None
    return {'club': 'retired' if retired else club, 'value_now': cur.group(1) if cur and cur.group(1) else None,
            'last_value': last, 'peak': peak}


def fmt(v):
    return '-' if v is None else (f'{v / 1e6:.2f}M' if v >= 1e6 else f'{v / 1e3:.0f}k')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('team')
    ap.add_argument('slug')
    ap.add_argument('club_id')
    ap.add_argument('--season', default='2016')
    ap.add_argument('--cut-only', action='store_true', help='only the players without a FIFA 17 slot')
    ap.add_argument('--sleep', type=float, default=1.5)
    a = ap.parse_args()
    global SLEEP
    SLEEP = a.sleep
    team = liga1orange_teams[a.team]
    sq = fifa16_squad(team.teamid_fifa16)
    slots = len(rd('db/teamplayerlinks.txt').query(f'teamid == "{team.teamid_fifa17}"'))
    pool = tm_squad(a.slug, a.club_id, a.season)
    print(f'{a.team}: {len(sq)} FIFA 16 players, {slots} slots in FIFA 17, {len(pool)} on Transfermarkt {a.season}')
    for i, (_, r) in enumerate(sq.iterrows()):
        m = best_match(r['name'], pool)
        tag = 'KEPT' if i < slots else 'CUT '
        if a.cut_only and i < slots:
            continue
        if not m:
            print(f'{tag} {r.ovr} {r["name"]}: no Transfermarkt match')
            continue
        try:
            p = profile(m[1])
        except Exception as e:  # noqa: BLE001
            print(f'{tag} {r.ovr} {r["name"]} <- {m[2]} ({m[0]:.2f}) profile failed: {e!r}')
            continue
        print(f'{tag} {r.ovr} {r["name"]} <- {m[2]} ({m[0]:.2f}) club today: {p["club"]}, value now {p["value_now"]}, '
              f'last {fmt(p["last_value"])}, peak {fmt(p["peak"])}')


if __name__ == '__main__':
    main()
