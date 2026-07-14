# AI Agents Guide for fifa-17-liga-1-orange

This file provides guidelines and instructions for AI agents working on this project.

## Context
This project is a mod for FIFA 17 that adds the Romanian Liga 1 Orange (2016/2017 season) by replacing the Danish league. It heavily relies on Frosty Editor and Frosty Mod Manager, but database edits and asset generation are assisted by a custom Python CLI (`scripts/menu.py`) and a C# CLI tool (`CmCli.exe`).

## Important Paths and External Tools
- **Python Scripts**: The `scripts/` directory contains tools to edit `.tsv` database files (exported from `fifa_ng_db.DB`). Start from `scripts/menu.py` to navigate team and player operations.
- **CmCli.exe (CreationMaster16 CLI)**: This is a standalone C# CLI used for extracting FIFA 16 `.rx3` graphical assets (kits, crests, player faces). It allows extracting textures from FIFA 16 for injection into FIFA 17. The executable is currently located at: `C:\Users\remus\dnSpy-net-win64\CreationMaster16\CmCli\bin\Debug\CmCli.exe`.
- **Database TSVs**: Located in the `db/` directory. Be careful when updating these TSVs programmatically. Pay attention to `teamid`, `playerid`, and `leagueid` relations.

## AI Agent Guidelines
1. **Never edit Frostbite binary files directly**: Files like `.ebx`, `.res`, `.chunk`, or `.fbproject` should not be modified through code directly unless you specifically know the Frostbite serialization format.
2. **Work with TSV Database Dumps**: Instead of trying to parse the `.db` files natively, edit the `.tsv` representations found in `db/`. The workflow expects these TSVs to be modified and then imported manually by the user via DB Master.
3. **Use the Python CLI**: Expand `scripts/menu.py` to add new features or automations rather than creating standalone scattered scripts.
4. **Interact with CmCli**: When you need to retrieve legacy assets from FIFA 16 (kits, crests, player textures), automate the usage of `CmCli.exe`. 
5. **Aesthetics & Documentation**: Keep `README.md` and documentation files updated whenever you introduce a new script or workflow element.
