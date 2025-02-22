import os
from pathlib import Path
import pandas as pd
from dataframes import *
from constants import *

def save_tsv():
    teamkits_df.to_csv(teamkits, sep='\t', encoding='utf-16le', index=False)
    players_df.to_csv(players, sep='\t', encoding='utf-16le', index=False)
    playernames_df.to_csv(playernames, sep='\t', encoding='utf-16le', index=False)
    formations_df.to_csv(formations, sep='\t', encoding='utf-16le', index=False)
    default_teamsheets_df.to_csv(default_teamsheets, sep='\t', encoding='utf-16le', index=False)
    defaultteamdata_df.to_csv(defaultteamdata, sep='\t', encoding='utf-16le', index=False)
    teams_df.to_csv(teams, sep='\t', encoding='utf-16le', index=False)
    formations_df.to_csv(formations, sep='\t', encoding='utf-16le', index=False)
    languagestrings_df.to_csv(languagestrings, sep='\t', encoding='utf-16le', index=False)

def replace_team_details_from_fifa17_with_ones_from_fif16(fifa17_teamid, fifa16_teamid, foundation_year):
    fifa16_suffix = f"_{fifa16_teamid}"
    fifa17_suffix = f"_{fifa17_teamid}"

    for row in fifa16_languagestrings_df.itertuples():
        if isinstance(row.stringid, str) and row.stringid.endswith(fifa16_suffix):
            corresponding_stringid = row.stringid.replace(fifa16_suffix, fifa17_suffix)
            languagestrings_df.loc[languagestrings_df.stringid == corresponding_stringid, 'sourcetext'] = row.sourcetext

    
    teams_df.loc[teams_df.teamid == fifa17_teamid, 'foundationyear'] = foundation_year
    team_details_from_fifa16_df = fifa16_teams_df[fifa16_teams_df.teamid == fifa16_teamid]
    columns_to_replace = [
        'teamcolor1g', 'teamcolor1r', 'teamcolor2b', 'teamcolor2r',
         'teamcolor3r', 'teamcolor1b',  'teamcolor3g', 'teamcolor2g',
        'teamcolor3b',
    ]
    for column in columns_to_replace:
        if column in teams_df.columns and column in team_details_from_fifa16_df.columns:
            teams_df.loc[teams_df.teamid == fifa17_teamid, column] = team_details_from_fifa16_df[column].values[0]

def change_jersey_number_color(team, kit_type, color):
    teamkittypetechid = KitType.from_name(kit_type).id
    kit_id = teamkits_df.loc[(teamkits_df.teamtechid == team.teamid_fifa17) & (teamkits_df.teamkittypetechid == teamkittypetechid), 'teamkitid'].values[0]

    teamkits_df.loc[teamkits_df.teamkitid == kit_id, ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']] = color
def change_jersey_name_color(team, kit_type, color):
    teamkittypetechid = KitType.from_name(kit_type).id
    kit_id = teamkits_df.loc[(teamkits_df.teamtechid == team.teamid_fifa17) & (teamkits_df.teamkittypetechid == teamkittypetechid), 'teamkitid'].values[0]
    teamkits_df.loc[teamkits_df.teamkitid == kit_id, ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']] = color

# print([col for col in fifa16_players_df.columns])

def print_player_names(fifa16_teamid, fifa17_teamid):
    fifa16_players_and_names_join_df = pd.merge(fifa16_players_df, fifa16_teamplayerlinks_df, on='playerid')
    fifa16_players_and_names_join_df = fifa16_players_and_names_join_df[fifa16_players_and_names_join_df.teamid == fifa16_teamid]

    print("----------------------------")
    print("FIFA 16:")
    for(row) in fifa16_players_and_names_join_df.itertuples():
        print(
            row.playerid,
            fifa16_playernames_df[fifa16_playernames_df.nameid == row.firstnameid].name, 
            fifa16_playernames_df[fifa16_playernames_df.nameid == row.lastnameid].name, 
            fifa16_playernames_df[fifa16_playernames_df.nameid == row.commonnameid].name,
            )

    # print([col for col in players_df.columns])

    players_and_names_join_df = pd.merge(players_df, teamplayerlinks_df, on='playerid')
    players_and_names_join_df = players_and_names_join_df[players_and_names_join_df.teamid == fifa17_teamid]

    print("----------------------------")
    print("FIFA 17:")
    for(row) in players_and_names_join_df.itertuples():
        print(
            row.playerid,
            playernames_df[playernames_df.nameid == row.firstnameid].name, 
            playernames_df[playernames_df.nameid == row.lastnameid].name, 
            playernames_df[playernames_df.nameid == row.commonnameid].name,
            )
        
def get_player_from_fifa17_given_name_and_team(name, teamid):
    team_players_df = pd.merge(players_df, teamplayerlinks_df, on='playerid')
    team_players_df = team_players_df[team_players_df.teamid == teamid]

    for(row) in team_players_df.itertuples():
        firstname = playernames_df[playernames_df.nameid == row.firstnameid].name.values[0]
        lastname = playernames_df[playernames_df.nameid == row.lastnameid].name.values[0]
        
        if name.lower() in firstname.lower() or name.lower() in lastname.lower():            
            print(
                row.playerid,
                firstname,
                lastname
                )
            return Player(row.playerid, firstname, lastname)
        
def get_player_from_fifa16_given_name_and_team(name, teamid):
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
            return Player(row.playerid, firstname, lastname)
   
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
    fifa16_formation_name = fifa16_formations_df[fifa16_formations_df.teamid == fifa16_teamid].formationname.values[0] 
    formationfullnameid = -1
    #get the formationfullnameid
    for (row) in formations_df.itertuples():
        if row.formationname == fifa16_formation_name:
            formationfullnameid = row.formationid
            break
    
    formation_to_replace_df = fifa16_formations_df[fifa16_formations_df.teamid == fifa16_teamid]
    for column in formation_to_replace_df.columns:
        if column.endswith('id') is False and column in formations_df.columns:
            formations_df.loc[formations_df.teamid == fifa17_teamid, column] = formation_to_replace_df[column].values[0]
    
    default_teamsheets_to_replace_df = fifa16_defaul_teamsheets_df[fifa16_defaul_teamsheets_df.teamid == fifa16_teamid]
    for column in default_teamsheets_to_replace_df.columns:
        if not column.endswith('id') and column in default_teamsheets_df.columns:
            default_teamsheets_df.loc[default_teamsheets_df.teamid == fifa17_teamid, column] = default_teamsheets_df[column].values[0]

    defaultteamdata_to_replace_df = fifa16_defaultteamdata_df[fifa16_defaultteamdata_df.teamid == fifa16_teamid]
    for column in defaultteamdata_to_replace_df.columns:
        if column.endswith('id') is False and column in defaultteamdata_df.columns:
            defaultteamdata_df.loc[defaultteamdata_df.teamid == fifa17_teamid, column] = defaultteamdata_to_replace_df[column].values[0]
            
    #set the formationfullnameid which is missing in fifa16 default_teamsheets and defaultteamdata
    formations_df.loc[formations_df.teamid == fifa17_teamid, 'formationfullnameid'] = formationfullnameid
    default_teamsheets_df.loc[default_teamsheets_df.teamid == fifa17_teamid, 'formationfullnameid'] = formationfullnameid
    defaultteamdata_df.loc[defaultteamdata_df.teamid == fifa17_teamid, 'formationfullnameid'] = formationfullnameid
    