from .invite import Invite

def setup(bot):
    bot.add_cog(Invite(bot))
    bot.remove_cog(invite)
    