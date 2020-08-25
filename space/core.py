import discord

from redbot.core.bot import Red
from redbot.core import commands, Config

import random
import aiohttp
import asyncio
import logging
import contextlib

from typing import Union
from random import choice, sample

log = logging.getLogger("red.kennnyshiwa-cogs.Space")


class Core(commands.Cog):

    __author__ = "kennnyshiwa"

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot: Red):
        self.bot = bot
        self.cache = []

        self.config = Config.get_conf(self, 3765640575174574082, force_registration=True)
        self.config.register_channel(auto_apod=False, last_apod_sent=None)

        self.session = aiohttp.ClientSession()
        self.auto_apod_loop = bot.loop.create_task(self.auto_apod())
        self.new_channels_loop = bot.loop.create_task(self.check_new_channels())

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
        self.auto_apod_loop.cancel()
        self.new_channels_loop.cancel()
        self.cache.clear()

    async def auto_apod(self):
        """
        The task for sending APOD every day automatically.
        Check every 15 minutes to know if there is a new image.
        """
        await self.bot.wait_until_ready()
        while True:
            try:
                data = await self.get_data("https://api.martinethebot.com/images/apod")
                if not data:
                    continue
                all_channels = await self.config.all_channels()
                for channels in all_channels.items():
                    if channels[1]["auto_apod"]:
                        if channels[1]["last_apod_sent"] != data["date"]:
                            channel = self.bot.get_channel(channels[0])
                            if not channel:
                                await self.config.channel_from_id(channels[0]).auto_apod.set(False)
                                continue
                            await self.maybe_send_embed(
                                channel, await self.apod_text(data, channel)
                            )
                            await self.config.channel(channel).last_apod_sent.set(data["date"])
            except Exception as error:
                log.exception("Exception in auto_apod task: ", exc_info=error)
            await asyncio.sleep(900)

    async def check_new_channels(self):
        """
        Task used to check if there is new channels in config file.
        Check every 2 minutes.
        """
        await self.bot.wait_until_ready()
        while True:
            await asyncio.sleep(120)
            try:
                if self.cache:
                    all_channels = await self.config.all_channels()
                    for channels in all_channels.items():
                        if channels[1]["auto_apod"]:
                            for new_channels in self.cache:
                                channel = self.bot.get_channel(new_channels)
                                if not channel:
                                    await self.config.channel_from_id(new_channels).auto_apod.set(
                                        False
                                    )
                                    continue
                                msg = await self.apod_text(
                                    await self.get_data(
                                        "https://api.martinethebot.com/images/apod"
                                    ),
                                    channel,
                                )
                                await self.maybe_send_embed(channel, msg)
                                self.cache.remove(new_channels)
            except Exception as error:
                log.exception("Exception in check_new_channels task: ", exc_info=error)

    async def get_data(self, url: str):
        """Function used to fetch data from APIs."""
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data
        except aiohttp.ClientConnectionError:
            return None

    async def apod_text(self, data: dict, context: Union[commands.Context, discord.TextChannel]):
        if not data:
            return "Astronomy Picture of the Day: `Impossible to get Nasa API.`"

        details = data["explanation"]
        if len(details) > 2048:
            return f"**Astronomy Picture of the Day**\n\n__{data['title']}__```{details}```Today is **{data['date']}**\n{data['url']}"
        else:
            em = discord.Embed(
                color=await self.bot.get_embed_color(context)
                if hasattr(self.bot, "get_embed_color")
                else self.bot.color,
                title=data["title"],
                url=data["url"],
                description=details,
            )
            em.set_author(
                name="Astronomy Picture of the Day",
                url="https://apod.nasa.gov/apod/astropix.html",
                icon_url="https://i.imgur.com/Wh8jY9c.png",
            )
            em.set_image(url=data["url"])
            em.set_footer(
                text="{copyright}Today is {date}".format(
                    copyright=f"Image Credits: {data['copyright']} • "
                    if data.get("copyright")
                    else "",
                    date=data["date"],
                )
            )
            return em

    @staticmethod
    def star_wars_gifs():
        gifs = choice(
            [
                "https://media2.giphy.com/media/bR4poFy22rgUE/source.gif",
                "https://media.giphy.com/media/pvDp7Ewpzt0o8/giphy.gif",
                "https://media2.giphy.com/media/M4iOAkEAPwAnK/giphy.gif",
                "https://media.giphy.com/media/4GXQSVCsrbAQV1gqoS/giphy.gif",
                "https://media2.giphy.com/media/3o84sq21TxDH6PyYms/giphy.gif",
                "https://media.giphy.com/media/l3fZPV4s1oKmZiXJK/giphy.gif",
                "https://i.imgur.com/jA2Jmvl.gif",
                "https://media2.giphy.com/media/3o7abrH8o4HMgEAV9e/giphy.gif",
                "https://media3.giphy.com/media/3h2lUwrZKilQKbAK6f/source.gif",
                "https://media2.giphy.com/media/10LNU0do0k7blS/source.gif",
                "https://media3.giphy.com/media/TCmUPOuvhNzX2/source.gif",
                "https://media3.giphy.com/media/rsIuy6pUXTvSU/source.gif",
            ]
        )
        return gifs

    async def get_space_pic_data(self, ctx: commands.Context, query: str):
        """Run space pic lookup"""
        data = await self.get_data(f"https://images-api.nasa.gov/search?q={query}")
        if not data:
            await ctx.send("I can't get the data from the API. Try again later.")
            return False

        space_data = []
        try:
            if data.get("collection")["items"]:  # Only run the code with this key exists
                for x in range(99):  # Fet all 99 items
                    with contextlib.suppress(KeyError, IndexError):
                        # Ignore Key errors if this index
                        # doesn't exist
                        space_data.append(data.get("collection")["items"][x]["links"][0]["href"])
        except Exception:
            return None
        if not space_data:
            return None
        if len(space_data) > 10:  # If more than 10 pages get random 10 pages
            return sample(space_data, 10)
        return space_data  # this means we have between 0 and 10 pages return all

    @staticmethod
    def escape_query(query: str) -> str:
        """Escape mentions from queries"""
        return query.replace("`", "'")

    @staticmethod
    async def maybe_send_embed(
        destination: Union[commands.Context, discord.TextChannel], msg: str
    ):
        try:
            if isinstance(msg, discord.Embed):
                await destination.send(embed=msg)
            else:
                await destination.send(msg)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return
