# Remove command logic originally from : https://github.com/mikeshardmind/SinbadCogs/tree/v3/messagebox

import discord

from redbot.core import commands, checks, Config

old_invite = None


class Invite(commands.Cog):
    """Personalize invite command with an embed and multiple options."""

    def __init__(self, bot):
        self.bot = bot
        default = {
            "support": True,
            "support_serv": None,
            "colour": 0,
            "description": "Thanks for choosing to invite {name} to your server".format(
                name=self.bot.user.name
            ),
            "setpermissions": "",
        }
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
        self.config.register_global(**default)

    @checks.is_owner()
    @commands.group()
    async def invitesettings(self, ctx):
        """Settings for embedinvite cog."""
        pass

    @invitesettings.command()
    async def colour(self, ctx, colour: discord.Colour):
        """
        Set colour of the embed.
        Accepts either a hex value or color name.
        Default: Black
        """
        await self.config.colour.set(colour.value)
        await ctx.send("Embed colour set.")

    @invitesettings.command()
    async def description(self, ctx, *, text: str = ""):
        """
        Set the embed description.
        Set to None if you don't want description.
        Default: "Thanks for choosing to invite {botname} to your server"
        """
        if text == "":
            await self.config.description.clear()
            return await ctx.send("Embed description set to default.")
        elif text == "None":
            await self.config.description.set("")
            return await ctx.send("Embed description disabled.")
        await self.config.description.set(text)
        await ctx.send(f"Embed description set to :\n`{text}`")

    @invitesettings.command()
    async def support(self, ctx, toggle: bool = True):
        """
        Choose if you want support field.
        Default: True
        """
        if toggle:
            await self.config.support.set(True)
            await ctx.send("Support field set to `True`.")
        else:
            await self.config.support.set(False)
            await ctx.send("Support field set to `False`.")

    @invitesettings.command()
    async def supportserv(self, ctx, supportserver):
        """
        Set a support server.
        Enter the invite link to your server.
        """
        await self.config.support_serv.set(supportserver)
        await ctx.send("Support server set.")

    @invitesettings.command()
    async def setpermissions(self, ctx, *, text: int = ""):
        """Set the default permissions value for your bot.
        Get the permissions value from https://discordapi.com/permissions.html
        """
        if text == "":
            await self.config.setpermissions.clear()
            return await ctx.send("Permissions value reset")
        elif text == "None":
            await self.config.setpermission.set("")
            return await ctx.send("Permissions value disabled")
        await self.config.setpermissions.set(text)
        await ctx.send("Permissions set")

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def invite(self, ctx):
        """
        Send personalized invite for the bot.
        """
        permissions = await self.config.setpermissions()
        support_serv = await self.config.support_serv()
        support = await self.config.support()
        if support_serv is None and support is True:
            return await ctx.send("Owner needs to set support server !")
        embed = discord.Embed(
            description=await self.config.description(),
            color=await self.config.colour(),
        )
        embed.set_author(
            name=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar_url_as(static_format="png"),
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar_url_as(static_format="png"))
        embed.add_field(
            name="Bot Invite",
            value="https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions={}".format(
                self.bot.user.id, permissions
            ),
        )
        if support:
            embed.add_field(name="Support Server", value="{}".format(support_serv))
        embed.set_footer(
            text="{} made possible with the support of Red Discord Bot".format(
                ctx.bot.user.display_name
            ),
            icon_url="https://cdn.discordapp.com/icons/133049272517001216/83b39ff510bb7c3f5aeb51270af09ad3.webp",
        )
        await ctx.send(embed=embed)

    def cog_unload(self):
        global old_invite
        if old_invite:
            try:
                self.bot.remove_command("invite")
            except:
                pass
            self.bot.add_command(old_invite)
