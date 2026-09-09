import discord
from discord.ext import commands
import time as _time_module
import simpleeval
from currency_converter import CurrencyConverter
import math
import os
import pytz
from datetime import datetime
import asyncio
import base64
import hashlib
import re

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currency_converter = CurrencyConverter()
        self._start_time = _time_module.time()

    @commands.command(aliases=['clock', 't'])
    async def time(self, ctx, *, location: str = None):
        """Get the current time."""
        if location:
            # Common mappings
            mappings = {
                "thailand": "Asia/Bangkok", "bangkok": "Asia/Bangkok",
                "uk": "Europe/London", "london": "Europe/London", "britain": "Europe/London",
                "usa": "America/New_York", "ny": "America/New_York", "nyc": "America/New_York", "new york": "America/New_York",
                "la": "America/Los_Angeles", "los angeles": "America/Los_Angeles", "california": "America/Los_Angeles",
                "wa": "America/Los_Angeles", "washington": "America/Los_Angeles",
                "india": "Asia/Kolkata", "delhi": "Asia/Kolkata", "mumbai": "Asia/Kolkata",
                "japan": "Asia/Tokyo", "tokyo": "Asia/Tokyo", "jp": "Asia/Tokyo",
                "korea": "Asia/Seoul", "seoul": "Asia/Seoul", "sk": "Asia/Seoul",
                "china": "Asia/Shanghai", "shanghai": "Asia/Shanghai", "beijing": "Asia/Shanghai",
                "russia": "Europe/Moscow", "moscow": "Europe/Moscow",
                "france": "Europe/Paris", "paris": "Europe/Paris",
                "germany": "Europe/Berlin", "berlin": "Europe/Berlin",
                "brazil": "America/Sao_Paulo", "sao paulo": "America/Sao_Paulo",
                "australia": "Australia/Sydney", "sydney": "Australia/Sydney", "melbourne": "Australia/Melbourne",
                "vietnam": "Asia/Ho_Chi_Minh", "vn": "Asia/Ho_Chi_Minh", "hcm": "Asia/Ho_Chi_Minh",
                "philippines": "Asia/Manila", "manila": "Asia/Manila", "ph": "Asia/Manila",
                "singapore": "Asia/Singapore", "sg": "Asia/Singapore",
                "indonesia": "Asia/Jakarta", "jakarta": "Asia/Jakarta",
                "malaysia": "Asia/Kuala_Lumpur", "kl": "Asia/Kuala_Lumpur",
                "dubai": "Asia/Dubai", "uae": "Asia/Dubai",
                "turkey": "Europe/Istanbul", "istanbul": "Europe/Istanbul",
                "canada": "America/Toronto", "toronto": "America/Toronto", "vancouver": "America/Vancouver",
                "mexico": "America/Mexico_City", "mexico city": "America/Mexico_City",
                "argentina": "America/Argentina/Buenos_Aires", "buenos aires": "America/Argentina/Buenos_Aires",
                "spain": "Europe/Madrid", "madrid": "Europe/Madrid",
                "italy": "Europe/Rome", "rome": "Europe/Rome",
                "netherlands": "Europe/Amsterdam", "amsterdam": "Europe/Amsterdam",
                "sweden": "Europe/Stockholm", "stockholm": "Europe/Stockholm",
                "new zealand": "Pacific/Auckland", "nz": "Pacific/Auckland", "auckland": "Pacific/Auckland",
                "egypt": "Africa/Cairo", "cairo": "Africa/Cairo",
                "saudi": "Asia/Riyadh", "riyadh": "Asia/Riyadh",
                "south africa": "Africa/Johannesburg", "johannesburg": "Africa/Johannesburg"
            }
            
            timezone_str = mappings.get(location.lower())
            
            if not timezone_str:
                # Try to find in all timezones
                for tz in pytz.all_timezones:
                    if location.lower() in tz.lower():
                        timezone_str = tz
                        break
            
            if timezone_str:
                try:
                    tz = pytz.timezone(timezone_str)
                    now = datetime.now(tz)
                    current_time = now.strftime("%I:%M:%S %p")
                    current_date = now.strftime("%Y-%m-%d")
                    await ctx.send(f"**Time in {location.title()} ({timezone_str}):** `{current_time}`\n**Date:** `{current_date}`")
                except Exception as e:
                     await ctx.send(f"**Error:** Could not find timezone for `{location}`. ({e})")
            else:
                 await ctx.send(f"**Error:** Could not find timezone for `{location}`. Try asking for a major city.")
        else:
            # Local time
            current_time = _time_module.strftime("%I:%M:%S %p")
            current_date = _time_module.strftime("%Y-%m-%d")
            await ctx.send(f"**Current Time:** `{current_time}`\n**Date:** `{current_date}`")

    @commands.command(aliases=['p'])
    async def ping(self, ctx):
        """Check the bot's latency."""
        start_time = _time_module.time()
        message = await ctx.send("Pinging...")
        end_time = _time_module.time()
        latency = (end_time - start_time) * 1000
        await message.edit(content=f"Pong!\nMessage Latency: {latency:.2f}ms\nDiscord Gateway Latency: {self.bot.latency * 1000:.2f}ms")

    @commands.command(aliases=['av'])
    async def avatar(self, ctx, user: discord.User = None):
        """Get a user's avatar."""
        user = user or ctx.author
        await ctx.send(f"{user.avatar.url}")

    @commands.command(aliases=['ui', 'user'])
    async def whois(self, ctx, user: discord.User = None):
        """Get information about a user."""
        user = user or ctx.author
        info = f"**User Info for {user}:**\n" \
               f"ID: `{user.id}`\n" \
               f"Created Account: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n" \
               f"Bot: {'Yes' if user.bot else 'No'}"
        await ctx.send(info)

    @commands.command(aliases=['si', 'server'])
    async def serverinfo(self, ctx):
        """Get information about the server."""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server.")
            return

        info = f"**Server Info for {guild.name}:**\n" \
               f"ID: `{guild.id}`\n" \
               f"Owner: {guild.owner}\n" \
               f"Members: {guild.member_count}\n" \
               f"Created: {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        await ctx.send(info)

    @commands.command(aliases=['calc', 'math', 'c'])
    async def calculate(self, ctx, *, expression: str):
        """Evaluate a math expression."""
        try:
            # Pre-processing for common symbols
            expression = expression.replace('\u00d7', '*').replace('x', '*').replace('\u00f7', '/')
            expression = expression.replace('\u2212', '-') # Special minus
            expression = expression.replace('^', '**') # Power support
            
            # Factorial support: 5! -> factorial(5)
            expression = re.sub(r'(\d+)!', r'factorial(\1)', expression)

            # Safe evaluation using simpleeval
            functions = {
                "sqrt": math.sqrt, 
                "abs": abs, 
                "factorial": math.factorial,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log
            }
            result = simpleeval.simple_eval(expression, functions=functions)
            await ctx.send(f"**Result:** `{result}`")
        except Exception as e:
            await ctx.send(f"**Error:** Invalid expression. ({e})")

    @commands.command(aliases=['curr', 'money'])
    async def currency(self, ctx, amount: float, from_currency: str, to_currency: str):
        """Convert currency."""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            result = self.currency_converter.convert(amount, from_currency, to_currency)
            await ctx.send(f"**Conversion:** `{amount} {from_currency}` = `{result:.2f} {to_currency}`")
        except ValueError:
             await ctx.send(f"**Error:** Invalid currency code or amount.")
        except Exception as e:
            await ctx.send(f"**Error:** {e}")

    @commands.command()
    async def prefix(self, ctx, new_prefix: str):
        """Change the bot's prefix."""
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        config['prefix'] = new_prefix
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
            
        await ctx.send(f"Prefix changed to: `{new_prefix}`")

    # ------------------------------------------------------------------
    # Help system — compact categories
    # ------------------------------------------------------------------

    _HELP_CATEGORIES = {
        "utility": [
            "ping", "avatar", "whois", "serverinfo", "calculate", "currency",
            "help", "prefix", "time", "uptime", "usercount", "firstmsg",
            "nick", "embed", "poll", "remind", "base64e", "base64d",
            "hash", "len", "reload", "shortforms"
        ],
        "moderation": ["purge", "botclear"],
        "status": ["stream", "listen", "watch", "rotate", "online", "idle", "donotdisturb"],
        "fun": [
            "hack", "token", "ip", "nitro", "8ball", "roll", "coinflip",
            "rate", "pp", "ship", "mock", "reverse", "emojify", "clap",
            "say", "dm", "spam", "rps", "qotd", "roast", "compliment",
            "howgay", "iq", "slot", "choose", "truth", "dare", "fact",
            "joke", "quote", "ascii", "uwu", "typeracer",
            "fancy", "spoilerify", "encrypt", "decrypt"
        ],
        "tools": [
            "autorespond", "ghostping", "selfdestruct", "bookmark", "search", "privacy"
        ],
        "media": [
            "movie", "show", "msearch"
        ],
        "afk": ["afk"],
        "sniper": ["snipe", "editsnipe"],
        "ai": ["ai"]
    }

    _DELETE_AFTER = 30  # seconds before auto-deleting help messages

    @commands.group(aliases=['h'], invoke_without_command=True)
    async def help(self, ctx):
        """Show command categories. Use |help <category> for details."""
        prefix = ctx.prefix
        text = f"**Commands** (Prefix: `{prefix}`)\n\n"
        for cat, cmds in self._HELP_CATEGORIES.items():
            text += f"`{prefix}help {cat}` -- {cat.title()} ({len(cmds)} cmds)\n"
        text += f"\n-# auto-deletes in {self._DELETE_AFTER}s"

        await ctx.send(text, delete_after=self._DELETE_AFTER)
        try:
            await ctx.message.delete(delay=self._DELETE_AFTER)
        except:
            pass

    async def _show_category(self, ctx, category: str):
        """Helper to display all commands in a category."""
        prefix = ctx.prefix
        cmds = self._HELP_CATEGORIES.get(category)
        if not cmds:
            await ctx.send(f"Unknown category `{category}`.", delete_after=5)
            return

        text = f"**{category.title()} Commands**\n\n"
        for name in cmds:
            cmd = self.bot.get_command(name)
            if cmd:
                aliases = ', '.join(f"`{prefix}{a}`" for a in cmd.aliases) if cmd.aliases else ""
                alias_str = f" ({aliases})" if aliases else ""
                text += f"`{prefix}{name}`{alias_str}: {cmd.short_doc}\n"
        text += f"\n-# auto-deletes in {self._DELETE_AFTER}s"

        await ctx.send(text, delete_after=self._DELETE_AFTER)
        try:
            await ctx.message.delete(delay=self._DELETE_AFTER)
        except:
            pass

    @help.command(name='utility', aliases=['util', 'u'])
    async def help_utility(self, ctx):
        """Show utility commands."""
        await self._show_category(ctx, 'utility')

    @help.command(name='moderation', aliases=['mod', 'm'])
    async def help_moderation(self, ctx):
        """Show moderation commands."""
        await self._show_category(ctx, 'moderation')

    @help.command(name='status', aliases=['st'])
    async def help_status(self, ctx):
        """Show status commands."""
        await self._show_category(ctx, 'status')

    @help.command(name='fun', aliases=['f'])
    async def help_fun(self, ctx):
        """Show fun commands."""
        await self._show_category(ctx, 'fun')

    @help.command(name='afk')
    async def help_afk(self, ctx):
        """Show AFK commands."""
        await self._show_category(ctx, 'afk')

    @help.command(name='sniper', aliases=['snipe'])
    async def help_sniper(self, ctx):
        """Show sniper commands."""
        await self._show_category(ctx, 'sniper')

    @help.command(name='ai')
    async def help_ai(self, ctx):
        """Show AI commands."""
        await self._show_category(ctx, 'ai')

    @help.command(name='tools', aliases=['t'])
    async def help_tools(self, ctx):
        """Show tools commands."""
        await self._show_category(ctx, 'tools')

    @help.command(name='media')
    async def help_media(self, ctx):
        """Show media commands."""
        await self._show_category(ctx, 'media')

    @commands.command(aliases=['sf', 'aliases'])
    async def shortforms(self, ctx):
        """List command aliases (shortforms)."""
        p = ctx.prefix
        text = (
            "**Command Shortforms**\n\n"
            "**Utility**\n"
            f"`{p}ping` -> `{p}p`\n"
            f"`{p}time` -> `{p}t`\n"
            f"`{p}whois` -> `{p}ui`\n"
            f"`{p}serverinfo` -> `{p}si`\n"
            f"`{p}avatar` -> `{p}av`\n"
            f"`{p}calc` -> `{p}c`\n"
            f"`{p}currency` -> `{p}curr`\n"
            f"`{p}help` -> `{p}h`\n"
            f"`{p}reload` -> `{p}rl`\n\n"
            "**Status**\n"
            f"`{p}stream` -> `{p}st`\n"
            f"`{p}listen` -> `{p}l`\n"
            f"`{p}watch` -> `{p}w`\n"
            f"`{p}online` -> `{p}on`\n"
            f"`{p}idle` -> `{p}id`\n"
            f"`{p}dnd` -> `{p}dn`\n"
            f"`{p}rotate` -> `{p}r`\n\n"
            "**Moderation**\n"
            f"`{p}purge` -> `{p}cl`\n"
            f"`{p}botclear` -> `{p}bc`\n\n"
            "**Sniper**\n"
            f"`{p}snipe` -> `{p}s`\n"
            f"`{p}editsnipe` -> `{p}es`\n"
            f"`{p}afk` -> `{p}brb`\n\n"
            "**AI**\n"
            f"`{p}ai start` -> `{p}ai on`\n"
            f"`{p}ai stop` -> `{p}ai off`\n"
            f"`{p}ai auto` -- Auto-reply (all or @user)\n"
            f"`{p}ai <prompt>` -- Ask the AI\n\n"
            "**Fun**\n"
            f"`{p}8ball` -> `{p}ask`\n"
            f"`{p}roll` -> `{p}dice`\n"
            f"`{p}coinflip` -> `{p}flip`\n"
            f"`{p}ship` -> `{p}love`\n"
            f"`{p}reverse` -> `{p}rev`\n"
            f"`{p}emojify` -> `{p}emoji`\n"
            f"`{p}choose` -> `{p}pick`\n"
            f"`{p}slot` -> `{p}slots`\n"
            f"`{p}typeracer` -> `{p}tr`\n"
            f"`{p}qotd` -> `{p}question`\n\n"
            "**New Utility**\n"
            f"`{p}base64e` / `{p}base64d` -- Encode/decode base64\n"
            f"`{p}hash` -- MD5 + SHA256\n"
            f"`{p}len` -- Char/word count\n"
            f"`{p}uptime` -- Bot uptime\n"
            f"`{p}nick` -- Change nickname\n"
            f"`{p}embed` -- Fancy codeblock msg\n"
            f"`{p}poll` -- Simple poll\n"
            f"`{p}remind` -- Set a reminder\n"
            f"`{p}usercount` -- Member count\n"
            f"`{p}firstmsg` -- First msg in channel"
        )
        
        await ctx.send(text)

    @commands.command(aliases=['rl'])
    async def reload(self, ctx):
        """Reloads all cogs."""
        try:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await self.bot.reload_extension(f'cogs.{filename[:-3]}')
            await ctx.send(f"**Reloaded all cogs!**")
        except Exception as e:
            await ctx.send(f"**Error reloading:** {e}")

    # ==================================================================
    # NEW UTILITY COMMANDS
    # ==================================================================

    # ------------------------------------------------------------------
    # .base64e / .base64d — base64 encode/decode
    # ------------------------------------------------------------------
    @commands.command(aliases=['b64e'])
    async def base64e(self, ctx, *, text: str):
        """Base64 encode text."""
        encoded = base64.b64encode(text.encode()).decode()
        await ctx.send(f"**Encoded:**\n`{encoded}`")

    @commands.command(aliases=['b64d'])
    async def base64d(self, ctx, *, text: str):
        """Base64 decode text."""
        try:
            decoded = base64.b64decode(text.encode()).decode()
            await ctx.send(f"**Decoded:**\n`{decoded}`")
        except Exception:
            await ctx.send("**Error:** Invalid base64 string.")

    # ------------------------------------------------------------------
    # .hash <text> — generate hashes
    # ------------------------------------------------------------------
    @commands.command()
    async def hash(self, ctx, *, text: str):
        """Generate MD5 and SHA256 hashes of text."""
        md5 = hashlib.md5(text.encode()).hexdigest()
        sha256 = hashlib.sha256(text.encode()).hexdigest()
        await ctx.send(
            f"**Hashes for:** `{text[:50]}`\n"
            f"**MD5:** `{md5}`\n"
            f"**SHA256:** `{sha256}`"
        )

    # ------------------------------------------------------------------
    # .len <text> — character and word count
    # ------------------------------------------------------------------
    @commands.command(name='len', aliases=['length', 'count'])
    async def length_cmd(self, ctx, *, text: str):
        """Count characters and words in text."""
        chars = text.__len__()
        words = text.split().__len__()
        lines = text.count('\n') + 1
        await ctx.send(
            f"**Characters:** {chars}\n"
            f"**Words:** {words}\n"
            f"**Lines:** {lines}"
        )

    # ------------------------------------------------------------------
    # .uptime — bot uptime
    # ------------------------------------------------------------------
    @commands.command()
    async def uptime(self, ctx):
        """Show how long the bot has been running."""
        elapsed = int(_time_module.time() - self._start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        await ctx.send(f"**Uptime:** {' '.join(parts)}")

    # ------------------------------------------------------------------
    # .nick <name> — change your server nickname
    # ------------------------------------------------------------------
    @commands.command()
    async def nick(self, ctx, *, name: str = None):
        """Change your nickname in the server."""
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return
        try:
            await ctx.author.edit(nick=name)
            if name:
                await ctx.send(f"Nickname changed to: **{name}**", delete_after=3)
            else:
                await ctx.send("Nickname reset.", delete_after=3)
        except discord.Forbidden:
            await ctx.send("**Error:** Missing permissions to change nickname.")
        except Exception as e:
            await ctx.send(f"**Error:** {e}")

    # ------------------------------------------------------------------
    # .embed <text> — send a fancy codeblock message
    # ------------------------------------------------------------------
    @commands.command()
    async def embed(self, ctx, *, text: str):
        """Send a message as a fancy codeblock (selfbots can't use real embeds)."""
        try:
            await ctx.message.delete()
        except Exception:
            pass
        # Create a nicely formatted codeblock message
        border = "=" * min(len(text) + 4, 50)
        await ctx.send(f"```\n{border}\n  {text}\n{border}\n```")

    # ------------------------------------------------------------------
    # .poll question | option1 | option2 ...
    # ------------------------------------------------------------------
    @commands.command()
    async def poll(self, ctx, *, content: str):
        """Create a simple poll. Separate question and options with |"""
        parts = [p.strip() for p in content.split('|') if p.strip()]
        if len(parts) < 3:
            await ctx.send(f"Format: `{ctx.prefix}poll Question | Option 1 | Option 2`")
            return
        if len(parts) > 11:  # 1 question + 10 options max
            await ctx.send("Max 10 options.")
            return

        question = parts[0]
        options = parts[1:]
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        try:
            await ctx.message.delete()
        except Exception:
            pass

        poll_text = f"**POLL: {question}**\n\n"
        for i, opt in enumerate(options):
            poll_text += f"**{letters[i]}.** {opt}\n"
        poll_text += f"\n-# React with your choice"

        msg = await ctx.send(poll_text)

        # Add letter reactions
        letter_emojis = [
            '\N{REGIONAL INDICATOR SYMBOL LETTER A}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER D}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER G}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
            '\N{REGIONAL INDICATOR SYMBOL LETTER J}',
        ]
        for i in range(len(options)):
            try:
                await msg.add_reaction(letter_emojis[i])
            except Exception:
                pass

    # ------------------------------------------------------------------
    # .remind <time> <message> — set a reminder
    # ------------------------------------------------------------------
    @commands.command(aliases=['timer', 'remindme'])
    async def remind(self, ctx, time_str: str, *, message: str):
        """Set a reminder. Example: |remind 5m check oven"""
        # Parse time string like 5s, 5m, 5h
        match = re.match(r'^(\d+)([smh])$', time_str.lower())
        if not match:
            await ctx.send(f"Format: `{ctx.prefix}remind <number><s/m/h> <message>`\nExample: `{ctx.prefix}remind 5m check oven`")
            return

        amount = int(match.group(1))
        unit = match.group(2)
        multipliers = {'s': 1, 'm': 60, 'h': 3600}
        seconds = amount * multipliers[unit]

        if seconds > 86400:  # 24 hours max
            await ctx.send("Max reminder time is 24 hours.")
            return

        unit_names = {'s': 'second(s)', 'm': 'minute(s)', 'h': 'hour(s)'}
        await ctx.send(f"Reminder set for **{amount} {unit_names[unit]}**: {message}", delete_after=5)

        await asyncio.sleep(seconds)
        await ctx.send(f"**REMINDER:** {message}")

    # ------------------------------------------------------------------
    # .usercount — server member count
    # ------------------------------------------------------------------
    @commands.command(aliases=['members', 'mc'])
    async def usercount(self, ctx):
        """Show the server member count."""
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return
        await ctx.send(f"**{ctx.guild.name}** has **{ctx.guild.member_count}** members.")

    # ------------------------------------------------------------------
    # .firstmsg — link to first message in channel
    # ------------------------------------------------------------------
    @commands.command(aliases=['first'])
    async def firstmsg(self, ctx):
        """Get the first message in this channel."""
        try:
            async for msg in ctx.channel.history(limit=1, oldest_first=True):
                link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{msg.id}"
                await ctx.send(
                    f"**First message in this channel:**\n"
                    f"**Author:** {msg.author}\n"
                    f"**Date:** {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"**Link:** {link}"
                )
                return
            await ctx.send("No messages found in this channel.")
        except Exception as e:
            await ctx.send(f"**Error:** {e}")

    # ==================================================================
    # NEW UTILITY COMMANDS (batch 2)
    # ==================================================================

    # ------------------------------------------------------------------
    # .banner @user — grab profile banner
    # ------------------------------------------------------------------
    @commands.command()
    async def banner(self, ctx, user: discord.User = None):
        """Get a user's profile banner."""
        user = user or ctx.author
        try:
            fetched = await self.bot.fetch_user(user.id)
            if fetched.banner:
                await ctx.send(f"**{fetched.name}**'s banner:\n{fetched.banner.url}")
            else:
                await ctx.send(f"**{fetched.name}** has no banner set.")
        except Exception as e:
            await ctx.send(f"**Error:** {e}")

    # ------------------------------------------------------------------
    # .snowflake <id> — decode Discord snowflake
    # ------------------------------------------------------------------
    @commands.command(aliases=['sf_decode', 'idinfo'])
    async def snowflake(self, ctx, snowflake_id: int):
        """Decode a Discord snowflake ID into creation date."""
        # Discord epoch: 2015-01-01T00:00:00.000Z
        discord_epoch = 1420070400000
        timestamp_ms = (snowflake_id >> 22) + discord_epoch
        timestamp_s = timestamp_ms / 1000
        dt = datetime.utcfromtimestamp(timestamp_s)
        unix_ts = int(timestamp_s)

        await ctx.send(
            f"**Snowflake Decode:** `{snowflake_id}`\n"
            f"**Created:** {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"**Unix:** `{unix_ts}`\n"
            f"**Discord format:** <t:{unix_ts}:F> (<t:{unix_ts}:R>)"
        )

    # ------------------------------------------------------------------
    # .timestamp <time_description> — Discord timestamp generator
    # ------------------------------------------------------------------
    @commands.command(aliases=['ts'])
    async def timestamp(self, ctx, *, time_input: str):
        """Generate Discord timestamps. Use: |ts now, |ts +5m, |ts +2h, |ts +1d"""
        import re as _re
        now = int(_time_module.time())

        if time_input.strip().lower() == 'now':
            unix = now
        else:
            # Parse relative time: +5m, +2h, +1d, +30s
            match = _re.match(r'^\+?(\d+)([smhd])$', time_input.strip().lower())
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
                unix = now + (amount * multipliers[unit])
            else:
                await ctx.send(
                    f"**Formats:** `now`, `+30s`, `+5m`, `+2h`, `+1d`\n"
                    f"Example: `{ctx.prefix}ts +5m`",
                    delete_after=10
                )
                return

        await ctx.send(
            f"**Timestamp:** `{unix}`\n"
            f"**Formats (copy these):**\n"
            f"`<t:{unix}:t>` -> <t:{unix}:t> (short time)\n"
            f"`<t:{unix}:T>` -> <t:{unix}:T> (long time)\n"
            f"`<t:{unix}:d>` -> <t:{unix}:d> (short date)\n"
            f"`<t:{unix}:D>` -> <t:{unix}:D> (long date)\n"
            f"`<t:{unix}:f>` -> <t:{unix}:f> (short datetime)\n"
            f"`<t:{unix}:F>` -> <t:{unix}:F> (long datetime)\n"
            f"`<t:{unix}:R>` -> <t:{unix}:R> (relative)",
            delete_after=30
        )

    # ------------------------------------------------------------------
    # .msgcount @user — count messages from a user in this channel
    # ------------------------------------------------------------------
    @commands.command(aliases=['mc2'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def msgcount(self, ctx, user: discord.User = None):
        """Count messages from a user in this channel (scans last 1000)."""
        user = user or ctx.author
        msg = await ctx.send(f"Counting messages from **{user.name}**...")
        count = 0
        async for message in ctx.channel.history(limit=1000):
            if message.author.id == user.id:
                count += 1
        await msg.edit(content=f"**{user.name}** has **{count}** messages in the last 1000 messages of this channel.")

    # ------------------------------------------------------------------
    # .color <hex> — color converter
    # ------------------------------------------------------------------
    @commands.command(aliases=['colour', 'rgb'])
    async def color(self, ctx, *, value: str):
        """Convert between hex and RGB colors. Example: |color #ff5733 or |color 255 87 51"""
        value = value.strip()

        # Try hex input
        hex_match = re.match(r'^#?([0-9a-fA-F]{6})$', value)
        if hex_match:
            hex_val = hex_match.group(1)
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            # HSL conversion
            r_norm, g_norm, b_norm = r/255, g/255, b/255
            c_max = max(r_norm, g_norm, b_norm)
            c_min = min(r_norm, g_norm, b_norm)
            l = (c_max + c_min) / 2
            if c_max == c_min:
                h = s = 0
            else:
                d = c_max - c_min
                s = d / (2 - c_max - c_min) if l > 0.5 else d / (c_max + c_min)
                if c_max == r_norm:
                    h = ((g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)) / 6
                elif c_max == g_norm:
                    h = ((b_norm - r_norm) / d + 2) / 6
                else:
                    h = ((r_norm - g_norm) / d + 4) / 6

            await ctx.send(
                f"**Color Info**\n"
                f"**Hex:** `#{hex_val.upper()}`\n"
                f"**RGB:** `{r}, {g}, {b}`\n"
                f"**HSL:** `{int(h*360)}, {int(s*100)}%, {int(l*100)}%`\n"
                f"**Discord Int:** `{int(hex_val, 16)}`"
            )
            return

        # Try RGB input
        rgb_match = re.match(r'^(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})$', value)
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            if all(0 <= v <= 255 for v in [r, g, b]):
                hex_val = f"{r:02X}{g:02X}{b:02X}"
                await ctx.send(
                    f"**Color Info**\n"
                    f"**Hex:** `#{hex_val}`\n"
                    f"**RGB:** `{r}, {g}, {b}`\n"
                    f"**Discord Int:** `{int(hex_val, 16)}`"
                )
                return

        await ctx.send(f"Format: `{ctx.prefix}color #FF5733` or `{ctx.prefix}color 255 87 51`", delete_after=10)

    # ------------------------------------------------------------------
    # .delay <time> <message> — delayed message send
    # ------------------------------------------------------------------
    @commands.command(aliases=['schedule'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def delay(self, ctx, time_str: str, *, text: str):
        """Send a message after a delay. Example: |delay 5m hello everyone"""
        match = re.match(r'^(\d+)([smh])$', time_str.lower())
        if not match:
            await ctx.send(f"Format: `{ctx.prefix}delay <number><s/m/h> <message>`", delete_after=5)
            return

        amount = int(match.group(1))
        unit = match.group(2)
        multipliers = {'s': 1, 'm': 60, 'h': 3600}
        seconds = amount * multipliers[unit]

        if seconds > 86400:
            await ctx.send("Max delay is 24 hours.", delete_after=5)
            return

        unit_names = {'s': 'second(s)', 'm': 'minute(s)', 'h': 'hour(s)'}
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(f"Message scheduled in **{amount} {unit_names[unit]}**.", delete_after=5)
        await asyncio.sleep(seconds)
        await ctx.send(text)

    # ------------------------------------------------------------------
    # .password <length> — generate secure password
    # ------------------------------------------------------------------
    @commands.command(aliases=['genpass', 'pw'])
    async def password(self, ctx, length: int = 16):
        """Generate a secure random password."""
        import secrets
        if length < 8 or length > 64:
            await ctx.send("Length must be between 8 and 64.", delete_after=5)
            return
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*-_=+'
        pw = ''.join(secrets.choice(chars) for _ in range(length))
        await ctx.send(f"**Generated password ({length} chars):**\n`{pw}`", delete_after=15)
        try:
            await ctx.message.delete()
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Utility(bot))

