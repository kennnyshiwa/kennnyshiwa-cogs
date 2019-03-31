from .invite import invite

def setup(bot):
    bot.add_cog(invite(bot))
    bot.remove_cog(invite)
    