import sys
from constants import *
from db_operations import *

selected_team = liga1orange_teams['cfr']
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
    "2": {"name": "Change jersey number color", "function": lambda: handle_change_jersey_number_color()},
    "3": {"name": "Change jersey name color", "function": lambda: handle_change_jersey_name_color()},
    "4": {"name": "Replace formation and team data from FIFA 17 with one from FIFA 16", "function": lambda: replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(selected_team.teamid_fifa17, selected_team.teamid_fifa16)}, 
    "5": {"name": "Replace team details from FIFA 17 with one from FIFA 16", "function": lambda: replace_team_details_from_fifa17_with_ones_from_fif16(selected_team.teamid_fifa17, selected_team.teamid_fifa16, selected_team.foundation_year, selected_team.cityname)},
    "0": {"name": "Go back", "function": print_menu},
}

player_menu_options = {
    "1": {"name": "Print player names", "function": lambda: print_player_names(selected_team.teamid_fifa16, selected_team.teamid_fifa17)},
    "2": {"name": "Select player from FIFA 17 given name and selected team", "function": lambda: assign_selected_player_from_fifa17()},
    "3": {"name": "Select player from FIFA 16 given name and selected team", "function": lambda: assign_selected_player_from_fifa16()},
    "4": {"name": "Insert name into playernames table", "function": None},  # TODO: implement function
    "5": {"name": "Replace player from FIFA 17 with one from FIFA 16", "function": lambda: replace_player_from_fifa17_with_one_from_fifa16(selected_fifa17_player.playerid, selected_fifa16_player.playerid, selected_team.teamid_fifa17, selected_team.teamid_fifa16)},
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

def handle_change_jersey_name_color():
    global selected_team
    change_jersey_name_color(selected_team, input("Enter the kit type (home, away, gk, tertiary): "))
    
def handle_change_jersey_number_color():
    global selected_team
    change_jersey_number_color(selected_team, input("Enter the kit type (home, away, gk, tertiary): ") )

print_menu()
