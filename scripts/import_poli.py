import os
import shutil
import glob
import subprocess
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from constants import liga1orange_teams
from db_operations import (
    replace_team_details_from_fifa17_with_ones_from_fif16,
    replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16,
    replace_players_from_fifa16_with_players_from_fifa17,
    save_tsv
)
from menu import extract_assets_with_cmcli

def main():
    selected_team = liga1orange_teams['poli']
    
    print(f"Starting full import for {selected_team.name}...")
    
    print("1. Replacing team details...")
    replace_team_details_from_fifa17_with_ones_from_fif16(
        selected_team.teamid_fifa17, 
        selected_team.teamid_fifa16, 
        selected_team.foundation_year, 
        selected_team.cityname
    )
    
    print("2. Replacing formation and team data...")
    replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(
        selected_team.teamid_fifa17, 
        selected_team.teamid_fifa16
    )
    
    print("3. Replacing players...")
    replace_players_from_fifa16_with_players_from_fifa17(
        selected_team.teamid_fifa17, 
        selected_team.teamid_fifa16
    )
    
    print("4. Saving TSV files...")
    save_tsv()
    
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'teams', 'poli')
    os.makedirs(out_dir, exist_ok=True)
    
    print("5. Extracting kits...")
    extract_assets_with_cmcli("export-kit", selected_team.teamid_fifa16, out_dir, convert_to_dds=True)
    
    print("Renaming extracted kits for FIFA 17 format...")
    import glob
    for dds_file in glob.glob(os.path.join(out_dir, "*.dds")):
        basename = os.path.basename(dds_file)
        if "_kit_" in basename:
            # e.g., team_130022_kit_0_tex_1.dds
            parts = basename.split("_")
            if len(parts) >= 6:
                team_id = parts[1]
                kit_type = parts[3]
                tex_idx = parts[5].split(".")[0]
                
                new_name = None
                if tex_idx == "1":
                    new_name = f"jersey_{team_id}_{kit_type}_0_color.dds"
                elif tex_idx == "2":
                    new_name = f"shorts_{team_id}_{kit_type}_0_color.dds"
                elif tex_idx == "3":
                    new_name = f"socks_{team_id}_{kit_type}_0_color.dds"
                
                if new_name:
                    shutil.copy(dds_file, os.path.join(out_dir, new_name))
                    try:
                        os.remove(dds_file)
                    except Exception:
                        pass
            elif "minikit" in basename:
                # e.g. team_130022_kit_0_minikit.dds
                team_id = parts[1]
                kit_type = parts[3]
                new_name = f"team_{team_id}_kit_{kit_type}_minikit.dds" # Or however FIFA 17 names it. Wait, Frosty doesn't have minikits in textures.txt maybe? Let's leave it.
                # Actually minikits are not standard in the 3D kits folder. Let's just pass.
                
    print("6. Extracting crests...")
    extract_assets_with_cmcli("export-crests", selected_team.teamid_fifa16, out_dir, convert_to_dds=True)
    
    print("Renaming extracted crests for FIFA 17 format...")
    for dds_file in glob.glob(os.path.join(out_dir, "*.dds")):
        basename = os.path.basename(dds_file)
        if "crest_light_256x256" in basename:
            # e.g., team_130022_crest_light_256x256.dds
            parts = basename.split("_")
            team_id = parts[1]
            
            # Copy to 3D kit crests
            shutil.copy(dds_file, os.path.join(out_dir, f"crest_{team_id}_0_0_color.dds"))
            shutil.copy(dds_file, os.path.join(out_dir, f"crest_{team_id}_1_0_color.dds"))
            shutil.copy(dds_file, os.path.join(out_dir, f"crest_{team_id}_2_0_color.dds"))
            shutil.copy(dds_file, os.path.join(out_dir, f"crest_{team_id}_3_0_color.dds"))
            
    print("7. Rebuilding database files with DbCli...")
    dbcli_path = os.environ.get("DBCLI_PATH")
    frostycli_path = os.environ.get("FROSTYCLI_PATH")
    fbproject_path = os.path.join(os.path.dirname(__file__), '..', 'Liga1Orange.fbproject')
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'db')
    project_root = os.path.join(os.path.dirname(__file__), '..')

    print("0. Restoring clean Liga1Orange.fbproject baseline from Git...")
    subprocess.run(["git", "checkout", fbproject_path], check=True)

    base_fifa_db = os.path.join(project_root, "fifa_ng_db.og.DB")
    base_fifa_xml = os.path.join(project_root, "clean_from_game_fifa_ng_db-meta.xml")
    base_eng_db = os.path.join(project_root, "clean_from_game_eng_us.DB")
    base_eng_xml = os.path.join(project_root, "clean_from_game_eng_us-meta.xml")

    out_fifa_db = os.path.join(db_dir, "fifa_ng_db.DB")
    out_fifa_xml = os.path.join(db_dir, "fifa_ng_db-meta.XML")
    out_eng_db = os.path.join(db_dir, "eng_us.DB")
    out_eng_xml = os.path.join(db_dir, "eng_us-meta.XML")

    print("Rebuilding fifa_ng_db.DB in single-pass import-all...")
    scratch_tsv_dir = os.path.join(project_root, "scratch", "tsv_tables")
    os.makedirs(scratch_tsv_dir, exist_ok=True)

    fifa_tables = [
        "defaultteamdata.txt", "default_teamsheets.txt", "formations.txt",
        "teams.txt", "teamkits.txt", "players.txt", "playernames.txt", "teamplayerlinks.txt"
    ]
    for tbl in fifa_tables:
        src = os.path.join(db_dir, tbl)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(scratch_tsv_dir, tbl))

    subprocess.run([
        dbcli_path, "import-all",
        base_fifa_db,
        base_fifa_xml,
        scratch_tsv_dir,
        out_fifa_db
    ], check=True)

    print("Rebuilding eng_us.DB from LanguageStrings.txt...")
    subprocess.run([
        dbcli_path, "import-table",
        base_eng_db,
        base_eng_xml,
        "LanguageStrings",
        os.path.join(db_dir, "LanguageStrings.txt"),
        out_eng_db
    ], check=True)

    print("8. Injecting DBs and Meta XMLs into Frostbite project...")
    subprocess.run([
        frostycli_path, "FIFA17", "import-legacy",
        fbproject_path,
        "data/db/fifa_ng_db.db",
        out_fifa_db
    ], check=True)

    subprocess.run([
        frostycli_path, "FIFA17", "import-legacy",
        fbproject_path,
        "data/db/fifa_ng_db-meta.xml",
        out_fifa_xml
    ], check=True)

    print("Injecting eng_us Language DB into Frostbite project...")
    subprocess.run([
        frostycli_path, "FIFA17", "import-legacy",
        fbproject_path,
        "data/loc/eng_us.db",
        out_eng_db
    ], check=True)
    subprocess.run([
        frostycli_path, "FIFA17", "import-legacy",
        fbproject_path,
        "data/loc/eng_us-meta.xml",
        out_eng_xml
    ], check=True)

    print("9. Injecting 3D kits into Frostbite...")
    cmd = [
        frostycli_path,
        "FIFA17",
        "import-team",
        str(selected_team.teamid_fifa16),
        str(selected_team.teamid_fifa17),
        out_dir,
        fbproject_path
    ]
    subprocess.run(cmd, check=True)

    print("10. Injecting UI crests and minikits into Frostbite via import-legacy...")
    fifa17_id = selected_team.teamid_fifa17
    fifa16_id = selected_team.teamid_fifa16
    ui_legacy_mappings = [
        (f"data/ui/imgAssets/crest/light/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_standard.dds")),
        (f"data/ui/imgAssets/crest/dark/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_dark_standard.dds")),
        (f"data/ui/imgAssets/crest16x16/light/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_16x16.dds")),
        (f"data/ui/imgAssets/crest16x16/dark/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_dark_16x16.dds")),
        (f"data/ui/imgAssets/crest32x32/light/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_32x32.dds")),
        (f"data/ui/imgAssets/crest32x32/dark/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_dark_32x32.dds")),
        (f"data/ui/imgAssets/crest50x50/light/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_50x50.dds")),
        (f"data/ui/imgAssets/crest50x50/dark/l{fifa17_id}.dds", os.path.join(out_dir, f"team_{fifa16_id}_crest_dark_50x50.dds")),
        (f"data/ui/imgAssets/kits/j0_{fifa17_id}_0.dds", os.path.join(out_dir, f"team_{fifa16_id}_kit_0_minikit.dds")),
        (f"data/ui/imgAssets/kits/j1_{fifa17_id}_0.dds", os.path.join(out_dir, f"team_{fifa16_id}_kit_1_minikit.dds")),
        (f"data/ui/imgAssets/kits/j2_{fifa17_id}_0.dds", os.path.join(out_dir, f"team_{fifa16_id}_kit_2_minikit.dds")),
    ]

    for target_legacy, src_file in ui_legacy_mappings:
        if os.path.exists(src_file):
            print(f"Injecting {os.path.basename(src_file)} into {target_legacy}...")
            subprocess.run([
                frostycli_path, "FIFA17", "import-legacy",
                fbproject_path,
                target_legacy,
                src_file
            ], check=True)

    print("Done! All database, kit textures, UI crests, and minikits successfully imported.")

if __name__ == '__main__':
    main()
