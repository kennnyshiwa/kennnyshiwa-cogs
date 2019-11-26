import discord
from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify

__author__ = "kennnyshiwa"


class Listemoji(commands.Cog):
    """List all available emojis in a server"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.admin_or_permissions(manage_emojis=True)
    async def listemoji(self, ctx):
    """Lists all available emojis in a server, perfect for an emoji channel"""
        description = f"Emojis for {ctx.guild.name}"
        text = f"{description}" "\n\u200b\n" + "\n".join(
            [f"{emoji} `:{emoji.name}:`" for emoji in ctx.guild.emojis]
        )
        for page in pagify(text):
            await ctx.send(page)
