"""discord red-bot ark search"""
import requests
from discord import Embed
from redbot.core import commands

__author__="kennnyshiwa and Beryju"

class ARKCog(commands.Cog):
    """ARK lookup Cog"""

    special_queries = {
        '@everyone': "Hah. Nice try. Being very funny. Cheeky cunt.",
        ':(){ :|: & };: -': "This is a python bot, not a bash bot you nimwit."
    }

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def do_lookup(query: str) -> dict:
        """Run the actual ARK lookup"""
        base_url = ("https://odata.intel.com/API/v1_0/Products/Processors()?&$filter="
                    "substringof(%%27%s%%27,ProductName)&$format=json")
        response = requests.get(base_url % query).json()
        if not response.get('d'):
            return None
        return response.get('d')[0]

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace('`', "'")

    @commands.command()
    async def ark(self, *query):
        """Search for `query` on Intel's ARK. By default shows the following attributes:

          - ProductName
          - ClockSpeed
          - ClockSpeedMax
          - CoreCount
          - ThreadCount
          - VTD
          - AESTech

        Reference of fields can be found here: https://odata.intel.com/
        """
        query = self.escape_query(' '.join(query))
        # Check special queries first
        if query in self.special_queries:
            await self.bot.say(self.special_queries[query])
            return
        cpu_data = ARKCog.do_lookup(query)
        if not cpu_data:
            await self.bot.say("I couldn't find anything matching `%s`" % query)
            return
        fields = ['ProductName', 'ClockSpeed', 'ClockSpeedMax',
                  'CoreCount', 'ThreadCount', 'VTD', 'AESTech']

        # Create embedded message
        embed = Embed(title="ARK Search Result",
                      description="Query was `%s`" % query,
                      color=0x0071c5)
        for field in fields:
            embed.add_field(name=field, value=cpu_data[field])
        await self.bot.say(embed=embed)

