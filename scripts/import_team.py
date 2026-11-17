"""Import one Liga 1 team from FIFA 16 into FIFA 17 and inject it into a TEST copy of the Frosty project.

    python scripts/import_team.py poli [--skip-db] [--skip-assets] [--skip-frosty]

Never touches Liga1Orange.fbproject: a clean baseline (git ref FBPROJECT_BASELINE_REF) is written to
Liga1Orange.test.fbproject and everything is injected there. Copy it over the real project yourself
once it works in game.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from dotenv import load_dotenv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(ROOT, '.env'))

from constants import liga1orange_teams
from db_operations import (
    replace_team_details_from_fifa17_with_ones_from_fif16,
    replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16,
    replace_players_from_fifa16_with_players_from_fifa17,
    save_tsv,
)
from menu import extract_assets_with_cmcli
from kit_textures import socks_from_f16_atlas
import validate

DB_DIR = os.path.join(ROOT, 'db')
ORIGINAL_DIR = os.path.join(DB_DIR, 'original_tables')
# Last commit of Liga1Orange.fbproject before the (broken) Poli injection.
FBPROJECT_BASELINE_REF = '00ac879'
TEST_PROJECT = os.path.join(ROOT, 'Liga1Orange.test.fbproject')

FIFA_TABLES = [
    'defaultteamdata.txt', 'default_teamsheets.txt', 'formations.txt',
    'teams.txt', 'teamkits.txt', 'players.txt', 'playernames.txt', 'teamplayerlinks.txt',
]


def run(cmd, **kwargs):
    print('>', ' '.join(f'"{c}"' if ' ' in c else c for c in cmd))
    subprocess.run(cmd, check=True, **kwargs)


def import_db(team):
    print('1. Team details')
    replace_team_details_from_fifa17_with_ones_from_fif16(
        team.teamid_fifa17, team.teamid_fifa16, team.foundation_year, team.cityname)
    print('2. Formation, teamsheet, teamdata')
    replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(team.teamid_fifa17, team.teamid_fifa16)
    print('3. Players (sorted by overall, best first)')
    replace_players_from_fifa16_with_players_from_fifa17(team.teamid_fifa17, team.teamid_fifa16)
    print('4. Saving TSV files')
    save_tsv()


def build_assets(key, team):
    raw = os.path.join(ROOT, 'assets', 'teams', key, 'f16_raw')
    final = os.path.join(ROOT, 'assets', 'teams', key, 'final')
    for d in (raw, final):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)

    print('5. Extracting FIFA 16 kits and crests (CmCli)')
    extract_assets_with_cmcli('export-kit', team.teamid_fifa16, raw, convert_to_dds=True)
    extract_assets_with_cmcli('export-crests', team.teamid_fifa16, raw, convert_to_dds=True)

    # FIFA 16 kit export: tex_1 = jersey colour 1024x1024, tex_3 = 1024x512 atlas (socks on top, shorts below).
    # FIFA 17 wants jersey 1024x1024, shorts 1024x512 and a separate socks texture 512x256.
    # tex_0/2/4 are minikit and data maps: FIFA 17 keeps its own coeff/normal maps.
    f17, f16 = team.teamid_fifa17, team.teamid_fifa16
    kits = sorted({os.path.basename(p).split('_')[3] for p in glob.glob(os.path.join(raw, f'team_{f16}_kit_*_tex_3.png'))})
    if not kits:
        sys.exit(f'No kit textures exported for FIFA 16 team {f16} into {raw}')
    for k in kits:
        def src(n):
            return os.path.join(raw, f'team_{f16}_kit_{k}_tex_{n}.png')
        shutil.copy(src(1), os.path.join(final, f'jersey_{f17}_{k}_0_color.png'))
        shutil.copy(src(3), os.path.join(final, f'shorts_{f17}_{k}_0_color.png'))
        socks_from_f16_atlas(src(3), os.path.join(final, f'socks_{f17}_{k}_0_color.png'))
    # New CmCli names the 256x256 crest "standard"; the older build called it "light_256x256".
    crest = next((c for c in (os.path.join(raw, f'team_{f16}_crest_standard.png'),
                              os.path.join(raw, f'team_{f16}_crest_light_256x256.png')) if os.path.exists(c)), None)
    if crest:
        for n in range(4):
            shutil.copy(crest, os.path.join(final, f'crest_{f17}_{n}_0_color.png'))
    else:
        print('WARNING: no 256x256 crest exported, 3D kit crests not generated')

    print('6. PNG -> DDS (final)')
    run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(ROOT, 'scripts', 'ConvertPNGsToDDS.ps1'),
         '-TargetDirectory', final])
    return raw, final


def rebuild_dbs():
    dbcli = os.environ['DBCLI_PATH']
    out_fifa_db = os.path.join(DB_DIR, 'fifa_ng_db.DB')
    out_fifa_xml = os.path.join(DB_DIR, 'fifa_ng_db-meta.XML')
    out_eng_db = os.path.join(DB_DIR, 'eng_us.DB')
    out_eng_xml = os.path.join(DB_DIR, 'eng_us-meta.XML')
    print('Rebuilding databases (DbCli)')
    # Start from the original schema XMLs; DbCli overwrites them with a regenerated XML when the schema changes.
    shutil.copy2(os.path.join(ORIGINAL_DIR, 'fifa_ng_db-meta.og.XML'), out_fifa_xml)
    shutil.copy2(os.path.join(ORIGINAL_DIR, 'eng_us-meta.XML'), out_eng_xml)
    with tempfile.TemporaryDirectory() as tsv_dir:
        for table in FIFA_TABLES:
            shutil.copy2(os.path.join(DB_DIR, table), tsv_dir)
        run([dbcli, 'import-all', os.path.join(ORIGINAL_DIR, 'fifa_ng_db.og.DB'),
             os.path.join(ORIGINAL_DIR, 'fifa_ng_db-meta.og.XML'), tsv_dir, out_fifa_db])
    run([dbcli, 'import-table', os.path.join(ORIGINAL_DIR, 'eng_us.DB'), os.path.join(ORIGINAL_DIR, 'eng_us-meta.XML'),
         'LanguageStrings', os.path.join(DB_DIR, 'LanguageStrings.txt'), out_eng_db])
    return out_fifa_db, out_fifa_xml, out_eng_db, out_eng_xml


def inject(team, raw, final, dbs):
    frosty = os.environ['FROSTYCLI_PATH']
    cwd = os.path.dirname(frosty)  # FrostyCmd loads sibling DLLs from its own folder
    print(f'7. Writing clean baseline project ({FBPROJECT_BASELINE_REF}) to {os.path.basename(TEST_PROJECT)}')
    with open(TEST_PROJECT, 'wb') as out:
        subprocess.run(['git', '-C', ROOT, 'show', f'{FBPROJECT_BASELINE_REF}:Liga1Orange.fbproject'], check=True, stdout=out)

    def legacy(target, source):
        run([frosty, 'FIFA17', 'import-legacy', TEST_PROJECT, target, source], cwd=cwd)

    print('8. Injecting DBs + meta XMLs')
    out_fifa_db, out_fifa_xml, out_eng_db, out_eng_xml = dbs
    legacy('data/db/fifa_ng_db.db', out_fifa_db)
    legacy('data/db/fifa_ng_db-meta.xml', out_fifa_xml)
    legacy('data/loc/eng_us.db', out_eng_db)
    legacy('data/loc/eng_us-meta.xml', out_eng_xml)

    print('9. Injecting 3D kit textures')
    run([frosty, 'FIFA17', 'import-team', str(team.teamid_fifa16), str(team.teamid_fifa17), final, TEST_PROJECT], cwd=cwd)

    print('10. Injecting UI crests and minikits')
    f17, f16 = team.teamid_fifa17, team.teamid_fifa16
    for variant, tag in (('light', ''), ('dark', 'dark_')):
        for folder, size in (('crest', 'standard'), ('crest16x16', '16x16'), ('crest32x32', '32x32'), ('crest50x50', '50x50')):
            src = os.path.join(raw, f'team_{f16}_crest_{tag}{size}.dds')
            if os.path.exists(src):
                legacy(f'data/ui/imgAssets/{folder}/{variant}/l{f17}.dds', src)
    for n in range(3):
        src = os.path.join(raw, f'team_{f16}_kit_{n}_minikit.dds')
        if os.path.exists(src):
            legacy(f'data/ui/imgAssets/kits/j{n}_{f17}_0.dds', src)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('team', choices=sorted(liga1orange_teams))
    parser.add_argument('--skip-db', action='store_true', help='keep current TSVs')
    parser.add_argument('--skip-assets', action='store_true', help='reuse assets/teams/<team>/{f16_raw,final}')
    parser.add_argument('--skip-frosty', action='store_true', help='stop before touching the Frosty project')
    args = parser.parse_args()
    team = liga1orange_teams[args.team]
    print(f'Importing {team.name}: FIFA 16 id {team.teamid_fifa16} -> FIFA 17 id {team.teamid_fifa17}')

    if not args.skip_db:
        import_db(team)
    if args.skip_assets:
        raw = os.path.join(ROOT, 'assets', 'teams', args.team, 'f16_raw')
        final = os.path.join(ROOT, 'assets', 'teams', args.team, 'final')
    else:
        raw, final = build_assets(args.team, team)

    problems = validate.validate(team, final)
    if problems:
        print('VALIDATION FAILED, nothing injected:')
        print('\n'.join(' - ' + p for p in problems))
        sys.exit(1)
    print('Validation OK')

    dbs = rebuild_dbs()
    if args.skip_frosty:
        return
    inject(team, raw, final, dbs)
    print(f'Done. Test project: {TEST_PROJECT}')


if __name__ == '__main__':
    main()
