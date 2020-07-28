from typing import Optional

import discord
from redbot.core.config import Config
from redbot.core import commands, checks
from redbot.core.utils import AsyncIter
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.antispam import AntiSpam
from typing import Literal
from .checks import has_active_box

_ = Translator("??", __file__)


@cog_i18n(_)
class RequestBox(commands.Cog):
    """
    A configureable Request Channel cog
    """

    __author__ = "kennnyshiwa, Sharky The King, Sinbad"
    __version__ = "1.0.6"

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        if requester == "discord_deleted_user":
            # user is deleted, must comply on IDs here...

            data = await self.config.all_members()
            await self.config.user_from_id(user_id).clear()
            async for guild_id, members in AsyncIter(data.items(), steps=100):
                if user_id in members:
                    await self.config.member_from_ids(guild_id, user_id).clear()

            grp = self.config.custom("REQUEST")

            async with grp as data:
                async for message_id, request in AsyncIter(data.items(), steps=100):
                    if d := request.get("data"):
                        if d.get("author_id", 0) == user_id:
                            d["author_id"] = 0

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=78631113035100160, force_registration=True
        )
        self.config.register_guild(
            boxes=None,
            add_reactions=False,
            reactions=["\N{THUMBS UP SIGN}"],
        )
        self.config.register_global(
            boxes=None,
            add_reactions=False,
            reactions=["\N{THUMBS UP SIGN}"],
        )
        self.config.init_custom("REQUEST", 1)
        self.config.register_custom("REQUEST", data={})

        self.config.register_member(blocked=False)
        self.config.register_user(blocked=False)
        self.antispam = {}

    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.group(name="requestset", aliases=["setrequest"])
    async def rset(self, ctx: commands.Context):
        """
        Configuration settings for Request Box
        """
        pass

    @rset.command(name="make")
    async def rset_make(self, ctx, *, channel: discord.TextChannel):
        """
        sets a channel as a Request Box
        """
        await self.config.guild(ctx.guild).boxes.set(channel.id)

        await ctx.tick()

    @rset.command(name="remove")
    async def rset_rm(self, ctx, *, channel: discord.TextChannel):
        """
        removes a channel as a Request Box
        """
        await self.config.guild(ctx.guild).boxes.clear()

        await ctx.tick()

    @rset.command(name="addreactions")
    async def rset_adds_reactions(self, ctx, option: bool = None):
        """
        sets whether to add reactions to each request

        displays current setting without a provided option.

        off = Don't use reactions
        on = Use reactions
        """
        if option is None:
            current = await self.config.guild(ctx.guild).add_reactions()
            if current:
                base = _(
                    "I am adding reactions to requests."
                    "\nUse {command} for more information"
                )
            else:
                base = _(
                    "I am not adding reactions to requests."
                    "\nUse {command} for more information"
                )

            await ctx.send(
                base.format(
                    command=f"`{ctx.clean_prefix}help requestset addreactions`"
                )
            )
            return

        await self.config.guild(ctx.guild).add_reactions.set(option)
        await ctx.tick()

    @has_active_box()
    @commands.guild_only()
    @commands.command()
    async def request(
        self,
        ctx,
        *,
        request: str = "",
    ):
        """
        Request something.

        Options
        channel : Mention channel to specify which channel to post your request
        """
        if ctx.guild not in self.antispam:
            self.antispam[ctx.guild] = {}

        if ctx.author not in self.antispam[ctx.guild]:
            self.antispam[ctx.guild][ctx.author] = AntiSpam([])

        if self.antispam[ctx.guild][ctx.author].spammy:
            return await ctx.send(_("You've send too many requests recently."))

        channels = await self.config.guild(ctx.guild).boxes()
        if not request:
            return await ctx.send(_("Please try again while including a request."))

        embed = discord.Embed(color=(await ctx.embed_color()), description=request)

        embed.set_author(
            name=_("New bounty from {author_info}").format(
                author_info=f"{ctx.author.display_name} ({ctx.author.id})"
            ),
            icon_url=ctx.author.avatar_url,
        )

        try:
            msg = await self.bot.get_channel(channels).send(embed=embed)
        except discord.HTTPException:
            return await ctx.send(_("An unexpected error occured."))
        else:
            grp = self.config.custom("REQUEST", msg.id)
            async with grp.data() as data:
                data.update(
                    channel=channels, request=request, author=ctx.author.id
                )
            self.antispam[ctx.guild][ctx.author].stamp()
            await ctx.send(
                f'{ctx.author.mention}: {_("Your request has been sent")}'
            )

        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            try:
                await ctx.message.delete()
            except discord.HTTPException:
                pass

        if await self.config.guild(ctx.guild).add_reactions():

            for reaction in await self.config.guild(ctx.guild).reactions():
                await msg.add_reaction(reaction)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user):
        """
        Detects for when someone adds reaction
        """
        if user.bot:
            return
        if not reaction.message.embeds:
            return
        if not reaction.message.guild:
            return
        if reaction.message.author != self.bot.user:
            return
        request = await self.config.guild(reaction.message.guild).boxes()   # Making sure reaction is purely in specific channel
        if request is None:
            return
        chan = discord.utils.get(reaction.message.guild.channels, id=int(request))
        if reaction.message.channel.id != request:
            return
        chan = reaction.message.channel
        if "Request Claimed:" in str(reaction.message.embeds[0].fields):   # Detecting if this field is already there, if it is then do nothing, if it's not then add field
            return
        em = reaction.message.embeds[0]
        em.add_field(
            name="Request Claimed:",
            value="{} has claimed this.".format(user.mention),
        )
        try:
            await reaction.message.edit(embed=em)
        except:
            return
        if await self.config.guild(reaction.message.guild).reactions(): #   If this is True, then it'll clear all reactions
            try:
                await reaction.message.clear_reactions()
            except discord.Errors.Forbidden:
                pass
