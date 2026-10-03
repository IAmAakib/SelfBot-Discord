# SelfBot

Feature-rich Discord selfbot with local AI, TUI dashboard, and 60+ commands. 

## Key Features

- **TUI Dashboard**: Rich console interface for tracking commands and bot status.
- **Local AI**: Integration with `llama-cpp-python` for local AI command processing.
- **Multiple Accounts**: Token management for switching between multiple Discord accounts.
- **Extensive Commands**: 60+ commands categorized into fun, utility, tools, AI, media, and moderation.

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: `discord.py-self` (for interacting with Discord as a user account)
- **AI Processing**: `llama-cpp-python`
- **Dashboard**: `rich`
- **Configuration**: `pyproject.toml`, `python-dotenv`

## Prerequisites

- Python 3.10 or higher
- Discord user token
- C++ build tools (for compiling `llama-cpp-python`)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/IAmAakib/SelfBot-Discord
cd SelfBot-Discord
```

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

| Variable | Description | Example |
|---|---|---|
| `DISCORD_TOKEN` | Your Discord user token | `Nzc2Mjk0...` |

### 3. Configuration

Edit `config.json` to customize the bot prefix:

```json
{
    "prefix": "."
}
```

### 4. Start the Bot

The provided launcher scripts will automatically create a virtual environment, install dependencies, and start the bot.

**Linux / macOS:**
```bash
./start.sh
```

**Windows:**
```bat
start.bat
```

Or manually:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
python main.py
```

## Architecture

### Directory Structure

```
├── core/                 # Core modules (config_manager, token_manager, tui)
├── cogs/                 # Command modules (afk, ai, fun, media, moderation, sniper, status, tools, utility)
├── models/               # Local AI models (.gguf)
├── main.py               # Main bot entrypoint and event handlers
├── config.json           # Bot configuration (prefix, etc.)
├── pyproject.toml        # Project metadata and linting config
├── requirements.txt      # Python dependencies
├── start.sh              # Unix startup script
└── start.bat             # Windows startup script
```

### Key Components

**TUI Dashboard (`core/tui.py`)**
- Utilizes the `rich` library to draw a live updating dashboard in the console.
- Tracks command usage, logs, and cog loading status.

**Token Manager (`core/token_manager.py`)**
- Interactively prompts the user to select or add new Discord tokens on startup.
- Stores tokens securely in `tokens.json`.

**Cogs (`cogs/`)**
- Modular command loading.
- Includes local AI capabilities (`ai.py`) loading models from the `models/` directory.

## Environment Variables

### Required

| Variable | Description | How to Get |
|---|---|---|
| `DISCORD_TOKEN` | Discord user token | Open Discord web -> F12 -> Network -> Find `authorization` header |

## Available Scripts

| Command | Description |
|---|---|
| `./start.sh` | Run the bot on Linux/macOS |
| `start.bat` | Run the bot on Windows |
| `python main.py` | Run the bot manually |

## Troubleshooting

### Build Failures for llama-cpp-python

**Error:** `Failed to build llama-cpp-python`

**Solution:**
Ensure you have C++ build tools installed.
- **Windows:** Install Visual Studio Build Tools.
- **Linux:** `sudo apt install build-essential python3-dev`
- **macOS:** `xcode-select --install`

### Invalid Token

**Error:** `Invalid Token. Check your token or re-add the account.`

**Solution:**
Ensure you are using a user token, not a bot token. Your token should be placed in `.env` or added via the interactive CLI prompt.

## Disclaimer & Limitations

> [!WARNING]
> Using a selfbot is against the Discord Terms of Service. This project is for educational and hobby purposes only. Use at your own risk.

This is a hobby project. It may or may not receive further updates. No support is guaranteed.
