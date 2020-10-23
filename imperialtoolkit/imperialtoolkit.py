import discord
import os
import sys
import cpuinfo
import platform
import lavalink
from collections import Counter

from datetime import datetime

from redbot.core import version_info as red_version_info, commands, Config

from redbot.core.utils import AsyncIter

from redbot.core.utils.chat_formatting import humanize_timedelta

from redbot.cogs.audio.manager import JAR_BUILD as jarversion

import psutil

if sys.platform == "linux":
    import distro


class ImperialToolkit(commands.Cog):
    """Collection of useful commands and tools."""

    __author__ = "kennnyshiwa"

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()
        self.sticky_counter = Counter()
        lavalink.register_event_listener(self.event_handler)

    def cog_unload(self):
        lavalink.unregister_event_listener(self.event_handler)

    async def event_handler(self, player, event_type, extra):  # To delete at next audio update.
        # Thanks Draper#6666
        if event_type == lavalink.LavalinkEvents.TRACK_START:
            self.update_counters("tracks_played")

    def update_counters(self, key: str):
        self.counter[key] += 1
        self.sticky_counter[key] += 1

    def get_bot_uptime(self):
        delta = datetime.utcnow() - (
            self.bot.uptime if hasattr(self.bot, "uptime") else self.bot._uptime
        )
        uptime = humanize_timedelta(timedelta=delta)
        return uptime

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
                cpu = cpuinfo.get_cpu_info()["brand_raw"]
            except:
                cpu = "unknown"
            cpucount = psutil.cpu_count()
            ramamount = psutil.virtual_memory()
            ram_ios = "{1:>{width}}".format("", self._size(ramamount.total), width=width)

            servers = len(self.bot.guilds)
            shards = self.bot.shard_count
            totalusers = len(self.bot.users)
            channels = sum(len(s.channels) for s in self.bot.guilds)
            numcommands = len(self.bot.commands)
            uptime = str(self.get_bot_uptime())
            emojis = len(self.bot.emojis)
            tracks_played = "`{:,}`".format(self.counter["tracks_played"])
            total_num = "`{:,}`".format(len(lavalink.active_players()))

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
                inline=False,
            )
            embed.add_field(
                name="\N{ROBOT FACE} Bot Info",
                value=(
                    "Servers: `{servs:,}`\n"
                    "Users: `{users:,}`\n"
                    "Shard{s}: `{shard:,}`\n"
                    "Emojis: `{emojis:,}`\n"
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
                    emojis=emojis,
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
