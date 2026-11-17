# AI Agents Guide for fifa-17-liga-1-orange

Guidelines and project memory for AI agents (Claude Code, Gemini CLI, Antigravity `agy`, Codex...).
`CLAUDE.md` imports this file. This file was `GEMINI.md` before 2026-11-17 (renamed with `git mv`).

## Context
Mod for FIFA 17 that adds the Romanian Liga 1 Orange (2016/2017) by replacing the Danish league.
It relies on Frosty Editor / Frosty Mod Manager. Database edits and asset generation are done by a Python
CLI (`scripts/menu.py`) plus three custom C# CLIs. Data is taken from **FIFA 16 (with the FRLT V2 patch)** and
written into **FIFA 17**. Other game versions (e.g. FIFA 14) are not supported.
The user (Gabarsolon on GitHub) speaks Romanian. Repo docs stay in English.

## Machine setup (user's PC, verified 2026-11-17)
All paths live in the git-ignored `.env` (template: `.env.example`). Never hardcode paths in scripts.
`scripts/Load-Env.ps1` loads `.env` for PowerShell scripts; Python uses `python-dotenv`.

| Item | Location |
|---|---|
| FIFA 17 | `C:\Games\FIFA 17` (`FIFA17.exe`) |
| FIFA 16 | `C:\Program Files (x86)\by Decepticon\FIFA 16` |
| FRLT 16 V2 patch | installed over FIFA 16 from `C:\Users\remus\Downloads\FRLT 16 V2.zip` (29,239 loose files in `data/`, `dlc/`); gives `data\db\fifa_ng_db.db` + `-meta.xml` |
| Creation Master 16 / DB Master (GUI) | `C:\Program Files (x86)\Fifa Master\...` (read-only reference, never modify) |
| Custom CLIs (current builds) | `C:\Users\remus\fifa-tools\{CreationMaster16Cli,DbMasterCli,FrostyCLI}` (branch `audit-and-bh`, not pushed) |
| Older CLI builds / decompiled sources | `C:\Users\remus\dnSpy-net-win64\{CreationMaster16,DbMaster,FrostyToolsuite}` (do not delete) |
| texconv | `C:\Users\remus\tools\texconv\texconv.exe` (`TEXCONV_PATH`) |
| Python deps | `requirements.txt`: pandas, python-dotenv, deep-translator (Python 3.12) |

- **No injector needed.** A custom `CryptBase.dll` (95,744 bytes, not the 70,096-byte System32 one) already sits in `C:\Games\FIFA 17`, so the game loads it by itself (the README's Extreme Injector step is the alternative way). FIFA 16 is a data source only and is never launched.
- Not found on disk yet: `FrostyEditor.exe` / Frosty Mod Manager (`FROSTY_EDITOR_PATH` empty).
- GitHub repos of the user: `Gabarsolon/CreationMaster16Cli`, `DbMasterCli`, `FrostyCLI` (public). The user also runs `agyp` (`~/.local/bin/agyp.ps1`, profile `remus` exists): `agyp remus --dangerously-skip-permissions -p "<prompt>"` runs the Antigravity agent headless. Used once to audit and extend the CLIs.

## Custom CLIs
- **CmCli.exe** (`CreationMaster16Cli`): `export-kit|export-crests|export-player <db> <xml> <fifa_dir> <id> <out_dir>` (no `year` argument any more; `menu.py` was adapted), table export/import, and `regenerate-bh <fifa_dir_or_big>` (rewrites `.bh` indexes, makes `.bh.bak`, redirects loose files). `regenerate-bh` was run on the FIFA 16 folder on 2026-11-17: 26/26 files, 6498 loose files redirected, not yet confirmed in-game.
- **DbCli.exe** (`DbMasterCli`): `import-all <input_db> <schema_xml> <tsv_dir> <output_db>`, `import-table <db> <xml> <table> <tsv> <out_db>`, exports. Fixed: CRC was written over the input DB; auto-detects UTF-16LE/UTF-8; non-zero exit codes on error.
- **FrostyCmd.exe** (`FrostyCLI`, `FROSTYCLI_PATH`): `FIFA17 import-legacy|export-legacy|inject-legacy|import-team|launch-project`, `project-info`. Syntax is `<exe> FIFA17 <command> ...`. Headless fix for `FrostyMessageBox` (`Application.Current.MainWindow` is null). Run it from its own folder (it loads sibling DLLs). Tested only on a copy of the fbproject; `launch-project` never run.
- The agent that built these reported its own tests; only the build outputs and `regenerate-bh` on the real FIFA 16 folder were verified by a second pair of eyes.

## Rules
1. **Self-documentation (CRITICAL):** update this file after every discussion, discovery or workflow change. Also record what the user says (preferences, decisions, ideas).
2. Never edit Frostbite binaries (`.ebx`, `.res`, `.chunk`, `.fbproject`) directly. Use FrostyCmd.
3. Edit the TSV dumps in `db/`, not the `.db` files. Rebuild `.db` with DbCli.
4. Prefer extending `scripts/menu.py` / modules over scattered one-off scripts.
5. **DB + meta pairing (CRITICAL):** whenever `fifa_ng_db.db` or `eng_us.db` is regenerated, inject BOTH the `.db` and its `-meta.xml` into the `.fbproject` (`import-legacy`). A mismatch causes a silent ~500MB RAM crash at startup.
6. `CT_TeamName_<fifa17_teamid>` must be set in `LanguageStrings.txt` from `TeamName_Abbr15_<id>`.
7. UI legacy assets: crests `data/ui/imgAssets/crest{,16x16,32x32,50x50}/{light,dark}/l<teamid>.dds`; minikits `data/ui/imgAssets/kits/j{0,1,2}_<teamid>_0.dds`.
8. Pristine FIFA 17 baselines live in `db/original_tables/` (`fifa_ng_db.og.DB`, `fifa_ng_db-meta.og.XML`, `eng_us.DB`, `eng_us-meta.XML`). `import_team.py` always rebuilds the `.db` files from them.
9. Per user config: ask clarifying questions before architecture-changing work.
10. **Squad report after every team import (user rule, 2026-11-17):** when the pipeline is run on a team, finish by showing the user which players were chosen. Report: the kept players (FIFA 16 name, OVR, FIFA 17 slot, jersey) and the cut players (name, OVR), plus for every player the Transfermarkt data when available (club today or retired, peak and current market value, matched Transfermarkt name and match score), the swaps applied from `Team.player_swaps`, players Transfermarkt could not be matched for, and which cut players look relevant today so the user can decide on swaps. Do not apply Transfermarkt-based swaps silently: propose them, let the user confirm, then record them in `player_swaps`.

## Launching the game from the CLI (2026-11-17)
`FrostyCmd FIFA17 launch-project <project>` works: it writes `Mods/<profile>/FrostyCmdMod.fbmod` next to the exe, rebuilds `C:\Games\FIFA 17\ModData\Editor` (symlink `Data`) and starts `FIFA17.exe` (~10 s). Must run with `FIFA17_DIR` set (load `.env`) and cwd = FrostyCmd folder.
(Resolved) `FIFA17.exe` exiting after ~4 s with exit code -6 was an environment problem the user fixed by hand (cause unknown); direct launches work now. The later 0xC0000005 crashes with mods were the DbCli bug below. `stp-origin_emu.ini` and `unins000.dat` were rewritten today 14:34, so the game was (re)installed today; FIFA 17 files date from 2017, `CryptBase.dll` from 2026-08-17.

### ROOT CAUSE of the startup crash (found 2026-11-17 night)
Bisecting on the clean baseline project proved the crash was the database, not Poli's textures: even an unchanged export-all/import-all roundtrip through the GitHub `DbMasterCli` crashed the game (access violation 0xC0000005, ~5 s after start), while the original DB injected through the CLI ran fine. Cause: the decompiled `FifaLibrary14` in the GitHub repo had two writer bugs fixed only in the user's local copy: `FifaUtil.WriteNullPaddedString` used `w.Write(0)` (4 bytes) instead of `w.Write((byte)0)`, and `Table.cs` wrote `w.Write(0); w.Write(0);` instead of `w.Write(new byte[3])`. Every table came out 5 bytes too long (+745 bytes, 149 tables). Fixed in `DbMasterCli` branch `audit-and-bh`; an unchanged roundtrip now has exactly the original size (4,121,308 bytes). DbCli also writes a regenerated meta XML next to the output DB when the schema changed (`<out minus .DB>-meta.XML`); `import_team.py` copies the original XML first and lets DbCli overwrite it.
With the fixed DbCli the Poli test project (`Liga1Orange.test.fbproject`) started and stayed up: `FIFA17.exe` running with the window "FIFA 17", 2.2 GB, responding, >2 minutes. Kits, socks, crests and formation still need to be checked by eye in game.
Test method that works: `FrostyCmd FIFA17 launch-project <project>` (launches the game elevated via runas; the launcher does not return while the game keeps running, a hung launcher means the game survived), then poll `Get-Process FIFA17`. A crash shows within ~5 s.

## Findings and fixes (2026-11-17)

### Default formation always 4-2-3-1 (fixed in TSVs and in code)
`formationfullnameid` is the id of the string `Formation_FullName_<id>` (3 = "4-2-3-1 Wide", 7 = "4-3-3 Holding", 17 = "4-3-3 Flat", 11 = "4-4-2"...). The old code stored the `formationid` of the first FIFA 17 row with the same name instead. Result: 4-2-3-1 for several teams, Craiova 4-4-2 got 16 (= 4-2-3-1), Dinamo got 248 and Viitorul -1 (invalid). Fix in `db_operations.replace_formation_and_teamdata_from_fifa17_with_one_from_fifa16`: pick the id from FIFA 17 original rows with the same shape ("4-3-3 Halten" -> "4-3-3"), tie-break by nearest player offsets. Current ids: FCSB 16, Astra 3, CFR 4, Viitorul 7, Craiova 11, Dinamo 7, Poli 16. Not yet verified in-game.

### Poli Timisoara crashes the game: likely causes
1. **Duplicate primary key** `formations.formationid`: the old code copied `formationid` from FIFA 16. Poli got 721 (owned by team 113009), Dinamo 707 (owned by 112954). `formationid` is unique 1..739 in FIFA 17. Fixed: `formationid` is no longer copied and was restored from `db/original_tables/formations.txt` (Poli 306, Dinamo 248). Zero duplicates now.
2. **Wrong kit texture mapping in `import_poli.py`:** it renames tex_1 -> jersey, tex_2 -> shorts, tex_3 -> socks. Real FIFA 16 layout: tex_1 = jersey colour 1024x1024, tex_2 = 512x512 data map, **tex_3 = 1024x512 colour atlas (socks on top, shorts below)**, tex_4 = 512x256 data map, tex_0 = 256x256 (minikit). FIFA 17 wants shorts colour 1024x512 and socks colour 512x256. The Poli files in `assets/teams/poli` have shorts 512x512 and socks 1024x512 (wrong sizes). Fixed in `scripts/import_team.py` (see Poli status below).
3. Poli assets are named with the FIFA 16 team id (`*_130022_*`); `import-team` is supposed to map them to 1443 (unverified).
Still unproven: none of this was tested in-game. Crash diagnosis needs a validator and a crash logger (see plan).

### Socks (replaces the manual Photoshop step)
FIFA 17 socks = crop of the FIFA 16 atlas (tex_3) resized to 512x256. `scripts/kit_textures.py` does it (`python scripts/kit_textures.py <tex_3.png> <out.png> [--box x0 y0 x1 y1]`). Default box (208,12,820,186) was fitted on FCSB (error 14/255); CFR fits (244,0,784,150) (error 5.6/255), so the box depends on the kit template: always check the result visually. Poli previews generated and look right against Astra's. Not yet wired into the import pipeline.

### DDS formats
Existing assets: colour textures DXT5 (BC3, sRGB), `*_coeff` and `*_normal` DXT1 (BC1, linear), a few DX10/DXT3 legacy files. `ConvertPNGsToDDS.ps1` used BC3+sRGB for everything and `Invoke-Expression` (broke on paths with spaces). Fixed: `_coeff`/`_normal` -> `BC1_UNORM`, others `BC3_UNORM -srgb`, texconv from `TEXCONV_PATH`. Full mip chains are generated by texconv by default.

## Poli Timisoara status (2026-11-17, evening)
Run: `python scripts/import_team.py poli --skip-db` (TSVs already contain Poli with the formation fix). Result: exit 0.
- `scripts/validate.py` passed (no duplicate keys/orphans, valid `formationfullnameid`, jersey 1024x1024 / shorts 1024x512 / socks 512x256, all DXT5 with mips).
- `db/fifa_ng_db.DB` and `db/eng_us.DB` rebuilt by DbCli from `db/original_tables/`; DB + meta XML injected for both.
- `import-team 130022 1443` injected 12 textures into `content/character/kit/kit_1000/viborg_ff_1443/{home_0_0,away_1_0,goalie_home_2_0}` (jersey, shorts, socks, 3D crest). Warning "crest_1443_3_0_color not found" is harmless (no tertiary kit).
- UI crests (light/dark, 4 sizes) and minikits injected with `import-legacy`.
- Output is `Liga1Orange.test.fbproject` (git-ignored). The real `Liga1Orange.fbproject` is untouched. The user tests manually in game and copies the test project over the real one if it works. NOT verified in game.
- Baseline project = `git show 00ac879:Liga1Orange.fbproject` (before the broken Poli injection).
- `import_team.py` is generic: `python scripts/import_team.py <key> [--skip-db] [--skip-assets] [--skip-frosty]`. Without `--skip-db` it re-runs the player/team replacement on the current TSVs (names get appended to `playernames` again), so use `--skip-db` when the TSVs already contain the team.
- Assets per team: `assets/teams/<key>/f16_raw` (CmCli export + DDS) and `assets/teams/<key>/final` (FIFA 17 names, validated). Both are generated; the old flat Poli files in `assets/teams/poli` are obsolete.

### Poli Timisoara works in game (user confirmed 2026-11-17 night)
After the DbCli fix, the baseline-DB change and the minifaces, the user confirmed Poli runs correctly ("merge perfect") with the Romanian teams under Romania. The `Liga1Orange.test.fbproject` is the version that works; it has not been copied over `Liga1Orange.fbproject` yet.
- **Base databases = the ones inside the baseline project, not the pristine game files.** The pristine files lacked manual edits that are not in any TSV: the `leagues` row (Denmark Superliga, `countryid` 13 -> "Romania Liga 1 Orange", `countryid` 39) and one `career_lastnames` row. Rebuilding on the pristine DB made all Romanian teams show Denmark at Kick-Off. `import_team.py` now exports the baseline project's `fifa_ng_db.db`, `eng_us.db` (+ meta XMLs) with `FrostyCmd export-legacy` and imports the TSV tables on top.
- **Minifaces** (2D head photos): `data/ui/imgAssets/heads/p<FIFA17 playerid>.dds`, 128x128 DXT5, one mip (`texconv -m 1`, handled for files named `p<digits>.png` in `ConvertPNGsToDDS.ps1`). Source is the FIFA 16 file `data/ui/imgassets/heads/p<FIFA16 playerid>.dds`, exported with the new `CmCli export-photo <db> <xml> <fifa_dir> <player_id> <out_dir>` (exit code 2 = no photo). The FIFA 17 id is the id of the replaced Danish player; pairs are matched by name text in `db_operations.player_pairs`. The baseline project already contains 136 minifaces for the six earlier teams. Poli: 22 of 23 have a photo.
- **Players without a FIFA 16 photo** (Poli: FIFA 16 ids 50273 and 50253 = Mailat; FIFA 17 ids 189512 and 215686): the FIFA 17 slot would keep the face of the replaced Danish player. Rule (user decision 2026-11-17): they get the neutral silhouette `assets/generic/notfound_head.png` (128x128, taken from the user's `assets/teams/viitorul/notfound_0.dds`); `import_team.py` does this automatically when `CmCli export-photo` finds no photo. Do NOT use Transfermarkt portraits for faces: they are copyrighted photos and are recent (Mailat's was uploaded 2025-10-31, an adult with a beard, not the 2016-17 look; the number after the dash in the image URL is the upload Unix timestamp). Hand-made faces are still possible via `assets/teams/<key>/heads_custom/p<FIFA17 playerid>.png` (copied over the exported photos).
- `import_team.py` order: TSV (unless `--skip-db`) -> CmCli kit/crest/photo export -> PNG to DDS -> validate -> clean baseline project -> export base DBs from it -> DbCli import -> inject DBs, `import-team`, UI crests/minikits, minifaces.
- Other earlier teams were done by hand (names such as `alibec.png` in `assets/teams/astra`) and were not re-run through this pipeline.
- Liga 1 in FIFA 16 + FRLT (`leagueid` 83, 14 teams): Steaua 106000, Botosani 130020, CS U Craiova 130021, Poli Timisoara 130022, CFR 130023, Viitorul 130024, Pandurii 130025, Astra 130026, Dinamo 130027, Poli Iasi 130028, Voluntari 130030, Concordia Chiajna 130031, Gaz Metan 130039, ASA Targu Mures 130067. Done: Steaua, Craiova, Poli Timisoara, CFR, Viitorul, Astra, Dinamo. Remaining: the other 7 (issues #12-#18).

### CmCli fix needed for FIFA 16 + FRLT
The repo version of `export-kit|export-crests|export-player` never called `FifaEnvironment.LoadLists`, so `Teams` was null. Calling the full `LoadLists()` crashes in `CompobjList.CollectDescriptions` (FRLT), so the CLI now loads every list except `FifaTournament`. Build: `dotnet build -c Debug -p:Platform=AnyCPU` in `CmCli/`. Crest export names changed: the 256x256 crest is `team_<id>_crest_standard.png` (old build: `crest_light_256x256`).

### Imported details that are NOT copied from FIFA 16
- `teams`: only the 9 `teamcolor*` columns and `foundationyear` are copied. Not copied (still FIFA 17 values): `overallrating`, `attackrating`, `midfieldrating`, `defenserating` (+ `matchday*`), `domesticprestige`, `internationalprestige`, `transferbudget`, `latitude`, `longitude`, `utcoffset`, `balltype`, `jerseytype`, `trait1`, `rivalteam` (id), `teamname`, tactics columns (`defteamwidth`, `busdribbling`, ...; partially handled via `defaultteamdata`).
- `teamkits`: only `*color*` columns copied. Not copied: `numberfonttype`, `jerseynamefonttype`, `shortsnumberfonttype`, `jerseybacknameplacementcode`, `shortsnumberplacementcode`, `jerseycollargeometrytype`, `hasadvertisingkit` (FIFA 16 font ids differ from FIFA 17; use `change_kit_font_type`).
- Players: names, attributes, kit numbers and link data are copied. See player-count note below.
- Decide per column whether to copy before changing code.

### Players: how they are chosen (and the plan)
**Current rule (implemented): overall rating only.** `replace_players_from_fifa16_with_players_from_fifa17` sorts the FIFA 16 squad by `overallrating` descending and pairs it with the FIFA 17 squad of the replaced Danish team; if the FIFA 16 squad is bigger the lowest-rated players are dropped, if it is smaller the extra FIFA 17 links are deleted from `teamplayerlinks` (rows stay in `players`). Transfermarkt is NOT used yet. Example, Poli: 31 players in FIFA 16, 23 slots, dropped (OVR 51-56): Razvan Rus, Sebastian Mailat, Harald Fridrich, Lucian Oprea, Bogdan Straut, Cristian Padurariu, Radu Motreanu, Mario Contra.
**User's intended rule (not implemented, decided 2026-11-17):** when a squad does not fit, prefer players who stayed relevant after that season (still playing / reached a good level later, "who made it to today"), not just the highest OVR in 2016. Use OVR as the base ordering and the Transfermarkt API as a second signal, e.g. peak or current market value and career length. `https://github.com/felipeall/transfermarkt-api` (async Python SDK, `pip install transfermarkt-api`, Python 3.12/3.13; public instance is limited to 2 requests per 3 s; it uses Transfermarkt's internal JSON API which can change; the data is under Transfermarkt's terms, not the MIT licence). Endpoints: `/clubs/search/{name}`, `/clubs/{id}/players`, `/players/search/{name}`, `/players/{id}/market_value`, `/players/{id}/profile`. Matching FIFA 16 names to Transfermarkt players (diacritics, Steaua/FCSB naming) will need fuzzy matching and a manual override list. Also consider adding new `players` rows instead of dropping when the squad is bigger.

### Transfermarkt check of Poli's squad (2026-11-17) and player swaps
Ran `transfermarkt-api` (SDK 5.0.0 in a scratch venv, `max_concurrency=2`) on Poli: Transfermarkt club id `36590` ("ACS Poli Timisoara (2012 - 2021)"), `club_players(season_id="2016")` returns 44 players with their club today, then `player_market_value(id)` for the peak and current value. Matching FIFA 16 names to Transfermarkt used diacritic-stripped fuzzy matching (ratio >= 0.78); 27 of 31 matched, Ignea, Lazar, Novak, Motreanu did not.
Result: of the 8 players cut by the OVR ranking only **Sebastian Mailat** clearly mattered (peak 1.2 M EUR in 2025, 1 M EUR now, FC Botosani); Mario Contra and Cristian Padurariu are small (<=200k); most of the 23 kept players are retired. Decision (user): add Mailat. `Team.player_swaps = [(out_f16_id, in_f16_id)]` in `scripts/constants.py` hands the FIFA 17 slot of `out` to `in` after the OVR import (`db_operations.apply_player_swaps`); the incoming player takes the outgoing player's jersey number (FIFA 16 data can have a number twice in one squad). Poli: `(50311, 50253)` = Emanuel Vasi (OVR 58, retired, peak 50k) -> Sebastian Mailat (FIFA 16 jersey 29 was already taken). To re-run: `python scripts/import_team.py poli` re-pairs from scratch and appends names again, so for a TSV that is already imported use `--skip-db` and apply a new swap by calling `apply_player_swaps` then `save_tsv`.
Idea for the other teams: run the same Transfermarkt comparison (club search by name, squad, market value history) for each squad that does not fit, rank by OVR first and list the cut players with peak/current value, then let the user pick swaps.

### Script audit (hand-written scripts)
- `dataframes.py` loads ~20 tables at import (slow, prints column lists) and `db_operations.py` ends with a module-level debug `print` of all `teamkits` columns.
- `save_tsv()` writes `formations` twice. `constants.py` mixes classes, a team dict and loose magic ids (`nitza`).
- (old) `import_poli.py` was hard-wired to Poli, ran `git checkout Liga1Orange.fbproject` (discards uncommitted work) and needed missing `clean_from_game_*` files. Replaced by `scripts/import_team.py`.
- `menu.py` and `import_poli.py` import each other's helpers; `menu.py` pulled in `year` for CmCli (removed).
- Previous history is in git (170 commits): per-team manual work for FCSB, CFR, Viitorul, Craiova, Dinamo, Astra (kits/hotspots/fonts/logos/socks done by hand in Photoshop, `.psd` kept in `assets/teams/fcsb`).

## Issue #5: 3D league logo (root cause of the FBX corruption found 2026-11-18)
Goal: replace the 3D logo of the Danish league with a Liga 1 Orange one. In FIFA 17 each league has `content/character/leaguelogo/<country>_<leagueid>/leaguelogo_<id>` (ObjectBlueprint) plus `_mesh` (RigidMeshAsset -> RES MeshSet), `_color`, `_coeff`, `_normal` (textures). Danish league: `content/character/leaguelogo/denmark_1/leaguelogo_1_mesh` (1 LOD, 2 sections: `logo_mat` 6051 vertices / 5317 triangles and an unnamed one with 3235 vertices; flat extruded "alka SUPERLIGA" text, bounding box about 0.94 x 0.26 x 0.08). FIFA 17 league 1 is the slot our mod uses for Liga 1 Orange.

**Root cause of "Frosty corrupts the imported FBX, even the original":** in `FrostyToolsuite/Plugins/MeshSetPlugin/Resources/MeshSet.cs` the `MeshSetSection` reader for Fifa17/Fifa18/Madden19 reads three 8-byte pointers after the bone-list pointer, but the writer (`Process`) has only `// @todo` there and writes nothing, so every saved section is 24 bytes short and the resource cannot be read back (`ArgumentOutOfRangeException: Stream length must be non-negative...` in `MeshSetSection..ctor`). Fix (patched copy, not applied to the Frosty source tree): write three `(ulong)0` in that block.

Tools (local only, in `C:/Users/remus/fifa-tools/FrostyMeshCli`, NOT pushed: it compiles the GPL Frosty `MeshSetPlugin` sources from the dnSpy tree plus two patched copies, see `patch_sources.py`):
- `FrostyMeshCli.exe FIFA17 export-mesh <ebx> <out.fbx|obj> [project|-] [version] [units] [binary|ascii|obj]`
- `FrostyMeshCli.exe FIFA17 import-mesh <project> <ebx> <in.fbx>`
- `FrostyMeshCli.exe FIFA17 mesh-info <ebx> [project]`
- Needs `FIFA17_DIR`; run it from its own folder (Profiles/Plugins/ThirdParty/Caches copied from FrostyCmd's bin). Build: `dotnet build FrostyMeshCli.csproj -c "Developer - Debug" -p:Platform=x64`. `MeshSetPlugin` cannot be built from the dnSpy tree with the dotnet CLI (net48 vs net481 projects, C++ FrostyHash).

Verified: export original -> import -> read back works with the patched writer (the unpatched one fails on read-back). FBX candidates in `assets/league`: `leaguelogo_1_mesh.fbx` (2006/2012/2013) re-import fine; `untitled.fbx` is the Danish logo at 100x scale (not Liga 1); `Liga_I_logo.fbx` and the ImageToStl extrusion are rejected with `FBXImportInvalidLodCountException` (no LOD structure). The importer also makes the unnamed second section a copy of the first (6051 vertices instead of 3235); the effect in game is not checked.

Open work: build the Liga 1 logo mesh (extrude the silhouette of `assets/league/Liga_I_logo.png/svg`, planar UVs, normals/tangents) in the FBX structure the importer expects (idea: export an ASCII FBX of the original and replace its geometry arrays, keep node/material/LOD names), import it into `Liga1Orange.test.fbproject`, replace the `_color/_coeff/_normal` textures if the logo needs its own colours, then check in game (where the 3D league logo is shown in game is not known yet, ask the user). FIFA 16 + FRLT only has the Liga 1 trophy (`data/sceneassets/trophy/trophy_83.rx3`, a cup, exported with `CmCli export-obj <rx3> <obj> float32`), not a logo mesh.

## Proposed project structure (not applied, needs user OK)
```
liga1/                 python package (replaces scripts/*.py)
  config.py            .env loading, paths
  tables.py            lazy TSV loading/saving (no work at import)
  tools/{cmcli,dbcli,frosty,texconv}.py   subprocess wrappers
  importers/{players,teams,formations,kits}.py
  validate.py          PK/FK checks, meta/db pairing, texture size checks
  cli.py               menu
teams.toml             team key -> fifa17 id, fifa16 id, year, city (replaces constants.py)
assets/teams/<key>/{raw_f16,generated,final}/
data/{fifa17_clean,fifa16,working}/        replaces db/
releases/              .fbmod (not in git root)
```
Also: move `.fbmod`, `.zip`, `legacy_dump.txt` out of git history/GitHub Releases, one issue per team with a checklist, milestones v0.1/v0.2/v0.3.

## Plan (agreed order)
1. DONE: setup (requirements, `.env`, no hardcoded paths, AGENTS/CLAUDE docs, CLIs rebuilt, FRLT installed, BH regenerated).
2. NEXT: `validate.py` (PK uniqueness, FK integrity, ffnid exists, db/meta pairing, DDS size/format per target slot, all assets present).
3. DONE: `import_team.py` (texture mapping, socks, generic team, test project). NEXT: user tests Poli in game; if it still crashes, debug with the validator and the crash-logger idea.
4. Generic one-team import from `teams.toml`; then the remaining teams (issues #9, #12-#18; #9 Poli is open but not truly done).
5. Crash logger (vectored exception handler DLL injected at runtime, map RVA in Ghidra; pyghidra + Ghidra MCP available; FIFA 17 may have Denuvo so avoid static exe patching).
6. Screenshot QA: scripted Kick-Off walk-through (SendInput / virtual gamepad via vgamepad, `PIL.ImageGrab`), Claude reviews screenshots; wait on image changes, not fixed sleeps.
7. Later epics: formations #24, flags/banners #22, translation #6, Romanian commentary #2, loans #20, custom heads #21.

## GitHub
Open issues: #24 formations, #23 presentation page, #22 flags/banners, #21 custom heads, #20 loans, #18 Poli Iasi, #17 Botosani, #16 Gaz Metan, #15 Pandurii, #14 ASA Tg. Mures, #13 Voluntari, #12 Chiajna, #9 Poli Timisoara, #6 translate LanguageStrings, #5 3D league logo, #3 vgmstream, #2 commentary. The user also uses a Kanboard/GitHub project board; `gh` needs `gh auth refresh -s read:project` to read it.

## Team import workflow
1. Add the team to `liga1orange_teams` in `scripts/constants.py` (FIFA 17 id of a Danish team, FIFA 16 id, foundation year, city).
2. DB: team details (colours, year, strings), formation/teamdata/teamsheets, players (sorted by OVR), TSV save.
3. `CmCli export-kit` / `export-crests` into `assets/teams/<team>/`, `ConvertPNGsToDDS.ps1`, rename to FIFA 17 names (see texture layout above).
4. `DbCli import-all` / `import-table` from pristine FIFA 17 files, inject `.db` + `-meta.xml` for `fifa_ng_db` and `eng_us`.
5. `FrostyCmd FIFA17 import-team <f16id> <f17id> <dir> <fbproject>` and `import-legacy` for UI crests/minikits.
6. `FrostyCmd launch-project`, test in Kick-Off before Career Mode.
