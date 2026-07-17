# AI Agents Guide for fifa-17-liga-1-orange

This file provides guidelines and instructions for AI agents working on this project.

## Context
This project is a mod for FIFA 17 that adds the Romanian Liga 1 Orange (2016/2017 season) by replacing the Danish league. It heavily relies on Frosty Editor and Frosty Mod Manager, but database edits and asset generation are assisted by a custom Python CLI (`scripts/menu.py`) and a C# CLI tool (`CmCli.exe`).

## Important Paths and External Tools
All external tool paths and game directory paths must be managed through a local `.env` file in the root directory. Hardcoded paths inside the scripts should be avoided.

- **Game Directories**: The project is strictly about importing assets from **FIFA 16** and replacing them in **FIFA 17**. Other game versions (like FIFA 14) are not supported. Example `.env` properties: `FIFA16_DIR`, `FIFA17_DIR`.
- **Python Scripts**: The `scripts/` directory contains tools to edit `.tsv` database files. Start from `scripts/menu.py`.
- **CmCli.exe (CreationMaster16 CLI)**: A custom standalone C# CLI wrapper built on top of the decompiled Creation Master 16 source. Used for extracting FIFA 16 `.rx3` graphical assets (kits, crests, player faces). Configure `CMCLI_PATH` and the decompiled source directory `CM16_DECOMPILED_DIR` in `.env`.
- **DbCli.exe (DbMaster CLI)**: A custom CLI wrapper built from the decompiled DB Master. Used for exporting and importing `.db` table data directly from/to the TSVs. Configure `DBCLI_PATH` and `DBMASTER_DECOMPILED_DIR` in `.env`.
- **FrostyCli.exe (Frostbite CLI)**: A custom CLI wrapper built on top of the Frosty Editor source code. Used for interacting with the `.fbproject` and extracting/inspecting Frostbite engine modifications. Configure `FROSTYCLI_PATH` and `FROSTY_EDITOR_DECOMPILED_DIR` in `.env`.
- **Database TSVs**: Located in the `db/` directory. Be careful when updating these TSVs programmatically. Pay attention to `teamid`, `playerid`, and `leagueid` relations.
- **Conversion Scripts**: The `scripts/ConvertPNGsToDDS.ps1` script is used to batch convert PNGs (exported by CmCli) into `BC3_UNORM` `.dds` format using `texconv`, preparing them for Frosty Editor injection.

## Project Automation Workflow
- The Python CLI (`scripts/menu.py`) orchestrates the pipeline. It features a "1-Click Full Team Import" that automatically:
  1. Rewrites database entries for teams and players
  2. Extracts FIFA 16 textures using `CmCli`
  3. Instantly converts the extracted textures to `.dds` using `ConvertPNGsToDDS.ps1`
  4. Automatically injects legacy textures into the `.fbproject` using `FrostyCmd inject-legacy`
- The project can then be immediately launched from the command line using `FrostyCmd launch-project`.

## AI Agent Guidelines
1. **Self-Documentation (CRITICAL)**: You MUST update this `AGENTS.md` file after every discussion and after every new project discovery or workflow modification. This ensures future agents have an up-to-date context of the repository's state.
2. **Never edit Frostbite binary files directly**: Files like `.ebx`, `.res`, `.chunk`, or `.fbproject` should not be modified through code directly unless you specifically know the Frostbite serialization format.
2. **Work with TSV Database Dumps**: Instead of trying to parse the `.db` files natively, edit the `.tsv` representations found in `db/`. The workflow expects these TSVs to be modified and then imported manually by the user via DB Master.
3. **Use the Python CLI**: Expand `scripts/menu.py` to add new features or automations rather than creating standalone scattered scripts.
4. **Interact with Custom CLIs**: 
   - **CmCli**: Use this to retrieve legacy assets from FIFA 16 (kits, crests, player textures).
   - **DbCli**: Use this for automated database table dumps and imports to/from `.tsv` files.
   - **FrostyCli**: Use this to query modified files in the `.fbproject` programmatically.
5. **Aesthetics & Documentation**: Keep `README.md` and documentation files updated whenever you introduce a new script or workflow element.

## Team Import Workflow Plan
Here is the step-by-step plan for importing a team from FIFA 16 and replacing one in FIFA 17:
1. **Identify Target Teams**: Find the FIFA 16 Team ID of the team to import and select a FIFA 17 Team ID (typically from the Danish League) to replace.
2. **Update Constants**: Add the new team mapping to liga1orange_teams in scripts/constants.py with its foundation year and city name.
3. **Database Import**: Use scripts/import_poli.py (or the menu's 1-click import) to:
   - Replace team details (colors, IDs, foundation year).
   - Replace formation and team data.
   - Replace player rosters (names, attributes, kit numbers).
   - Save changes to TSV files in the db/ folder.
4. **Asset Extraction**: The script will automatically trigger CmCli.exe to extract kits, crests, and optionally player faces from the FIFA 16 database, placing them in ssets/teams/<team_name>/.
5. **Texture Conversion**: Extracted .png assets are automatically converted to Frosty-compatible .dds formats using ConvertPNGsToDDS.ps1.
6. **Frostbite Injection**: Automatically inject the newly generated `.dds` assets using `FrostyCmd inject-legacy`.
7. **Database Import**: Use `DbCli.exe` or DB Master to import the modified TSV files into the actual `.db` file for the mod.
8. **Final Build**: Automatically build and launch the mod through `FrostyCmd launch-project`.
