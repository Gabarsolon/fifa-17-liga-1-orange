@AGENTS.md

# Claude Code notes
- The user writes Romanian, often in short mid-task messages. Answer in Romanian.
- Ask before architecture changes (global rule). The "Proposed project structure" in AGENTS.md is a proposal only.
- Update AGENTS.md whenever the user states a decision, preference or idea, and after every finding.
- Before running anything that writes into a game folder, `Program Files`, or `Liga1Orange.fbproject`: make a backup or work on a copy, and say so. `regenerate-bh` already writes `.bh.bak` files.
- No game, injector or Frosty GUI is available to the agent: in-game results must be reported as unverified until the user tests.
- Screenshots and temp files go to the scratchpad directory, not the repo.
- After running the import pipeline on a team, always end with the squad report described in AGENTS.md rule 10 (chosen/cut players with OVR and Transfermarkt data). Propose swaps, do not apply them without the user's OK.
- Players without a FIFA 16 miniface get the generic silhouette `assets/generic/notfound_head.png` (automatic in `import_team.py`). Never use Transfermarkt or other scraped portraits as faces: copyright, and they show the player today, not in 2016-17. Use Transfermarkt only for data (squad, market value, current club).
