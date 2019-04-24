from .botlistupdate import BotListUpdate

def setup(bot):
    bot.add_cog(BotListUpdate(bot))