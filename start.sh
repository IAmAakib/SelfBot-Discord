#!/bin/bash

# Discord Selfbot Launcher

# CachyOS detection
if grep -qi "cachyos" /etc/os-release 2>/dev/null; then
    echo " [INFO] CachyOS detected: Using optimized build environment."
fi

echo ""
echo " =============================================================================="
echo "                          DISCORD SELFBOT LAUNCHER"
echo " =============================================================================="
echo ""

echo " [INFO] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo " [ERROR] Failed to create virtual environment."
        echo " [TIP] Make sure python3-venv is installed."
        read -p "Press any key to exit..." -n1 -s
        echo ""
        exit 1
    fi
fi

source venv/bin/activate

echo " [INFO] Checking dependencies..."
python3 -m pip install -r requirements.txt > pip_install.log 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo " [ERROR] Failed to install dependencies."
    echo " [TIP] Please check pip_install.log for detailed error messages (e.g. missing build tools like gcc/g++)."
    cat pip_install.log
    read -p "Press any key to exit..." -n1 -s
    echo ""
    exit 1
fi
echo " [INFO] Dependencies check passed."
echo ""

echo " [INFO] Starting Bot..."
echo " =============================================================================="
echo ""

export PYTHONDONTWRITEBYTECODE=1
python3 -O main.py

echo ""
echo " =============================================================================="
echo " [WARN] Bot has stopped or crashed."
echo " =============================================================================="
read -p "Press any key to exit..." -n1 -s
echo ""
