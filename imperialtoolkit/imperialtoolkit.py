import discord
import datetime
import sys
import cpuinfo
import os
import platform
import getpass
import redbot.core
import lavalink

from datetime import datetime

from redbot.core import commands, Config

from redbot.core.utils.chat_formatting import humanize_timedelta

from redbot.cogs.audio.manager import JAR_BUILD as jarversion

try:
    import psutil

    psutilAvailable = True
except ImportError:
    psutilAvailable = False


class ImperialToolkit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
  
    @commands.command()
    async def clink(self, ctx, id: int):
        """Get a message link from a message id."""
        for x in self.bot.get_all_channels():
            try:
                msg = await x.get_message(id)
                break
            except:
                continue
        try:
            await ctx.send(msg.jump_url)
        except:
            await ctx.send('Message not found.')

    @staticmethod
    def _size(num):
        for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if abs(num) < 1024.0:
                return "{0:.1f}{1}".format(num, unit)
            num /= 1024.0
        return "{0:.1f}{1}".format(num, "YB")

    def get_bot_uptime(self):
        delta = datetime.utcnow() - self.bot.uptime
        uptime = humanize_timedelta(timedelta=delta)
        return uptime

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def botstat(self, ctx: commands.Context):
        """Get stats about the bot including messages sent and recieved and other info"""
        cpustats = psutil.cpu_percent()
        ramusage = psutil.virtual_memory()
        netusage = psutil.net_io_counters()
        width = max([len(self._size(n)) for n in [netusage.bytes_sent, netusage.bytes_recv]])
        net_ios = ( "\u200b""\n\t{0:<11}: {1:>{width}}".format("Bytes sent", self._size(netusage.bytes_sent), width=width) +
                "\n\t{0:<11}: {1:>{width}}".format("Bytes recv", self._size(netusage.bytes_recv), width=width))

        if sys.platform == "linux":
            import distro

        IS_WINDOWS = os.name == "nt"
        IS_MAC = sys.platform == "darwin"
        IS_LINUX = sys.platform == "linux"

        if IS_WINDOWS:
            os_info = platform.uname()
            osver = "``{} {} (version {})``".format(os_info.system, os_info.release, os_info.version)
        elif IS_MAC:
            os_info = platform.mac_ver()
            osver = "``Mac OSX {} {}``".format(os_info[0], os_info[2])
        elif IS_LINUX:
            os_info = distro.linux_distribution()
            osver = "``{} {}``".format(os_info[0], os_info[1]).strip()
        else:
            osver = "Could not parse OS, report this on Github."
        user_who_ran = getpass.getuser()
        
        cpu = cpuinfo.get_cpu_info()['brand']
        
        servers = len(self.bot.guilds)
        shards = self.bot.shard_count
        totalusers = sum(len(s.members) for s in self.bot.guilds)
        channels = sum(len(s.channels) for s in self.bot.guilds)
        numcogs = len(self.bot.commands)
        uptime = str(self.get_bot_uptime())
        
        red = redbot.core.__version__
        dpy = discord.__version__
        

        embed = discord.Embed(title= "Bot Stats for {}".format(ctx.bot.user.name),description="Below are various stats about the bot and the machine "
                "that runs the bot", color=await ctx.embed_color())
        embed.add_field(name="\N{DESKTOP COMPUTER} Server Info",
                        value="CPU usage `{}%`\n RAM usage `{}%`\n"
                        "Network usage `{}`\n Boot Time `{}`\n OS {}\n CPU Info `{}`".format(
                            str(cpustats),
                            str(ramusage.percent),
                            net_ios,
                            datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
                            osver,
                            cpu
                        )
        )
        embed.add_field(name="\N{ROBOT FACE} Bot Info",
                        value="Servers: `{servs}`\n"
                            "Users: `{users}`\n"
                            "Shard{s}: `{shard}`\n"
                            "Channels: `{channels}`\n"
                            "Number of commands: `{numcogs}`\n"
                            "Bot Uptime: `{uptime}`".format(
                                servs=servers,
                                users=totalusers,
                                s="s" if shards >=2 else "",
                                shard=shards,
                                channels=channels,
                                numcogs = numcogs,
                                uptime = uptime,
                                inline=True)
                        )
        embed.add_field(name="\N{BOOKS} Libraries,",
                        value="Lavalink: `{lavalink}`\n"
                        "Jar Version: `{jarbuild}`\n"
                        "Red Version: `{redversion}`\n"
                        "Discord.py Version: `{discordversion}`".format(
                            lavalink=lavalink.__version__,
                            jarbuild=jarversion,
                            redversion=red,
                            discordversion=dpy)
                        )
        embed.set_footer(text="{}".format(await ctx.bot.db.help.tagline()))
        embed.set_thumbnail(url=ctx.bot.user.avatar_url_as(static_format="png"))
        await ctx.send(embed=embed)