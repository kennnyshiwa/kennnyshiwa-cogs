from .tickets import Tickets


def setup(bot):
    bot.add_cog(Tickets(bot))
