import os
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
                    os.replace(dds_file, os.path.join(out_dir, new_name))
            elif "minikit" in basename:
                # e.g. team_130022_kit_0_minikit.dds
                team_id = parts[1]
                kit_type = parts[3]
                new_name = f"team_{team_id}_kit_{kit_type}_minikit.dds" # Or however FIFA 17 names it. Wait, Frosty doesn't have minikits in textures.txt maybe? Let's leave it.
                # Actually minikits are not standard in the 3D kits folder. Let's just pass.
                
    print("6. Extracting crests...")
    extract_assets_with_cmcli("export-crests", selected_team.teamid_fifa16, out_dir, convert_to_dds=True)
    
    print("Renaming extracted crests for FIFA 17 format...")
    import shutil
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
            
    print("7. Injecting into Frostbite...")
    import subprocess
    frostycli_path = os.environ.get("FROSTYCLI_PATH")
    fbproject_path = os.path.join(os.path.dirname(__file__), '..', 'Liga1Orange.fbproject')
    cmd = [
        frostycli_path,
        "FIFA17",
        "import-team",
        str(selected_team.teamid_fifa16),
        str(selected_team.teamid_fifa17),
        out_dir,
        fbproject_path
    ]
    subprocess.run(cmd, check=True, cwd=os.path.dirname(frostycli_path))
    
    print("Done!")

if __name__ == '__main__':
    main()
