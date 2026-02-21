import os
import pandas as pd

#FIFA 17 tables
defaultteamdata = os.path.join(os.path.dirname(__file__), "..", "db", "defaultteamdata.txt")
default_teamsheets = os.path.join(os.path.dirname(__file__), "..", "db", "default_teamsheets.txt")
formations = os.path.join(os.path.dirname(__file__), "..", "db", "formations.txt")
teams = os.path.join(os.path.dirname(__file__), "..", "db", "teams.txt")
teamkits = os.path.join(os.path.dirname(__file__), "..", "db", "teamkits.txt")
players = os.path.join(os.path.dirname(__file__), "..", "db", "players.txt")
playernames = os.path.join(os.path.dirname(__file__), "..", "db", "playernames.txt")
teamplayerlinks = os.path.join(os.path.dirname(__file__), "..", "db", "teamplayerlinks.txt")
languagestrings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")


defaultteamdata_df = pd.read_csv(defaultteamdata, sep='\t', encoding='utf-16le')
default_teamsheets_df = pd.read_csv(default_teamsheets, sep='\t', encoding='utf-16le')
formations_df = pd.read_csv(formations, sep='\t', encoding='utf-16le')
teams_df = pd.read_csv(teams, sep='\t', encoding='utf-16le')
teamkits_df = pd.read_csv(teamkits, sep='\t', encoding='utf-16le')
players_df = pd.read_csv(players, sep='\t', encoding='utf-16le')
playernames_df = pd.read_csv(playernames, sep='\t', encoding='utf-16le')
teamplayerlinks_df = pd.read_csv(teamplayerlinks, sep='\t', encoding='utf-16le')
languagestrings_df = pd.read_csv(languagestrings, sep='\t', encoding='utf-16le')


# playernames_df = playernames_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
# # Strip spaces from the 'Name' column
# playernames_df['commentaryid'] = playernames_df['commentaryid'].apply(lambda x: str(int(x)) if not pd.isna(x) else x)
# playernames_df['nameid'] = playernames_df['nameid'].apply(lambda x: str(int(x)) if not pd.isna(x) else x)

#FIFA 16 tables
fifa16_defaultteamdata = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "defaultteamdata.txt")
fifa16_defaul_teamsheets = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "default_teamsheets.txt")
fifa16_teams = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "teams.txt")
fifa16_teamkits = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "teamkits.txt")
fifa16_formations = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "formations.txt")
fifa16_players = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "players.txt")
fifa16_playernames = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "playernames.txt")
fifa16_teamplayerlinks = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "teamplayerlinks.txt")
fifa16_languagestrings = os.path.join(os.path.dirname(__file__), "..", "db", "fifa-16", "LanguageStrings.txt")

fifa16_defaultteamdata_df = pd.read_csv(fifa16_defaultteamdata, sep='\t', encoding='utf-16le')
fifa16_defaul_teamsheets_df = pd.read_csv(fifa16_defaul_teamsheets, sep='\t', encoding='utf-16le')
fifa16_teams_df = pd.read_csv(fifa16_teams, sep='\t', encoding='utf-16le')
fifa16_teamkits_df = pd.read_csv(fifa16_teamkits, sep='\t', encoding='utf-16le')
fifa16_formations_df = pd.read_csv(fifa16_formations, sep='\t', encoding='utf-16le')
fifa16_players_df = pd.read_csv(fifa16_players, sep='\t', encoding='utf-16le')
fifa16_playernames_df = pd.read_csv(fifa16_playernames, sep='\t', encoding='utf-16le')
fifa16_teamplayerlinks_df = pd.read_csv(fifa16_teamplayerlinks, sep='\t', encoding='utf-16le')
fifa16_languagestrings_df = pd.read_csv(fifa16_languagestrings, sep='\t', encoding='utf-16le')

def print_new_columns_in_fifa17():
    df_pairs = [
        ("defaultteamdata", defaultteamdata_df, fifa16_defaultteamdata_df),
        ("default_teamsheets", default_teamsheets_df, fifa16_defaul_teamsheets_df),
        ("formations", formations_df, fifa16_formations_df),
        ("teams", teams_df, fifa16_teams_df),
        ("teamkits", teamkits_df, fifa16_teamkits_df),
        ("players", players_df, fifa16_players_df),
        ("playernames", playernames_df, fifa16_playernames_df),
        ("teamplayerlinks", teamplayerlinks_df, fifa16_teamplayerlinks_df),
        ("languagestrings", languagestrings_df, fifa16_languagestrings_df),
    ]

    for name, df17, df16 in df_pairs:
        new_cols = set(df17.columns) - set(df16.columns)
        if new_cols:
            print(f"Table: {name}")
            print(f"New columns in FIFA 17: {sorted(list(new_cols))}\n")

print_new_columns_in_fifa17()


# folder with all tables
base_dir = os.path.join(os.path.dirname(__file__), "..", "db", "all_tables")

# collect all DataFrames in a dict
tables = {}

for fname in os.listdir(base_dir):
    if not fname.lower().endswith(".txt"):
        continue

    path = os.path.join(base_dir, fname)
    # use utf-16le (as in your original code) and tab separator
    df = pd.read_csv(path, sep="\t", encoding="utf-16le")
    
    # store in dict without extension
    key = os.path.splitext(fname)[0]
    tables[key] = df

# Example: access `players` table as DataFrame
# players_df = tables["players"]


def detect_relations(tables):
    relations = []

    for table_name, df in tables.items():
        for column in df.columns:
            # detect columns ending in "id"
            if column.lower().endswith("id"):
                target_table = column[:-2].lower() + "s"  # teamid -> teams
                if target_table in tables:
                    relations.append((table_name, column, target_table))

    return relations


# relations = detect_relations(tables)

# for r in relations:
#     print(f"{r[0]}.{r[1]}  --->  {r[2]}")