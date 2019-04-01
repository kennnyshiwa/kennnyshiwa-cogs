# Remove command logic originally from : https://github.com/mikeshardmind/SinbadCogs/tree/v3/messagebox

import discord

from redbot.core import commands, checks, Config

old_invite = None


class Invite(commands.Cog):
    def __init__(self, bot):
        default = {
            "support_serv": None,
            "colour": 0
        }
        self.bot = bot
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
        self.config.register_global(**default)

    def _unload(
        self
    ):  # We remove this version of invite command at unload of the cog, after that a restart is needed to restore original version
        global old_invite
        if old_invite:
            try:
                self.bot.remove_command("invite")
            except:
                pass
            self.bot.add_command(old_invite)

    @checks.is_owner()
    @commands.group()
    async def inviteset(self, ctx):
        """Settings for embedinvite cog."""
        pass

    @inviteset.command()
    async def colour(self, ctx, colour: discord.Colour):
        """Set colour of embed."""
        await self.config.colour.set(colour.value)
        await ctx.send("Embed colour set.")

    @inviteset.command()
    async def support(self, ctx, supportserver):  # A little example to how to use config
        """Set support server."""
        await self.config.support_serv.set(supportserver)
        await ctx.send("Support server set.")

    @commands.command()  # You need to use commands.command() / invite.command() would be for a command group
    @commands.bot_has_permissions(embed_links=True)
    async def invite(self, ctx):
        """Send personalized invite for the bot."""
        support = await self.config.support_serv()
        if support is None:  # Check if owner as set support server.
            return await ctx.send("Owner need to set support server !")
        embed = discord.Embed(
            description="Thanks for choosing to invite {name} to your server".format(
                name=ctx.bot.user.display_name
            ),
            color=await self.config.colour(),
        )
        embed.set_author(
            name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url_as(static_format="png")
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar_url_as(static_format="png"))
        embed.add_field(
            name="Bot Invite",  # I don't know how to add permissions for a link like that, need to check it
            value="https://discordapp.com/oauth2/authorize?client_id={}&scope=bot".format(
                self.bot.user.id
            ),
        )
        embed.add_field(name="Support Server", value="{}".format(support))
        embed.set_footer(
            text="{} made possible with the support of Red Discord Bot".format(
                ctx.bot.user.display_name
            ),
            icon_url="https://cdn.discordapp.com/icons/133049272517001216/83b39ff510bb7c3f5aeb51270af09ad3.webp",
        )
        await ctx.send(embed=embed)


def setup(bot):
    invite = Invite(bot)
    global old_invite
    old_invite = bot.get_command("invite")
    if old_invite:  # This used for removing old invite command, and then add the cog,
        # otherwise you can't load it cause of already existing command
        bot.remove_command(old_invite.name)
    bot.add_cog(invite)
