from pathlib import Path
import pandas as pd
import os

fcsb_teamid = 269
home_kitid = 0
away_kitid = 1

teamkits = os.path.join(os.path.dirname(__file__), "teamkits.txt")
teamkits_df = pd.read_csv(teamkits, sep='\t', encoding='utf-16le')
# print(teamkits_df.columns)

def change_jersey_number_color(kit_id, color):
    print(teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']])

    teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']] = color

def save_tsv():
    teamkits_df.to_csv(teamkits, sep='\t', encoding='utf-16le', index=False)

def change_jersey_name_color(kit_id, color):
    print([col for col in teamkits_df.columns if 'name' in col.lower()])
    teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']] = color
    print(teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == kit_id), ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']])
    
    
change_jersey_name_color(away_kitid, [0, 92, 180])
change_jersey_number_color(away_kitid, [0, 92, 180])

save_tsv()