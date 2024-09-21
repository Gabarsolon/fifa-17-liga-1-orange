import sys
def print_menu():
    print("\n")
    print("FIFA 17 LIGA 1 ORANGE DB EDITOR")
    print("----------------------------")
    print("1. Team menu")
    print("2. Players menu")
    print("3. Save changes to TSV's")
    print("0. Exit")
    print("----------------------------")
    print("Enter your choice: ")
    
def print_team_menu():
    print("\n")
    print("Team menu")
    print("Currently selected team: " + str(fcsb_teamid))
    print("----------------------------")
    print("1. Select team")
    print("2. Change jersey number color")
    print("----------------------------")
    print("Enter your choice: ")

print_menu()