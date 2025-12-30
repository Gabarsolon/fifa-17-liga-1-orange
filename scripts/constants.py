class Team:
    def __init__(self, teamid_fifa17, teamid_fifa16, name="", foundation_year="", cityname=""):
        self.teamid_fifa17 = teamid_fifa17
        self.teamid_fifa16 = teamid_fifa16
        self.name = name
        #Foundation year is not part of FIFA 16 table, but part of FIFA 17. Must be modified manually
        self.foundation_year = foundation_year
        self.cityname = cityname

class Player:
    def __init__(self, playerid, firstname, lastname):
        self.playerid = playerid
        self.firstname = firstname
        self.lastname = lastname
    
    def __str__(self):
        return f"{self.playerid} {self.firstname} {self.lastname}"

liga1orange_teams = {
    'fcsb' : Team(269, 106000, "FCSB", foundation_year=1947),
    'astra': Team(270, 130026, "Astra", foundation_year=1921),
    'cfr': Team(271, 130023, "CFR", foundation_year=1907, cityname="Cluj-Napoca"),
    'viitorul': Team(272, 130024, "Viitorul", foundation_year=2009, cityname="Constanța"),
    'craiova': Team(819, 130021, "Craiova", foundation_year=2013, cityname="Craiova"),
    'dinamo': Team(820, 130027, "Dinamo", foundation_year=1948, cityname="București"),
}

from enum import Enum

class KitType(Enum):
    HOME = (0, "home")
    AWAY = (1, "away")
    GK = (2, "gk")
    TERTIARY = (3, "tertiary")

    @property
    def id(self):
        return self.value[0]

    @property
    def name(self):
        return self.value[1]

    @classmethod
    def from_id(cls, id):
        for kit_type in cls:
            if kit_type.id == id:
                return kit_type
            
    @classmethod
    def from_name(cls, name):
        for kit_type in cls:
            if kit_type.name == name:
                return kit_type


fcsb_teamid = 269
fifa16_fcsb_teamid = 106000
home_kitid = 0
away_kitid = 1
nitza = 240007
nitza_sub = 198455