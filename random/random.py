import discord
import asyncio
import aiohttp

from redbot.core import commands, checks, Config

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop) 
        
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

    token = 'b33f92b290dfc8d6f05041df0ed7207b25791ab15e9c43f8eafe8b29d850b49d613b3a142d56122105c1563442e4b95edac56584d2832aa7a9898130d7325ced'

    @commands.command()
    async def Update(self):
        guild_count = len(self.bot.guilds)
        payload = json.dumps({
        'server_count': guild_count
        })

        headers = {
            'authorization': token,
            'content-type': 'application/json'
        }

        url = 'https://divinediscordbots.com/bot/{}/stats'.format(self.bot.user.id)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print('divinediscordbots statistics returned {} for {}'.format(resp.status, payload))

