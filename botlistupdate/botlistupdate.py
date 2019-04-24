import discord
import asyncio
import contextlib
import aiohttp

from redbot.core import commands, checks, Config

class BotListUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@checks.is_owner() 
@commands.command()
async def _update(self):
    async with aiohttp.ClientSession(loop=self.bot.loop) as cs:
        await cs.post(
            f"https://botsfordiscord.com/api/bots/{self.id}",
            json={"server count": self.guilds},
            header={"Authorization": c404406caed32deccb251b6147ac83c0a981c0b1f24db77936b70119ab417a3b7ec65447144adb38c39c0cb9234e6965e5779591f5d2ef2f1eeb4d9d12e813cc, "content-type": "application/json"},
        )
        await channel.send("Update sent to BotsForDiscord")