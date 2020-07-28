import asyncio
import discord
import aiohttp
import io
from io import BytesIO
from typing import Any
from datetime import datetime
from redbot.core import Config, checks, commands

from redbot.core.bot import Red

Cog: Any = getattr(commands, "Cog", object)


class Autogallery(Cog):
    """
    Auto post pictures into a gallery!
    """

    __author__ = "kennnyshiwa"

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=376564057517457408, force_registration=True
        )
        default_guild = {
            "channel": None,
            "channels": [],
        }
        
        self.config.register_guild(**default_guild)


    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    @checks.bot_has_permissions(manage_messages=True)
    async def addautogallery(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        """Add a channel to the list of Gallery channels."""
        if channel.id not in await self.config.guild(ctx.guild).channels():
            async with self.config.guild(ctx.guild).channels() as channels:
                channels.append(channel.id)
            await ctx.send(f"{channel.mention} has been added into the Gallery channels list.")
        else:
            await ctx.send(f"{channel.mention} is already in the Gallery channels list.")

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    @checks.bot_has_permissions(manage_messages=True)
    async def rmautogallery(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        """Remove a channel from the list of Gallery channels."""
        if channel.id in await self.config.guild(ctx.guild).channels():
            async with self.config.guild(ctx.guild).channels() as channels:
                channels.remove(channel.id)
            await ctx.send(f"{channel.mention} has been removed from the Gallery channels list.")
        else:
            await ctx.send(f"{channel.mention} already isn't in the Gallery channels list.")
    
    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    @checks.bot_has_permissions(manage_messages=True)
    async def gallerychannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Add the gallery channel for auto posting images"""
        autochannel = await self.config.guild(ctx.guild).channel()
        if autochannel is None:
            if channel is not None:
                channelid = channel.id
            await self.config.guild(ctx.guild).channel.set(channelid)
            await ctx.send(f"{channel.mention} has been set as the gallery channel")
        else:
            await ctx.send(f"{channel.mention} is already in the Gallery channels list.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if message.channel.id not in await self.config.guild(message.guild).channels():
            return
        if not message.attachments:
            return
        gallery = await self.config.guild(message.guild).channel()
        if not gallery:
            return
        gallerychannel = self.bot.get_channel(gallery)
        if not gallerychannel.permissions_for(message.guild.me).embed_links:
            return
        embed = discord.Embed(color=0x4aff00, timestamp=datetime.utcnow())
        for attachment in message.attachments:
            if attachment.filename.endswith(".png") or attachment.filename.endswith(".jpg") or attachment.filename.endswith(".gif"):
                pass
            else:
                return
            embed.set_author(name=message.author, icon_url=str(message.author.avatar_url))
            embed.set_footer(text=message.channel)
            embed.set_image(url=attachment.url)
            await gallerychannel.send(embed=embed)