import discord
from discord.ext import commands
import datetime

class Sniper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages = {}
        self.edited_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignore comments/commands if desired, but for sniper we usually want everything.
        if message.author.bot:
            return
            
        self.sniped_messages[message.channel.id] = {
            'content': message.content,
            'author': message.author,
            'time': datetime.datetime.now(),
            'attachments': message.attachments
        }

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content == after.content:
            return

        self.edited_messages[before.channel.id] = {
            'before': before.content,
            'after': after.content,
            'author': before.author,
            'time': datetime.datetime.now()
        }

    @commands.command(aliases=['s'])
    async def snipe(self, ctx):
        """Snipes the last deleted message."""
        channel_id = ctx.channel.id
        if channel_id in self.sniped_messages:
            sniped = self.sniped_messages[channel_id]
            author = sniped['author']
            content = sniped['content']
            time_sniped = sniped['time'].strftime("%I:%M %p")
            
            msg = f"**Sniped Message**\n**User:** {author} (`{author.id}`)\n**Time:** {time_sniped}\n\n{content}"
            
            if sniped['attachments']:
                msg += f"\n**Attachment:** {sniped['attachments'][0].url}"
                
            await ctx.send(msg)
        else:
            await ctx.send("There's nothing to snipe!")

    @commands.command(aliases=['es'])
    async def editsnipe(self, ctx):
        """Snipes the last edited message."""
        channel_id = ctx.channel.id
        if channel_id in self.edited_messages:
            data = self.edited_messages[channel_id]
            author = data['author']
            time_edited = data['time'].strftime("%I:%M %p")

            msg = (
                f"**Sniped Edit**\n"
                f"**User:** {author} (`{author.id}`)\n"
                f"**Time:** {time_edited}\n\n"
                f"**Before:** {data['before']}\n"
                f"**After:** {data['after']}"
            )
            await ctx.send(msg)
        else:
            await ctx.send("No recent edits to snipe!")

async def setup(bot):
    await bot.add_cog(Sniper(bot))
