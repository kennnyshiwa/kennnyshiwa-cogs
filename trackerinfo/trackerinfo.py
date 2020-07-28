from redbot.core import commands
import discord

import aiohttp


class Trackerinfo(commands.Cog):
    """Look up information about a trackers status"""

    __author__ = "kennnyshiwa"

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def ptp(self, ctx):
        """Gets info on PTP"""
        async with self.session.get("https://ptp.trackerstatus.info/api/status/") as r:
            data = await r.json()
        color = await ctx.embed_color()
        website = data["Website"]
        website = f'Website is {"down" if website == "0" else "up"}'
        irc = data["IRC"]
        irc = f'IRC is {"down" if irc == "0" else "up"}'
        ircannounce = data["IRCTorrentAnnouncer"]
        ircannounce = f'IRC Announce is {"down" if ircannounce == "0" else "up"}'
        tracker = data["TrackerHTTPS"]
        if tracker == "0":
            trackerstatus = "down"
        elif tracker == "1":
            trackerstatus = "up"
        elif tracker == "2":
            trackerstatus = "unstable"
        tracker = f"HTTPS Tracker is {trackerstatus}"

        embed = discord.Embed(
            title="PTP Status", url="https://ptp.trackerstatus.info", color=color
        )
        embed.set_image(url="https://ptp.trackerstatus.info/images/logo.png")
        embed.add_field(name="Website", value="{}".format(website))
        embed.add_field(name="IRC", value="{}".format(irc))
        embed.add_field(name="IRC Torrent Announcer", value="{}".format(ircannounce))
        embed.add_field(name="TrackerHTTP", value="{}".format(tracker))

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def ggn(self, ctx):
        """Gets info on GGN"""
        async with self.session.get("https://ggn.trackerstatus.info/api/status/") as r:
            data = await r.json()
        color = await ctx.embed_color()
        website = data["Website"]
        website = f'Website is {"down" if website == "0" else "up"}'
        irc = data["IRC"]
        irc = f'IRC is {"down" if irc == "0" else "up"}'
        ircannounce = data["IRCTorrentAnnouncer"]
        ircannounce = f'IRC Announce is {"down" if ircannounce == "0" else "up"}'
        tracker = data["TrackerHTTPS"]
        if tracker == "0":
            trackerstatus = "down"
        elif tracker == "1":
            trackerstatus = "up"
        elif tracker == "2":
            trackerstatus = "unstable"
        tracker = f"HTTPS Tracker is {trackerstatus}"

        embed = discord.Embed(
            title="GGN Status", url="https://ggn.trackerstatus.info", color=color
        )
        embed.set_image(url="https://ggn.trackerstatus.info/images/logo.png")
        embed.add_field(name="Website", value="{}".format(website))
        embed.add_field(name="IRC", value="{}".format(irc))
        embed.add_field(name="IRC Torrent Announcer", value="{}".format(ircannounce))
        embed.add_field(name="TrackerHTTP", value="{}".format(tracker))

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def red(self, ctx):
        """Gets info on RED"""
        async with self.session.get("https://red.trackerstatus.info/api/status/") as r:
            data = await r.json()
        color = await ctx.embed_color()
        website = data["Website"]
        website = f'Website is {"down" if website == "0" else "up"}'
        irc = data["IRC"]
        irc = f'IRC is {"down" if irc == "0" else "up"}'
        ircannounce = data["IRCTorrentAnnouncer"]
        ircannounce = f'IRC Announce is {"down" if ircannounce == "0" else "up"}'
        tracker = data["TrackerHTTPS"]
        if tracker == "0":
            trackerstatus = "down"
        elif tracker == "1":
            trackerstatus = "up"
        elif tracker == "2":
            trackerstatus = "unstable"
        tracker = f"HTTPS Tracker is {trackerstatus}"

        embed = discord.Embed(
            title="RED Status", url="https://red.trackerstatus.info", color=color
        )
        embed.set_image(url="https://red.trackerstatus.info/images/logo.png")
        embed.add_field(name="Website", value="{}".format(website))
        embed.add_field(name="IRC", value="{}".format(irc))
        embed.add_field(name="IRC Torrent Announcer", value="{}".format(ircannounce))
        embed.add_field(name="TrackerHTTP", value="{}".format(tracker))

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def btn(self, ctx):
        """Gets info on BTN"""
        async with self.session.get("https://btn.trackerstatus.info/api/status/") as r:
            data = await r.json()
        color = await ctx.embed_color()
        website = data["Website"]
        website = f'Website is {"down" if website == "0" else "up"}'
        irc = data["IRC"]
        irc = f'IRC is {"down" if irc == "0" else "up"}'
        ircannounce = data["Barney"]
        ircannounce = f'IRC Announce is {"down" if ircannounce == "0" else "up"}'
        tracker = data["TrackerHTTPS"]
        if tracker == "0":
            trackerstatus = "down"
        elif tracker == "1":
            trackerstatus = "up"
        elif tracker == "2":
            trackerstatus = "unstable"
        tracker = f"HTTPS Tracker is {trackerstatus}"

        embed = discord.Embed(
            title="BTN Status", url="https://BTN.trackerstatus.info", color=color
        )
        embed.set_image(url="https://btn.trackerstatus.info/images/logo.png")
        embed.add_field(name="Website", value="{}".format(website))
        embed.add_field(name="IRC", value="{}".format(irc))
        embed.add_field(name="IRC Torrent Announcer", value="{}".format(ircannounce))
        embed.add_field(name="TrackerHTTP", value="{}".format(tracker))

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def mtv(self, ctx):
        """Gets info on MTV"""
        async with self.session.get("https://mtv.trackerstatus.info/api/status/") as r:
            data = await r.json()
        color = await ctx.embed_color()
        website = data["Website"]
        website = f'Website is {"down" if website == "0" else "up"}'
        irc = data["IRC"]
        irc = f'IRC is {"down" if irc == "0" else "up"}'
        ircannounce = data["IRCTorrentAnnouncer"]
        ircannounce = f'IRC Announce is {"down" if ircannounce == "0" else "up"}'
        tracker = data["TrackerHTTPS"]
        if tracker == "0":
            trackerstatus = "down"
        elif tracker == "1":
            trackerstatus = "up"
        elif tracker == "2":
            trackerstatus = "unstable"
        tracker = f"HTTPS Tracker is {trackerstatus}"

        embed = discord.Embed(
            title="MTV Status", url="https://mtv.trackerstatus.info", color=color
        )
        embed.set_image(url="https://mtv.trackerstatus.info/images/logo.png")
        embed.add_field(name="Website", value="{}".format(website))
        embed.add_field(name="IRC", value="{}".format(irc))
        embed.add_field(name="IRC Torrent Announcer", value="{}".format(ircannounce))
        embed.add_field(name="TrackerHTTP", value="{}".format(tracker))

        await ctx.send(embed=embed)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
