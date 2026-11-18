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
    'fcsb' : Team(269, 106000, "FCSB", foundation_year=1947, cityname="București"),
    'astra': Team(270, 130026, "Astra", foundation_year=1921, cityname="Giurgiu"),
    'cfr': Team(271, 130023, "CFR", foundation_year=1907, cityname="Cluj-Napoca"),
    'viitorul': Team(272, 130024, "Viitorul", foundation_year=2009, cityname="Constanța"),
    'craiova': Team(819, 130021, "Craiova", foundation_year=2013, cityname="Craiova"),
    'dinamo': Team(820, 130027, "Dinamo", foundation_year=1948, cityname="București"),
    'poli': Team(1443, 130022, "Poli", foundation_year=2012, cityname="Timișoara",
                 player_swaps=[(50311, 50253)]),  # Emanuel Vasi (retired) -> Sebastian Mailat (FC Botosani, 1M EUR)
    # Remaining Liga 1 teams. FIFA 17 ids are the remaining Danish league slots (proposed order, 1445 Esbjerg, 1446 Horsens,
    # 1447 SonderjyskE, 1516 Midtjylland, 1786 Randers, 1788 Nordsjaelland, 15001 Lyngby).
    # foundation_year is not in the FIFA 16 tables: filled in 2026-11-18 from Wikipedia via agyp (year of the club entity that played 2016/17; same convention as craiova 2013, poli 2012).
    'botosani': Team(1445, 130020, "FC Botoșani", foundation_year=2001, cityname="Botoșani",
                  # Lorand Fulop (OVR 58, 100+ Liga 1 matches, played in Hungary, peak 700k) replaces Raul Avram (OVR 60, peak 300k)
                  player_swaps=[(50021, 50305)]),
    'pandurii': Team(1446, 130025, "Pandurii", foundation_year=1962, cityname="Târgu Jiu"),
    'poli_iasi': Team(1447, 130028, "Poli Iași", foundation_year=2010, cityname="Iași"),
    'voluntari': Team(1516, 130030, "FC Voluntari", foundation_year=2010, cityname="Voluntari"),
    'chiajna': Team(1786, 130031, "Concordia Chiajna", foundation_year=1957, cityname="Chiajna"),
    'gazmetan': Team(1788, 130039, "Gaz Metan", foundation_year=1945, cityname="Mediaș",
                  # Alexandru Greab (OVR 53, peak 800k, later Gloria Bistrita) replaces Raul Ignat (OVR 57, peak 75k, no club)
                  player_swaps=[(50580, 50578)]),
    'asa': Team(15001, 130067, "ASA Târgu Mureș", foundation_year=2008, cityname="Târgu Mureș"),
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

# Career facts at the START of 2016/17 (end of 2015-16), from Wikipedia via agyp (2026-11-18): Liga I titles, Cupa Romaniei wins as the
# club counts them, capacity of the stadium used in 2016/17. Used by db_operations.port_career_team_columns.
TEAM_FACTS = {
    'fcsb': {'league_titles': 26, 'cup_wins': 22, 'capacity': 55634},
    'astra': {'league_titles': 1, 'cup_wins': 1, 'capacity': 8500},
    'cfr': {'league_titles': 3, 'cup_wins': 4, 'capacity': 23500},
    'viitorul': {'league_titles': 0, 'cup_wins': 0, 'capacity': 4554},
    'craiova': {'league_titles': 4, 'cup_wins': 5, 'capacity': 7000},
    'dinamo': {'league_titles': 18, 'cup_wins': 13, 'capacity': 15032},
    'poli': {'league_titles': 0, 'cup_wins': 2, 'capacity': 32972},  # cups 1958 (Stiinta Timisoara) and 1980 (Politehnica), confirmed by the user's web check
    'botosani': {'league_titles': 0, 'cup_wins': 0, 'capacity': 7782},
    'pandurii': {'league_titles': 0, 'cup_wins': 0, 'capacity': 20054},  # Severin stadium (2015-2017 home, FRLT: Stadionul Municipal Severin); 20054 = nominal after the 2009 renovation; 18878 is today's LPF homologation, not used (rule 11)
    'poli_iasi': {'league_titles': 0, 'cup_wins': 0, 'capacity': 11390},
    'voluntari': {'league_titles': 0, 'cup_wins': 0, 'capacity': 4600},
    'chiajna': {'league_titles': 0, 'cup_wins': 0, 'capacity': 5123},
    'gazmetan': {'league_titles': 0, 'cup_wins': 0, 'capacity': 7814},
    'asa': {'league_titles': 0, 'cup_wins': 0, 'capacity': 8200},
}
