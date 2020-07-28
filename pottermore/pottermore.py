import contextlib

from redbot.core import commands, Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from typing import Literal
import discord

import aiohttp
import random

slytherin = "https://cdn.shopify.com/s/files/1/1325/3287/products/HP8040B_930f8033-607f-41ee-a8e4-fa90871ce7a7.png?v=1546231154"
gryffindor = "https://cdn10.bigcommerce.com/s-9p3fydit/products/370/images/1328/gryff1c__34591.1449620321.1280.1280.PNG?c=2"
ravenclaw = "https://cdn10.bigcommerce.com/s-9p3fydit/products/372/images/1332/raven1c__54237.1449620971.1200.1200.PNG?c=2"
hufflepuff = "https://cdn.shopify.com/s/files/1/0221/1146/products/Hufflepuff_Embroidered_Patch_Scaled_large.png?v=1553528874"
harry = "https://www.freepngimg.com/thumb/harry_potter/5-2-harry-potter-png-file.png"
hermione = "https://66.media.tumblr.com/3ce8453be755f31f93381918985b4918/tumblr_nn2lopIypj1rxkqbso1_1280.png"
voldemort = (
    "https://vignette.wikia.nocookie.net/harrypotter/images/6/6e/VoldemortHeadshot_DHP1.png"
)
snape = "https://vignette.wikia.nocookie.net/harrypotter/images/a/a3/Severus_Snape.jpg"
draco = "https://vignette.wikia.nocookie.net/harrypotter/images/7/7e/Draco_Malfoy_TDH.png"
dumbledore = "https://images.ctfassets.net/bxd3o8b291gf/5ocauY6zAsqGiIgeECw06e/8accc1c586d2be7d9de6a3d9aec37b90/AlbusDumbledore_WB_F1_DumbledoreSmiling_Still_080615_Port.jpg"
ron = "https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/Ron_Weasley_poster.jpg/220px-Ron_Weasley_poster.jpg"
hagrid = "https://vignette.wikia.nocookie.net/harrypotter/images/e/ee/Rubeushagrid.PNG/revision/latest?cb=20161123044204"
ginny = "http://hp-intothefire.wdfiles.com/local--files/ginny/ginny.jpg"
sirius = "https://vignette.wikia.nocookie.net/harrypotter/images/7/75/Sirius_Black_profile.jpg/revision/latest?cb=20150918055024"
mcgonagall = "https://vignette.wikia.nocookie.net/harrypotter/images/6/65/ProfessorMcGonagall-HBP.jpg/revision/latest?cb=20100612114856"


class Pottermore(commands.Cog):
    """Lookup information about the Harry Potter Universe"""

    __author__ = "kennnyshiwa"

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """This cog stores a user ID to match them to their Harry Potter house,
        this will wipe their saved house from the cog"""
        await self.config.user_from_id(user_id).clear()


    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)

        default_user = {"house": None}

        self.config.register_user(**default_user)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def housesort(self, ctx):
        """Find your Harry Potter House"""
        if await self.config.user(ctx.author).house() is None:
            async with self.session.get("https://www.potterapi.com/v1/sortinghat") as r:
                data = await r.json()
            house = data
            await self.config.user(ctx.author).house.set(str(house))
        color = await ctx.embed_color()
        house_user = await self.config.user(ctx.author).house()
        if house_user == "Slytherin":
            image = slytherin
            embed = discord.Embed(
                title="Find your Harry Potter House", description=house_user, color=color
            )
            embed.set_thumbnail(url=image)
        if house_user == "Gryffindor":
            image = gryffindor
            embed = discord.Embed(
                title="Find your Harry Potter House", description=house_user, color=color
            )
            embed.set_thumbnail(url=image)
        if house_user == "Ravenclaw":
            image = ravenclaw
            embed = discord.Embed(
                title="Find your Harry Potter House", description=house_user, color=color
            )
            embed.set_thumbnail(url=image)
        if house_user == "Hufflepuff":
            image = hufflepuff
            embed = discord.Embed(
                title="Find your Harry Potter House", description=house_user, color=color
            )
            embed.set_thumbnail(url=image)
        await ctx.send(embed=embed)

    @staticmethod
    async def do_lookup(query: str) -> list:
        """Run pottermore lookup pic lookup"""
        base_url = "https://www.potterapi.com/v1/characters/?key=$2a$10$ZiItg0fhdYll4R2A4hNareLdTmuYByHnzL9mSqw3r7Mkh/nMh2WUa&name=%s"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % query) as r:
                data = await r.json()
                if not data or isinstance(data, dict):
                    return None
                return data[0]

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace("`", "'")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def charactersearch(self, ctx, *, query):
        """
        Search for Harry Potter characters
        
        Note: Searchs are case senseative and require full name
        """
        async with ctx.typing():
            query = self.escape_query("".join(query))
        pottermore_data = await self.do_lookup(query)
        if not pottermore_data:
            await ctx.send("🔮 Muggle error! Could not find `%s`" % query)
            return
        if "alias" in pottermore_data:
            alias = pottermore_data["alias"]
        else:
            alias = ""
        embed = discord.Embed(
            title=pottermore_data["name"], description=alias, color=await ctx.embed_color()
        )
        name = pottermore_data["name"]
        if name == "Harry Potter":
            embed.set_thumbnail(url=harry)
        if name == "Hermione Granger":
            embed.set_thumbnail(url=hermione)
        if name == "Lord Voldemort":
            embed.set_thumbnail(url=voldemort)
        if name == "Severus Snape":
            embed.set_thumbnail(url=snape)
        if name == "Albus Dumbledore":
            embed.set_thumbnail(url=dumbledore)
        if name == "Draco Malfoy":
            embed.set_thumbnail(url=draco)
        if name == "Ron Weasley":
            embed.set_thumbnail(url=ron)
        if name == "Rubeus Hagrid":
            embed.set_thumbnail(url=hagrid)
        if name == "Ginny Weasley":
            embed.set_thumbnail(url=ginny)
        if name == "Sirius Black":
            embed.set_thumbnail(url=sirius)
        if name == "Minerva McGonagall":
            embed.set_thumbnail(url=mcgonagall)
        if "house" in pottermore_data:
            embed.add_field(name="House", value=pottermore_data["house"], inline=True)
        if "school" in pottermore_data:
            embed.add_field(name="School Name", value=pottermore_data["school"], inline=True)
        if "role" in pottermore_data:
            embed.add_field(name="Role", value=pottermore_data["role"], inline=True)
        if "wand" in pottermore_data:
            embed.add_field(name="Wand", value=pottermore_data["wand"], inline=True)
        if "boggart" in pottermore_data:
            embed.add_field(name="Boggart", value=pottermore_data["boggart"], inline=True)
        if "patronus" in pottermore_data:
            embed.add_field(name="Patronus", value=pottermore_data["patronus"], inline=True)
        if pottermore_data["ministryOfMagic"] == False:
            embed.add_field(name="Ministry of Magic", value="Not a member", inline=True)
        else:
            embed.add_field(name="Ministry of Magic", value="Member", inline=True)
        if pottermore_data["orderOfThePhoenix"] == False:
            embed.add_field(name="Order Of The Phoenix", value="Not a member", inline=True)
        else:
            embed.add_field(name="Order Of The Phoenix", value="Member", inline=True)
        if pottermore_data["dumbledoresArmy"] == False:
            embed.add_field(name="Dumbledores Army", value="Not a member", inline=True)
        else:
            embed.add_field(name="Dumbledores Army", value="Member", inline=True)
        if pottermore_data["deathEater"] == False:
            embed.add_field(name="DeathEater", value="No", inline=True)
        else:
            embed.add_field(name="DeathEater", value="Yes", inline=True)
        embed.add_field(name="Blood Status", value=pottermore_data["bloodStatus"], inline=True)
        embed.add_field(name="Species", value=pottermore_data["species"], inline=True)
        if "animagus" in pottermore_data:
            embed.add_field(name="Animagus", value=pottermore_data["animagus"], inline=True)
        await ctx.send(embed=embed)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
