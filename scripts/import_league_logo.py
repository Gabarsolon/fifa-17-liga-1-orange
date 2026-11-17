"""Replace the 3D league logo (intro and replays) with the Liga 1 Orange logo in Liga1Orange.test.fbproject.

    python scripts/import_league_logo.py [--logo assets/league/Liga_I_logo_hires.png] [--league denmark_1 --league-id 1]

Steps: export the original mesh as ASCII FBX (template) -> scripts/league_logo_mesh.py builds the new mesh + colour
palette texture -> FrostyMeshCli imports the mesh -> the palette is injected as leaguelogo_<id>_color.
Needs FROSTYMESHCLI_PATH in .env (local tool, see AGENTS.md) and the extra packages of requirements-league-logo.txt.
Works on the cumulative test project, so run it after (or before) any import_team.py runs.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from dotenv import load_dotenv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(ROOT, '.env'))
TEST_PROJECT = os.path.join(ROOT, 'Liga1Orange.test.fbproject')


def run(cmd, **kwargs):
    print('>', ' '.join(f'"{c}"' if ' ' in c else c for c in cmd))
    subprocess.run(cmd, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logo', default=os.path.join(ROOT, 'assets', 'league', 'Liga_I_logo_hires.png'))
    parser.add_argument('--league', default='denmark_1', help='folder name under content/character/leaguelogo')
    parser.add_argument('--league-id', type=int, default=1, help='FIFA 17 league id of the replaced league (Denmark = 1)')
    parser.add_argument('--scale', type=int, default=2)
    parser.add_argument('--sigma', type=float, default=5.0)
    args = parser.parse_args()

    mesh_cli = os.environ.get('FROSTYMESHCLI_PATH')
    if not mesh_cli or not os.path.exists(mesh_cli):
        sys.exit('FROSTYMESHCLI_PATH is not set or does not exist (see .env.example)')
    if not os.path.exists(TEST_PROJECT):
        sys.exit(f'{TEST_PROJECT} not found: run scripts/import_team.py first')
    cwd = os.path.dirname(mesh_cli)  # FrostyMeshCli loads Profiles/Plugins/ThirdParty from its own folder
    ebx = f'content/character/leaguelogo/{args.league}/leaguelogo_{args.league_id}_mesh'

    with tempfile.TemporaryDirectory() as tmp:
        template = os.path.join(tmp, 'template.fbx')
        mesh_fbx = os.path.join(tmp, 'logo.fbx')
        palette = os.path.join(tmp, f'leaguelogo_{args.league_id}_color.png')
        print('1. Original mesh as ASCII FBX template')
        run([mesh_cli, 'FIFA17', 'export-mesh', ebx, template, '-', '2013', 'Centimeters', 'ascii'], cwd=cwd)
        print('2. Building the logo mesh and palette')
        run([sys.executable, os.path.join(ROOT, 'scripts', 'league_logo_mesh.py'), template, args.logo, mesh_fbx, palette,
             '--scale', str(args.scale), '--sigma', str(args.sigma), '--auto-palette', '8'])
        print('3. Importing the mesh into the test project')
        run([mesh_cli, 'FIFA17', 'import-mesh', TEST_PROJECT, ebx, mesh_fbx], cwd=cwd)
        print('4. Palette texture -> DDS -> project')
        run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(ROOT, 'scripts', 'ConvertPNGsToDDS.ps1'),
             '-TargetDirectory', tmp])
        tex_dir = os.path.join(tmp, 'tex')
        os.makedirs(tex_dir)
        shutil.copy(os.path.join(tmp, f'leaguelogo_{args.league_id}_color.dds'), tex_dir)
        frosty = os.environ['FROSTYCLI_PATH']
        # import-team replaces oldId by newId in the file name: same id keeps `leaguelogo_<id>_color`
        run([frosty, 'FIFA17', 'import-team', str(args.league_id), str(args.league_id), tex_dir, TEST_PROJECT],
            cwd=os.path.dirname(frosty))
    print('Done. League logo imported into', TEST_PROJECT)


if __name__ == '__main__':
    main()
