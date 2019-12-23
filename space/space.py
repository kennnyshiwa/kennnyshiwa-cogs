import discord

from redbot.core import commands, checks, Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.common_filters import filter_mass_mentions

import random
import aiohttp
import asyncio
import contextlib

from random import choice

from .core import Core


class Space(Core, commands.Cog):
    """Show pics of space."""

    __author__ = "kennnyshiwa"

    def __init__(self, bot):
        self.bot = bot
        self.cache = {"date": None, "new_channels": []}

        default_channel = dict(auto_apod=False, last_apod_sent=None)
        self.config = Config.get_conf(self, 3765640575174574082, force_registration=True)
        self.config.register_channel(**default_channel)

        self.session = aiohttp.ClientSession()
        self.auto_apod_loop = bot.loop.create_task(self.auto_apod(bot))
        self.new_channels_loop = bot.loop.create_task(self.check_new_channels(bot))

    @commands.group()
    @checks.mod_or_permissions(manage_channels=True)
    async def spaceset(self, ctx):
        """Group commands for Space cog settings."""
        pass

    @spaceset.command()
    async def autoapod(self, ctx, channel: discord.TextChannel = None):
        """
        Choose if you want to automatically receive \"Astronomy Picture of the Day\" every day.

        Set to actual channel by default. You can also use `[p]spaceset autoapod <channel_name>` if you want to receive APOD in others channels.
        Use the same command to disable it.
        """
        channel = ctx.channel if not channel else channel
        auto_apod = await self.config.channel(channel).auto_apod()
        await self.config.channel(channel).auto_apod.set(not auto_apod)
        if not auto_apod:
            self.cache["new_channels"].append(channel.id)
        msg = (
            "I will now automatically send Astronomy Picture of the Day every day in this channel."
            if not auto_apod
            else "No longer sending Astronomy Picture of the Day every day in this channel."
        )
        await channel.send(msg)
        await ctx.tick()

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def apod(self, ctx):
        """Astronomy Picture of the Day."""
        async with ctx.typing():
            msg = await self.apod_text(
                await self.get_data(
                    "https://api.nasa.gov/planetary/apod?api_key=pM1xDdu2D9jATa3kc2HE0xnLsPHdoG9cNGg850WR"
                ),
                ctx,
            )
            await self.maybe_send_embed(ctx, msg)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def spacepic(self, ctx, *, query):
        """
        Lookup pictures from space!
        Note - Some pictures are from presentations and other educational talks
        """
        async with ctx.typing():
            query = self.escape_query("".join(query))
            space_data = await self.get_space_pic_data(ctx, query)
            if space_data is None:
                await ctx.send(
                    f"Looks like you got lost in space looking for `{filter_mass_mentions(query)}`"
                )
                return
            if space_data is False:
                return
            if query.lower() == "star wars":
                await ctx.send(self.star_wars_gifs())
                return

            pages = []
            total_pages = len(space_data)  # Get total page count
            for c, i in enumerate(space_data, 1):  # Done this so I could get page count `c`
                space_data_clean = i.replace(" ", "%20")
                embed = discord.Embed(
                    title="Results from space",
                    description=f"Query was `{query}`",
                    color=await ctx.embed_color(),
                )
                embed.set_image(url=space_data_clean)
                embed.set_footer(text=f"Page {c}/{total_pages}")
                # Set a footer to let the user
                # know what page they are in
                pages.append(embed)
                # Added this embed to embed list that the menu will use
        return await menu(ctx, pages, DEFAULT_CONTROLS)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def isslocation(self, ctx):
        """Show the Current location of the ISS."""
        async with ctx.typing():
            data = await self.get_data("http://api.open-notify.org/iss-now.json")
            if not data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return

            embed = discord.Embed(
                title="Current location of the ISS",
                description="Latitude and longitude of the ISS",
                color=await ctx.embed_color(),
            )
            embed.add_field(name="Latitude", value=data["iss_position"]["latitude"], inline=True)
            embed.add_field(name="Longitude", value=data["iss_position"]["longitude"], inline=True)
            embed.set_thumbnail(url="https://photos.kstj.us/GrumpyMeanThrasher.jpg")
        return await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def astronauts(self, ctx):
        """Show who is currently in space."""
        async with ctx.typing():
            data = await self.get_data("http://api.open-notify.org/astros.json")
            if not data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return

            astrosnauts = []
            for astros in data["people"]:
                astrosnauts.append(astros["name"])

            embed = discord.Embed(title="Who's in space?", color=await ctx.embed_color())
            embed.add_field(name="Current Astronauts in space", value="\n".join(astrosnauts))
        return await ctx.send(embed=embed)
