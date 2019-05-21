from .trackerinfo import Trackerinfo

def setup(bot):
    bot.add_cog(Trackerinfo(bot))