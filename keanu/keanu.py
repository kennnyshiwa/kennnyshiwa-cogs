import os
import discord
import aiohttp
import asyncio
import functools

from redbot.core import commands, checks
from redbot.core.data_manager import cog_data_path

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


KEANU_LINK = (
    "https://cdn.discordapp.com/attachments/341265291814240257/589217424868507650/20190614-185203-Wyvern-id3257503.mp4"
)
# Use a historical link incase something changes
FONT_FILE = (
    "https://github.com/matomo-org/travis-scripts/"
    "raw/65cace9ce09dca617832cbac2bbae3dacdffa264/fonts/Verdana.ttf"
)

class Keanu(commands.Cog):
    """
        Create your very own Keanu video
    """

    def __init__(self, bot):
        self.bot = bot

    async def check_video_file(self):
        if not (cog_data_path(self) / "template.mp4").is_file():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(KEANU_LINK) as resp:
                        data = await resp.read()
                with open(cog_data_path(self) / "template.mp4", "wb") as save_file:
                    save_file.write(data)
            except Exception:
                log.error("Error downloading keanu video template", exc_info=True)
                return False
        return True

    async def check_font_file(self):
        if not (cog_data_path(self) / "Verdana.ttf").is_file():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(FONT_FILE) as resp:
                        data = await resp.read()
                with open(cog_data_path(self) / "Verdana.ttf", "wb") as save_file:
                    save_file.write(data)
            except Exception:
                log.error("Error downloading keanu video template", exc_info=True)
                return False
        return True

    @commands.command(aliases=["keanu"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @checks.bot_has_permissions(attach_files=True)
    async def keanuvid(self, ctx, *, text: str):
        """Make keanu videos
            There must be exactly 1 `,` to split the message
        """
        t = ctx.message.clean_content[len(f"{ctx.prefix}{ctx.invoked_with}"):]
        if not await self.check_video_file():
            return await ctx.send("I couldn't download the template file.")
        if not await self.check_font_file():
            return await ctx.send("I couldn't download the font file.")
        if len(t) != 1:
            return await ctx.send("You must submit exactly one string")
        if (not t[0] and not t[0].strip()) or (not t[1] and not t[1].strip()):
            return await ctx.send("Cannot render empty text")
        fake_task = functools.partial(self.make_keanu, t=t, u_id=ctx.message.id)
        task = self.bot.loop.run_in_executor(None, fake_task)
        async with ctx.typing():
            try:
                await asyncio.wait_for(task, timeout=300)
            except asyncio.TimeoutError:
                log.error("Error generating crabrave video", exc_info=True)
                return
        fp = cog_data_path(self) / f"{ctx.message.id}keanu.mp4"
        file = discord.File(str(fp), filename="keanu.mp4")
        try:
            await ctx.send(files=[file])
        except Exception:
            log.error("Error sending keanu video", exc_info=True)
            pass
        try:
            os.remove(fp)
        except Exception:
            log.error("Error deleting keanu video", exc_info=True)

    def make_keanu(self, t, u_id):
        """Non blocking keanuvideo generation from DankMemer bot
        https://github.com/DankMemer/meme-server/blob/master/endpoints/crab.py
        """
        fp = str(cog_data_path(self) / f"Verdana.ttf")
        clip = VideoFileClip(str(cog_data_path(self)) + "/template.mp4")
        # clip.volume(0.5)
        text = TextClip(t[0], fontsize=48, color="white", font=fp)
        
        video = CompositeVideoClip(
            [clip, text.crossfadein(1), text2.crossfadein(1), text3.crossfadein(1)]
        ).set_duration(11)
        video = video.volumex(0.1)
        video.write_videofile(
            str(cog_data_path(self)) + f"/{u_id}keanu.mp4",
            threads=1,
            preset="superfast",
            verbose=False,
            logger=None,
            temp_audiofile=str(cog_data_path(self) / f"{u_id}keanuaudio.mp3")
            # ffmpeg_params=["-filter:a", "volume=0.5"]
        )
        clip.close()
        video.close()
        return True