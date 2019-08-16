import contextlib

from redbot.core import commands
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
import discord
import random
from random import choice

import aiohttp


class Space(commands.Cog):
    """Show pics of space"""

    __author__ = "kennnyshiwa"

    special_queries = {
        "star wars",
        "Star Wars",
        "Star wars",
        "star Wars"
    }
    starwars = [
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

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    async def apod(self, ctx):
        """Astronomy Picture of the Day"""
        async with ctx.typing():
            async with self.session.get(
                "https://api.nasa.gov/planetary/apod?api_key=pM1xDdu2D9jATa3kc2HE0xnLsPHdoG9cNGg850WR"
            ) as r:
                data = await r.json()
            color = await ctx.embed_color()
            date = data["date"]
            details = data["explanation"]
            url = data["url"]
            title = data["title"]

            if len(details) > 1024:
                await ctx.send("**Astronomy Picture of the Day**\n```{}```".format(details))
                await ctx.send(url)
            else:
                embed = discord.Embed(
                    title="Astronomy Picture of the Day", url="{}".format(url), color=color
                )
                embed.set_image(url=url)
                embed.add_field(name=title, value=details)
                embed.set_footer(text="Today is {}".format(date))
                await ctx.send(embed=embed)

    @staticmethod
    async def do_lookup(query: str) -> list:
        """Run space pic lookup"""
        base_url = "https://images-api.nasa.gov/search?q=%s"
        space_data = []
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % query) as r:
                data = await r.json()
            if data.get("collection")["items"]:  # Only run the code with this key exists
                for x in range(99):  # Fet all 99 items
                    with contextlib.suppress(KeyError):
                        # Ignore Key errors if this index
                        # doesn't exist
                        space_data.append(data.get("collection")["items"][x]["links"][0]["href"])
        if len(space_data) > 10:  # If more than 10 pages get random 10 pages
            return random.sample(space_data, 10)
        return space_data  # this means we have between 0 and 10 pages return all

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace("`", "'")

    @commands.command()
    async def spacepic(self, ctx, *, query):
        """
        Lookup pictures from space!
        Note - Some pictures are from presentations and other educational talks
        """
        pages = []
        async with ctx.typing():
            query = self.escape_query("".join(query))
            if query in self.special_queries: 
                await ctx.send(choice(self.starwars))
                return
            space_data = await self.do_lookup(query)
            if not space_data:
                await ctx.send("I couldn't find anything matching `%s`" % query)
                return
            total_pages = len(space_data)  # Get total page count
            for c, i in enumerate(space_data, 1):  # Done this so I could get page count `c`
                space_data_clean = i.replace(" ", "%20")
                embed = discord.Embed(
                    title="Results from space",
                    description="Query was `%s`" % query,
                    color=await ctx.embed_color(),
                )
                embed.set_image(url=space_data_clean)
                embed.set_footer(text=f"Page {c}/{total_pages}")
                # Set a footer to let the user
                # know what page they are in
                pages.append(embed)
                # Added this embed to embed list that the menu will use
        if pages:  # Only show menu if there pages in list otherwise send the Error message
            return await menu(ctx, pages, DEFAULT_CONTROLS)
        await ctx.send("Error when finding message")

    @commands.command()
    async def isslocation(self, ctx):
        """Show the Current location of the ISS"""
        async with ctx.typing():
            async with self.session.get("http://api.open-notify.org/iss-now.json") as r:
                data = await r.json()
            color = await ctx.embed_color()
            isslat = data["iss_position"]["latitude"]
            isslong = data["iss_position"]["longitude"]
            embed = discord.Embed(
                title="Current location of the ISS",
                description="Latitude and longitude of the ISS",
                color=color,
            )
            embed.add_field(name="Latitude", value=isslat, inline=True)
            embed.add_field(name="Longitude", value=isslong, inline=True)
            embed.set_thumbnail(url="https://photos.kstj.us/GrumpyMeanThrasher.jpg")
            await ctx.send(embed=embed)

    @commands.command()
    async def astronauts(self, ctx):
        """Show who is currently in space"""
        async with ctx.typing():
            async with self.session.get("http://api.open-notify.org/astros.json") as r:
                data = await r.json()
            color = await ctx.embed_color()
            person1 = data["people"][0]["name"]
            person2 = data["people"][1]["name"]
            person3 = data["people"][2]["name"]
            person4 = data["people"][3]["name"]
            person5 = data["people"][4]["name"]
            person6 = data["people"][5]["name"]
            embed = discord.Embed(
                title="Who's in space?",
                color=color
            )
            embed.add_field(name="Current Astronauts in space", value="{}\n{}\n{}\n{}\n{}\n{}".format(person1, person2, person3, person4, person5, person6), inline=True)
            await ctx.send(embed=embed)
    
    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
