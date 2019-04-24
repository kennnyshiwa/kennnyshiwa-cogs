import discord
import asyncio
import contextlib
import aiohttp

from redbot.core import commands, checks, Config

class ImperialToolkit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        default = {"colour": 0}
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
        self.config.register_global(**default)
     
    @commands.command()
    async def clink(self, ctx, id: int):
        """Get a message link from a message id."""
        for x in self.bot.get_all_channels():
            try:
                msg = await x.get_message(id)
                break
            except:
                continue
        try:
            await ctx.send(msg.jump_url)
        except:
            await ctx.send('Message not found.')

    @checks.is_owner() 
    @commands.command()
    async def usage(self, ctx: commands.Context):
        """Get the latest usage of the bot"""
        core = self.bot.get_cog("Core")
        description = (
            f"**Commands processed:** {self.bot.counter['processed_commands']} commands\n"
            f"**Command errors:** {self.bot.counter['cmd_error']} errors\n"
            f"**Messages received:** {self.bot.counter['messages_read']} messages\n"
            f"**Messages sent** (not including this one): {self.bot.counter['msg_sent']} messages\n"
            f"**Guilds joined:** {self.bot.counter['guild_join']} guilds\n"
            f"**Guilds left:** {self.bot.counter['guild_remove']} guilds"
        )
        embed = discord.Embed(title="Usage of {} since the last restart".format(ctx.bot.user.name),
            color=await ctx.embed_color(), description=description)
        embed.set_footer(text=f"Been up for {core.get_bot_uptime()} | Modeled after Neuro's Modok")
        m = await ctx.send(embed=embed)
        if self.bot.is_owner(ctx.author):
            await m.add_reaction("\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}")
            await m.add_reaction("\N{BLACK SQUARE FOR STOP}")
            await m.add_reaction("\N{BLACK RIGHT-POINTING TRIANGLE WITH DOUBLE VERTICAL BAR}")
            await m.add_reaction("\N{NO ENTRY SIGN}")

            def check(reaction, user):
                return (str(reaction.emoji) in ["\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}", "\N{BLACK SQUARE FOR STOP}",
                     "\N{BLACK RIGHT-POINTING TRIANGLE WITH DOUBLE VERTICAL BAR}", "\N{NO ENTRY SIGN}"]) and (user.id == ctx.author.id) and (reaction.message.id == m.id)
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60.0)
                except asyncio.TimeoutError:
                    return
                with contextlib.suppress(discord.HTTPException):
                    await m.remove_reaction(str(reaction.emoji), user)
                if str(reaction.emoji) == "\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}":
                    cmd = self.bot.get_command("restart")
                    await ctx.invoke(cmd)
                elif str(reaction.emoji) == "\N{BLACK SQUARE FOR STOP}":
                    cmd = self.bot.get_command("shutdown")
                    await ctx.invoke(cmd)
                elif str(reaction.emoji) == "\N{BLACK RIGHT-POINTING TRIANGLE WITH DOUBLE VERTICAL BAR}":
                    cog = self.bot.get_cog("Maintenance")
                    if cog:
                        on = await cog.conf.on()
                        if on[0]:
                            cmd = self.bot.get_command("maintenance off")
                            d = "off"
                        else:
                            cmd = self.bot.get_command("maintenance on")
                            d = "on"
                        await ctx.invoke(cmd)
                        await ctx.send(f"Maintenance {d}.")
                    else:
                        await m.add_reaction("\N{CROSS MARK}")
                        await asyncio.sleep(1)
                        await m.remove_reaction("\N{CROSS MARK}", ctx.guild.me)
                elif str(reaction.emoji) == "\N{NO ENTRY SIGN}":
                    await m.delete()
    
    @checks.is_owner()
    @commands.command()
    async def update(self, ctx):
        guild_count = len(ctx.bot.guilds)
        payload = guild_count
        token = 'b33f92b290dfc8d6f05041df0ed7207b25791ab15e9c43f8eafe8b29d850b49d613b3a142d56122105c1563442e4b95edac56584d2832aa7a9898130d7325ced'

        headers = {
            'authorization': token,
            'content-type': 'application/json'
            }
  
        url = 'https://divinediscordbots.com/bot/{}/stats'.format(ctx.bot.user.id)
        async with self.session.post(url, json={'server_count': guild_count}, headers=headers) as resp:
            embed = discord.Embed(
                title="Bot Stats",
                description="Sent Statistics to Divine Discord Bots",
                color=await self.config.colour()
            )
            embed.add_field(name="HTTP Return Code", value= "{}".format(resp.status), inline=True)
            embed.add_field(name="Number of guilds sent", value="{}".format(payload), inline=True)
            await ctx.send(embed=embed)
    
    async def on_guild_join(self, guild): 
        await self.update()
  
    async def on_guild_remove(self, guild): 
        await self.update()
  
    async def on_ready(self):
        await self.update()