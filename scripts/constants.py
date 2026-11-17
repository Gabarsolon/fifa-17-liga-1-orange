class Team:
    def __init__(self, teamid_fifa17, teamid_fifa16, name="", foundation_year="", cityname="", player_swaps=None):
        self.teamid_fifa17 = teamid_fifa17
        self.teamid_fifa16 = teamid_fifa16
        self.name = name
        #Foundation year is not part of FIFA 16 table, but part of FIFA 17. Must be modified manually
        self.foundation_year = foundation_year
        self.cityname = cityname
        # [(fifa16_playerid_out, fifa16_playerid_in)]: after the OVR import, the slot of "out" is given to "in".
        # Used when a player who became relevant later (Transfermarkt) would otherwise be cut by the OVR ranking.
        self.player_swaps = player_swaps or []

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
    'poli': Team(1443, 130022, "Poli", foundation_year=2012, cityname="Timișoara",
                 player_swaps=[(50311, 50253)]),  # Emanuel Vasi (retired) -> Sebastian Mailat (FC Botosani, 1M EUR)
    # Remaining Liga 1 teams. FIFA 17 ids are the remaining Danish league slots (proposed order, 1445 Esbjerg, 1446 Horsens,
    # 1447 SonderjyskE, 1516 Midtjylland, 1786 Randers, 1788 Nordsjaelland, 15001 Lyngby).
    # foundation_year is None on purpose: it is not in the FIFA 16 tables, fill it in before importing (import_team.py refuses None).
    'botosani': Team(1445, 130020, "FC Botoșani", foundation_year=None, cityname="Botoșani"),
    'pandurii': Team(1446, 130025, "Pandurii", foundation_year=None, cityname="Târgu Jiu"),
    'poli_iasi': Team(1447, 130028, "Poli Iași", foundation_year=None, cityname="Iași"),
    'voluntari': Team(1516, 130030, "FC Voluntari", foundation_year=None, cityname="Voluntari"),
    'chiajna': Team(1786, 130031, "Concordia Chiajna", foundation_year=None, cityname="Chiajna"),
    'gazmetan': Team(1788, 130039, "Gaz Metan", foundation_year=None, cityname="Mediaș"),
    'asa': Team(15001, 130067, "ASA Târgu Mureș", foundation_year=None, cityname="Târgu Mureș"),
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