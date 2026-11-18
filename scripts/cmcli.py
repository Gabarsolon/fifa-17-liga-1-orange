"""Wrapper around CmCli.exe (CreationMaster16Cli) for exporting kits, crests and player data from FIFA 16."""
import os
import subprocess


def extract_assets_with_cmcli(command, entity_id, out_dir, convert_to_dds=False):
    """Run `CmCli.exe <command> <fifa16 db> <meta xml> <fifa16 dir> <id> <out_dir>` (export-kit, export-crests,
    export-player, ...). Raises RuntimeError on any problem so the import never continues with missing assets."""
    if not entity_id:
        raise RuntimeError('no FIFA 16 entity id given')
    cmcli_path = os.environ.get('CMCLI_PATH')
    if not cmcli_path or not os.path.exists(cmcli_path):
        raise RuntimeError(f'CmCli.exe not found at {cmcli_path} (CMCLI_PATH in .env)')
    fifa16_dir = os.environ.get('FIFA16_DIR')
    if not fifa16_dir or not os.path.exists(fifa16_dir):
        raise RuntimeError('FIFA16_DIR in .env is invalid or missing')
    os.makedirs(out_dir, exist_ok=True)
    print(f'Running CmCli.exe {command} for ID {entity_id}...')
    subprocess.run([cmcli_path, command, os.environ.get('FIFA16_DB_PATH'), os.environ.get('FIFA16_XML_PATH'),
                    fifa16_dir, str(entity_id), out_dir], check=True)
    if convert_to_dds:
        ps_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ConvertPNGsToDDS.ps1')
        subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_script, '-TargetDirectory', out_dir],
                       check=True)
