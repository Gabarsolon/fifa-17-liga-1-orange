@echo off
rem Reads GUI tool paths from .env (FROSTY_EDITOR_PATH, CREATION_MASTER_PATH, DB_MASTER_PATH).
for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do (
    if /i "%%A"=="FROSTY_EDITOR_PATH" set "FROSTY_EDITOR_PATH=%%B"
    if /i "%%A"=="CREATION_MASTER_PATH" set "CREATION_MASTER_PATH=%%B"
    if /i "%%A"=="DB_MASTER_PATH" set "DB_MASTER_PATH=%%B"
)
if defined CREATION_MASTER_PATH start "" "%CREATION_MASTER_PATH%"
if defined DB_MASTER_PATH start "" "%DB_MASTER_PATH%"
if defined FROSTY_EDITOR_PATH start "" "%FROSTY_EDITOR_PATH%"
