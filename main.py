import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from core.config_manager import config
from core.tui import dashboard, RichLogHandler
from core.token_manager import select_token

# Setup structured logging
log = logging.getLogger("selfbot")
log.setLevel(logging.INFO)
log.addHandler(RichLogHandler())

load_dotenv()


def get_prefix(bot, message):
    return config.prefix


# Selfbot configuration
# self_bot=True is critical for this to work with user tokens
bot = commands.Bot(command_prefix=get_prefix, self_bot=True, help_command=None)


@bot.event
async def on_ready():
    # Load cogs
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                dashboard.show_cog_load(cog_name, True)
            except Exception as e:
                dashboard.show_cog_load(cog_name, False, e)

    # Show ready dashboard after cogs loaded
    dashboard.show_ready(bot)


@bot.event
async def on_command(ctx):
    """Track command usage in TUI."""
    dashboard.log_command(ctx)


@bot.event
async def on_command_error(ctx, error):
    # Global error handler
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Cooldown -- try again in {error.retry_after:.0f}s", delete_after=error.retry_after)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"**Usage:** `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"**Invalid Argument:** `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        log.error(f"Error in command {ctx.command}: {error}")


if __name__ == "__main__":
    if os.name != 'nt':
        try:
            import uvloop
            uvloop.install()
            log.info("uvloop event loop installed")
        except ImportError:
            pass

    dashboard.show_banner(prefix=config.prefix, version="2.0.0")

    # Token selection — interactive account switcher
    TOKEN = select_token()

    if not TOKEN:
        log.warning("No account selected. Exiting.")
        exit(0)

    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        log.critical("Invalid Token. Check your token or re-add the account.")
    except Exception as e:
        log.critical(f"Startup Error: {e}")
