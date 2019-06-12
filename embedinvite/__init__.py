from .invite import Invite


def setup(bot):
    invite = Invite(bot)
    global old_invite
    old_invite = bot.get_command("invite")
    if old_invite:
        bot.remove_command(old_invite.name)
    bot.add_cog(invite)
