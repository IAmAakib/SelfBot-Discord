# SelfBot for Discord

A powerful but easy-to-use tool that adds custom commands and a visual dashboard to your own Discord account. It includes over 60 commands and built-in local AI capabilities.

> [!WARNING]
> **Disclaimer & Limitations:** Using a selfbot is against the Discord Terms of Service. This is a hobby project created for educational purposes. It may or may not receive updates. No support is guaranteed. **Use at your own risk.**

---

## 🌟 What does it do?

Instead of adding a "bot" to a server, this runs on **your own account**. When you type `.ping` (or any other command), the script automatically responds for you. 

- **Visual Dashboard**: Watch your commands and bot status in a beautiful terminal interface.
- **Local AI**: Chat with AI locally on your machine without paying for API keys.
- **Multiple Accounts**: Easily switch between different Discord accounts using the built-in token manager.
- **60+ Commands**: Packed with tools for moderation, utility, media, and fun.

---

## 🛠️ What you need before starting

To run this on your computer, you need three things:

1. **Python (3.10 or newer)**
   - [Download Python here](https://www.python.org/downloads/).
   - *(Windows Users: When installing, make sure to check the box that says **"Add Python to PATH"**).*
2. **C++ Build Tools** *(Required for the AI features)*
   - **Windows:** Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). During installation, check the box for "Desktop development with C++".
   - **Mac:** Open your Terminal and run `xcode-select --install`
   - **Linux:** Open your Terminal and run `sudo apt install build-essential python3-dev`
3. **Your Discord User Token**
   - This is the secret password that lets the script control your account. **Never share this with anyone.** 
   - *How to find it:* Open Discord in your web browser > Press `F12` to open Developer Tools > Go to the `Network` tab > Send any message in Discord > Click on the `messages` request that appears in the network tab > Look for the `authorization` header.

---

## 🚀 Getting Started

Follow these instructions based on your Operating System:

### For Windows Users

1. **Download the code:** 
   Click the green **Code** button at the top of this page and select **Download ZIP**, then extract the folder. *(Alternatively, if you know how to use Git, run `git clone https://github.com/IAmAakib/SelfBot-Discord`)*
2. **Setup your Token:**
   Inside the extracted folder, find the file named `.env.example`. Rename it to `.env` (make sure it doesn't end in `.txt`). Open it in Notepad and paste your Discord token where it says `your_token_here`.
3. **Run the Bot:**
   Double-click the `start.bat` file. 
   *The very first time you run this, it will automatically download everything it needs. This might take a few minutes.*

### For Mac & Linux Users

1. **Download the code:**
   Open your Terminal and run:
   ```bash
   git clone https://github.com/IAmAakib/SelfBot-Discord
   cd SelfBot-Discord
   ```
2. **Setup your Token:**
   Run the following command to create your environment file:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file in a text editor (like nano or VS Code) and add your Discord token.
3. **Run the Bot:**
   Run the startup script:
   ```bash
   ./start.sh
   ```
   *The very first time you run this, it will automatically download everything it needs.*

---

## ⚙️ Configuration

You can easily change the bot's prefix (the symbol you type before a command) by opening the `config.json` file in any text editor:

```json
{
    "prefix": "."
}
```

---

## ❓ Troubleshooting

**"Failed to build llama-cpp-python"**
- This means your computer is missing the C++ Build Tools. Please check step 2 in the "What you need before starting" section above.

**"Invalid Token. Check your token or re-add the account."**
- Make sure you copied your *User* token, not a Bot token from the Discord Developer Portal. Double-check your `.env` file to ensure there are no spaces around the token.

**Windows: "Python is not recognized as an internal or external command"**
- You forgot to check the **"Add Python to PATH"** box when installing Python. Uninstall Python, run the installer again, and ensure that box is checked at the very bottom of the first screen.

---

## 🧠 For Developers (Architecture)

If you'd like to look at the code, here is how the project is structured:

```text
├── core/                 # Core engine (config, token management, visual dashboard)
├── cogs/                 # Command modules (afk, ai, fun, media, moderation, etc.)
├── models/               # Local AI models (.gguf) are stored here
├── main.py               # Main bot entrypoint
├── requirements.txt      # Python dependencies
├── start.sh              # Mac/Linux automatic launcher
└── start.bat             # Windows automatic launcher
```
