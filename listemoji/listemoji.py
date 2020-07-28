import discord
from redbot.core import commands, checks
from redbot.core.utils.chat_formatting import pagify

__author__ = "kennnyshiwa"


class Listemoji(commands.Cog):
    """List all available emojis in a server"""

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.admin_or_permissions(manage_emojis=True)
    async def listemoji(self, ctx: commands.Context, ids: bool = False):
        """Lists all available emojis in a server, perfect for an emoji channel"""
        description = f"Emojis for {ctx.guild.name}"
        if not ids:
            text = f"{description}\n\n" + "\n".join(
                [f"{emoji} `:{emoji.name}:`" for emoji in ctx.guild.emojis]
            )
        else:
            text = f"{description}\n\n" + "\n".join(
                [
                    f"{emoji} `:{emoji.name}:` `<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>`"
                    for emoji in ctx.guild.emojis
                ]
            )
        for page in pagify(text):
            await ctx.send(page)
