import discord
from redbot.core import commands

class Screenshare(commands.Cog):
    """Generate a screenshare link for a voice channel"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def screenshare(self, ctx):
        """Generate the screenshare link for the authors current voice channel"""
        guildid = ctx.guild.id

        if not ctx.message.author.voice:
            await ctx.send("You are currently not in a voice channel")
            return
        
        channel = ctx.message.author.voice.channel
        channelid = channel.id

        await ctx.send(
            "Here is the link for screen sharing in {channel}\n"
            "<https://discordapp.com/channels/{guildid}/{channelid}>".format(
                channel = channel,
                guildid = guildid,
                channelid = channelid
            )
        )




        
        