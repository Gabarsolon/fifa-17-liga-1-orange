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

## 📌 Features

- ✅ Romanian Liga 1 Orange 2016/2017 in FIFA 17 (replaces Denmark league)  
- ✅ Correct squads & formations  
- ✅ Real kits  
- ✅ Logos & badges  
- ✅ Updated league structure
- ⬜ Custom scoreboards 
- ⬜ Romanian commentary
- ⬜ Romanian language in the UI

---

## 📷 Screenshots

| | |
|---|---|
| ![](images/screenshot1.png) | ![](images/screenshot2.png) |

---

## 📦 Installation

1. Install **FIFA 17**
2. Install **Frosty Mod Manager**
3. Import the `.fbmod` file
4. Apply and launch the game

---

## 🛠 Tools Used

- Frosty Editor  
- Frosty Mod Manager  
- DB Master
- Creation Master 16
- Photoshop 
- Blender
---

## 📂 Project Structure
```
```text
.
├── assets/                  # Game assets
│   ├── league/              # League-specific assets
│   └── teams/               # One folder per team with faces, kits, logos
│
├── db/                      # Database files (TSV exports from fifa_ng_db.DB)
│   ├── fifa-16/             # Reference tables from FIFA 16
│   └── original_tables/     # Backup of original FIFA 17 tables
│
├── scripts/                 # Python & Windows scripts
│                            # Used for DB management & image processing
│
├── Liga1Orange.fbmod        # Exported Frosty mod
└── Liga1Orange.fbproject    # Frosty Editor project file
```


---

## 🎮 Compatibility

- Game Version: FIFA 17 (PC)
- Mode: Career Mode / Kick-Off
- Platform: Windows

---

## 🛠 Troubleshooting

If something isn’t working correctly, check the solutions below.

### 🚫 Mod Not Showing in Game

- Make sure the mod is applied in Frosty Mod Manager  
- Launch the game through Frosty, not directly from Origin/EA App  
- Check for conflicts with other installed mods  

---

### 💥 Game Crashes on Launch

- Use [Extreme injector](https://github.com/master131/ExtremeInjector) to inject [cryptbase.dll](https://www.dll-files.com/cryptbase.dll.html) when the game launches. You can use a helper script for this (place in game dir) [scripts\extreme_injector_loop.ps1](scripts\extreme_injector_loop.ps1)
- Disable other mods and test again  
- Delete the `ModData` folder and let Frosty regenerate it  
- Run Frosty as Administrator  

---

### 👕 Kits / Logos Not Appearing

- Check if team IDs match correctly in database tables  
- Verify kit assignments in `teamkits` table  
- Make sure texture files are properly imported  
- Clear ModData and rebuild  

---

### 📊 Database Changes Not Applying

- Confirm you saved and exported the mod properly  
- Check table relations (teamId, playerId, leagueId)  
- Ensure no duplicate IDs exist  
- Test changes in Kick-Off before Career Mode  

---

### 🐌 Performance Issues

- Remove unnecessary high-resolution textures  
- Disable other heavy mods  
- Clear ModData folder  

---

If the issue persists:

1. Open an Issue  
2. Describe the problem clearly  
3. Include screenshots  
4. Mention your FIFA 17 version and Frosty version  

---


## 🤝 How to Contribute

Contributions are welcome! If you’d like to improve this mod, follow the steps below.

### 🔧 Ways You Can Help

- Fix incorrect player data
- Update squads / transfers
- Improve kits or textures
- Fix player's faces
- Improve banners, flags, or UI elements
- Report bugs or database issues

#### Don't forget to check the issues page!

### 🧰 Preparing Your Workspace

Before making changes, make sure your environment is properly set up.

#### 1️⃣ Requirements

- FIFA 17 (PC)
- FIFA 16 (PC)
- Frosty Editor
- Frosty Mod Manager
- Creation Master 16
- DB Master
- Python 3.x (for scripts)
- Photo editor
- Git
- [FRLT V2 Patch](https://dl.fifa-infinity.com/fifa-16/frlt-16-v2/) for FIFA 16 (used for importing liga 1 data)

#### 2️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/fifa-17-liga-1-orange.git
cd fifa-17-liga-1-orange
```

#### 3️⃣ Set Up Frosty
- Open Frosty Editor
- Load your FIFA 17 installation
- Open the Liga1Orange.fbproject file
- Make sure the project loads without errors

#### 4️⃣ Database Workflow
- TSV files are located in db/
- Edit tables carefully (respect IDs and relations)
- Run [menu.py](scripts\menu.py) for automation functions 
- Import the saved TSV's in DBMaster
- Import saved DB files in Frosty Editor

#### 5️⃣ FIFA 16 FRLT V2 importing 
- Download the [FRLT V2 Patch](https://dl.fifa-infinity.com/fifa-16/frlt-16-v2/) and add it to fifa 16
- Use CreationMaster16 for reading and exporting data



### 📥 Submitting Changes

1. Create a new branch 
2. Create a pull request with your changes 

Please describe clearly what you changed and include screenshots if relevant.

### 🐛 Reporting Issues

If you find a bug:

- Open an Issue
- Describe the problem
- Include steps to reproduce
- Attach screenshots if possible

---

### 📋 Contribution Guidelines

- Keep database structure consistent
- Do not overwrite unrelated tables
- Test changes in-game before submitting
- Use clear commit messages

---

Thank you for helping improve the project! ⚽

## ⚠ Disclaimer

This is a fan-made project.  
All rights belong to EA Sports & EFET team for FRLT V2 patch

---

## 👤 Author

Created by **Gabarsolon**

If you like the project, give it a ⭐

---