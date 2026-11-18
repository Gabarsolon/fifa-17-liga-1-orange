"""One-off: add the flat normal/coeff maps (kit_flat_maps.py) of the teams imported with the pipeline to the cumulative
test project and to every per-team snapshot that contains the team. Teams made by hand (fcsb..dinamo) are skipped.
python scripts/apply_flat_maps.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_flat_maps as k  # noqa: E402
from constants import liga1orange_teams  # noqa: E402

ORDER = ['poli', 'botosani', 'poli_iasi', 'voluntari', 'chiajna', 'gazmetan', 'pandurii', 'asa']
for i, key in enumerate(ORDER):
    team = liga1orange_teams[key]
    paths = k.build(os.path.join(k.ROOT, 'assets', 'teams', key, 'final'), team.teamid_fifa17)
    projects = [os.path.join(k.ROOT, 'Liga1Orange.test.fbproject')]
    # snapshots of this team and of every later one contain it (poli was there from the start)
    later = ORDER[max(i, 1):] if key != 'poli' else ORDER[1:]
    projects += [os.path.join(k.ROOT, f'Liga1Orange.{later_key}.test.fbproject') for later_key in later]
    for project in projects:
        if os.path.exists(project):
            k.inject(team, paths, project)
    print(key, 'flat maps injected into', len(projects), 'projects', flush=True)
