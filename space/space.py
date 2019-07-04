from redbot.core import commands
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
import discord
import random
import datetime

import aiohttp

class Space(commands.Cog):
    """Show pics of space"""

    __author__ = "kennnyshiwa"    

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    async def apod(self, ctx):
        """Astronomy Picture of the Day"""
        async with ctx.typing():
            async with self.session.get("https://api.nasa.gov/planetary/apod?api_key=pM1xDdu2D9jATa3kc2HE0xnLsPHdoG9cNGg850WR") as r:
                data = await r.json()
            color = await ctx.embed_color()
            date = data["date"]
            details = data["explanation"]
            url = data["url"]
            title = data["title"]

            if (len(details)) > 1024:
                await ctx.send("**Astronomy Picute of the Day**\n```{}```".format(details))
                await ctx.send(url)
            else:
                embed = discord.Embed(
                    title="Astronomy Picture of the Day",
                    url="{}".format(url),
                    color=color 
                )
                embed.set_image(url=url)
                embed.add_field(name=title, value=details)
                embed.set_footer(text="Today is {}".format(date))
                await ctx.send(embed=embed)

    @staticmethod
    async def do_lookup(query: str) -> dict:
        """Run space pic lookup"""
        base_url = (
            "https://images-api.nasa.gov/search?q=%s"
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % query) as r:
                data = await r.json()
            if not data.get('collection')['items']:
                return None
            x = 0
            for x in range(99):
                    x = random.randint(1,99)
                    space_data = (data.get('collection')['items'][x]['links'][0]['href'])
                    return space_data

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace("`", "'")

    @commands.command()
    async def spacepic(self, ctx, *, query):
        """
        Lookup pictures from space!
        Note - Some pictures are from presentations and other educational talks
        """
        async with ctx.typing():
            query = self.escape_query("".join(query))
            space_data = await self.do_lookup(query)
            if not space_data:
                await ctx.send("I couldn't find anything matching `%s`" % query)
                return
            space_data_clean = space_data.replace(" ","%20")
            print(space_data_clean)
            embed = discord.Embed(
                title="Results from space",
                description="Query was `%s`" % query,
                color=await ctx.embed_color(),
            )
            embed.set_image(url=space_data_clean)
            await ctx.send(embed=embed)

    @commands.command()
    async def isslocation(self, ctx):
        """Show the Current location of the ISS"""
        async with ctx.typing():
            async with self.session.get("http://api.open-notify.org/iss-now.json") as r:
                data = await r.json()
            color = await ctx.embed_color()
            isslat = data['iss_position']['latitude']
            isslong = data['iss_position']['longitude']
            embed = discord.Embed(
                title="Current location of the ISS",
                description="Latitude and longitude of the ISS",
                color=color
            )
            embed.add_field(name="Latitude", value=isslat, inline=True)
            embed.add_field(name="Longitude", value=isslong, inline=True)
            embed.set_thumbnail(url="https://photos.kstj.us/GrumpyMeanThrasher.jpg")
            await ctx.send(embed=embed)


    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())