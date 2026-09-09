import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print(Fore.RED + "Error: DISCORD_TOKEN not found in .env file.")
    print(Fore.YELLOW + "Please set your DISCORD_TOKEN in the .env file.")
    exit(1)

import json

def get_prefix(bot, message):
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config.get('prefix', '.')

# Selfbot configuration
# self_bot=True is critical for this to work with user tokens
bot = commands.Bot(command_prefix=get_prefix, self_bot=True, help_command=None)

@bot.event
async def on_ready():
    print(Fore.GREEN + f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(Fore.CYAN + "--------------------------------------------------")
    print(Fore.BLUE + f"Command Prefix: {get_prefix(bot, None)}")

    # Load cogs
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(Fore.GREEN + f"Loaded extension: {filename}")
            except Exception as e:
                print(Fore.RED + f"Failed to load extension {filename}: {e}")

@bot.event
async def on_command_error(ctx, error):
    # Global error handler
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Cooldown -- try again in {error.retry_after:.0f}s", delete_after=error.retry_after)
    elif isinstance(error, commands.MissingRequiredArgument):
        # Shows usage: >cmd <arg>
        await ctx.send(f"**Usage:** `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"**Invalid Argument:** `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.CommandNotFound):
        # Ignore unknown commands (common in selfbots to avoid spamming)
        return
    else:
        print(Fore.RED + f"Error in command {ctx.command}: {error}")
        # Uncomment below to debug in chat
        # await ctx.send(f"An error occurred: {error}")

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
         print(Fore.RED + "Invalid Token. Please check your .env file.")
    except Exception as e:
        print(Fore.RED + f"Startup Error: {e}")
