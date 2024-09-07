from pathlib import Path
import pandas as pd
import os

#Constants
fcsb_teamid = 269
fifa16_fcsb_teamid = 106000
home_kitid = 0
away_kitid = 1
nitza = 240007
nitza_sub = 198455

#FIFA 17 tables
defaultteamdata = os.path.join(os.path.dirname(__file__), "defaultteamdata.txt")
default_teamsheets = os.path.join(os.path.dirname(__file__), "default_teamsheets.txt")
formations = os.path.join(os.path.dirname(__file__), "formations.txt")
teams = os.path.join(os.path.dirname(__file__), "teams.txt")
teamkits = os.path.join(os.path.dirname(__file__), "teamkits.txt")
players = os.path.join(os.path.dirname(__file__), "players.txt")
playernames = os.path.join(os.path.dirname(__file__), "playernames.txt")
teamplayerlinks = os.path.join(os.path.dirname(__file__), "teamplayerlinks.txt")

#FIFA 16 tables
fifa16_defaultteamdata = os.path.join(os.path.dirname(__file__), "fifa-16/defaultteamdata.txt")
fifa16_defaul_teamsheets = os.path.join(os.path.dirname(__file__), "fifa-16/default_teamsheets.txt")
fifa16_teams = os.path.join(os.path.dirname(__file__), "fifa-16/teams.txt")
fifa16_teamkits = os.path.join(os.path.dirname(__file__), "fifa-16/teamkits.txt")
fifa16_formations = os.path.join(os.path.dirname(__file__), "fifa-16/formations.txt")
fifa16_players = os.path.join(os.path.dirname(__file__), "fifa-16/players.txt")
fifa16_playernames = os.path.join(os.path.dirname(__file__), "fifa-16/playernames.txt")
fifa16_teamplayerlinks = os.path.join(os.path.dirname(__file__), "fifa-16/teamplayerlinks.txt")

defaultteamdata_df = pd.read_csv(defaultteamdata, sep='\t', encoding='utf-16le')
default_teamsheets_df = pd.read_csv(default_teamsheets, sep='\t', encoding='utf-16le')
formations_df = pd.read_csv(formations, sep='\t', encoding='utf-16le')
teams_df = pd.read_csv(teams, sep='\t', encoding='utf-16le')
teamkits_df = pd.read_csv(teamkits, sep='\t', encoding='utf-16le')
players_df = pd.read_csv(players, sep='\t', encoding='utf-16le')
playernames_df = pd.read_csv(playernames, sep='\t', encoding='utf-16le')
teamplayerlinks_df = pd.read_csv(teamplayerlinks, sep='\t', encoding='utf-16le')

fifa16_defaultteamdata_df = pd.read_csv(fifa16_defaultteamdata, sep='\t', encoding='utf-16le')
fifa16_defaul_teamsheets_df = pd.read_csv(fifa16_defaul_teamsheets, sep='\t', encoding='utf-16le')
fifa16_teams_df = pd.read_csv(fifa16_teams, sep='\t', encoding='utf-16le')
fifa16_teamkits_df = pd.read_csv(fifa16_teamkits, sep='\t', encoding='utf-16le')
fifa16_formations_df = pd.read_csv(fifa16_formations, sep='\t', encoding='utf-16le')
fifa16_players_df = pd.read_csv(fifa16_players, sep='\t', encoding='utf-16le')
fifa16_playernames_df = pd.read_csv(fifa16_playernames, sep='\t', encoding='utf-16le')
fifa16_teamplayerlinks_df = pd.read_csv(fifa16_teamplayerlinks, sep='\t', encoding='utf-16le')

# print(teamkits_df.columns)

def change_jersey_number_color(kit_id, color):
    print(teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']])

    teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']] = color

def save_tsv():
    teamkits_df.to_csv(teamkits, sep='\t', encoding='utf-16le', index=False)
    players_df.to_csv(players, sep='\t', encoding='utf-16le', index=False)
    playernames_df.to_csv(playernames, sep='\t', encoding='utf-16le', index=False)
    formations_df.to_csv(formations, sep='\t', encoding='utf-16le', index=False)
    default_teamsheets_df.to_csv(default_teamsheets, sep='\t', encoding='utf-16le', index=False)
    defaultteamdata_df.to_csv(defaultteamdata, sep='\t', encoding='utf-16le', index=False)

def change_jersey_name_color(kit_id, color):
    print([col for col in teamkits_df.columns if 'name' in col.lower()])
    teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']] = color
    print(teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']])

# print([col for col in fifa16_players_df.columns])

def print_player_names():
    fifa16_fcsb_players_df = pd.merge(fifa16_players_df, fifa16_teamplayerlinks_df, on='playerid')
    fifa16_fcsb_players_df = fifa16_fcsb_players_df[fifa16_fcsb_players_df.teamid == fifa16_fcsb_teamid]

    for(row) in fifa16_fcsb_players_df.itertuples():
        print(
            row.playerid,
            fifa16_playernames_df[fifa16_playernames_df.nameid == row.firstnameid].name, 
            fifa16_playernames_df[fifa16_playernames_df.nameid == row.lastnameid].name, 
            fifa16_playernames_df[fifa16_playernames_df.nameid == row.commonnameid].name,
            )

    # print([col for col in players_df.columns])

    fcsb_players_df = pd.merge(players_df, teamplayerlinks_df, on='playerid')
    fcsb_players_df = fcsb_players_df[fcsb_players_df.teamid == fcsb_teamid]

    for(row) in fcsb_players_df.itertuples():
        print(
            row.playerid,
            playernames_df[playernames_df.nameid == row.firstnameid].name, 
            playernames_df[playernames_df.nameid == row.lastnameid].name, 
            playernames_df[playernames_df.nameid == row.commonnameid].name,
            )

def get_playerid_from_fifa16_given_name_and_team(name, teamid):
    fifa16_team_players_df = pd.merge(fifa16_players_df, fifa16_teamplayerlinks_df, on='playerid')
    fifa16_team_players_df = fifa16_team_players_df[fifa16_team_players_df.teamid == teamid]

    for(row) in fifa16_team_players_df.itertuples():
        firstname = fifa16_playernames_df[fifa16_playernames_df.nameid == row.firstnameid].name.values[0]
        lastname = fifa16_playernames_df[fifa16_playernames_df.nameid == row.lastnameid].name.values[0]
        
        if name.lower() in firstname.lower() or name.lower() in lastname.lower():            
            print(
                row.playerid,
                firstname,
                lastname
                )
            return row.playerid
        
def get_playerid_from_fifa17_given_name_and_team(name, teamid):
    team_players_df = pd.merge(players_df, teamplayerlinks_df, on='playerid')
    team_players_df = team_players_df[team_players_df.teamid == fcsb_teamid]

    for(row) in team_players_df.itertuples():
        firstname = playernames_df[playernames_df.nameid == row.firstnameid].name.values[0]
        lastname = playernames_df[playernames_df.nameid == row.lastnameid].name.values[0]
        
        if name.lower() in firstname.lower() or name.lower() in lastname.lower():            
            print(
                row.playerid,
                firstname,
                lastname
                )
            return row.playerid
   
def insert_name_into_playernames_df(name):
    last_available_nameid = playernames_df.iloc[-1].nameid + 1
    playernames_df.loc[len(playernames_df)] = [name, 900000, last_available_nameid]
    return last_available_nameid
        
def replace_player_from_fifa17_with_one_from_fifa16(fifa17_playerid, fifa16_playerid, fifa17_teamid, fifa16_teamid):
    player_to_replace_df = fifa16_players_df[fifa16_players_df.playerid == fifa16_playerid]
    player_to_replace_df = player_to_replace_df.drop('playerid', axis=1)

    for column in player_to_replace_df.columns:
        if column in players_df.columns:
            players_df.loc[players_df.playerid == fifa17_playerid, column] = player_to_replace_df[column].values[0]

    firstname = fifa16_playernames_df[fifa16_playernames_df.nameid == player_to_replace_df.firstnameid.values[0]].name.values[0]
    lastname = fifa16_playernames_df[fifa16_playernames_df.nameid == player_to_replace_df.lastnameid.values[0]].name.values[0]

    firstnameid = insert_name_into_playernames_df(firstname)
    lastnameid = insert_name_into_playernames_df(lastname)
    
    players_df.loc[players_df.playerid == fifa17_playerid, 'firstnameid'] = firstnameid
    players_df.loc[players_df.playerid == fifa17_playerid, 'lastnameid'] = lastnameid
    players_df.loc[players_df.playerid == fifa17_playerid, 'playerjerseynameid'] = lastnameid
    
    #adjust teamplayer_links
    fifa16_teamplayerlink_df = fifa16_teamplayerlinks_df[(fifa16_teamplayerlinks_df.teamid == fifa16_teamid) & (fifa16_teamplayerlinks_df.playerid == fifa16_playerid)]
    fifa16_teamplayerlink_df = fifa16_teamplayerlink_df.drop(['playerid', 'teamid'], axis=1)

    for column in fifa16_teamplayerlink_df.columns:
        if column in teamplayerlinks_df.columns:
            teamplayerlinks_df.loc[(teamplayerlinks_df.playerid == fifa17_playerid)  & (teamplayerlinks_df.teamid == fifa17_teamid), column] = fifa16_teamplayerlink_df[column].values[0]
        
    print(players_df[players_df.playerid == fifa17_playerid])
    print(playernames_df.iloc[-1])

def replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(fifa17_teamid, fifa16_teamid):
    default_teamsheets_to_replace_df = fifa16_defaul_teamsheets_df[fifa16_defaul_teamsheets_df.teamid == fifa16_teamid]
    for column in default_teamsheets_to_replace_df.columns:
        if not column.endswith('id') and column in default_teamsheets_df.columns:
            default_teamsheets_df.loc[default_teamsheets_df.teamid == fifa17_teamid, column] = default_teamsheets_df[column].values[0]

    formation_to_replace_df = fifa16_formations_df[fifa16_formations_df.teamid == fifa16_teamid]
    for column in formation_to_replace_df.columns:
        if column.endswith('id') is False and column in formations_df.columns:
            formations_df.loc[formations_df.teamid == fifa17_teamid, column] = formation_to_replace_df[column].values[0]
            
    defaultteamdata_to_replace_df = fifa16_defaultteamdata_df[fifa16_defaultteamdata_df.teamid == fifa16_teamid]
    for column in defaultteamdata_to_replace_df.columns:
        if column.endswith('id') is False and column in defaultteamdata_df.columns:
            defaultteamdata_df.loc[defaultteamdata_df.teamid == fifa17_teamid, column] = defaultteamdata_to_replace_df[column].values[0]
    
replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(fcsb_teamid, fifa16_fcsb_teamid)
save_tsv()