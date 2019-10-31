import redbot.core.data_manager as datam
import json
import urllib
import discord
import aiohttp
import os
from redbot.core import commands
from redbot.core.i18n import Translator

_ = Translator('Last_FM', __file__)

BaseCog = getattr(commands, "Cog", object)

# TODO
# Top artist, album, tracks of past 7 days


class LastFM(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.path = str(datam.cog_data_path(self)).replace('\\', '/')
        self.settings_file = 'settings'

        self.check_folder()
        self.check_file()

        self.bot.loop.create_task(self.load_settings())

        self.lf_gateway = 'http://ws.audioscrobbler.com/2.0/'

        self.payload = {}
        self.payload['api_key'] = 'c44979d5d86ff515ba9fba378c610474'
        self.payload['format'] = 'json'

    def save_json(self, filename, data):
        with open(self.path + '/{}.json'.format(filename), encoding='utf-8', mode="w") as f:
            json.dump(data, f, indent=4, sort_keys=True, separators=(',', ' : '))
        return data

    def load_json(self, filename):
        with open(self.path + '/{}.json'.format(filename), encoding='utf-8', mode="r") as f:
            data = json.load(f)
        return data

    def check_folder(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def check_file(self):
        if not os.path.exists(self.path + '/{}.json'.format(self.settings_file)):
            self.save_json(self.settings_file, {})

    def generate_default_settings(self):
        if 'users' not in self.settings or 'servers' not in self.settings:
            self.settings = {}
            self.settings['users'] = {}
            self.settings['servers'] = {}
            self.save_json(self.settings_file, self.settings)
        return True

    async def load_settings(self):
        self.settings = self.load_json(self.settings_file)
        self.generate_default_settings()

    async def save_settings(self):
        self.save_json(self.settings_file, self.settings)

    async def _url_decode(self, url):
        # Fuck non-ascii URLs!!!@##$@
        url = urllib.parse.urlparse(url)
        url = '{0.scheme}://{0.netloc}{1}'.format(url, urllib.parse.quote(url.path))
        return url

    async def _api_request(self, method=None, username=None, limit=None, artist=None, track=None, mbid=None, autocorrect=None):
        payload = self.payload

        if method:
            payload['method'] = method
        if username:
            payload['username'] = username
        if artist:
            payload['artist'] = artist
        if track:
            payload['track'] = track
        if limit:
            payload['limit'] = int(limit)
        if autocorrect:
            payload['autocorrect'] = autocorrect

        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector())
        async with session.get(self.lf_gateway, params=payload) as r:
            data = await r.json()
        session.close()
        return data

    # {
    #   'servers': {
    #               'youtube': false|true
    #               },
    #   'users': {
    #               'id': 'username'
    #            }
    #
    # }

    @commands.command(pass_context=True, name='nowplaying')
    async def _nowplaying(self, context):
        """Shows the current played song"""
        if str(context.author.id) in self.settings['users']:
            username = self.settings['users'][str(context.author.id)]

            method = 'user.getRecentTracks'
            limit = 1
            response = await self._api_request(method=method, username=username, limit=limit)
            user = response['recenttracks']['@attr']['user']
            track = response['recenttracks']['track'][0]
            if '@attr' in track:
                if track['@attr']['nowplaying'] == 'true':
                    artist = track['artist']['#text']
                    artist_url = await self._url_decode('https://www.last.fm/music/{}'.format(artist.replace(' ', '+')))
                    song = track['name']
                    track_url = await self._url_decode(track['url'])

                    album = track['album']['#text']
                    album_url = await self._url_decode('https://www.last.fm/music/{}/{}'.format(artist.replace(' ', '+'), album.replace(' ', '+')))

                    image = track['image'][-1]['#text']
                    tags = await self._api_request(method='track.getTopTags', track=song, artist=artist, autocorrect=1)
                    trackinfo = await self._api_request(method='track.getInfo', track=song, artist=artist, username=username)

                    if 'userplaycount' in trackinfo['track']:
                        playcount = trackinfo['track']['userplaycount']
                    else:
                        playcount = '0'

                    if 'error' not in tags:
                        tags = ', '.join(['[{}]({})'.format(tag['name'], tag['url']) for tag in tags['toptags']['tag'][:10]])
                    else:
                        tags = None

                    song = [song if len(song) < 18 else song[:18] + '...'][0]
                    artist = [artist if len(artist) < 18 else artist[:18] + '...'][0]
                    album = [album if len(album) < 18 else album[:18] + '...'][0]

                    em = discord.Embed()
                    em.set_thumbnail(url=image)
                    em.add_field(name=_('**Artist**'), value='[{}]({})'.format(artist, artist_url))
                    em.add_field(name=_('**Track**'), value='[{}]({})'.format(song, track_url))
                    em.add_field(name=_('**Playcount**'), value='{}'.format(playcount))
                    em.add_field(name=_('**Album**'), value='[{}]({})'.format(album, album_url))
                    if tags:
                        em.add_field(name=_('**Tags**'), value=tags, inline=False)
                    await context.send(embed=em)
            else:
                await context.send(_('{} is not playing any song right now').format(user))

    @commands.group(pass_context=True, name='lastfm', aliases=['lf'])
    async def _lastfm(self, context):
        """Get Last.fm statistics of a user."""

    @_lastfm.command(pass_context=True, name='set')
    async def _set(self, context, username: str):
        """Set a username"""
        method = 'user.getInfo'
        response = await self._api_request(method=method, username=username)
        if 'error' not in response:
            self.settings['users'][str(context.author.id)] = username
            await self.save_settings()
            message = _('Username set')
        else:
            message = response['message']
        await context.send(message)

    @_lastfm.command(pass_context=True, name='recent')
    async def _recent(self, context):
        """Shows recent tracks"""
        if str(context.author.id) in self.settings['users']:
            username = self.settings['users'][str(context.author.id)]
            limit = '10'
            method = 'user.getRecentTracks'
            response = await self._api_request(method=method, username=username, limit=limit)
            if 'error' not in response:
                user = response['recenttracks']['@attr']['user']
                author = context.author
                text = ''
                for i, track in enumerate(response['recenttracks']['track'][:8], 1):
                    artist = track['artist']['#text']
                    song = track['name']

                    url = await self._url_decode(track['url'])
                    artist = [artist if len(artist) < 25 else artist[:25] + '...'][0]
                    song = [song if len(song) < 25 else song[:25] + '...'][0]
                    text += _('`{}`{:<5}**[{}]({})** — **[{}]({})**\n').format(str(i), '', artist, 'https://www.last.fm/music/{}'.format(artist.replace(' ', '+')), song, url)
                em = discord.Embed(description=text)
                avatar = author.avatar_url if author.avatar else author.default_avatar_url
                em.set_author(name=_('{}\'s Recent Tracks').format(user), icon_url=avatar, url='http://www.last.fm/user/{}/library'.format(user))
                await context.send(embed=em)
            else:
                message = response['message']
                await context.send(message)
