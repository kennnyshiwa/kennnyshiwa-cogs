from .lastfm import LastFM


def setup(bot):
    bot.add_cog(LastFM(bot))
