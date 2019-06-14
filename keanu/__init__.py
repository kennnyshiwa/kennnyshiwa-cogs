from .keanu import Keanu


def setup(bot):
    cog = Keanu(bot)
    bot.add_cog(cog)