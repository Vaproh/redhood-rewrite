# importing discord modules
import discord
from discord.ext import commands

# improting main bot class
from redhood import RedHood

# importing utility modules
import wavelink
from wavelink import Player
from typing import cast

# importing config file
import config

# logger
logger = config.logging.getLogger("lavalink")

# just read the func name ;-;


def convert_to_minutes(milliseconds: int) -> str:
    """Converts milliseconds to minutes and seconds in a proper way.

    Args:
        milliseconds (int): The number of milliseconds to convert.

    Returns:
        str: The converted time in minutes and seconds.
    """

    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02.0f}:{seconds:02.0f}"


# cog strats here


class MusicHandler(commands.Cog):
    def __init__(self, bot: RedHood):
        self.bot = bot

    # wavelink node ready
    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self, payload: wavelink.NodeReadyEventPayload
    ) -> None:
        logger.info(f"Wavelink Node connected: `{
                    payload.node!r}` | Resumed: `{payload.resumed}`")

    # on track start event
    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: wavelink.TrackStartEventPayload
    ) -> None:
        player: Player | None = payload.player
        if not player:
            # Handle edge cases...
            return

        # original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed_play = discord.Embed(color=config.color_main)
        embed_play.set_author(
            name=f"Playing!",
            url=track.uri,
            icon_url="https://cdn.discordapp.com/emojis/1226964487572029554.gif?size=96&quality=lossless",
        )
        embed_play.set_image(url=track.artwork)
        embed_play.add_field(
            name="Track", value=f"[{track.title}]({track.uri})", inline=False
        )
        embed_play.add_field(name="Track Author", value=f"`{track.author}`")
        embed_play.add_field(
            name="Track Length",
            value=f"{
                convert_to_minutes(track.length)}",
        )
        source = track.source
        if source == "spotify":
            embed_play.add_field(
                name="Track Source",
                value=f"<a:spotify:1226989191150309536> {track.source}",
            )
        elif source == "youtube":
            embed_play.add_field(
                name="Track Source",
                value=f"<:Youtube_music:1226989661797486634>  {track.source}",
            )
        else:
            embed_play.add_field(name="Track Source", value=f"{track.source}")
        embed_play.add_field(name="Autoplay", value=f"On (Default)")
        embed_play.set_footer(
            icon_url=self.bot.user.avatar.url, text=config.footer_text
        )

        await player.home.send(embed=embed_play)

        logger.info(f"A track has started on `{player.channel.name}` in guild `{
                    player.guild.name}` and track name is {track}")

    # inactive player event
    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        player: Player
        await player.home.send(
            f"The player has been inactive for `{
                player.inactive_timeout}` seconds. Goodbye!"
        )
        logger.info(print(f"A player has been inactive for"))
        await player.channel.send(
            f"The player has been inactive for `{
                player.inactive_timeout}` seconds. Goodbye!"
        )
        await player.disconnect()


# setup


async def setup(bot: RedHood):
    await bot.add_cog(MusicHandler(bot))
