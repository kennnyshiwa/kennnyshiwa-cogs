from .invite import invite

def setup(bot):
    bot.remove.cog(invite)
    bot.add.cog(invite(bot))
    