import discord
from discord.ext import commands
import asyncio
import json
import os
import time as _time

# Path for persistent auto-responder data
_DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AR_FILE = os.path.join(_DATA_DIR, 'autoresponder.json')


class Tools(commands.Cog):
    """Auto-responder, ghost ping detector, self-destruct, bookmark, search."""

    def __init__(self, bot):
        self.bot = bot
        self._auto_responses: dict[str, str] = {}  # trigger -> response
        self._ghost_pings: dict[int, dict] = {}     # channel_id -> {author, content, time}
        self._ghost_ping_enabled = False
        self._privacy_mode = 0  # 0 = off, >0 = seconds before auto-delete
        self._load_auto_responses()

    # ------------------------------------------------------------------
    # Persistence for auto-responder
    # ------------------------------------------------------------------

    def _load_auto_responses(self):
        try:
            if os.path.exists(_AR_FILE):
                with open(_AR_FILE, 'r') as f:
                    self._auto_responses = json.load(f)
        except Exception:
            self._auto_responses = {}

    def _save_auto_responses(self):
        try:
            with open(_AR_FILE, 'w') as f:
                json.dump(self._auto_responses, f, indent=2)
        except Exception:
            pass

    # ==================================================================
    # AUTO-RESPONDER
    # ==================================================================

    @commands.group(aliases=['ar'], invoke_without_command=True)
    async def autorespond(self, ctx):
        """Manage auto-responses. Triggers -> auto-replies."""
        prefix = ctx.prefix
        if not self._auto_responses:
            await ctx.send(
                f"No auto-responses set.\n"
                f"`{prefix}ar add <trigger> | <response>`\n"
                f"`{prefix}ar remove <trigger>`\n"
                f"`{prefix}ar list`\n"
                f"`{prefix}ar clear`",
                delete_after=10
            )
        else:
            await ctx.send(
                f"**Auto-Responder** -- {len(self._auto_responses)} trigger(s) active\n"
                f"`{prefix}ar add` / `{prefix}ar remove` / `{prefix}ar list` / `{prefix}ar clear`",
                delete_after=10
            )

    @autorespond.command(name='add')
    async def ar_add(self, ctx, *, content: str):
        """Add an auto-response. Format: |ar add trigger | response"""
        parts = content.split('|', 1)
        if len(parts) < 2:
            await ctx.send(f"Format: `{ctx.prefix}ar add trigger | response`", delete_after=5)
            return
        trigger = parts[0].strip().lower()
        response = parts[1].strip()
        if not trigger or not response:
            await ctx.send("Both trigger and response are required.", delete_after=5)
            return
        if len(self._auto_responses) >= 50:
            await ctx.send("Max 50 auto-responses. Remove some first.", delete_after=5)
            return
        self._auto_responses[trigger] = response
        self._save_auto_responses()
        await ctx.send(f"Auto-response added: `{trigger}` -> `{response}`", delete_after=5)

    @autorespond.command(name='remove', aliases=['rm', 'del'])
    async def ar_remove(self, ctx, *, trigger: str):
        """Remove an auto-response by trigger."""
        trigger = trigger.lower()
        if trigger in self._auto_responses:
            del self._auto_responses[trigger]
            self._save_auto_responses()
            await ctx.send(f"Removed auto-response for: `{trigger}`", delete_after=5)
        else:
            await ctx.send(f"No auto-response found for: `{trigger}`", delete_after=5)

    @autorespond.command(name='list', aliases=['ls'])
    async def ar_list(self, ctx):
        """List all auto-responses."""
        if not self._auto_responses:
            await ctx.send("No auto-responses set.", delete_after=5)
            return
        text = "**Auto-Responses:**\n"
        for i, (trigger, response) in enumerate(self._auto_responses.items(), 1):
            text += f"`{i}.` `{trigger}` -> {response}\n"
            if len(text) > 1800:
                text += f"...and {len(self._auto_responses) - i} more"
                break
        await ctx.send(text, delete_after=15)

    @autorespond.command(name='clear')
    async def ar_clear(self, ctx):
        """Clear all auto-responses."""
        self._auto_responses.clear()
        self._save_auto_responses()
        await ctx.send("All auto-responses cleared.", delete_after=5)

    # ==================================================================
    # GHOST PING DETECTOR
    # ==================================================================

    @commands.command(aliases=['gp'])
    async def ghostping(self, ctx):
        """Toggle ghost ping detection."""
        self._ghost_ping_enabled = not self._ghost_ping_enabled
        status = "**ON**" if self._ghost_ping_enabled else "**OFF**"
        await ctx.send(f"Ghost ping detection: {status}", delete_after=5)

    # ==================================================================
    # SELF-DESTRUCT MESSAGE
    # ==================================================================

    @commands.command(aliases=['sd'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def selfdestruct(self, ctx, seconds: int, *, text: str):
        """Send a self-destructing message. Example: |sd 5 hello"""
        if seconds < 1 or seconds > 60:
            await ctx.send("Time must be between 1 and 60 seconds.", delete_after=3)
            return
        try:
            await ctx.message.delete()
        except Exception:
            pass
        msg = await ctx.send(f"{text}\n-# self-destructs in {seconds}s")
        await asyncio.sleep(seconds)
        try:
            await msg.delete()
        except Exception:
            pass

    # ==================================================================
    # BOOKMARK (save message to DMs)
    # ==================================================================

    @commands.command(aliases=['bm', 'save'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bookmark(self, ctx, message_id: int = None):
        """Save a message to your DMs. Reply to a message or pass a message ID."""
        target = None

        # Check if replying to a message
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                target = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            except Exception:
                pass

        # Or use provided message ID
        if not target and message_id:
            try:
                target = await ctx.channel.fetch_message(message_id)
            except Exception:
                pass

        if not target:
            await ctx.send(f"Reply to a message or provide a message ID: `{ctx.prefix}bookmark <id>`", delete_after=5)
            return

        # Build bookmark content
        link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{target.id}" if ctx.guild else "DM"
        content = target.content or "[no text content]"
        if len(content) > 1500:
            content = content[:1500] + "..."

        bookmark_text = (
            f"**Bookmarked Message**\n"
            f"**From:** {target.author} in #{ctx.channel.name if ctx.guild else 'DM'}\n"
            f"**Date:** {target.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**Link:** {link}\n\n"
            f"{content}"
        )

        if target.attachments:
            bookmark_text += f"\n**Attachments:** {', '.join(a.url for a in target.attachments[:3])}"

        try:
            await ctx.author.send(bookmark_text)
            await ctx.send("Bookmarked -- check your DMs.", delete_after=3)
        except Exception:
            await ctx.send("Couldn't send DM. Check your privacy settings.", delete_after=5)

        try:
            await ctx.message.delete()
        except Exception:
            pass

    # ==================================================================
    # MESSAGE SEARCH
    # ==================================================================

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def search(self, ctx, *, query: str):
        """Search channel history for a keyword. Scans last 500 messages."""
        if len(query) < 2:
            await ctx.send("Query must be at least 2 characters.", delete_after=5)
            return

        msg = await ctx.send(f"Searching for `{query}`...")
        results = []
        query_lower = query.lower()

        async for message in ctx.channel.history(limit=500):
            if query_lower in message.content.lower():
                results.append(message)
                if len(results) >= 10:  # Cap at 10 results
                    break

        if not results:
            await msg.edit(content=f"No results found for `{query}`.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        text = f"**Search results for** `{query}` **({len(results)} found):**\n\n"
        for i, m in enumerate(results, 1):
            timestamp = m.created_at.strftime("%m/%d %H:%M")
            preview = m.content[:80].replace('\n', ' ')
            if len(m.content) > 80:
                preview += "..."
            link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{m.id}" if ctx.guild else ""
            text += f"`{i}.` **{m.author.name}** ({timestamp}): {preview}"
            if link:
                text += f" [jump]({link})"
            text += "\n"

        if len(text) > 1900:
            text = text[:1900] + "\n..."

        await msg.edit(content=text)
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except Exception:
            pass

    # ==================================================================
    # PRIVACY MODE
    # ==================================================================

    @commands.command(aliases=['priv'])
    async def privacy(self, ctx, seconds: int = 0):
        """Toggle privacy mode. Auto-deletes your messages after X seconds. 0 = off."""
        if seconds < 0 or seconds > 300:
            await ctx.send("Seconds must be between 0 and 300.", delete_after=5)
            return
        self._privacy_mode = seconds
        if seconds == 0:
            await ctx.send("Privacy mode **OFF**.", delete_after=5)
        else:
            await ctx.send(f"Privacy mode **ON** -- your messages auto-delete after **{seconds}s**.", delete_after=5)

    # ==================================================================
    # LISTENERS
    # ==================================================================

    @commands.Cog.listener()
    async def on_message(self, message):
        # --- Token protector (always active for self) ---
        if message.author.id == self.bot.user.id and message.content:
            import re as _re
            # Discord token pattern: base64.base64.base64 (rough match)
            token_pattern = r'[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27,}'
            if _re.search(token_pattern, message.content):
                try:
                    await message.delete()
                    await message.channel.send(
                        "**[TOKEN PROTECTOR]** Deleted a message that contained a token pattern.",
                        delete_after=5
                    )
                except Exception:
                    pass
                return

        # --- Privacy mode (auto-delete own messages) ---
        if message.author.id == self.bot.user.id and self._privacy_mode > 0:
            # Don't delete the privacy command itself or system messages
            if message.content and not message.content.startswith(('**[', 'Privacy mode')):
                # Read prefix to skip commands
                try:
                    with open('config.json', 'r') as f:
                        pfx = json.load(f).get('prefix', '.')
                    if message.content.startswith(pfx):
                        return
                except Exception:
                    pass
                await asyncio.sleep(self._privacy_mode)
                try:
                    await message.delete()
                except Exception:
                    pass
            return

        # Don't respond to self for other features
        if message.author.id == self.bot.user.id:
            return

        # --- Auto-responder ---
        if self._auto_responses and message.content:
            content_lower = message.content.lower()
            for trigger, response in self._auto_responses.items():
                if trigger in content_lower:
                    try:
                        await asyncio.sleep(1)  # Small delay to look natural
                        await message.reply(response, mention_author=False)
                    except Exception:
                        pass
                    break  # Only respond to first match

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not self._ghost_ping_enabled:
            return
        # Check if the deleted message mentioned us
        if message.author.id == self.bot.user.id:
            return
        if self.bot.user.mentioned_in(message):
            self._ghost_pings[message.channel.id] = {
                'author': str(message.author),
                'content': message.content[:200],
                'time': _time.time()
            }
            try:
                await message.channel.send(
                    f"**Ghost ping detected**\n"
                    f"**From:** {message.author} (`{message.author.id}`)\n"
                    f"**Content:** {message.content[:200]}",
                    delete_after=10
                )
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(Tools(bot))

