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

echo  [INFO] Setting up virtual environment...
if not exist "venv\" (
    python -m venv venv
    if %errorlevel% neq 0 (
        color 0c
        echo.
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit
    )
)

call venv\Scripts\activate.bat

echo  [INFO] Checking dependencies...
python -m pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    color 0c
    echo.
    echo  [ERROR] Failed to install dependencies.
    echo  [TIP] Make sure C++ Build Tools are installed for llama-cpp-python.
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
