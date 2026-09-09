import discord
from discord.ext import commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['cl', 'clear'])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def purge(self, ctx, amount: int):
        """Delete your own messages."""
        if amount < 1:
            await ctx.send("Amount must be at least 1.")
            return

        deleted = 0
        async for message in ctx.channel.history(limit=amount * 2): # Check more messages to find own
            if message.author == self.bot.user:
                try:
                    await message.delete()
                    deleted += 1
                    if deleted >= amount:
                        break
                    await asyncio.sleep(0.8) # Avoid rate limits
                except Exception as e:
                    print(f"Failed to delete message: {e}")
        
        confirmation = await ctx.send(f"Deleted {deleted} messages.")
        await asyncio.sleep(3)
        await confirmation.delete()

    @commands.command(aliases=['bc'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def botclear(self, ctx, limit: int = 100):
        """Delete all your bot messages in this channel. Scans last <limit> messages (default 100)."""
        if limit < 1 or limit > 500:
            await ctx.send("Limit must be between 1 and 500.")
            return

        deleted = 0
        try:
            await ctx.message.delete()
        except Exception:
            pass

        async for message in ctx.channel.history(limit=limit):
            if message.author == self.bot.user:
                try:
                    await message.delete()
                    deleted += 1
                    await asyncio.sleep(0.8)  # Avoid rate limits
                except Exception:
                    pass

        confirmation = await ctx.send(f"Cleared {deleted} bot messages.", delete_after=3)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
