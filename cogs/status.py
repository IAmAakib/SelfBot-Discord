import discord
from discord.ext import commands, tasks
import asyncio
from itertools import cycle

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status = cycle(['with Discord API', 'Visual Studio Code', 'Cyberpunk 2077', 'Humans'])

    @tasks.loop(seconds=10)
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(next(self.status)))

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()

    @commands.command(aliases=['st'])
    async def stream(self, ctx, *, message):
        """Set a streaming status."""
        self.change_status.cancel() # Stop rotation
        await self.bot.change_presence(activity=discord.Streaming(name=message, url="https://twitch.tv/monstercat"))
        await ctx.send(f"Streaming status set to: **{message}**")

    @commands.command(aliases=['l'])
    async def listen(self, ctx, *, message):
        """Set a listening status."""
        self.change_status.cancel()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=message))
        await ctx.send(f"Listening status set to: **{message}**")

    @commands.command(aliases=['w'])
    async def watch(self, ctx, *, message):
        """Set a watching status."""
        self.change_status.cancel()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message))
        await ctx.send(f"Watching status set to: **{message}**")

    @commands.command(aliases=['on'])
    async def online(self, ctx):
        """Set status to Online."""
        self.change_status.cancel()
        await self.bot.change_presence(status=discord.Status.online)
        await ctx.send("Status set to: **Online**")

    @commands.command(aliases=['id'])
    async def idle(self, ctx):
        """Set status to Idle."""
        self.change_status.cancel()
        await self.bot.change_presence(status=discord.Status.idle)
        await ctx.send("Status set to: **Idle**")

    @commands.command(aliases=['dn', 'dnd'])
    async def donotdisturb(self, ctx):
        """Set status to Do Not Disturb."""
        self.change_status.cancel()
        await self.bot.change_presence(status=discord.Status.dnd)
        await ctx.send("Status set to: **Do Not Disturb**")

    @commands.command(aliases=['r', 'cycle'])
    async def rotate(self, ctx):
        """Resume status rotation."""
        if not self.change_status.is_running():
            self.change_status.start()
            await ctx.send("Status rotation resumed.")
        else:
            await ctx.send("Status rotation is already running.")

async def setup(bot):
    await bot.add_cog(Status(bot))
