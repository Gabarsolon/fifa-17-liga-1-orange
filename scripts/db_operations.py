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
    teamplayerlinks_df.to_csv(teamplayerlinks, sep='\t', encoding='utf-16le', index=False)
    for df, name in ((leagueteamlinks_df, 'leagueteamlinks'), (rivals_df, 'rivals'), (manager_df, 'manager'),
                     (teamstadiumlinks_df, 'teamstadiumlinks'), (stadiumassignments_df, 'stadiumassignments'),
                     (playerloans_df, 'playerloans')):
        df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'db', name + '.txt'), sep='\t', encoding='utf-16le', index=False)

def replace_team_details_from_fifa17_with_ones_from_fif16(fifa17_teamid, fifa16_teamid, foundation_year, cityname):
    fifa16_suffix = f"_{fifa16_teamid}"
    fifa17_suffix = f"_{fifa17_teamid}"

    for row in fifa16_languagestrings_df.itertuples():
        if isinstance(row.stringid, str) and row.stringid.endswith(fifa16_suffix):
            corresponding_stringid = row.stringid.replace(fifa16_suffix, fifa17_suffix)
            languagestrings_df.loc[languagestrings_df.stringid == corresponding_stringid, 'sourcetext'] = row.sourcetext

    ct_stringid = f"CT_TeamName_{fifa17_teamid}"
    team_name_15 = languagestrings_df.loc[languagestrings_df.stringid == f"TeamName_Abbr15_{fifa17_teamid}", 'sourcetext']
    if not team_name_15.empty and pd.notna(team_name_15.values[0]):
        languagestrings_df.loc[languagestrings_df.stringid == ct_stringid, 'sourcetext'] = team_name_15.values[0]

    #replace city name
    cityid = teams_df.loc[teams_df.teamid == fifa17_teamid, 'cityid'].values[0]
    citystringid = f"CityName_{cityid}_FullChar"
    languagestrings_df.loc[languagestrings_df.stringid == citystringid, 'sourcetext'] = cityname
    
    fix_kits_colors(Team(teamid_fifa16=fifa16_teamid, teamid_fifa17=fifa17_teamid))
    apply_fifa16_number_colors(Team(teamid_fifa16=fifa16_teamid, teamid_fifa17=fifa17_teamid))
    
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

def fix_kits_colors(team):
    fifa16_kit_types = fifa16_teamkits_df.loc[fifa16_teamkits_df.teamtechid == team.teamid_fifa16, 'teamkittypetechid'].unique()
    for teamkittypetechid in set(teamkits_df.loc[teamkits_df.teamtechid == team.teamid_fifa17, 'teamkittypetechid']).intersection(fifa16_kit_types):
        for column in teamkits_df.columns:
            if 'color' in column.lower() and column in fifa16_teamkits_df.columns:
                teamkits_df.loc[
                    (teamkits_df.teamtechid == team.teamid_fifa17) & 
                    (teamkits_df.teamkittypetechid == teamkittypetechid), 
                    column
                ] = fifa16_teamkits_df.loc[
                    (fifa16_teamkits_df.teamtechid == team.teamid_fifa16) & 
                    (fifa16_teamkits_df.teamkittypetechid == teamkittypetechid), 
                    column
                ].values[0]

# FIFA 16 `teamkits.numbercolor` / `shortsnumbercolor` are indexes into Creation Master's KitForm.c_ColorPalette
# (.NET colours). FIFA 17 stores the number colours as RGB in jersey/shortsnumbercolor{prim,sec,ter}{r,g,b}.
# White and black use the slightly dimmed values the finished teams use (no pure 255 / 0 bloom).
FIFA16_NUMBER_COLORS = [
    (255, 255, 255),  # 0 Transparent (treated as white)
    (255, 255, 255),  # 1 White
    (12, 12, 12),     # 2 Black
    (0, 0, 255),      # 3 Blue
    (255, 0, 0),      # 4 Red
    (255, 255, 0),    # 5 Yellow
    (0, 128, 0),      # 6 Green
    (255, 165, 0),    # 7 Orange
    (148, 0, 211),    # 8 DarkViolet
    (90, 60, 30),     # 9
    (255, 192, 203),  # 10 Pink
    (139, 0, 0),      # 11 DarkRed
    (135, 206, 250),  # 12 LightSkyBlue
    (0, 0, 139),      # 13 DarkBlue
    (128, 128, 128),  # 14 Gray
    (200, 200, 100),  # 15
    (160, 140, 85),   # 16
    (255, 215, 0),    # 17 Gold
    (255, 69, 0),     # 18 OrangeRed
    (34, 139, 34),    # 19 ForestGreen
]


def apply_fifa16_number_colors(team):
    """Set the FIFA 17 jersey/shorts number colours (prim = sec = ter) of every kit of the team from the FIFA 16 indexes.
    Without this the number keeps the colour of the replaced Danish team (e.g. Viborg's green)."""
    for kit_type in teamkits_df.loc[teamkits_df.teamtechid == team.teamid_fifa17, 'teamkittypetechid'].unique():
        src = fifa16_teamkits_df[(fifa16_teamkits_df.teamtechid == team.teamid_fifa16) & (fifa16_teamkits_df.teamkittypetechid == kit_type)]
        if src.empty:
            continue
        target = (teamkits_df.teamtechid == team.teamid_fifa17) & (teamkits_df.teamkittypetechid == kit_type)
        # where the back name / front number / shorts number are printed (FIFA 16 codes, same meaning in FIFA 17)
        for column in ('jerseybacknameplacementcode', 'jerseyfrontnumberplacementcode', 'shortsnumberplacementcode'):
            if column in teamkits_df.columns and column in src.columns:
                teamkits_df.loc[target, column] = src.iloc[0][column]
        for prefix, column in (('jersey', 'numbercolor'), ('shorts', 'shortsnumbercolor')):
            index = int(src.iloc[0][column])
            rgb = FIFA16_NUMBER_COLORS[index] if 0 <= index < len(FIFA16_NUMBER_COLORS) else FIFA16_NUMBER_COLORS[1]
            for level in ('prim', 'sec', 'ter'):
                for channel, value in zip('rgb', rgb):
                    teamkits_df.loc[target, f'{prefix}numbercolor{level}{channel}'] = value


def change_kit_foreground_color(team, kit_type, color):
    teamkittypetechid = KitType.from_name(kit_type).id
    kit_id = teamkits_df.loc[(teamkits_df.teamtechid == team.teamid_fifa17) & (teamkits_df.teamkittypetechid == teamkittypetechid), 'teamkitid'].values[0]

    color_columns = [
        ['jerseynamecolorb', 'jerseynamecolorg', 'jerseynamecolorr'],
        ['jerseynumbercolorprimb', 'jerseynumbercolorprimg', 'jerseynumbercolorprimr'],
        ['jerseynumbercolorsecb', 'jerseynumbercolorsecg', 'jerseynumbercolorsecr'],
        ['jerseynumbercolorterb', 'jerseynumbercolorterg', 'jerseynumbercolorterr'],
        ['shortsnumbercolorprimb', 'shortsnumbercolorprimg', 'shortsnumbercolorprimr'],
        ['shortsnumbercolorsecb', 'shortsnumbercolorsecg', 'shortsnumbercolorsecr'],
        ['shortsnumbercolorterb', 'shortsnumbercolorterg', 'shortsnumbercolorterr'],
    ]
    
    for color_columns_group in color_columns:
        print(teamkits_df.loc[teamkits_df.teamkitid == kit_id, color_columns_group])
        teamkits_df.loc[teamkits_df.teamkitid == kit_id, color_columns_group] = color

def change_kit_font_type(team, kit_type, font_code):
    teamkittypetechid = KitType.from_name(kit_type).id
    kit_id = teamkits_df.loc[(teamkits_df.teamtechid == team.teamid_fifa17) & (teamkits_df.teamkittypetechid == teamkittypetechid), 'teamkitid'].values[0]

    for font_column in ['jerseynamefonttype', 'numberfonttype', 'shortsnumberfonttype']:
        print(teamkits_df.loc[teamkits_df.teamkitid == kit_id, font_column])
        teamkits_df.loc[teamkits_df.teamkitid == kit_id, font_column] = font_code

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
        fullname = firstname.lower() + ' ' + lastname.lower()

        if name.lower() in firstname.lower() or name.lower() in lastname.lower() or name.lower() in fullname  or name == row.playerid:
            print(
                row.playerid,
                firstname,
                lastname
                )
            return Player(row.playerid, firstname, lastname)
   
PLAYERNAMES_MAX_NAMEID = 29999  # fifa_ng_db-meta.XML: playernames.nameid rangehigh. Higher ids show as an empty name in game.
ORIGINAL_PLAYERNAMES_ROWS = 28708  # rows of the pristine FIFA 17 table (nameid 0..28707)
NAME_COLUMNS = ['firstnameid', 'lastnameid', 'commonnameid', 'playerjerseynameid']


def insert_name_into_playernames_df(name):
    """Id of a playernames row with this text: an existing row is reused (it keeps its commentary id), otherwise a new
    row is appended. nameid must stay <= 29999 (meta rangehigh); players with a higher id have no name in game."""
    existing = playernames_df.index[playernames_df.name == name]
    if len(existing):
        return playernames_df.loc[existing[0], 'nameid']
    last_available_nameid = playernames_df.iloc[-1].nameid + 1
    if last_available_nameid > PLAYERNAMES_MAX_NAMEID:
        raise RuntimeError(f'playernames is full: nameid {last_available_nameid} > {PLAYERNAMES_MAX_NAMEID} (meta rangehigh)')
    playernames_df.loc[len(playernames_df)] = [name, 900000, last_available_nameid]
    return last_available_nameid


def compact_playernames():
    """Repair a table filled by the old insert (one row per occurrence): rows >= ORIGINAL_PLAYERNAMES_ROWS are merged by
    text (an original row with the same text wins), renumbered contiguously and the players' name ids are remapped."""
    global playernames_df
    orig = playernames_df[playernames_df.nameid < ORIGINAL_PLAYERNAMES_ROWS]
    text_to_id = {}
    for row in orig.itertuples():
        text_to_id.setdefault(row.name, row.nameid)
    mapping, new_rows, next_id = {}, [], ORIGINAL_PLAYERNAMES_ROWS
    for row in playernames_df[playernames_df.nameid >= ORIGINAL_PLAYERNAMES_ROWS].itertuples():
        if row.name in text_to_id:
            mapping[row.nameid] = text_to_id[row.name]
        else:
            text_to_id[row.name] = next_id
            mapping[row.nameid] = next_id
            new_rows.append([row.name, row.commentaryid, next_id])
            next_id += 1
    assert next_id - 1 <= PLAYERNAMES_MAX_NAMEID, next_id
    for column in NAME_COLUMNS:
        players_df[column] = players_df[column].map(lambda v: mapping.get(v, v))
    playernames_df = pd.concat([orig, pd.DataFrame(new_rows, columns=playernames_df.columns)], ignore_index=True)
    print(f'playernames: {len(mapping)} appended rows -> {len(new_rows)} new rows, last nameid {next_id - 1}')
        
def replace_player_from_fifa17_with_one_from_fifa16(fifa17_playerid, fifa16_playerid, fifa17_teamid, fifa16_teamid):
    player_to_replace_df = fifa16_players_df[fifa16_players_df.playerid == fifa16_playerid]
    player_to_replace_df = player_to_replace_df.drop('playerid', axis=1)

    for column in player_to_replace_df.columns:
        if column in players_df.columns:
            players_df.loc[players_df.playerid == fifa17_playerid, column] = player_to_replace_df[column].values[0]

    # FIFA 16 head flags mean "this player has his own head model", but FIFA 17 has no head assets
    # for this slot, so every imported player uses a generic head (issue #21).
    players_df.loc[players_df.playerid == fifa17_playerid, 'headclasscode'] = 1
    players_df.loc[players_df.playerid == fifa17_playerid, 'hashighqualityhead'] = 0

    firstname_matches = fifa16_playernames_df[fifa16_playernames_df.nameid == player_to_replace_df.firstnameid.values[0]]
    lastname_matches = fifa16_playernames_df[fifa16_playernames_df.nameid == player_to_replace_df.lastnameid.values[0]]
    
    firstname = firstname_matches.name.values[0] if not firstname_matches.empty else ""
    lastname = lastname_matches.name.values[0] if not lastname_matches.empty else ""
    
    commonname_id_val = player_to_replace_df.commonnameid.values[0]
    if commonname_id_val != 0:
        common_matches = fifa16_playernames_df[fifa16_playernames_df.nameid == commonname_id_val]
        commonname = common_matches.name.values[0] if not common_matches.empty else None
    else:
        commonname = None

    firstnameid = insert_name_into_playernames_df(firstname)
    lastnameid = insert_name_into_playernames_df(lastname)
    commonnameid = insert_name_into_playernames_df(commonname) if commonname is not None else 0

    players_df.loc[players_df.playerid == fifa17_playerid, 'firstnameid'] = firstnameid
    players_df.loc[players_df.playerid == fifa17_playerid, 'lastnameid'] = lastnameid
    players_df.loc[players_df.playerid == fifa17_playerid, 'playerjerseynameid'] = lastnameid
    players_df.loc[players_df.playerid == fifa17_playerid, 'commonnameid'] = commonnameid
    
    #adjust teamplayer_links
    fifa16_teamplayerlink_df = fifa16_teamplayerlinks_df[(fifa16_teamplayerlinks_df.teamid == fifa16_teamid) & (fifa16_teamplayerlinks_df.playerid == fifa16_playerid)]
    fifa16_teamplayerlink_df = fifa16_teamplayerlink_df.drop(['playerid', 'teamid'], axis=1)

    # Only the jersey number is copied. Everything else in teamplayerlinks must stay: `artificialkey` is globally unique,
    # `position` has to agree with default_teamsheets, and the season stats are the replaced player's. (Before
    # 2026-11-18 every column was assigned in memory, but save_tsv() never wrote teamplayerlinks, so nothing persisted.)
    teamplayerlinks_df.loc[(teamplayerlinks_df.playerid == fifa17_playerid) & (teamplayerlinks_df.teamid == fifa17_teamid),
                           'jerseynumber'] = fifa16_teamplayerlink_df['jerseynumber'].values[0]
        
    # print(players_df[players_df.playerid == fifa17_playerid])
    # print(playernames_df.iloc[-1])

ORIGINAL_FORMATIONS_TSV = os.path.join(os.path.dirname(__file__), "..", "db", "original_tables", "formations.txt")
def normalize_formation_name(name):
    # FIFA 17 `formations.formationname` is only the shape ("4-3-3"); the variant ("Holding", "Wide"...) lives in
    # formationfullnameid. FIFA 16 rows may carry a suffix ("4-3-3 Holding", "4-3-3 Halten"): keep the shape only.
    return str(name).split(' ')[0]

def find_formationfullnameid(fifa16_formation_row, fifa17_reference_df):
    """formationfullnameid is the id of the string Formation_FullName_<id> (e.g. 3 = '4-2-3-1 Wide').
    It is NOT a formationid. Pick it from FIFA 17 rows with the same shape (formation name without suffix); if there are several
    variants (Wide/Narrow, Flat/Holding...) take the one whose player offsets are closest to the FIFA 16 layout."""
    name = normalize_formation_name(fifa16_formation_row.formationname)
    candidates = fifa17_reference_df[(fifa17_reference_df.formationname.map(normalize_formation_name) == name) & (fifa17_reference_df.formationfullnameid > 0)]
    if candidates.empty:
        print(f"WARNING: no FIFA 17 formation named '{name}', formationfullnameid left unchanged")
        return None
    offset_cols = [c for c in candidates.columns if c.startswith('offset') and c in fifa16_formation_row.index]
    distances = ((candidates[offset_cols].astype(float) - fifa16_formation_row[offset_cols].astype(float)) ** 2).sum(axis=1)
    return int(candidates.loc[distances.idxmin(), 'formationfullnameid'])

def replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16(fifa17_teamid, fifa16_teamid):
    original_formations_df = pd.read_csv(ORIGINAL_FORMATIONS_TSV, sep='	', encoding='utf-16le')
    formation_to_replace_df = fifa16_formations_df[fifa16_formations_df.teamid == fifa16_teamid]
    fifa16_formation_row = formation_to_replace_df.iloc[0]
    formationfullnameid = find_formationfullnameid(fifa16_formation_row, original_formations_df)

    # formationid is the primary key of `formations` (unique per row): never copy it from FIFA 16, it collides
    # with other FIFA 17 rows (duplicate key -> crash). Everything else that is not an id is copied.
    copy_id_columns = ['tacticid', 'formationaudioid']
    for column in formation_to_replace_df.columns:
        if (not column.endswith('id') or column in copy_id_columns) and column in formations_df.columns:
            formations_df.loc[formations_df.teamid == fifa17_teamid, column] = formation_to_replace_df[column].values[0]
    original_formationid = original_formations_df.loc[original_formations_df.teamid == fifa17_teamid, 'formationid'].values
    if len(original_formationid):
        formations_df.loc[formations_df.teamid == fifa17_teamid, 'formationid'] = original_formationid[0]

    for target_df, source_df in (
        (default_teamsheets_df, fifa16_defaul_teamsheets_df),
        (defaultteamdata_df, fifa16_defaultteamdata_df),
    ):
        source_row_df = source_df[source_df.teamid == fifa16_teamid]
        for column in source_row_df.columns:
            if (not column.endswith('id') or column in copy_id_columns) and column in target_df.columns:
                target_df.loc[target_df.teamid == fifa17_teamid, column] = source_row_df[column].values[0]

    #set the formationfullnameid which is missing in fifa16 default_teamsheets and defaultteamdata
    if formationfullnameid is not None:
        for target_df in (formations_df, default_teamsheets_df, defaultteamdata_df):
            target_df.loc[target_df.teamid == fifa17_teamid, 'formationfullnameid'] = formationfullnameid

def player_pairs(fifa17_teamid, fifa16_teamid):
    """[(fifa17_playerid, fifa16_playerid)] for a team that was already imported: players are matched by
    (first, last, common) name text, which replace_player_from_fifa17_with_one_from_fifa16 copied from FIFA 16."""
    def names(players_df, names_df, links_df, teamid):
        rows = pd.merge(players_df, links_df[links_df.teamid == teamid], on='playerid')
        by_id = names_df.drop_duplicates('nameid').set_index('nameid')['name']
        def text(nameid):
            return by_id.get(nameid, '') if nameid != 0 else ''
        return [(row.playerid, (text(row.firstnameid), text(row.lastnameid), text(row.commonnameid))) for row in rows.itertuples()]

    fifa16 = {}
    for playerid, key in names(fifa16_players_df, fifa16_playernames_df, fifa16_teamplayerlinks_df, fifa16_teamid):
        fifa16.setdefault(key, []).append(playerid)
    pairs = []
    for playerid, key in names(players_df, playernames_df, teamplayerlinks_df, fifa17_teamid):
        candidates = fifa16.get(key)
        if candidates:
            pairs.append((int(playerid), int(candidates.pop(0))))
    return pairs


def apply_player_swaps(fifa17_teamid, fifa16_teamid, swaps):
    """Give the FIFA 17 slot of FIFA 16 player `out` to FIFA 16 player `in`. The incoming player takes the
    jersey number of the outgoing one (FIFA 16 data can have the same number twice in one squad)."""
    for out_id, in_id in swaps:
        slot = {f16: f17 for f17, f16 in player_pairs(fifa17_teamid, fifa16_teamid)}.get(out_id)
        if slot is None:
            print(f"WARNING: FIFA 16 player {out_id} is not in the FIFA 17 squad, swap with {in_id} skipped")
            continue
        mask = (teamplayerlinks_df.playerid == slot) & (teamplayerlinks_df.teamid == fifa17_teamid)
        jersey = teamplayerlinks_df.loc[mask, 'jerseynumber'].values[0]
        replace_player_from_fifa17_with_one_from_fifa16(slot, in_id, fifa17_teamid, fifa16_teamid)
        teamplayerlinks_df.loc[mask, 'jerseynumber'] = jersey
        print(f"Swapped FIFA 16 player {out_id} -> {in_id} in FIFA 17 slot {slot}, jersey {jersey}")


ROLE_COLUMNS = ['captainid', 'penaltytakerid', 'freekicktakerid', 'leftfreekicktakerid', 'rightfreekicktakerid',
                'longkicktakerid', 'leftcornerkicktakerid', 'rightcornerkicktakerid']
SHEET_SQUAD_COLUMNS = 42  # default_teamsheets.playerid0..41 hold the squad (XI, bench, reserves) then -1 padding; 42..51 are 0


def pairs_by_identity(fifa17_teamid, fifa16_teamid):
    """{fifa16_playerid: fifa17_playerid} of the squad. Name text first (player_pairs); slots that still have no
    partner are matched by identical (overallrating, birthdate, height, weight, preferredposition1), because the import
    copied every common `players` column of the FIFA 16 player into the slot."""
    pairs = {f16: f17 for f17, f16 in player_pairs(fifa17_teamid, fifa16_teamid)}
    slots = players_df[players_df.playerid.isin(teamplayerlinks_df[teamplayerlinks_df.teamid == fifa17_teamid].playerid)]
    squad16 = fifa16_players_df[fifa16_players_df.playerid.isin(
        fifa16_teamplayerlinks_df[fifa16_teamplayerlinks_df.teamid == fifa16_teamid].playerid)]
    key = ['overallrating', 'birthdate', 'height', 'weight', 'preferredposition1']
    taken = set(pairs.values())
    for slot in slots[~slots.playerid.isin(taken)].itertuples():
        match = squad16[(~squad16.playerid.isin(pairs)) & (squad16[key] == [getattr(slot, c) for c in key]).all(axis=1)]
        if len(match):
            pairs[int(match.iloc[0].playerid)] = int(slot.playerid)
    return pairs


def port_lineup_and_roles(fifa17_teamid, fifa16_teamid):
    """Translate FIFA 16 player ids into the FIFA 17 slot ids for everything that points at players:
    - teamplayerlinks.position: the FIFA 16 squad position of the paired player (0 = goalkeeper, formation slots, bench)
    - default_teamsheets.playerid0..41: the FIFA 16 squad order with the ids translated (cut players dropped, -1 padding)
    - captain and set-piece takers (teams + default_teamsheets)
    The import used to copy the FIFA 16 ids verbatim, so the sheet pointed at players that do not exist in FIFA 17 and
    position 0 was a field player for most teams."""
    pairs = pairs_by_identity(fifa17_teamid, fifa16_teamid)
    links17 = teamplayerlinks_df[teamplayerlinks_df.teamid == fifa17_teamid]
    links16 = fifa16_teamplayerlinks_df[fifa16_teamplayerlinks_df.teamid == fifa16_teamid].set_index('playerid')
    # 1. positions
    used = set()
    for f16, f17 in pairs.items():
        position = int(links16.loc[f16, 'position'])
        teamplayerlinks_df.loc[(teamplayerlinks_df.teamid == fifa17_teamid) & (teamplayerlinks_df.playerid == f17), 'position'] = position
        used.add(position)
    unpaired = links17[~links17.playerid.isin(pairs.values())]
    free = [n for n in list(range(11, 28)) + [28, 29] + list(range(2, 11)) if n not in used]
    for idx in unpaired.index:
        teamplayerlinks_df.loc[idx, 'position'] = free.pop(0)
    # 2. team sheet. XI (playerid0..10, roles = position0..10) first: a FIFA 16 starter that was cut by the OVR selection
    # is replaced by the closest kept player (same position group, nearest position code, then best OVR).
    row = default_teamsheets_df.index[default_teamsheets_df.teamid == fifa17_teamid][0]
    sheet16 = fifa16_defaul_teamsheets_df[fifa16_defaul_teamsheets_df.teamid == fifa16_teamid].iloc[0]
    kept = [int(p) for p in teamplayerlinks_df[teamplayerlinks_df.teamid == fifa17_teamid].playerid]
    info = players_df.set_index('playerid')

    def group(code):
        return 0 if code == 0 else 1 if code <= 8 else 2 if code <= 19 else 3

    xi = []
    for i in range(11):
        old = int(sheet16[f'playerid{i}'])
        xi.append(pairs.get(old))
    for i in range(11):
        if xi[i] is not None:
            continue
        role = int(sheet16[f'position{i}'])
        candidates = [p for p in kept if p not in xi]
        best = min(candidates, key=lambda p: (group(int(info.loc[p, 'preferredposition1'])) != group(role),
                                              abs(int(info.loc[p, 'preferredposition1']) - role),
                                              -int(info.loc[p, 'overallrating'])))
        xi[i] = best
        teamplayerlinks_df.loc[(teamplayerlinks_df.teamid == fifa17_teamid) & (teamplayerlinks_df.playerid == best), 'position'] = role
        print(f'  team {fifa17_teamid}: FIFA 16 starter {sheet16[f"playerid{i}"]} was cut, slot {i} (role {role}) goes to player {best}')
    rest = [pairs[int(sheet16[f'playerid{i}'])] for i in range(11, SHEET_SQUAD_COLUMNS)
            if int(sheet16[f'playerid{i}']) in pairs and pairs[int(sheet16[f'playerid{i}'])] not in xi]
    rest += [p for p in kept if p not in xi and p not in rest]  # players the FIFA 16 sheet did not list (swapped in)
    ordered = (xi + rest)[:SHEET_SQUAD_COLUMNS]
    ordered += [-1] * (SHEET_SQUAD_COLUMNS - len(ordered))
    for i in range(SHEET_SQUAD_COLUMNS):
        default_teamsheets_df.loc[row, f'playerid{i}'] = ordered[i]
    # 3. captain and takers
    fallback = ordered[1]  # a field player of the XI when the FIFA 16 choice was cut
    teams_row = teams_df.index[teams_df.teamid == fifa17_teamid][0]
    team16 = fifa16_teams_df[fifa16_teams_df.teamid == fifa16_teamid].iloc[0]
    for column in ROLE_COLUMNS:
        for df, index, source in ((teams_df, teams_row, team16), (default_teamsheets_df, row, sheet16)):
            if column in df.columns and column in source.index:
                df.loc[index, column] = pairs.get(int(source[column]), fallback)
    return len(pairs), len(unpaired)


# teams columns copied from FIFA 16 as they are: same meaning and scale in both games (checked on the 621 teams that exist in
# both: correlation 0.95-1.0 and similar means). The prestige columns use another scale and are fitted, see below.
TEAM_COPY_COLUMNS = ['transferbudget', 'latitude', 'longitude', 'utcoffset', 'adboardid', 'defteamwidth', 'defaggression', 'ccpassing',
                     'cccrossing', 'ccshooting', 'busdribbling', 'ccpositioning', 'buspositioning', 'defdefenderline']
PRESTIGE_COLUMNS = ['domesticprestige', 'internationalprestige']
LEAGUE_ROW_KEEP = {'teamid', 'leagueid', 'prevleagueid', 'artificialkey'}  # everything else is the FIFA 16 start of season


def _fit_prestige(column):
    """Linear fit FIFA 16 -> FIFA 17 over the teams that exist in both games (prestige is 0-20 in FIFA 16, 0-10 in FIFA 17)."""
    common = fifa16_teams_df.merge(teams_df, on='teamid', suffixes=('_16', '_17'))
    a, b = common[column + '_16'].astype(float), common[column + '_17'].astype(float)
    slope = a.cov(b) / a.var()
    intercept = b.mean() - slope * a.mean()
    low, high = int(teams_df[column].min()), int(teams_df[column].max())
    return lambda value: int(min(high, max(low, round(slope * float(value) + intercept))))


def _xi_features(sheet_row, info):
    """Mean OVR of the XI and of its goalkeeper+defence / midfield / attack, from the formation roles position0..10."""
    groups = {'all': [], 'def': [], 'mid': [], 'att': []}
    for i in range(11):
        pid = int(sheet_row[f'playerid{i}'])
        if pid not in info.index:
            return None
        role = int(sheet_row[f'position{i}'])
        ovr = float(info.loc[pid, 'overallrating'])
        groups['all'].append(ovr)
        groups['def' if role <= 8 else 'mid' if role <= 19 else 'att'].append(ovr)
    if not all(groups.values()):
        return None
    return {k: sum(v) / len(v) for k, v in groups.items()}


def fit_team_rating_models(exclude_teamids):
    """Linear models XI mean OVR -> team rating, fitted on the FIFA 17 teams that were not imported. Returns
    {rating column: (slope, intercept, r)} for overall/attack/midfield/defense."""
    import numpy as np
    info = players_df.set_index('playerid')
    targets = {'overallrating': 'all', 'attackrating': 'att', 'midfieldrating': 'mid', 'defenserating': 'def'}
    xs, ys = {c: [] for c in targets}, {c: [] for c in targets}
    teams_by_id = teams_df.set_index('teamid')
    for sheet in default_teamsheets_df.itertuples(index=False):
        sheet = pd.Series(sheet._asdict())
        if sheet['teamid'] in exclude_teamids or sheet['teamid'] not in teams_by_id.index:
            continue
        feat = _xi_features(sheet, info)
        if feat is None:
            continue
        for column, group in targets.items():
            xs[column].append(feat[group])
            ys[column].append(float(teams_by_id.loc[sheet['teamid'], column]))
    models = {}
    for column in targets:
        x, y = np.array(xs[column]), np.array(ys[column])
        slope, intercept = np.polyfit(x, y, 1)
        models[column] = (slope, intercept, float(np.corrcoef(x, y)[0, 1]), len(x))
    return models


def set_team_ratings(fifa17_teamid, models):
    """Team ratings from the imported XI (FIFA 16 only has the default 50 for most of these teams)."""
    info = players_df.set_index('playerid')
    sheet = default_teamsheets_df[default_teamsheets_df.teamid == fifa17_teamid].iloc[0]
    feat = _xi_features(sheet, info)
    row = teams_df.index[teams_df.teamid == fifa17_teamid][0]
    groups = {'overallrating': 'all', 'attackrating': 'att', 'midfieldrating': 'mid', 'defenserating': 'def'}
    for column, group in groups.items():
        slope, intercept = models[column][:2]
        value = int(round(min(99, max(1, slope * feat[group] + intercept))))
        teams_df.loc[row, column] = value
        teams_df.loc[row, 'matchday' + column] = value


LOAN_END_JAN, LOAN_END_JUN = 158594, 158775  # the two loan end dates FIFA 17 uses most (Jan / Jun 2017)


def port_loans():
    """playerloans (teamidloanedfrom, playerid, loandateend) for the 14 teams. The FIFA 17 rows were the Danish league's:
    5 rows named our slots as the lending club or used slot player ids. They are removed; the FIFA 16 loans that involve
    a Liga 1 squad player are added with the player id translated to the FIFA 17 slot id: loans INTO Liga 1 (the lender is
    a club that exists in FIFA 17) and loans between Liga 1 clubs. FIFA 16 loan dates (2016) are mapped to the FIFA 17 ones."""
    ours = {int(t.teamid_fifa17) for t in liga1orange_teams.values()}
    f16_to_f17_team = {int(t.teamid_fifa16): int(t.teamid_fifa17) for t in liga1orange_teams.values()}
    pair_map = {}
    for t in liga1orange_teams.values():
        pair_map.update(pairs_by_identity(t.teamid_fifa17, t.teamid_fifa16))
    slot_players = set(teamplayerlinks_df[teamplayerlinks_df.teamid.isin(ours)].playerid)
    playerloans_df.drop(playerloans_df.index[playerloans_df.teamidloanedfrom.isin(ours) | playerloans_df.playerid.isin(slot_players)],
                        inplace=True)
    playerloans_df.reset_index(drop=True, inplace=True)
    known_teams = set(teams_df.teamid)
    added = []
    for row in fifa16_playerloans_df.itertuples():
        f17_player = pair_map.get(int(row.playerid))
        if f17_player is None:
            continue  # the loaned player is not in a Liga 1 squad (e.g. a Liga 1 club's player loaned abroad)
        lender = f16_to_f17_team.get(int(row.teamidloanedfrom), int(row.teamidloanedfrom))
        current = int(teamplayerlinks_df[teamplayerlinks_df.playerid == f17_player].teamid.iloc[0])
        if lender == current or lender not in known_teams:
            continue
        end = LOAN_END_JAN if int(row.loandateend) < 158300 else LOAN_END_JUN
        playerloans_df.loc[len(playerloans_df)] = [lender, f17_player, end]
        added.append((f17_player, lender, current, end))
    return added


def normalize_league_table():
    """The FIFA 16 league rows have repeated and missing table positions (e.g. two teams at 13). At the start of a season
    the table follows last season: rank by previousyeartableposition, ties by team rating, positions 1..n."""
    ours = {int(t.teamid_fifa17) for t in liga1orange_teams.values()}
    rows = leagueteamlinks_df[leagueteamlinks_df.teamid.isin(ours)]
    rating = teams_df.set_index('teamid').overallrating
    order = sorted(rows.index, key=lambda i: (int(rows.loc[i, 'previousyeartableposition']), -int(rating[rows.loc[i, 'teamid']])))
    for rank, i in enumerate(order, start=1):
        leagueteamlinks_df.loc[i, 'currenttableposition'] = rank
        leagueteamlinks_df.loc[i, 'previousyeartableposition'] = rank


RATING_MODELS = None


def port_team_extras(fifa17_teamid, fifa16_teamid):
    """The team level data that is not players or kits (issue #26): rivals, manager names, ratings/budget/location/tactics,
    prestige, stadium and its Romanian name, and the Career league row (season state of the replaced Danish team)."""
    global RATING_MODELS
    team_ids = {int(t.teamid_fifa16): int(t.teamid_fifa17) for t in liga1orange_teams.values()}
    if RATING_MODELS is None:
        RATING_MODELS = fit_team_rating_models({int(t.teamid_fifa17) for t in liga1orange_teams.values()})
    row16 = fifa16_teams_df[fifa16_teams_df.teamid == fifa16_teamid].iloc[0]
    row = teams_df.index[teams_df.teamid == fifa17_teamid][0]
    # budget, location, tactics (the ratings come from set_team_ratings, run port_lineup_and_roles first)
    set_team_ratings(fifa17_teamid, RATING_MODELS)
    for column in TEAM_COPY_COLUMNS:
        if column in teams_df.columns and column in fifa16_teams_df.columns:
            teams_df.loc[row, column] = row16[column]
    for column in PRESTIGE_COLUMNS:
        teams_df.loc[row, column] = _fit_prestige(column)(row16[column])
    # rivals: FIFA 16 has no `rivals` rows for these teams, only teams.rivalteam; the FIFA 17 rows are the Danish rivalries
    rival17 = team_ids.get(int(row16['rivalteam']))
    if rival17 is not None:
        teams_df.loc[row, 'rivalteam'] = rival17
        ours = {int(t.teamid_fifa17) for t in liga1orange_teams.values()}
        rivals_df.drop(rivals_df.index[(rivals_df.teamid1 == fifa17_teamid) |
                                       ((rivals_df.teamid2 == fifa17_teamid) & ~rivals_df.teamid1.isin(ours))], inplace=True)
        rivals_df.reset_index(drop=True, inplace=True)  # `loc[len(df)]` below must not reuse an existing label
        new = {'rivaltype': 0, 'teamid2': rival17, 'teamid1': fifa17_teamid}
        rivals_df.loc[len(rivals_df)] = [new[c] for c in rivals_df.columns]
    # manager (names only; the look of the Danish manager stays)
    m16 = fifa16_manager_df[fifa16_manager_df.teamid == fifa16_teamid]
    m17 = manager_df.index[manager_df.teamid == fifa17_teamid]
    if len(m16) and len(m17):
        manager_df.loc[m17[0], 'firstname'] = str(m16.iloc[0].firstname).strip()
        manager_df.loc[m17[0], 'surname'] = str(m16.iloc[0].surname).strip()
    # stadium: the same stadium id means the same stadium in both games (512 of 619 teams use the same id); the Romanian
    # name goes to stadiumassignments (a FIFA 16 feature, empty in FIFA 17: unverified in game)
    link16 = fifa16_teamstadiumlinks_df[fifa16_teamstadiumlinks_df.teamid == fifa16_teamid]
    names = dict(zip(teamstadiumlinks_df.stadiumid, teamstadiumlinks_df.stadiumname))
    if len(link16) and int(link16.iloc[0].stadiumid) in names:
        stadium = int(link16.iloc[0].stadiumid)
        idx = teamstadiumlinks_df.index[teamstadiumlinks_df.teamid == fifa17_teamid]
        teamstadiumlinks_df.loc[idx, 'stadiumid'] = stadium
        teamstadiumlinks_df.loc[idx, 'stadiumname'] = names[stadium]
    custom = fifa16_stadiumassignments_df[fifa16_stadiumassignments_df.teamid == fifa16_teamid]
    stadiumassignments_df.drop(stadiumassignments_df.index[stadiumassignments_df.teamid == fifa17_teamid], inplace=True)
    stadiumassignments_df.reset_index(drop=True, inplace=True)
    if len(custom):
        text = str(custom.iloc[0].stadiumcustomname).replace('\\t', ' ').strip()
        stadiumassignments_df.loc[len(stadiumassignments_df)] = [text, fifa17_teamid]
    # Career league row: start of the FIFA 16 season (no matches played, last season's table position, objective)
    link17 = leagueteamlinks_df.index[leagueteamlinks_df.teamid == fifa17_teamid][0]
    row16_league = fifa16_leagueteamlinks_df[fifa16_leagueteamlinks_df.teamid == fifa16_teamid].iloc[0]
    for column in leagueteamlinks_df.columns:
        if column not in LEAGUE_ROW_KEEP and column in fifa16_leagueteamlinks_df.columns:
            leagueteamlinks_df.loc[link17, column] = row16_league[column]


ORIGINAL_MAX_PLAYERID = 236210  # highest playerid of the pristine FIFA 17 players table; players added by us are above it


def add_extra_players(fifa17_teamid, fifa16_teamid):
    """Issue #25: the FIFA 17 team only has as many slots as the replaced Danish team, so the OVR selection drops the rest of
    the FIFA 16 squad. Every FIFA 16 squad member without a slot gets a NEW player row (playerid above the pristine maximum)
    and a teamplayerlinks row, so the whole FIFA 16 squad is in the team. The new players have no miniface file (Frosty cannot
    add legacy files), the game shows the generic head for them. Returns the list of new FIFA 17 player ids."""
    global players_df, teamplayerlinks_df
    pairs = pairs_by_identity(fifa17_teamid, fifa16_teamid)
    squad16 = fifa16_teamplayerlinks_df[fifa16_teamplayerlinks_df.teamid == fifa16_teamid].playerid
    extras = [int(p) for p in squad16 if int(p) not in pairs]
    links = teamplayerlinks_df[teamplayerlinks_df.teamid == fifa17_teamid]
    template_player_id = int(links.iloc[-1].playerid)
    added = []
    for f16_player in extras:
        new_id = int(players_df.playerid.max()) + 1
        player_row = players_df[players_df.playerid == template_player_id].copy()
        player_row['playerid'] = new_id
        players_df = pd.concat([players_df, player_row], ignore_index=True)
        link_row = teamplayerlinks_df[(teamplayerlinks_df.teamid == fifa17_teamid) & (teamplayerlinks_df.playerid == template_player_id)].copy()
        link_row['playerid'] = new_id
        link_row['artificialkey'] = int(teamplayerlinks_df.artificialkey.max()) + 1
        link_row['position'] = 29
        teamplayerlinks_df = pd.concat([teamplayerlinks_df, link_row], ignore_index=True)
        replace_player_from_fifa17_with_one_from_fifa16(new_id, f16_player, fifa17_teamid, fifa16_teamid)
        added.append(new_id)
    return added


def dedupe_jersey_numbers(fifa17_teamid):
    """FIFA 16 data can give two players of a squad the same number: the later row gets the lowest free number."""
    rows = teamplayerlinks_df[teamplayerlinks_df.teamid == fifa17_teamid]
    seen = set()
    for idx, number in rows.jerseynumber.items():
        if number in seen:
            free = next(n for n in range(1, 100) if n not in seen and n not in set(rows.jerseynumber))
            print(f"  duplicate jersey {number} in team {fifa17_teamid}, row {idx} -> {free}")
            teamplayerlinks_df.loc[idx, 'jerseynumber'] = free
            number = free
        seen.add(number)


def apply_fifa16_jersey_numbers(fifa17_teamid, fifa16_teamid):
    """For a team that was imported before the jersey fix: copy the FIFA 16 jersey numbers by name pairs."""
    pairs = player_pairs(fifa17_teamid, fifa16_teamid)
    for fifa17_playerid, fifa16_playerid in pairs:
        number = fifa16_teamplayerlinks_df[(fifa16_teamplayerlinks_df.teamid == fifa16_teamid) &
                                           (fifa16_teamplayerlinks_df.playerid == fifa16_playerid)].jerseynumber.values[0]
        teamplayerlinks_df.loc[(teamplayerlinks_df.playerid == fifa17_playerid) &
                               (teamplayerlinks_df.teamid == fifa17_teamid), 'jerseynumber'] = number
    dedupe_jersey_numbers(fifa17_teamid)
    return len(pairs)


def replace_players_from_fifa16_with_players_from_fifa17(fifa17_teamid, fifa16_teamid):
    fifa16_players = pd.merge(fifa16_players_df, fifa16_teamplayerlinks_df, on='playerid')
    fifa16_players = fifa16_players[fifa16_players.teamid == fifa16_teamid]
    
    fifa17_players = pd.merge(players_df, teamplayerlinks_df, on='playerid')
    fifa17_players = fifa17_players[fifa17_players.teamid == fifa17_teamid]

    fifa16_players = fifa16_players.sort_values(by='overallrating', ascending=False)

    for (fifa16_index, fifa16_row), (fifa17_index, fifa17_row) in zip(fifa16_players.iterrows(), fifa17_players.iterrows()):
        replace_player_from_fifa17_with_one_from_fifa16(fifa17_row.playerid, fifa16_row.playerid, fifa17_teamid, fifa16_teamid)

    if len(fifa16_players) < len(fifa17_players):
        extra_players = fifa17_players.iloc[len(fifa16_players):]
        drop_indices = teamplayerlinks_df[
            (teamplayerlinks_df.teamid == fifa17_teamid) & 
            (teamplayerlinks_df.playerid.isin(extra_players.playerid))
        ].index
        teamplayerlinks_df.drop(drop_indices, inplace=True)

    dedupe_jersey_numbers(fifa17_teamid)
