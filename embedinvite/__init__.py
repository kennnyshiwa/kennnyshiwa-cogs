from .invite import invite

def setup(bot):
    bot.add.cog(invite(bot))
    