class Team:
    def __init__(self, teamid_fifa17, teamid_fifa16, name, foundation_year):
        self.teamid_fifa17 = teamid_fifa17
        self.teamid_fifa16 = teamid_fifa16
        self.name = name
        #Foundation year is not part of FIFA 16 table, but part of FIFA 17. Must be modified manually
        self.foundation_year = foundation_year

class Player:
    def __init__(self, playerid, firstname, lastname):
        self.playerid = playerid
        self.firstname = firstname
        self.lastname = lastname
    
    def __str__(self):
        return f"{self.playerid} {self.firstname} {self.lastname}"

liga1orange_teams = {
    'fcsb' : Team(269, 106000, "FCSB", foundation_year=1947),
    'astra': Team(270, 130026, "Astra", foundation_year=1921)
}


fcsb_teamid = 269
fifa16_fcsb_teamid = 106000
home_kitid = 0
away_kitid = 1
nitza = 240007
nitza_sub = 198455