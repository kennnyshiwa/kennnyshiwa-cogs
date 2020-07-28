from .pottermore import Pottermore

__red_end_user_data_statement__ = (
    "This cog stores data to match a user to a Harry Potter House"
    "Nothing else is stored which is not provided through a command"
    "This cog will remove data through a data request"
)

def setup(bot):
    bot.add_cog(Pottermore(bot))
