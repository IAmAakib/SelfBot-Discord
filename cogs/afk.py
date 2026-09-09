import discord
from discord.ext import commands
import time

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_reason = None
        self.afk_time = None

    @commands.command(aliases=['brb'])
    async def afk(self, ctx, *, reason="AFK"):
        """Set your status to AFK."""
        if self.afk_reason:
            self.afk_reason = None
            self.afk_time = None
            await ctx.send("Welcome back! AFK status removed.")
        else:
            self.afk_reason = reason
            self.afk_time = time.time()
            await ctx.send(f"AFK set: **{reason}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not self.afk_reason:
            return

        # Check if mentioned or DM
        if self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            elapsed = int(time.time() - self.afk_time)
            # Prevent spamming: only reply every 30 seconds per user? 
            # For simplicity, we just reply. Selfbots shouldn't be too spammy though.
            
            reply = f"**[Auto-Reply]** I am currently AFK.\nReason: {self.afk_reason}\nTime elapsed: {elapsed} seconds."
            
            try:
                await message.reply(reply, delete_after=20)
            except:
                pass # Can't reply or blocked

async def setup(bot):
    await bot.add_cog(AFK(bot))
