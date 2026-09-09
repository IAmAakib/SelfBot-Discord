@echo off
title Discord Selfbot Launcher
mode con: cols=80 lines=20
color 0b
cls

echo.
echo  ==============================================================================
echo                           DISCORD SELFBOT LAUNCHER
echo  ==============================================================================
echo.

echo  [INFO] Checking dependencies...
python -m pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    color 0c
    echo.
    echo  [ERROR] Failed to install dependencies.
    echo  [TIP] Make sure Python is installed and added to PATH.
    pause
    exit
)
echo  [INFO] Dependencies check passed.
echo.

echo  [INFO] Starting Bot...
echo  ==============================================================================
echo.

python main.py

color 0c
echo.
echo  ==============================================================================
echo  [WARN] Bot has stopped or crashed.
echo  ==============================================================================
pause
