"""Pre-injection checks. Returns a list of error strings; empty list means OK.

Texture slots and expected sizes (FIFA 17 kit textures):
  jersey_<id>_<kit>_0_color  1024x1024, BC3 (DXT5)
  shorts_<id>_<kit>_0_color  1024x512,  BC3
  socks_<id>_<kit>_0_color   512x256,   BC3
"""
import glob
import os
import struct

import pandas as pd

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")

TEXTURE_SIZES = {"jersey": (1024, 1024), "shorts": (1024, 512), "socks": (512, 256)}

# table -> primary key columns
TABLE_KEYS = {
    "players": ["playerid"],
    "playernames": ["nameid"],
    "teams": ["teamid"],
    "teamkits": ["teamkitid"],
    "formations": ["formationid"],
    "default_teamsheets": ["teamid"],
    "defaultteamdata": ["teamid"],
    "teamplayerlinks": ["teamid", "playerid"],
}


def _read(name):
    return pd.read_csv(os.path.join(DB_DIR, f"{name}.txt"), sep="\t", encoding="utf-16le")


def check_tables(team):
    errors = []
    tables = {name: _read(name) for name in TABLE_KEYS}
    for name, keys in TABLE_KEYS.items():
        dups = tables[name][tables[name].duplicated(keys, keep=False)]
        if len(dups):
            errors.append(f"{name}: {len(dups)} rows with duplicate key {keys}, e.g. {dups[keys[0]].unique()[:5].tolist()}")

    links, players, names = tables["teamplayerlinks"], tables["players"], tables["playernames"]
    orphan = links[~links.playerid.isin(players.playerid)]
    if len(orphan):
        errors.append(f"teamplayerlinks: {len(orphan)} links to missing players")
    for column in ("firstnameid", "lastnameid", "commonnameid", "playerjerseynameid"):
        missing = players[(players[column] != 0) & (~players[column].isin(names.nameid))]
        if len(missing):
            errors.append(f"players.{column}: {len(missing)} ids missing in playernames")

    # formationfullnameid must be a Formation_FullName_<id> string, never -1 for an imported team
    for name in ("formations", "default_teamsheets", "defaultteamdata"):
        row = tables[name][tables[name].teamid == team.teamid_fifa17]
        if row.empty:
            errors.append(f"{name}: no row for team {team.teamid_fifa17}")
        elif (row.formationfullnameid <= 0).any():
            errors.append(f"{name}: formationfullnameid {row.formationfullnameid.tolist()} invalid for team {team.teamid_fifa17}")
    if (tables["teams"].teamid == team.teamid_fifa17).sum() != 1:
        errors.append(f"teams: team {team.teamid_fifa17} not found exactly once")
    return errors


def _dds_info(path):
    with open(path, "rb") as f:
        header = f.read(128)
    if header[:4] != b"DDS ":
        return None
    height, width = struct.unpack("<II", header[12:20])
    mips = struct.unpack("<I", header[28:32])[0]
    return width, height, mips, header[84:88]


def check_textures(final_dir, team):
    errors = []
    for kind, (width, height) in TEXTURE_SIZES.items():
        files = glob.glob(os.path.join(final_dir, f"{kind}_{team.teamid_fifa17}_*_0_color.dds"))
        if not files:
            errors.append(f"no {kind} colour DDS for team {team.teamid_fifa17} in {final_dir}")
        for path in files:
            info = _dds_info(path)
            if info is None:
                errors.append(f"{os.path.basename(path)}: not a DDS file")
                continue
            w, h, mips, fourcc = info
            if (w, h) != (width, height):
                errors.append(f"{os.path.basename(path)}: {w}x{h}, expected {width}x{height}")
            if fourcc != b"DXT5":
                errors.append(f"{os.path.basename(path)}: format {fourcc!r}, expected DXT5")
            if mips < 2:
                errors.append(f"{os.path.basename(path)}: no mip chain")
    return errors


def validate(team, final_dir=None):
    errors = check_tables(team)
    if final_dir:
        errors += check_textures(final_dir, team)
    return errors


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from constants import liga1orange_teams

    key = sys.argv[1] if len(sys.argv) > 1 else "poli"
    team = liga1orange_teams[key]
    final = os.path.join(os.path.dirname(__file__), "..", "assets", "teams", key, "final")
    problems = validate(team, final if os.path.isdir(final) else None)
    print("\n".join(problems) if problems else "OK")
    sys.exit(1 if problems else 0)
