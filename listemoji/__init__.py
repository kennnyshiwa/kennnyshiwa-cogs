from .listemoji import Listemoji


def setup(bot):
    bot.add_cog(Listemoji(bot))