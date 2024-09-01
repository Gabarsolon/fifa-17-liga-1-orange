from pathlib import Path
import pandas as pd
import os

fcsb_teamid = 269
home_kitid = 0

teamkits = os.path.join(os.path.dirname(__file__), "teamkits.txt")
teamkits_df = pd.read_csv(teamkits, sep='\t', encoding='utf-16le')
# print(teamkits_df.columns)

def change_jersey_number_color():
    print(teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == home_kitid), ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']])

    teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == home_kitid), ['jerseynumbercolorprimr', 'jerseynumbercolorprimg', 'jerseynumbercolorprimb']] = [255, 255, 0]

def save_tsv():
    teamkits_df.to_csv(teamkits, sep='\t', encoding='utf-16le', index=False)

def change_jersey_name_color():
    print([col for col in teamkits_df.columns if 'name' in col.lower()])
    teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == home_kitid), ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']] = [255, 255, 255]
    print(teamkits_df.loc[(teamkits_df.teamtechid == fcsb_teamid) & (teamkits_df.teamkittypetechid == home_kitid), ['jerseynamecolorr', 'jerseynamecolorg', 'jerseynamecolorb']])
    
change_jersey_name_color()
save_tsv()