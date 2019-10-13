import discord
import os
import sys
import cpuinfo
import platform
import lavalink
import asyncio
import contextlib
import asyncio
from collections import Counter
from copy import copy
from .listeners import Listeners

from datetime import datetime

from redbot.core import version_info as red_version_info, commands, Config

from redbot.core.utils.chat_formatting import humanize_timedelta, box

from redbot.cogs.audio.manager import JAR_BUILD as jarversion

# from redbot.cogs.audio.dataclasses import Query

import psutil

if sys.platform == "linux":
    import distro


class ImperialToolkit(Listeners, commands.Cog):
    """Collection of useful commands and tools."""

    __author__ = "kennnyshiwa"

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()
        self.sticky_counter = Counter()
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
        self._monitor_time = datetime.utcnow().timestamp()
        global_defauls = dict(
            command_error=0,
            msg_sent=0,
            dms_received=0,
            messages_read=0,
            guild_join=0,
            guild_remove=0,
            sessions_resumed=0,
            processed_commands=0,
            new_members=0,
            members_left=0,
            messages_deleted=0,
            messages_edited=0,
            reactions_added=0,
            reactions_removed=0,
            roles_added=0,
            roles_removed=0,
            roles_updated=0,
            members_banned=0,
            members_unbanned=0,
            emojis_removed=0,
            emojis_added=0,
            emojis_updated=0,
            users_joined_bot_music_room=0,
        )
        self.config.register_global(**global_defauls)
        self._task = self.bot.loop.create_task(self._save_counters_to_config())
        lavalink.register_event_listener(self.event_handler)  # To delete at next audio update.

    def cog_unload(self):
        lavalink.unregister_event_listener(self.event_handler)
        self.bot.loop.create_task(self._clean_up())

    async def event_handler(self, player, event_type, extra):  # To delete at next audio update.
        # Thanks Draper#6666
        if event_type == lavalink.LavalinkEvents.TRACK_START:
            self.update_counters("tracks_played")

    def update_counters(self, key: str):
        self.counter[key] += 1
        self.sticky_counter[key] += 1

    # Planned for next audio update.
    # @commands.Cog.listener()
    # async def on_track_start(self, guild: discord.Guild, track, reuester):
    #     self.bot.counter["tracks_played"] += 1

    def get_bot_uptime(self):
        delta = datetime.utcnow() - (
            self.bot.uptime if hasattr(self.bot, "uptime") else self.bot._uptime
        )
        uptime = humanize_timedelta(timedelta=delta)
        return uptime

    async def _save_counters_to_config(self):
        await self.bot.wait_until_ready()
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                users_data = copy(self.sticky_counter)
                self.sticky_counter = Counter()
                async with self.config.all() as new_data:
                    for key, value in users_data.items():
                        if key in new_data:
                            new_data[key] += value
                        else:
                            new_data[key] = value
                    if "start_date" not in new_data:
                        new_data["start_date"] = self._monitor_time
                await asyncio.sleep(60)

    async def _clean_up(self):
        if self._task:
            self._task.cancel()
        async with self.config.all() as new_data:
            for key, value in self.sticky_counter.items():
                if key in new_data:
                    new_data[key] += value
                else:
                    new_data[key] = value

    @staticmethod
    def _size(num):
        for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if abs(num) < 1024.0:
                return "{0:.1f}{1}".format(num, unit)
            num /= 1024.0
        return "{0:.1f}{1}".format(num, "YB")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def botstat(self, ctx):
        """Get stats about the bot including messages sent and recieved and other info."""
        async with ctx.typing():
            cpustats = psutil.cpu_percent()
            ramusage = psutil.virtual_memory()
            netusage = psutil.net_io_counters()
            width = max([len(self._size(n)) for n in [netusage.bytes_sent, netusage.bytes_recv]])
            net_ios = (
                "\u200b"
                "\n"
                "{sent_text:<11}: {sent:>{width}}\n"
                "{recv_text:<11}: {recv:>{width}}"
            ).format(
                sent_text="Bytes sent",
                sent=self._size(netusage.bytes_sent),
                width=width,
                recv_text="Bytes recv",
                recv=self._size(netusage.bytes_recv),
            )

            IS_WINDOWS = os.name == "nt"
            IS_MAC = sys.platform == "darwin"
            IS_LINUX = sys.platform == "linux"

            if IS_WINDOWS:
                os_info = platform.uname()
                osver = "``{} {} (version {})``".format(
                    os_info.system, os_info.release, os_info.version
                )
            elif IS_MAC:
                os_info = platform.mac_ver()
                osver = "``Mac OSX {} {}``".format(os_info[0], os_info[2])
            elif IS_LINUX:
                os_info = distro.linux_distribution()
                osver = "``{} {}``".format(os_info[0], os_info[1]).strip()
            else:
                osver = "Could not parse OS, report this on Github."

            try:
                cpu = cpuinfo.get_cpu_info()["brand"]
            except:
                cpu = "unknown"
            cpucount = psutil.cpu_count()
            ramamount = psutil.virtual_memory()
            ram_ios = "{0:<11} {1:>{width}}".format("", self._size(ramamount.total), width=width)

            servers = len(self.bot.guilds)
            shards = self.bot.shard_count
            totalusers = sum(len(s.members) for s in self.bot.guilds)
            channels = sum(len(s.channels) for s in self.bot.guilds)
            numcommands = len(self.bot.commands)
            uptime = str(self.get_bot_uptime())
            tracks_played = "`{:,}`".format(self.counter["tracks_played"])
            try:
                total_num = "`{:,}`".format(len(lavalink.active_players()))
            except AttributeError:
                total_num = "`{:,}`".format(
                    len([p for p in lavalink.players if p.current is not None])
                )

            red = red_version_info
            dpy = discord.__version__

            embed = discord.Embed(
                title="Bot Stats for {}".format(ctx.bot.user.name),
                description="Below are various stats about the bot and the machine that runs the bot",
                color=await ctx.embed_color(),
            )
            embed.add_field(
                name="\N{DESKTOP COMPUTER} Server Info",
                value=(
                    "CPU usage: `{cpu_usage}%`\n"
                    "RAM usage: `{ram_usage}%`\n"
                    "Network usage: `{network_usage}`\n"
                    "Boot Time: `{boot_time}`\n"
                    "OS: {os}\n"
                    "CPU Info: `{cpu}`\n"
                    "Core Count: `{cores}`\n"
                    "Total Ram: `{ram}`"
                ).format(
                    cpu_usage=str(cpustats),
                    ram_usage=str(ramusage.percent),
                    network_usage=net_ios,
                    boot_time=datetime.fromtimestamp(psutil.boot_time()).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    os=osver,
                    cpu=cpu,
                    cores=cpucount,
                    ram=ram_ios,
                ),
            )
            embed.add_field(
                name="\N{ROBOT FACE} Bot Info",
                value=(
                    "Servers: `{servs:,}`\n"
                    "Users: `{users:,}`\n"
                    "Shard{s}: `{shard:,}`\n"
                    "Playing Music on: `{totalnum:}` servers\n"
                    "Tracks Played: `{tracksplayed:}`\n"
                    "Channels: `{channels:,}`\n"
                    "Number of commands: `{numcommands:,}`\n"
                    "Bot Uptime: `{uptime}`"
                ).format(
                    servs=servers,
                    users=totalusers,
                    s="s" if shards >= 2 else "",
                    shard=shards,
                    totalnum=total_num,
                    tracksplayed=tracks_played,
                    channels=channels,
                    numcommands=numcommands,
                    uptime=uptime,
                ),
                inline=True,
            )
            embed.add_field(
                name="\N{BOOKS} Libraries,",
                value=(
                    "Lavalink: `{lavalink}`\n"
                    "Jar Version: `{jarbuild}`\n"
                    "Red Version: `{redversion}`\n"
                    "Discord.py Version: `{discordversion}`"
                ).format(
                    lavalink=lavalink.__version__,
                    jarbuild=jarversion,
                    redversion=red,
                    discordversion=dpy,
                ),
            )
            embed.set_thumbnail(url=ctx.bot.user.avatar_url_as(static_format="png"))
            embed.set_footer(text=await ctx.bot._config.help.tagline())

        return await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def advbotstats(self, ctx):
        avatar = self.bot.user.avatar_url_as(static_format="png")
        uptime = str(self.get_bot_uptime())
        errors_count = "{:,}".format(self.counter["command_error"])
        messages_read = "{:,}".format(self.counter["messages_read"])
        messages_sent = "{:,}".format(self.counter["msg_sent"])
        dms_received = "{:,}".format(self.counter["dms_received"])
        guild_join = "{:,}".format(self.counter["guild_join"])
        guild_leave = "{:,}".format(self.counter["guild_remove"])
        resumed_sessions = "{:,}".format(self.counter["sessions_resumed"])
        commands_count = "{:,}".format(self.counter["processed_commands"])
        new_mem = "{:,}".format(self.counter["new_members"])
        left_mem = "{:,}".format(self.counter["members_left"])
        msg_deleted = "{:,}".format(self.counter["messages_deleted"])
        msg_edited = "{:,}".format(self.counter["messages_edited"])
        react_added = "{:,}".format(self.counter["reactions_added"])
        react_removed = "{:,}".format(self.counter["reactions_removed"])
        roles_add = "{:,}".format(self.counter["roles_added"])
        roles_rem = "{:,}".format(self.counter["roles_removed"])
        roles_up = "{:,}".format(self.counter["roles_updated"])
        mem_ban = "{:,}".format(self.counter["members_banned"])
        mem_unban = "{:,}".format(self.counter["members_unbanned"])
        emoji_add = "{:,}".format(self.counter["emojis_added"])
        emoji_rem = "{:,}".format(self.counter["emojis_removed"])
        emoji_up = "{:,}".format(self.counter["emojis_updated"])
        vc_joins = "{:,}".format(self.counter["users_joined_bot_music_room"])
        tracks_played = "{:,}".format(self.counter["tracks_played"])
        # streams_played = "{:,}".format(self.counter["streams_played"])
        # yt_streams = "{:,}".format(self.counter["yt_streams_played"])
        # mixer_streams = "{:,}".format(self.counter["mixer_streams_played"])
        # ttv_streams = "{:,}".format(self.counter["ttv_streams_played"])
        # other_streams = "{:,}".format(self.counter["other_streams_played"])
        # youtube_tracks = "{:,}".format(self.counter["youtube_tracks"])
        # soundcloud_tracks = "{:,}".format(self.counter["soundcloud_tracks"])
        # bandcamp_tracks = "{:,}".format(self.counter["bandcamp_tracks"])
        # vimeo_tracks = "{:,}".format(self.counter["vimeo_tracks"])
        # mixer_tracks = "{:,}".format(self.counter["mixer_tracks"])
        # twitch_tracks = "{:,}".format(self.counter["twitch_tracks"])
        # other_tracks = "{:,}".format(self.counter["other_tracks"])
        try:
            total_num = "{:,}/{:,}".format(
                len(lavalink.active_players()), len(lavalink.all_players())
            )
        except AttributeError:
            total_num = "{:,}/{:,}".format(
                len([p for p in lavalink.players if p.current is not None]),
                len([p for p in lavalink.players]),
            )

        em = discord.Embed(
            title="Usage count of {} since last restart:".format(ctx.bot.user.name),
            color=await ctx.embed_colour(),
        )
        em.add_field(
            name="Message Stats",
            value=box(
                f"""
Messages Read:       {messages_read}
Messages Sent:       {messages_sent}
Messages Deleted:    {msg_deleted}
Messages Edited      {msg_edited}
DMs Recieved:        {dms_received}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Commands Stats",
            value=box(
                f"""
Commands Processed:  {commands_count}
Errors Occured:      {errors_count}
Sessions Resumed:    {resumed_sessions}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Guild Stats",
            value=box(
                f"""
Guilds Joined:       {guild_join}
Guilds Left:         {guild_leave}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="User Stats",
            value=box(
                f"""
New Users:           {new_mem}
Left Users:          {left_mem}
Banned Users:        {mem_ban}
Unbanned Users:      {mem_unban}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Role Stats",
            value=box(
                f"""
Roles Added:         {roles_add}
Roles Removed:       {roles_rem}
Roles Updated:       {roles_up}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Emoji Stats",
            value=box(
                f"""
Reacts Added:        {react_added}
Reacts Removed:      {react_removed}
Emoji Added:         {emoji_add}
Emoji Removed:       {emoji_rem}
Emoji Updated:       {emoji_up}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Audio Stats",
            value=box(
                f"""
Users Who Joined VC: {vc_joins}
Tracks Played:       {tracks_played}
Number Of Players:   {total_num}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.set_thumbnail(url=avatar)
        em.set_footer(text=("Since {}").format(uptime))
        await ctx.send(embed=em)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def alltimestats(self, ctx):
        avatar = self.bot.user.avatar_url_as(static_format="png")
        uptime = str(self.get_bot_uptime())
        errors_count = "{:,}".format(await self.config.command_error())
        messages_read = "{:,}".format(await self.config.messages_read())
        messages_sent = "{:,}".format(await self.config.msg_sent())
        dms_received = "{:,}".format(await self.config.dms_received())
        guild_join = "{:,}".format(await self.config.guild_join())
        guild_leave = "{:,}".format(await self.config.guild_remove())
        resumed_sessions = "{:,}".format(await self.config.sessions_resumed())
        commands_count = "{:,}".format(await self.config.processed_commands())
        new_mem = "{:,}".format(await self.config.new_members())
        left_mem = "{:,}".format(await self.config.members_left())
        msg_deleted = "{:,}".format(await self.config.messages_deleted())
        msg_edited = "{:,}".format(await self.config.messages_edited())
        react_added = "{:,}".format(await self.config.reactions_added())
        react_removed = "{:,}".format(await self.config.reactions_removed())
        roles_add = "{:,}".format(await self.config.roles_added())
        roles_rem = "{:,}".format(await self.config.roles_removed())
        roles_up = "{:,}".format(await self.config.roles_updated())
        mem_ban = "{:,}".format(await self.config.members_banned())
        mem_unban = "{:,}".format(await self.config.members_unbanned())
        emoji_add = "{:,}".format(await self.config.emojis_added())
        emoji_rem = "{:,}".format(await self.config.emojis_removed())
        emoji_up = "{:,}".format(await self.config.emojis_updated())
        vc_joins = "{:,}".format(await self.config.users_joined_bot_music_room())
        tracks_played = "{:,}".format(self.counter["tracks_played"])
        # streams_played = "{:,}".format(await self.config.streams_played())
        # yt_streams = "{:,}".format(await self.config.yt_streams_played())
        # mixer_streams = "{:,}".format(await self.config.mixer_streams_played())
        # ttv_streams = "{:,}".format(await self.config.ttv_streams_played())
        # other_streams = "{:,}".format(await self.config.other_streams_played())
        # youtube_tracks = "{:,}".format(await self.config.youtube_tracks())
        # soundcloud_tracks = "{:,}".format(await self.config.soundcloud_tracks())
        # bandcamp_tracks = "{:,}".format(await self.config.bandcamp_tracks())
        # vimeo_tracks = "{:,}".format(await self.config.vimeo_tracks())
        # mixer_tracks = "{:,}".format(await self.config.mixer_tracks())
        # twitch_tracks = "{:,}".format(await self.config.twitch_tracks())
        # other_tracks = "{:,}".format(await self.config.other_tracks())
        try:
            total_num = "{:,}/{:,}".format(
                len(lavalink.active_players()), len(lavalink.all_players())
            )
        except AttributeError:
            total_num = "{:,}/{:,}".format(
                len([p for p in lavalink.players if p.current is not None]),
                len([p for p in lavalink.players]),
            )

        em = discord.Embed(
            title="Persistent usage count of {}:".format(ctx.bot.user.name),
            color=await ctx.embed_colour(),
        )
        em.add_field(
            name="Message Stats",
            value=box(
                f"""
Messages Read:       {messages_read}
Messages Sent:       {messages_sent}
Messages Deleted:    {msg_deleted}
Messages Edited      {msg_edited}
DMs Recieved:        {dms_received}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Commands Stats",
            value=box(
                f"""
Commands Processed:  {commands_count}
Errors Occured:      {errors_count}
Sessions Resumed:    {resumed_sessions}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Guild Stats",
            value=box(
                f"""
Guilds Joined:       {guild_join}
Guilds Left:         {guild_leave}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="User Stats",
            value=box(
                f"""
New Users:           {new_mem}
Left Users:          {left_mem}
Banned Users:        {mem_ban}
Unbanned Users:      {mem_unban}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Role Stats",
            value=box(
                f"""
Roles Added:         {roles_add}
Roles Removed:       {roles_rem}
Roles Updated:       {roles_up}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Emoji Stats",
            value=box(
                f"""
Reacts Added:        {react_added}
Reacts Removed:      {react_removed}
Emoji Added:         {emoji_add}
Emoji Removed:       {emoji_rem}
Emoji Updated:       {emoji_up}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.add_field(
            name="Audio Stats",
            value=box(
                f"""
Users Who Joined VC: {vc_joins}
Tracks Played:       {tracks_played}
Number Of Players:   {total_num}""",
                lang="prolog",
            ),
            inline=False,
        )
        em.set_thumbnail(url=avatar)
        em.set_footer(text=("Since {}").format(uptime))
        await ctx.send(embed=em)
