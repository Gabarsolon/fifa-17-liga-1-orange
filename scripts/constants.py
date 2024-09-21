class Team:
    def __init__(self, teamid_fifa17, teamid_fifa16, name):
        self.teamid_fifa17 = teamid_fifa17
        self.teamid_fifa16 = teamid_fifa16
        self.name = name
    

teams = {
    'fcsb' : Team(269, 106000, "FCSB")
}


fcsb_teamid = 269
fifa16_fcsb_teamid = 106000
home_kitid = 0
away_kitid = 1
nitza = 240007
nitza_sub = 198455