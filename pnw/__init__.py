from .pnw import PnW


def setup(bot):
    bot.add_cog(PnW(bot))