from .lastfm import LastFM

__red_end_user_data_statement__ = (
    "This cog stores a user ID to match them to their lastfm user"
    "This will wipe their saved username from the cog"
)

def setup(bot):
    bot.add_cog(LastFM(bot))
