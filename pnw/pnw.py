import discord
import aiohttp
import asyncio
from aiohttp.client_exceptions import ContentTypeError
from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import box


class PnW(commands.Cog):
    """PnW Stuff"""

    __author__ = ["kennnyshiwa"]

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def initialize(self) -> None:
        """
        Move the API keys from cog stored config to core bot config if they exist.
        """
        pnw_key = await self.config.pnw_key()
        if hasattr(self.bot, "get_shared_api_tokens"):
            if pnw_key is not None and "pnw" not in await self.bot.get_shared_api_tokens():
                await self.bot.set.shared_api_tokens("pnw", value={"api_key": pnw_key})
                await self.config.pnw_key.clear()
        else:
            if pnw_key is not None and "pnw" not in await self.bot.db.api_tokens():
                await self.bot.db.api_tokens.set_raw("pnw", value={"api_key": pnw_key})
                await self.config.pnw_key.clear()

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace("`", "'")

    @checks.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def pnwkey(self, ctx):
        """
            Explain how to set PNW API key.
            Note: You have to have a PNW account to get a api key
        """
        message = (
            "So first, to get a PNW api key you need to have an account "
            "otherwise you can't use this cog.\n\n"
            "To find your API key:\n"
            "1. Login on PNW [here](https://politicsandwar.com/login/)\n"
            "2. Go on your [account](https://politicsandwar.com/account/)\n"
            "3. Scroll the bottom and copy the Key\n"
            "4. Use in DM `{}set api pnw api_key your_api_key_here`\n"
            "6. There you go! You can now use the PNW cog."
        ).format(ctx.prefix)
        await ctx.maybe_send_embed(message)

    @staticmethod
    async def do_lookup(ctx, nid) -> list:
        """
        Run Nation lookup.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "http://politicsandwar.com/api/nation/id=%s&key={}&$format=json".format(pnw_key)

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % nid) as r:
                data = await r.json()
                if not data:
                    return
                return data

    @staticmethod
    async def nations_lookup(ctx):
        """
        Lookup all nations.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "https://politicsandwar.com/api/nations/?vm=true&key={}".format(pnw_key)

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()
                if not data:
                    return
                return data

    @staticmethod
    async def alliances_lookup(ctx):
        """
        Run Alliance Lookup.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "http://politicsandwar.com/api/alliances/?key={}&$format=json".format(pnw_key)

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()
                if not data:
                    return
                return data

    @staticmethod
    async def alliance_lookup(ctx, alid: str) -> list:
        """
        Run Alliance Lookup.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "http://politicsandwar.com/api/alliance/id=%s&key={}&$format=json".format(
            pnw_key
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % alid) as r:
                data = await r.json()
                if not data:
                    return None
                return data

    @staticmethod
    async def city_api(ctx, alid: str) -> list:
        """
        Run City Lookup.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "http://politicsandwar.com/api/city/id=%s&key={}&$format=json".format(pnw_key)

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % alid) as r:
                data = await r.json()
                if not data:
                    return
                return data

    @staticmethod
    async def tradeprice_lookup(ctx, query):
        """
        Lookup resources trading info.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "http://politicsandwar.com/api/tradeprice/resource=%s&key={}&$format=json".format(
            pnw_key
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % query) as r:
                data = await r.json()
                if not data:
                    return
                return data

    @staticmethod
    async def bank_lookup(ctx, alid: str) -> list:
        """
        Run Bank Lookup.
        """
        if hasattr(ctx.bot, "get_shared_api_tokens"):  # 3.2
            api = await ctx.bot.get_shared_api_tokens("pnw")
            pnw_key = api.get("api_key")
        else:
            api = await ctx.bot.db.api_tokens.get_raw("pnw")
            pnw_key = api["api_key"]
        if not pnw_key:
            return await ctx.send(
                "You need to set an API key! Check ``{}pwnkey`` for instructions\n".format(
                    ctx.prefix
                )
            )
        base_url = "http://politicsandwar.com/api/alliance-bank/?allianceid=%s&key={}&$format=json".format(
            pnw_key
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % alid) as r:
                data = await r.json()
                if not data:
                    return
                return data

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def nation(self, ctx, *, name):
        """
        Look up a nation.
        """
        await ctx.send("This may take a while.....")
        async with ctx.typing():
            name = self.escape_query("".join(name))
            key = False
            nations_data = await self.nations_lookup(ctx)
            success = nations_data["success"]
            try:
                if success == False:
                    await ctx.send(
                        f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                    )
                    return
            except:
                pass

            for I in nations_data["nations"]:
                if name.lower() == I["nation"].lower():
                    key = True
                    nid = I["nationid"]
            if key == True:
                pass
            else:
                nid = name
            nation_data = await self.do_lookup(ctx, nid)
            if not nation_data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return
            success = nation_data["success"]
            if success == False:
                await ctx.send("No such nation exists! Please enter a vaild nation ID")
                return
            name = nation_data["name"]
            nationid = nation_data["nationid"]
            continent = nation_data["continent"]
            color = nation_data["color"]
            leadername = nation_data["leadername"]
            nationrank = nation_data["nationrank"]
            score = nation_data["score"]
            alliance = nation_data["alliance"]
            last_active = nation_data["minutessinceactive"]
            domestic_policy = nation_data["domestic_policy"]
            war_policy = nation_data["war_policy"]
            founded = nation_data["founded"]
            age = nation_data["daysold"]
            flag = nation_data["flagurl"]
            cities = nation_data["cities"]

            embed = discord.Embed(
                title="Nation Info for {}".format(name),
                url="https://politicsandwar.com/nation/id={}".format(nationid),
                color=await ctx.embed_color(),
            )

            embed.add_field(name="Leader Name", value=leadername, inline=True)
            embed.add_field(name="Color", value=color, inline=True)
            embed.add_field(name="Rank", value=nationrank, inline=True)
            embed.add_field(name="Score", value=score, inline=True)
            embed.add_field(name="Alliance", value=alliance, inline=True)
            embed.add_field(name="Continent", value=continent, inline=True)
            embed.add_field(name="Domestic Policy", value=domestic_policy, inline=True)
            embed.add_field(name="War Policy", value=war_policy, inline=True)
            embed.add_field(name="Age of nation", value=f"{age} Days Old", inline=True)
            embed.add_field(name="Number of Cities", value=cities, inline=True)
            embed.set_image(url=flag)
            embed.set_footer(
                text="Last active: {} minutes ago | Founded {}".format(last_active, founded)
            )
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def alliance(self, ctx, *, name):
        """
        Lookup an Alliance with an ID.
        """
        async with ctx.typing():
            name = self.escape_query("".join(name))
            key = False
            alliances_data = await self.alliances_lookup(ctx)
            success = alliances_data["success"]
            try:
                if success == False:
                    await ctx.send(
                        f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                    )
                    return
            except:
                pass

            for I in alliances_data["alliances"]:
                if name.lower() == I["name"].lower():
                    key = True
                    alid = I["id"]
            if key == True:
                pass
            else:
                alid = name
            alliance_data = await self.alliance_lookup(ctx, alid)
            if not alliance_data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return
            if alliance_data is None:
                await ctx.send("Can't find that alliance")
                return
            try:
                if alliance_data["error"]:
                    await ctx.send("Can't find that alliance")
                    return
            except:
                pass
            name = alliance_data["name"]
            allianceid = alliance_data["allianceid"]
            if alliance_data["irc"] == "":
                chat = "No Discord/IRC listed"
            else:
                chat = alliance_data["irc"]
            if alliance_data["forumurl"] == "":
                forum = "No forum link listed"
            else:
                forum = alliance_data["forumurl"]

            embed = discord.Embed(
                title="Alliance Info for {} - {}".format(name, allianceid),
                url="https://politicsandwar.com/alliance/id={}".format(alid),
                color=await ctx.embed_color(),
            )
            embed.add_field(name="Chat", value=chat, inline=False)
            embed.add_field(name="Forum Link:", value=forum, inline=False)
            embed.add_field(name="Score:", value=alliance_data["score"])
            embed.add_field(name="Members:", value=alliance_data["members"])
            embed.add_field(name="Cities:", value=alliance_data["cities"])
            embed.add_field(name="Soldiers:", value=alliance_data["soldiers"])
            embed.add_field(name="Tanks:", value=alliance_data["tanks"])
            embed.add_field(name="Aircraft:", value=alliance_data["aircraft"])
            embed.add_field(name="Ships:", value=alliance_data["ships"])
            embed.add_field(name="Missiles:", value=alliance_data["missiles"])
            embed.add_field(name="Nukes:", value=alliance_data["nukes"])
            embed.add_field(name="Treasures", value=alliance_data["treasures"])
            embed.set_image(url=alliance_data["flagurl"])
            embed.set_footer(text="Info Provided By http://politicsandwar.com/api/")
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def cityinfo(self, ctx, *, id):
        """
        Provides information about the alliance linked to the ID you have given.
        """
        data = await self.city_api(ctx, id)
        try:
            success = data["success"]
            if success == False:
                if data["general_message"]:
                    await ctx.send(
                        f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                    )
                    return
        except:
            pass

        if not data:
            await ctx.send("I can't get the data from the API. Try again later.")
            return
        try:
            if data["success"] == True:
                pass
        except:
            await ctx.send("That city doesn't exist")
            return
        nation = await self.do_lookup(ctx, data["nationid"])
        embed = discord.Embed(
            name="City Info",
            color=await ctx.embed_color(),
            description=f"""[{data['nation']} - {data['leader']}](https://politicsandwar.com/nation/id={data['nationid']})""",
        )
        embed.add_field(
            name=f"{data['name']} - General Info",
            inline=False,
            value=box(
                f"""
Infra                  {data['infrastructure']}
Land                   {data['land']}
Crime                  {data['crime']}
Disease                {data['disease']}
Pollution              {data['pollution']}
Commerce               {data['commerce']}"""
            ),
        )
        embed.add_field(
            name="Improvements - Power",
            value=box(
                f"""
Coal Power Plants      {data['imp_coalpower']}
Oil Power Plants       {data['imp_oilpower']}
Nuclear Power Plants   {data['imp_nuclearpower']}
Wind Power Plants      {data['imp_windpower']}"""
            ),
        )
        if nation["continent"] == "Europe":
            resources = box(
                f"""
Coal Mines             {data['imp_coalmine']}
Iron Mines             {data['imp_ironmine']}
Lead Mines             {data['imp_leadmine']}
Farms                  {data['imp_farm']}"""
            )
        elif nation["continent"] == "Asia":
            resources = box(
                f"""
Oil Wells              {data['imp_oilwell']}
Iron Mines             {data['imp_ironmine']}
Uranium Mines          {data['imp_uramine']}
Farms                  {data['imp_farm']}"""
            )
        elif nation["continent"] == "Africa":
            resources = box(
                f"""
Oil Wells              {data['imp_oilwell']}
Bauxite Mines          {data['imp_bauxitemine']}
Uranium Mines          {data['imp_uramine']}
Farms                  {data['imp_farm']}"""
            )
        elif nation["continent"] == "South America":
            resources = box(
                f"""
Oil Wells              {data['imp_oilwell']}
Bauxite Mines          {data['imp_bauxitemine']}
Lead Mines             {data['imp_leadmine']}
Farms                  {data['imp_farm']}"""
            )
        elif nation["continent"] == "North America":
            resources = box(
                f"""
Coal Mines             {data['imp_coalmine']}
Iron Mines             {data['imp_ironmine']}
Uranium Mines          {data['imp_uramine']}
Farms                  {data['imp_farm']}"""
            )
        elif nation["continent"] == "Australia":
            resources = box(
                f"""
Coal Mines             {data['imp_coalmine']}
Bauxite Mines          {data['imp_bauxitemine']}
Lead Mines             {data['imp_leadmine']}
Farms                  {data['imp_farm']}"""
            )
        embed.add_field(name="Improvements - Resources", value=f"{resources}")
        embed.add_field(
            name="Improvements - Production",
            value=box(
                f"""
Gas Refinerys          {data['imp_gasrefinery']}
Steel Mills            {data['imp_steelmill']}
Aluminum Refinerys     {data['imp_aluminumrefinery']}
Munitions Factorys     {data['imp_munitionsfactory']}"""
            ),
        )
        embed.add_field(
            name="Improvements - Civil",
            value=box(
                f"""
Police Stations        {data['imp_policestation']}
Hospitals              {data['imp_hospital']}
Recycling Centers      {data['imp_recyclingcenter']}
Subways                {data['imp_subway']}"""
            ),
        )
        embed.add_field(
            name="Improvements - Commerce",
            value=box(
                f"""
Supermarkets           {data['imp_supermarket']}
Banks                  {data['imp_bank']}
Malls                  {data['imp_mall']}
Stadiums               {data['imp_stadium']}"""
            ),
        )
        embed.add_field(
            name="Improvements - Military",
            value=box(
                f"""
Barracks               {data['imp_barracks']}
Factories              {data['imp_factory']}
Hangars                {data['imp_hangar']}
Drydocks               {data['imp_drydock']}"""
            ),
        )
        embed.set_footer(text="Info Provided By http://politicsandwar.com/api/")
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def tradeprice(self, ctx, *, query):
        """
            Lookup current avg trading price for a resource including last high and low values.

            By default this looks up the price of steel, any incorrect searches will also return steel.    
        """
        async with ctx.typing():
            query = self.escape_query("".join(query))
            trade_data = await self.tradeprice_lookup(ctx, query)
            try:
                success = trade_data["success"]
                if success == False:
                    if trade_data["general_message"]:
                        await ctx.send(
                            f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                        )
                        return
            except:
                pass

            if not trade_data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return
            resource = trade_data["resource"]
            avgprice = trade_data["avgprice"]
            marketindex = trade_data["marketindex"]
            highestbuyamount = trade_data["highestbuy"]["amount"]
            highestbuyprice = trade_data["highestbuy"]["price"]
            highestbuytotal = trade_data["highestbuy"]["totalvalue"]
            highestbuynation = trade_data["highestbuy"]["nationid"]
            highestbuydate = trade_data["highestbuy"]["date"]
            lowestbuyamount = trade_data["lowestbuy"]["amount"]
            lowestbuyprice = trade_data["lowestbuy"]["price"]
            lowestbuytotal = trade_data["lowestbuy"]["totalvalue"]
            lowestbuynation = trade_data["lowestbuy"]["nationid"]
            lowestbuydate = trade_data["lowestbuy"]["date"]

            embed = discord.Embed(
                title=f"Trade info for {resource}",
                description=f"Current Avg Price: ``{avgprice}``\n"
                f"Market Index: ``{marketindex}``",
                color=await ctx.embed_color(),
            )
            embed.add_field(
                name=f"Highest Buy amount: ``{highestbuyamount}``",
                value=f"Price: {highestbuyprice}\n"
                f"Total value: {highestbuytotal}\n"
                f"By nation: {highestbuynation}\n"
                f"At {highestbuydate}",
                inline=True,
            )
            embed.add_field(
                name=f"Lowest Buy amount: ``{lowestbuyamount}``",
                value=f"Price: {lowestbuyprice}\n"
                f"Total value: {lowestbuytotal}\n"
                f"By nation: {lowestbuynation}\n"
                f"At {lowestbuydate}",
                inline=True,
            )
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def bankinfo(self, ctx, *, name):
        """
            Lookup bank info for your alliance.
        
            Only available if you have the ability to view the bank data in game,
            and the api key must be set to your api key to work.
        
        """
        async with ctx.typing():
            name = self.escape_query("".join(name))
            key = False
            alliances_data = await self.alliances_lookup(ctx)
            success = alliances_data["success"]
            try:
                if success == False:
                    await ctx.send(
                        f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                    )
                    return
            except:
                pass

            for I in alliances_data["alliances"]:
                if name.lower() == I["name"].lower():
                    key = True
                    alid = I["id"]
            if key == True:
                pass
            else:
                alid = name
            bank_data = await self.bank_lookup(ctx, alid)
            if not bank_data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return
            if bank_data["success"] == False:
                await ctx.send("Unable to access this information. You are not in this alliance.")
                return
            else:
                pass
            name = bank_data["alliance_bank_contents"][0]["name"]
            alid = bank_data["alliance_bank_contents"][0]["alliance_id"]
            money = bank_data["alliance_bank_contents"][0]["money"]
            food = bank_data["alliance_bank_contents"][0]["food"]
            coal = bank_data["alliance_bank_contents"][0]["coal"]
            oil = bank_data["alliance_bank_contents"][0]["oil"]
            uranium = bank_data["alliance_bank_contents"][0]["uranium"]
            iron = bank_data["alliance_bank_contents"][0]["iron"]
            bauxite = bank_data["alliance_bank_contents"][0]["bauxite"]
            lead = bank_data["alliance_bank_contents"][0]["lead"]
            gasoline = bank_data["alliance_bank_contents"][0]["gasoline"]
            munitions = bank_data["alliance_bank_contents"][0]["munitions"]
            steel = bank_data["alliance_bank_contents"][0]["steel"]
            aluminum = bank_data["alliance_bank_contents"][0]["aluminum"]
            embed = discord.Embed(
                title=f"Bank Information for {name}",
                description=f"Total Money = {money}",
                color=await ctx.embed_color(),
            )
            embed.add_field(name="Alliance ID", value=alid)
            embed.add_field(name="Food", value=food)
            embed.add_field(name="Coal", value=coal)
            embed.add_field(name="Oil", value=oil)
            embed.add_field(name="Uranium", value=uranium)
            embed.add_field(name="Iron", value=iron)
            embed.add_field(name="Bauxite", value=bauxite)
            embed.add_field(name="Lead", value=lead)
            embed.add_field(name="Gasoline", value=gasoline)
            embed.add_field(name="Munitions", value=munitions)
            embed.add_field(name="Steel", value=steel)
            embed.add_field(name="Aluminum", value=aluminum)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def top50(self, ctx):
        """
        Show Top 50 Alliances
        """
        top50 = await self.alliances_lookup(ctx)
        success = top50["success"]
        try:
            if success == False:
                await ctx.send(
                    f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                )
                return
        except:
            pass
        output = ""
        for alliance in (top50["alliances"])[0:50]:
            arank = alliance["rank"]
            aname = alliance["name"]
            aid = alliance["id"]
            if len(aname) > 20:
                aname = aname[0:20] + "..."
            output = f'{output}\n{f"{arank}":<{5}}{f"{aname}":<{25}}{f"{aid}":>{5}}'
        await ctx.send(
            embed=discord.Embed(
                title="Top 50 Alliances\n",
                description="```Rank Name                      ID" + output + "```",
                color=await ctx.embed_color(),
            ).set_footer(text="Info Provided By http://politicsandwar.com/api/")
        )

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def infra(self, ctx, input: float, tobuy: float, urban=None, cce=None):
        """
        Provides the cost of infra accurate to +/- $100,000. Provide urban and/or cce as a command variable to trigger urbanization and cce infra discounts.
        """
        if input < 10000:
            if tobuy < 10000:
                if tobuy > 100:
                    count = 0
                    factor = 0
                    cost = 0
                    r = tobuy / 100 + 1.0
                    for _ in range(int(r)):
                        factor = input + count
                        count = count + 100
                        if tobuy >= 100:
                            buying = 100
                            tobuy = tobuy - 100
                        else:
                            buying = tobuy
                        x = (((factor - 10) ** 2.2) / 710) + 300
                        cost = cost + x * buying
                else:
                    x = (((input - 10) ** 2.2) / 710) + 300
                    cost = x * tobuy
                vars = ["urban", "cce"]
                if urban:
                    urban = urban.lower()
                    if urban in vars:
                        cost = cost - cost * 0.05
                if cce:
                    cce = cce.lower()
                    if cce in vars:
                        cost = cost - cost * 0.05
                embed = discord.Embed(
                    title="Infra Cost Calculator",
                    description="To accomidate for discrepincies in this calculator, please ensure you are capable of paying +/- $100,000 what is given here!",
                    color=await ctx.embed_color(),
                )
                embed.add_field(name="Total:", value=f"${cost:,.2f}")
                embed.set_footer(
                    text="Results generated based on equations provided by http://politicsandwar.wikia.com/wiki/"
                )
                await ctx.send(embed=embed)
        else:
            await ctx.send("You are currently at the max amount of infrastructure")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def land(self, ctx, input: float, tobuy: float):
        """
        Provides the cost of land accurate to +/- $100,000.
        """
        if input < 10000:
            if tobuy < 10000:
                if tobuy > 500:
                    count = 0
                    factor = 0
                    cost = 0
                    r = tobuy // 500 + 1.0
                    for _ in range(int(r)):
                        factor = input + count
                        count = count + 500
                        if tobuy >= 500:
                            buying = 500
                            tobuy = tobuy - 500
                        else:
                            buying = tobuy
                        x = 0.002 * (factor - 20) ** 2 + 50
                        cost = cost + x * buying
                else:
                    x = 0.002 * (input - 20) ** 2 + 50
                    cost = x * tobuy
                embed = discord.Embed(
                    title="Land Cost Calculator",
                    description="To accomidate for discrepincies in this calculator, please ensure you are capable of paying +/- $100,000 what is given here!",
                    color=await ctx.embed_color(),
                )
                embed.add_field(name="Total:", value=f"${cost:,.2f}")
                embed.set_footer(
                    text="Results generated based on equations provided by http://politicsandwar.wikia.com/wiki/"
                )
                await ctx.send(embed=embed)
        else:
            await ctx.send("You are at the max amount of land")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def citycost(self, ctx, city: int):
        """
        Provides the cost of the next city accurate to +/- $100,000.
        """
        if city < 100:
            cost = 50000 * (city - 1) ** 3 + 150000 * city + 75000
            embed = discord.Embed(
                title="City Cost Calculator",
                description="To accomidate for discrepincies in this calculator, please ensure you are capable of paying +/- $100,000 what is given here!",
                color=await ctx.embed_color(),
            )
            embed.add_field(name="Total:", value=f"${cost:,.2f}")
            embed.set_footer(
                text="Results generated based on equations provided by http://politicsandwar.wikia.com/wiki/"
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("You are at the max amount of cities")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def military(self, ctx, *, name):
        """
        Military Lookup
        """
        await ctx.send("This may take a while.....")
        async with ctx.typing():
            name = self.escape_query("".join(name))
            key = False
            nations_data = await self.nations_lookup(ctx)
            success = nations_data["success"]
            try:
                if success == False:
                    await ctx.send(
                        f"Your api seems to be invalid, make sure its correct and follow the instructions in {ctx.prefix}pnwkey"
                    )
                    return
            except:
                pass
            for I in nations_data["nations"]:
                if name.lower() == I["nation"].lower():
                    key = True
                    nid = I["nationid"]
            if key == True:
                pass
            else:
                nid = name
            nation_data = await self.do_lookup(ctx, nid)
            if not nation_data:
                await ctx.send("I can't get the data from the API. Try again later.")
                return
            success = nation_data["success"]
            if success == False:
                await ctx.send("No such nation exists! Please enter a vaild nation ID")
                return
            name = nation_data["name"]
            nationid = nation_data["nationid"]
            score = nation_data["score"]
            soldiers = nation_data["soldiers"]
            tank = nation_data["tanks"]
            aircraft = nation_data["aircraft"]
            ships = nation_data["ships"]
            missiles = nation_data["missiles"]
            nukes = nation_data["nukes"]
            if nation_data["allianceposition"] == "5":
                alliancepos = "Leader"
            elif nation_data["allianceposition"] == "4":
                alliancepos = "Vice Leader"
            elif nation_data["allianceposition"] == "3":
                alliancepos = "Officer"
            elif nation_data["allianceposition"] == "2":
                alliancepos = "Member"
            elif nation_data["allianceposition"] == "1":
                alliancepos = "Applicant"
            elif nation_data["allianceposition"] == "0":
                alliancepos = "None"

            if nation_data["allianceid"] == "0":
                allianceid = "None"
            else:
                allianceid = nation_data["allianceid"]
            intscore = float(score)
            low_defense_range = int(intscore * 0.57143)
            high_defense_range = int(intscore * 1.33335)
            low_offense_range = int(intscore * 0.75)
            high_offense_range = int(intscore * 1.75)
            

            embed = discord.Embed(
                title="Military Info for {}".format(name),
                description="Alliance Name: {}\nAlliance ID: {}\nAlliance Position: {}".format(
                    nation_data["alliance"], allianceid, alliancepos
                ),
                url="https://politicsandwar.com/nation/id={}".format(nationid),
                color=await ctx.embed_color(),
            )

            embed.add_field(
                name="Military Stats",
                value=(
                    f"""
                    Score: {score}
                    Soldiers: {soldiers}
                    Tanks: {tank}
                    Aircraft: {aircraft}
                    Ships: {ships}
                    Missiles: {missiles}
                    Nukes: {nukes}
                    Defense Range: {low_defense_range} - {high_defense_range}
                    Offense Range: {low_offense_range} - {high_offense_range}"""
                ),
            )

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def pnwcredits(self, ctx):
        """
        Credits for the PNW cog
        """
        embed = discord.Embed(
            title="Credits go to Reqiuem bot/Kyle Tyo for various aspects of this PNW cog",
            description="Reqiuem can be found here, https://gitlab.com/AnakiKaiver297/Requiem-Project, "
            "specific thanks for the various calculations and name searching for alliances/nations",
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
