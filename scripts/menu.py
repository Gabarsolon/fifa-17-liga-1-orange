import sys
import subprocess
import os
from constants import *
from db_operations import *
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))


selected_team = liga1orange_teams['dinamo']
selected_fifa17_player = None
selected_fifa16_player = None

def handle_menu_input(menu_options, menu):
    choice = input()
    if choice in menu_options:
        option = menu_options[choice]
        if option["function"]:
            option["function"]()
            print("Operation executed successfully")
        else:
            print("TODO: implement function")
        if choice != 0:
            menu()
    else:
        print("Invalid choice. Please try again.")
        menu()

def print_menu():
    print("\n")
    print("FIFA 17 LIGA 1 ORANGE DB EDITOR")
    print("----------------------------")
    for key, option in menu_options.items():
        print(f"{key}. {option['name']}")
    print("----------------------------")
    print("Enter your choice: ")

    handle_menu_input(menu_options, print_menu)
    
def print_team_menu():
    print("\n")
    print("Team menu")
    print("Selected team: " + selected_team.name)
    print("----------------------------")
    for key, option in team_menu_options.items():
        print(f"{key}. {option['name']}")
    print("----------------------------")
    print("Enter your choice: ")
    
    handle_menu_input(team_menu_options, print_team_menu)

def print_players_menu():
    print("\n")
    print("Players menu")
    print("Selected team: " + selected_team.name)
    print("Selected FIFA 17 player: " + str(selected_fifa17_player))
    print("Selected FIFA 16 player: " + str(selected_fifa16_player))
    print("----------------------------")
    for key, option in player_menu_options.items():
        print(f"{key}. {option['name']}")
    print("----------------------------")
    print("Enter your choice: ")
    
    handle_menu_input(player_menu_options, print_players_menu)
    
def print_select_team_menu():
    print("\n")
    print("Select team")
    print("----------------------------")
    for key, team in liga1orange_teams.items():
        print(f"{key}. {team.name}")
    print("----------------------------")
    print("Enter your choice: ")    
    
    global selected_team
    
    try:
        choice = input()
        if choice in liga1orange_teams.keys():
            selected_team = liga1orange_teams[choice]
            print_team_menu()
        else:
            print("Invalid choice. Please try again.")
            print_select_team_menu()
    except:
        print("Invalid choice. Please try again.")
        print_select_team_menu()
    

menu_options = {
    "1": {"name": "Team menu", "function": print_team_menu},
    "2": {"name": "Players menu", "function": print_players_menu},
    "3": {"name": "Save changes to TSV's", "function": save_tsv},
    "0": {"name": "Exit", "function": sys.exit},
}

team_menu_options = {
    "1": {"name": "Select team", "function": print_select_team_menu},
    "2": {"name": "Fix kits colors", "function": lambda: fix_kits_colors(selected_team)},
    "3": {"name": "Replace formation and team data from FIFA 17 with one from FIFA 16", "function": lambda: replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(selected_team.teamid_fifa17, selected_team.teamid_fifa16)}, 
    "4": {"name": "Replace team details from FIFA 17 with one from FIFA 16", "function": lambda: replace_team_details_from_fifa17_with_ones_from_fif16(selected_team.teamid_fifa17, selected_team.teamid_fifa16, selected_team.foundation_year, selected_team.cityname)},
    "5": {"name": "Change kit's foreground color", "function": lambda: handle_kits_foreground_color_change()},
    "6": {"name": "Change kit's font type", "function": lambda: handle_kits_font_type_change()},
    "7": {"name": "Extract team kits using CmCli (FIFA 16)", "function": lambda: extract_assets_with_cmcli("export-kit", selected_team.teamid_fifa16)},
    "8": {"name": "Extract team crests using CmCli (FIFA 16)", "function": lambda: extract_assets_with_cmcli("export-crests", selected_team.teamid_fifa16)},
    "9": {"name": "1-Click Full Team Import (Replace FIFA 17 team with FIFA 16 team)", "function": handle_full_team_import},
    "0": {"name": "Go back", "function": print_menu},
}

player_menu_options = {
    "1": {"name": "Print player names", "function": lambda: print_player_names(selected_team.teamid_fifa16, selected_team.teamid_fifa17)},
    "2": {"name": "Select player from FIFA 17 given name and selected team", "function": lambda: assign_selected_player_from_fifa17()},
    "3": {"name": "Select player from FIFA 16 given name and selected team", "function": lambda: assign_selected_player_from_fifa16()},
    "4": {"name": "Insert name into playernames table", "function": None},  # TODO: implement function
    "5": {"name": "Replace player from FIFA 17 with one from FIFA 16", "function": lambda: replace_player_from_fifa17_with_one_from_fifa16(selected_fifa17_player.playerid, selected_fifa16_player.playerid, selected_team.teamid_fifa17, selected_team.teamid_fifa16)},
    "6": {"name" : "Replace all players with the ones from FIFA 16", "function": lambda: replace_players_from_fifa16_with_players_from_fifa17(selected_team.teamid_fifa17, selected_team.teamid_fifa16)},
    "7": {"name": "Extract player assets using CmCli (FIFA 16)", "function": lambda: extract_assets_with_cmcli("export-player", selected_fifa16_player.playerid if selected_fifa16_player else None)},
    "0": {"name": "Go back", "function": print_menu},
}

def assign_selected_player_from_fifa17():
    global selected_fifa17_player
    selected_fifa17_player = get_player_from_fifa17_given_name_and_team(
        input("Enter the player name: "), selected_team.teamid_fifa17
    )
    
    
def assign_selected_player_from_fifa16():
    global selected_fifa16_player
    selected_fifa16_player = get_player_from_fifa16_given_name_and_team(
        input("Enter the player name: "), selected_team.teamid_fifa16
    )

def handle_kits_foreground_color_change():
    global selected_team
    change_kit_foreground_color(selected_team, input("Enter the kit type (home, away, gk, tertiary): "), [int(input("Enter the red channel value(0-255): ")), int(input("Enter the green channel value(0-255): ")), int(input("Enter the blue channel value(0-255): "))])
    
def handle_kits_font_type_change():
    global selected_team
    change_kit_font_type(selected_team, input("Enter the kit type (home, away, gk, tertiary): "), int(input("Enter font code: ")))

def handle_full_team_import():
    global selected_team
    print(f"\nStarting full 1-click import for {selected_team.name}...")
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
    
    ans = input("\nDo you also want to extract graphical assets (kits, crests) using CmCli? (y/n): ")
    if ans.lower() == 'y':
        out_dir = input("Enter output directory path (e.g. C:\\Users\\remus\\Desktop\\Extracted): ")
        if out_dir:
            extract_assets_with_cmcli("export-kit", selected_team.teamid_fifa16, out_dir, convert_to_dds=True)
            extract_assets_with_cmcli("export-crests", selected_team.teamid_fifa16, out_dir, convert_to_dds=True)
            
            # Optionally extract players faces too
            ans_players = input("Extract textures for ALL imported players? (y/n): ")
            if ans_players.lower() == 'y':
                print("Note: Batch player extraction is not yet a single CmCli command, but you can use the player menu to extract them individually.")
    
    print("\nFull import finished! Don't forget to save changes to TSV's from the main menu.")

def extract_assets_with_cmcli(command, entity_id, out_dir=None, convert_to_dds=False):
    if not entity_id:
        print("ERROR: No entity ID provided. Make sure you have selected a valid FIFA 16 team or player first.")
        return

    cmcli_path = os.environ.get("CMCLI_PATH")
    if not cmcli_path or not os.path.exists(cmcli_path):
        print(f"ERROR: CmCli.exe not found at {cmcli_path}")
        return
        
    fifa16_dir = os.environ.get("FIFA16_DIR")
    if fifa16_dir and os.path.exists(fifa16_dir):
        db_path = os.environ.get("FIFA16_DB_PATH")
        xml_path = os.environ.get("FIFA16_XML_PATH")
        fifa_dir = fifa16_dir
        year = "16"
    else:
        print("ERROR: FIFA 16 directory found as specified in .env is invalid or missing.")
        return
        
    if out_dir is None:
        out_dir = input("Enter output directory path (e.g. C:\\Users\\remus\\Desktop\\Extracted): ")
    if not out_dir:
        print("Export cancelled.")
        return
        
    print(f"Running CmCli.exe {command} for ID {entity_id}...")
    try:
        subprocess.run([
            cmcli_path, 
            command, 
            db_path, 
            xml_path, 
            fifa_dir, 
            year,
            str(entity_id), 
            out_dir
        ], check=True)
        
        if convert_to_dds:
            ps_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ConvertPNGsToDDS.ps1")
            if os.path.exists(ps_script):
                print(f"Converting extracted PNGs to DDS using {ps_script}...")
                subprocess.run([
                    "powershell.exe", 
                    "-ExecutionPolicy", "Bypass", 
                    "-File", ps_script,
                    "-TargetDirectory", out_dir
                ])
            else:
                print(f"WARNING: Conversion script not found at {ps_script}")
                
    except subprocess.CalledProcessError as e:
        print(f"ERROR: CmCli execution failed with exit code {e.returncode}")
    except Exception as e:
        print(f"ERROR: Failed to run CmCli: {e}")

print_menu()
