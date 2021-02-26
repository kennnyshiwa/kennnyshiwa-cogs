import json
import os
import re
import urllib
from typing import Literal

import aiohttp
import discord
import redbot.core.data_manager as datam
from bs4 import BeautifulSoup as Soup
from redbot.core import Config, checks, commands
from redbot.core.i18n import Translator
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

_ = Translator("Last_FM", __file__)

BaseCog = getattr(commands, "Cog", object)

# TODO
# Top artist, album, tracks of past 7 days


class LastFM(BaseCog):

    default_member_settings = {"username": ""}

    default_user_settings = default_member_settings

    default_guild_settings = {"emote": "🎵"}

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
        self.config.register_member(**self.default_member_settings)
        self.config.register_user(**self.default_user_settings)
        self.config.register_guild(**self.default_guild_settings)

        self.lf_gateway = "http://ws.audioscrobbler.com/2.0/"

        self.payload = {}
        self.payload["api_key"] = "c44979d5d86ff515ba9fba378c610474"
        self.payload["format"] = "json"

    @commands.command(name="nowplaying")
    async def _nowplaying(self, ctx):
        """Shows the current played song"""
        username = await self.config.user(ctx.author).username()

        if username == "":
            return await ctx.send("You need to set a username first")

        method = "user.getRecentTracks"
        limit = 1
        response = await self._api_request(
            method=method, username=username, limit=limit
        )
        user = response["recenttracks"]["@attr"]["user"]

        if response["recenttracks"]["track"] == []:
            print(response["recenttracks"]["track"])
            return await ctx.send(
                "{} is not playing anything, check to make sure you set the right lastfm username".format(
                    user
                )
            )

        track = response["recenttracks"]["track"][0]

        if "@attr" not in track:
            await ctx.send(_("{} is not playing any song right now").format(user))
            return

        if track["@attr"]["nowplaying"] == "true":
            artist = track["artist"]["#text"]
            artist_url = await self._url_decode(
                "https://www.last.fm/music/{}".format(artist.replace(" ", "+"))
            )
            song = track["name"]
            track_url = await self._url_decode(track["url"])

            album = track["album"]["#text"]
            album_url = await self._url_decode(
                "https://www.last.fm/music/{}/{}".format(
                    artist.replace(" ", "+"), album.replace(" ", "+")
                )
            )

            image = track["image"][-1]["#text"]
            tags = await self._api_request(
                method="track.getTopTags", track=song, artist=artist, autocorrect=1
            )
            trackinfo = await self._api_request(
                method="track.getInfo", track=song, artist=artist, username=username
            )

            if "error" not in tags:
                tags = ", ".join(
                    [
                        "[{}]({})".format(tag["name"], tag["url"])
                        for tag in tags["toptags"]["tag"][:10]
                    ]
                )
            else:
                tags = None

            song = [song if len(song) < 18 else song[:18] + "..."][0]
            artist = [artist if len(artist) < 18 else artist[:18] + "..."][0]
            album = [album if len(album) < 18 else album[:18] + "..."][0]
            spotify_url = await self._get_spotify_url(track_url)

            em = discord.Embed()
            em.set_thumbnail(url=image)
            em.add_field(
                name=_("**Artist**"), value="[{}]({})".format(artist, artist_url)
            )
            em.add_field(name=_("**Album**"), value="[{}]({})".format(album, album_url))
            em.add_field(
                name=_("**Track**"),
                value="[{}]({})".format(song, track_url),
                inline=False,
            )

            if tags:
                em.add_field(name=_("**Tags**"), value=tags, inline=False)

            msg = await ctx.send(embed=em)

            if not spotify_url:
                return

            emote = await self.config.guild(ctx.guild).emote() if ctx.guild else "🎵"
            start_adding_reactions(msg, (emote))
            predicate = ReactionPredicate.with_emojis((emote), msg)
            reaction, user = await ctx.bot.wait_for("reaction_add", check=predicate)

            if predicate.result == 0:
                await msg.clear_reactions()
                await ctx.send(spotify_url)

    @commands.group(name="lastfm", aliases=["lf"])
    async def _lastfm(self, ctx):
        """Get Last.fm statistics of a user."""

    @_lastfm.command(name="set")
    async def _set(self, ctx, username: str):
        """Set a username"""
        method = "user.getInfo"
        response = await self._api_request(method=method, username=username)
        if "error" not in response:
            await self.config.user(ctx.author).username.set(str(username))
            message = _("Username set")
        else:
            message = response["message"]
        await ctx.send(message)

    @_lastfm.command(name="recent")
    async def _recent(self, ctx):
        """Shows recent tracks"""
        username = await self.config.user(ctx.author).username()
        limit = "10"
        method = "user.getRecentTracks"
        response = await self._api_request(
            method=method, username=username, limit=limit
        )
        if "error" not in response:
            user = response["recenttracks"]["@attr"]["user"]
            author = ctx.author
            text = ""
            for i, track in enumerate(response["recenttracks"]["track"][:8], 1):
                artist = track["artist"]["#text"]
                song = track["name"]

                url = await self._url_decode(track["url"])
                artist = [artist if len(artist) < 25 else artist[:25] + "..."][0]
                song = [song if len(song) < 25 else song[:25] + "..."][0]
                text += _("`{}`{:<5}**[{}]({})** — **[{}]({})**\n").format(
                    str(i),
                    "",
                    artist,
                    "https://www.last.fm/music/{}".format(artist.replace(" ", "+")),
                    song,
                    url,
                )
            em = discord.Embed(description=text)
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            em.set_author(
                name=_("{}'s Recent Tracks").format(user),
                icon_url=avatar,
                url="http://www.last.fm/user/{}/library".format(user),
            )
            await ctx.send(embed=em)
        else:
            message = response["message"]
            await ctx.send(message)

    @_lastfm.command(name="setreact")
    @commands.guild_only()
    @checks.mod()
    async def _set_react(self, ctx, emote: str):
        """Sets the emote for the now playing embed to view the Spotify link"""
        async with self.config.guild(ctx.guild).emote() as guild_emote:
            guild_emote = emote
            await ctx.message.add_reaction(guild_emote)

    # Helper functions

    async def _api_request(
        self,
        method=None,
        username=None,
        limit=None,
        artist=None,
        track=None,
        mbid=None,
        autocorrect=None,
    ):
        payload = self.payload

        if method:
            payload["method"] = method
        if username:
            payload["username"] = username
        if artist:
            payload["artist"] = artist
        if track:
            payload["track"] = track
        if limit:
            payload["limit"] = int(limit)
        if autocorrect:
            payload["autocorrect"] = autocorrect

        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector())
        async with session.get(self.lf_gateway, params=payload) as r:
            data = await r.json()
        await session.close()
        return data

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """This cog stores a user ID to match them to their lastfm user
        this will wipe their saved username from the cog"""
        await self.config.user_from_id(user_id).clear()

    async def _get_spotify_url(self, track_url: str) -> str:
        """Fetches the spotify url from the LastFM track information page"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=2.0)
            ) as session:
                async with session.get(track_url) as response:
                    page_text = await response.text()
        except aiohttp.ServerTimeoutError:
            return
        page = Soup(page_text, "html.parser")
        try:
            spotify_url = page.find(
                "a", {"class": "play-this-track-playlink--spotify"}
            ).get("href")
        except AttributeError:
            return
        return spotify_url

    async def _url_decode(self, url):
        # Fuck non-ascii URLs!!!@##$@
        url = urllib.parse.urlparse(url)
        url = "{0.scheme}://{0.netloc}{1}".format(url, urllib.parse.quote(url.path))
        return url
