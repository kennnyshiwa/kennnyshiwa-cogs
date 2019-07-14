from .pottermore import Pottermore

def setup(bot):
    bot.add_cog(Pottermore(bot))
