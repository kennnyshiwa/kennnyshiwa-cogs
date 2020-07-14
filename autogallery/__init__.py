from .autogallery import Autogallery


def setup(bot):
    bot.add_cog(Autogallery(bot))
