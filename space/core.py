import discord

from redbot.core import Config

import random
import aiohttp
import asyncio
import logging
import contextlib

from random import choice, sample

log = logging.getLogger("red.Cog.Space")


class Core:
    def __init__(self, bot):
        self.bot = bot
        self.cache: dict
        self.config: Config
        self.session: aiohttp.ClientSession()
        self.auto_apod_loop: bot.loop
        self.new_channels_loop: bot.loop

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
        self.auto_apod_loop.cancel()
        self.new_channels_loop.cancel()

    async def get_data(self, url):
        """Function used to fetch data from APIs."""
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    log.error(f"Can't get data from {url}, code: {resp.status}")
                    return None
                data = await resp.json()
                return data
        except aiohttp.client_exceptions.ClientConnectionError as error:
            log.error(str(error))
            return None

    async def apod_text(self, data):
        if not data:
            return "Astronomy Picture of the Day: `Impossible to get Nasa API.`"

        details = data["explanation"]
        title = data["title"]
        url = data["url"]
        date = data["date"]
        if len(details) > 1024:
            return f"**Astronomy Picture of the Day**\n\n__{title}__```{details}```Today is **{date}**\n{url}"
        else:
            em = discord.Embed(
                color=self.bot.color, title="Astronomy Picture of the Day", url="{}".format(url)
            )
            em.set_image(url=url)
            em.add_field(name=title, value=details)
            em.set_footer(text="Today is {}".format(date))
            return em

    async def auto_apod(self, bot):
        """
        The task for sending APOD every day automatically.
        Check every 15 minutes to know if there is a new image.
        """
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Space"):
            data = await self.get_data(
                "https://api.nasa.gov/planetary/apod?api_key=pM1xDdu2D9jATa3kc2HE0xnLsPHdoG9cNGg850WR"
            )
            if self.cache["date"] != data["date"]:
                all_channels = await self.config.all_channels()
                for channels in all_channels.items():
                    if channels[1]["auto_apod"]:
                        channel = bot.get_channel(id=channels[0])
                        await self.maybe_send_embed(channel, await self.apod_text(data))
                self.cache["date"] = data["date"]
            else:
                await asyncio.sleep(900)
                continue

    async def check_new_channels(self, bot):
        """
        Task used to check if there is new channels in config file.
        Check every 5 seconds.
        """
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Space"):
            await asyncio.sleep(5)
            if self.cache["new_channels"]:
                all_channels = await self.config.all_channels()
                for channels in all_channels.items():
                    if channels[1]["auto_apod"]:
                        for new_channels in self.cache["new_channels"]:
                            channel = bot.get_channel(id=new_channels)
                            msg = await self.apod_text(
                                await self.get_data(
                                    "https://api.nasa.gov/planetary/apod?api_key=pM1xDdu2D9jATa3kc2HE0xnLsPHdoG9cNGg850WR"
                                )
                            )
                            await self.maybe_send_embed(channel, msg)
                            self.cache["new_channels"].remove(new_channels)

    def star_wars_gifs(self):
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

    async def get_space_pic_data(self, ctx, query: str):
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

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace("`", "'")

    async def maybe_send_embed(self, type, msg):
        try:
            if isinstance(msg, discord.Embed):
                await type.send(embed=msg)
            else:
                await type.send(msg)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as error:
            log.error(str(error))
            return
