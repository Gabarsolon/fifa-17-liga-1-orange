<!-- HEADER IMAGE -->
<p align="center">
  <img src="assets/league/Liga_I_logo.png" alt="Liga 1 Orange 16/17" width="50%">
</p>

<h1 align="center">⚽ FIFA 17 – Liga 1 Orange 16/17</h1>

<p align="center">
  <b>Romanian Liga 1 Orange 2016/2017 season mod for FIFA 17</b><br>
  Made for fun and nostalgia ✌️
</p>

---

## 📌 What this mod does

The mod replaces the Danish Superliga with the Romanian **Liga 1 Orange 2016/2017**. Players, kits, badges and team data come from **FIFA 16 with the FRLT V2 patch** and are written into **FIFA 17** (Frostbite) by a set of Python scripts and custom command-line tools. Other game versions are not supported.

### Status

- ✅ Romanian league replaces the Danish league: all **14 teams** (names, league structure, colours, formations, lineups, captains and takers)
- ✅ Squads from FIFA 16 / FRLT, sorted by overall rating into the free FIFA 17 squad slots, with FIFA 16 jersey numbers
- ✅ Kits (jersey, shorts, socks, minikits), crests and 3D badges; flat bump/material maps so the old sponsor prints are gone
- ✅ Player minifaces (FIFA 16 photos, generic silhouette when a player has none)
- ✅ Team data: ratings (computed from each squad), budget, prestige, rivals, managers, stadiums, clean Career league table
- ✅ Romanian language in the UI: all 32,025 texts translated and validated, Romanian flag and "Română" in the language menu ([#6](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/6))
- ✅ 3D league logo in the intro and replays
- ⬜ Romanian commentary ([#2](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/2), [#3](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/3)): researched, nothing implemented
- ⬜ Custom scoreboards, flags and banners ([#22](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/22)), player loans ([#20](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/20)), formations ([#24](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/24)), custom player heads ([#21](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/21))

Latest release: [v0.3.0](https://github.com/Gabarsolon/fifa-17-liga-1-orange/releases) (pre-release; the newer data is checked in the database, in-game checks are still pending).

### Teams

| Team | Status |
|---|---|
| FCSB (Steaua), Astra Giurgiu, CFR Cluj, Viitorul Constanța, CS U Craiova, Dinamo București | ✅ done, kits tuned by hand |
| ACS Poli Timișoara | ✅ confirmed working in Kick-Off |
| FC Botoșani, Pandurii Târgu Jiu, Poli Iași, FC Voluntari, Concordia Chiajna, Gaz Metan Mediaș, ASA Târgu Mureș | ✅ imported with the pipeline ([#12](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/12)–[#18](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/18)); kit fonts and number positions not tuned by hand yet |

### Known limitations

- Commentary stays in English.
- A squad is limited to the free slots of the replaced FIFA 17 team; extra FIFA 16 players are dropped ([#25](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues/25)).
- Players have generic 3D heads; only the 2D miniface comes from FIFA 16, and slots without a miniface file show a silhouette (Frosty cannot add legacy files).
- Kit fonts, collars and number positions of the seven pipeline teams use the replaced Danish kit's values; fabric weave is flat on the pipeline kits.
- Tested mostly in Kick-Off. Career Mode has not been checked team by team.

---

## 📷 Screenshots
| | | |
|---|---|---|
| ![](assets/screenshots/screenshot_1.png) | ![](assets/screenshots/screenshot_2.png) | ![](assets/screenshots/screenshot_3.png) |

---

## 📦 Installation

### Easiest: the launcher
1. Install **FIFA 17** (PC) with the patched `CryptBase.dll` in its folder (see Troubleshooting; it is not included).
2. Download `Liga1OrangeLauncher-<version>.zip` from the [releases](https://github.com/Gabarsolon/fifa-17-liga-1-orange/releases), unzip it anywhere (not in Program Files) and run `Liga1OrangeLauncher.exe` (it asks for administrator rights).
3. It finds FIFA 17 (or asks for the folder) and the button **JOACĂ LIGA 1 ORANGE** applies the mod and starts the game. The first start builds a cache (~4 minutes, once). "Pornește jocul original" starts FIFA 17 without the mod.

The launcher bundles a headless Frosty (`tools\`, GPL-3) and the mod; its source is in [`launcher/`](launcher/) and `scripts/package_launcher.ps1` builds the zip. It can download newer mod versions from GitHub Releases once they are public.

### With Frosty Mod Manager
1. Install **FIFA 17** (PC) and **Frosty Mod Manager**.
2. Download `Liga1Orange-<version>.fbmod` from the [latest release](https://github.com/Gabarsolon/fifa-17-liga-1-orange/releases) and import it in the Mod Manager (not tested with the stock Mod Manager yet).
3. Apply the mod and launch the game from Frosty.

> The source of truth is `Liga1Orange.fbproject` in this repository; releases are built from it with `FrostyCmd build-mod`.

## 🎮 Compatibility

- Game: FIFA 17 (PC), Windows
- Modes: Kick-Off (tested), Career Mode (partly tested)

---

## 🛠 Tools

| Tool | Used for |
|---|---|
| [Frosty Editor / Mod Manager](https://github.com/CadeEvs/FrostyToolsuite) | Editing and applying the mod |
| [FrostyCLI](https://github.com/Gabarsolon/FrostyCLI) | Headless build of Frosty: inject databases, legacy files and textures, launch the game |
| [DbMasterCli](https://github.com/Gabarsolon/DbMasterCli) | Headless DB Master: export/import the `.db` tables |
| [CreationMaster16Cli](https://github.com/Gabarsolon/CreationMaster16Cli) | Headless Creation Master 16: export kits, crests and player photos from FIFA 16 |
| texconv (DirectXTex) | PNG to DDS |
| Python 3.12 | Import pipeline (`pandas`, `python-dotenv`) |
| Photoshop / Blender | Hand-made kit and logo work |

The three CLIs are built from the decompiled sources of the original GUI tools and live in their own repositories.

---

## 📂 Project structure

```text
.
├── assets/
│   ├── league/              # League logo (2D and 3D sources)
│   ├── generic/             # Fallback assets (silhouette miniface)
│   ├── language_flags/      # Romanian language-select flag (12 frames)
│   └── teams/<team>/        # Hand-made kit/crest sources of the first six teams; the pipeline teams only
│                            # have generated f16_raw/, final/, heads/ (git-ignored)
│
├── db/
│   ├── *.txt                # TSV dumps of the FIFA 17 tables that the mod edits
│   ├── LanguageStrings.txt  # English strings (+ the Liga 1 team names); LanguageStrings.ro.txt = Romanian
│   ├── fifa-16/             # Reference tables from FIFA 16 (FRLT)
│   ├── original_tables/     # Pristine FIFA 17 baselines
│   ├── reference/           # Reference dumps (legacy file names of the game)
│   └── translation_ro/      # Romanian translation work (batches, instructions, overrides.json)
│
├── scripts/
│   ├── import_team.py       # Import one team end to end (also applies the Romanian UI)
│   ├── import_remaining.sh  # Import several teams one after another
│   ├── validate.py          # Checks keys, ids, texture sizes before injecting
│   ├── audit_teams.py       # Compares the imported teams with FIFA 16 and checks their assets in a project
│   ├── tm_report.py         # Transfermarkt part of the squad report
│   ├── kit_flat_maps.py     # Flat normal/coeff maps for kits (removes the old sponsor prints)
│   ├── ro_translate.py, ro_import.py   # Romanian translation: prepare/validate/merge, inject into a project
│   ├── translation/         # Drivers that run the translation with agyp / opencode / sub-agents
│   ├── import_league_logo.py, league_logo_mesh.py   # 3D league logo
│   ├── fan_flags.py, fix_hotspots.py                # fan flags/banners, kit name hotspots
│   ├── package_launcher.ps1 # builds the launcher zip
│   └── db_operations.py, dataframes.py, constants.py  # Table helpers and the team list
│
├── launcher/                # WPF launcher (source)
├── AGENTS.md                # Detailed project notes and findings (read this first)
├── .env.example             # Template for the local paths
├── requirements.txt
└── Liga1Orange.fbproject    # Frosty Editor project (the mod)
```

---

## 🧰 Working on the project

### 1. Requirements

- FIFA 17 and FIFA 16 (PC); FIFA 16 is only a data source and is never launched
- [FRLT V2 patch](https://dl.fifa-infinity.com/fifa-16/frlt-16-v2/) installed over FIFA 16 (gives the Liga 1 data)
- The three CLIs above, built with the .NET SDK
- texconv, Python 3.12, Git

### 2. Set up

```bash
git clone https://github.com/Gabarsolon/fifa-17-liga-1-orange.git
cd fifa-17-liga-1-orange
pip install -r requirements.txt
cp .env.example .env      # then fill in your own paths
```

All paths live in the git-ignored `.env`; never hardcode them in scripts.

### 3. Import a team

Teams are listed in `scripts/constants.py` (`liga1orange_teams`: FIFA 17 id of the Danish team it replaces, FIFA 16 id, foundation year, city).

```bash
python scripts/import_team.py <team_key>
# useful flags: --skip-db  --skip-assets  --skip-frosty  --fresh
```

The script replaces the players, team data and formations in the TSVs, exports and converts kits, crests and photos from FIFA 16, validates everything, rebuilds the databases with `DbCli` and injects the result into `Liga1Orange.test.fbproject` (created from the clean project and reused, so teams accumulate). Test that project in game; if it works, copy it over `Liga1Orange.fbproject`. Details and rules are in [AGENTS.md](AGENTS.md).

Important: whenever a database is rebuilt, inject both the `.db` **and** its `-meta.xml`, otherwise the game crashes at startup.

### 4. Other jobs

- Check data before injecting: `python scripts/validate.py`
- 3D league logo: `python scripts/import_league_logo.py`
- Romanian translation: `python scripts/ro_translate.py prepare | validate | merge`, then `python scripts/ro_import.py` (or just import a team: `import_team.py` applies it)
- Audit of the imported teams: `python scripts/audit_teams.py [team ...]`
- Release: `FrostyCmd FIFA17 build-mod <project> <out.fbmod> <title> <author> <category> <version>`; to test it apply it with `FrostyCmd FIFA17 apply-mods <pack> <mod.fbmod>` (this also starts the game; `launch <pack>` alone rebuilds the pack WITHOUT mods)

---

## 🛠 Troubleshooting

### 🚫 Mod not showing in game
- Make sure the mod is applied in Frosty Mod Manager and launch the game through Frosty.
- Check for conflicts with other mods.

### 💥 Game crashes on launch
- Most startup crashes come from the database: always inject the `.db` together with its `-meta.xml`, and never use a database with duplicate keys.
- If the game does not start at all, a patched `CryptBase.dll` may be needed. Place it in the game folder, or inject it with [Extreme Injector](https://github.com/master131/ExtremeInjector) (helper script: [scripts/extreme_injector_loop.ps1](scripts/extreme_injector_loop.ps1)).
- Disable other mods, delete the `ModData` folder and let Frosty regenerate it, run Frosty as administrator.

### 👕 Kits / logos not appearing
- Check that team ids match in the database tables and the texture names.
- Verify the `teamkits` rows and that the textures were imported.
- Clear `ModData` and rebuild.

### 📊 Database changes not applying
- Run `python scripts/validate.py` (duplicate ids, missing references).
- Test in Kick-Off before Career Mode.

If the issue persists, open an issue with a clear description, screenshots, and your FIFA 17 and Frosty versions.

---

## 🤝 How to contribute

- Fix incorrect player data or update squads
- Improve kits, textures, faces, banners and flags
- Pick one of the open [issues](https://github.com/Gabarsolon/fifa-17-liga-1-orange/issues) (remaining teams, translation, loans, formations)
- Report bugs

Guidelines: keep the database structure consistent, do not overwrite unrelated tables, test in game before submitting, use clear commit messages, and open a pull request from a new branch with screenshots when relevant.

---

## ⚠ Disclaimer

This is a fan-made project. All rights belong to EA Sports and to the EFET team for the FRLT V2 patch.

## 👤 Author

Created by **Gabarsolon**. If you like the project, give it a ⭐
