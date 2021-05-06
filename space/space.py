import discord

from redbot.core import commands, checks
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

from .core import Core


class Space(Core):
    """Show pics of space."""

    @commands.group()
    @checks.mod_or_permissions(manage_channels=True)
    async def spaceset(self, ctx: commands.Context):
        """Group commands for Space cog settings."""

    @spaceset.command()
    async def autoapod(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Choose if you want to automatically receive \"Astronomy Picture of the Day\" every day.

        Set to actual channel by default. You can also use `[p]spaceset autoapod <channel_name>` if you want to receive APOD in others channels.
        Use the same command to disable it.
        """
        channel = ctx.channel if not channel else channel
        auto_apod = await self.config.channel(channel).auto_apod()
        await self.config.channel(channel).auto_apod.set(not auto_apod)
        msg = (
            "I will now automatically send Astronomy Picture of the Day every day in this channel."
            if not auto_apod
            else "No longer sending Astronomy Picture of the Day every day in this channel."
        )
        await channel.send(msg)
        if not auto_apod:
            data = await self.get_data("https://api.martinebot.com/images/apod")
            apod_text = await self.apod_text(data, channel)
            await self.maybe_send_embed(channel, apod_text)
            await self.config.channel(channel).last_apod_sent.set(data["date"])
        await ctx.tick()

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def apod(self, ctx: commands.Context):
        """Astronomy Picture of the Day."""
        async with ctx.typing():
            apod_text = await self.apod_text(
                await self.get_data("https://api.martinebot.com/images/apod"),
                ctx,
            )
        return await self.maybe_send_embed(ctx, apod_text)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def spacepic(self, ctx: commands.Context, *, query: str):
        """
        Lookup pictures from space!
        Note - Some pictures are from presentations and other educational talks
        """
        async with ctx.typing():
            query = self.escape_query("".join(query))
            space_data = await self.get_space_pic_data(ctx, query)
            if space_data is None:
                await ctx.send(f"Looks like you got lost in space looking for `{query}`")
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
    async def isslocation(self, ctx: commands.Context):
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
    async def astronauts(self, ctx: commands.Context):
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
