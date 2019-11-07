from .screenshare import Screenshare


def setup(bot):
    bot.add_cog(Screenshare(bot))