from .core import RequestBox


def setup(bot):
    bot.add_cog(RequestBox(bot))
