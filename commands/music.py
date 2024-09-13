from redhood import RedHood
import discord
from discord.ext import commands
import wavelink
from wavelink import Player
from typing import cast
import config


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


# music class
class Music(commands.Cog):
    def __init__(self, bot: RedHood):
        self.bot = bot

    # play command
    @commands.command(aliases=["p", "P", "PLAY"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """Play a song with the given query."""

        # try to join vc
        try:
            vc: Player = await ctx.author.voice.channel.connect(
                cls=Player, reconnect=True, self_deaf=True
            )
        except:
            vc: Player = ctx.voice_client
        if not ctx.guild:
            return

        # joining vc...
        player: Player
        player = cast(Player, ctx.voice_client)  # type: ignore

        # checking some conditions
        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=Player)  # type: ignore
            except AttributeError:
                embed = discord.Embed(
                    title="Error detected",
                    description="<:crosss:1212440602659262505> Please join a voice channel first before using this command.",
                    color=config.color_err,
                )
                await ctx.send(embed=embed)
                return
            except discord.ClientException:
                embed1 = discord.Embed(
                    title="Error detected",
                    description="<:crosss:1212440602659262505> I was unable to join this voice channel. Please try again.",
                    color=config.color_err,
                )
                await ctx.send(embed=embed1)
                return

        # checking if paused
        if vc.paused:
            await ctx.send("Player is paued do `!resume` to play it again")

        # Turn on AutoPlay to enabled mode.
        # enabled = AutoPlay will play songs for us and fetch recommendations...
        # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
        # disabled = AutoPlay will do nothing...
        player.autoplay = wavelink.AutoPlayMode.partial

        # Lock the player to this channel...
        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await ctx.send(
                f"You can only play songs in {player.home.mention}, as the player has already started there."
            )
            return

        tracks: wavelink.Search = await wavelink.Playable.search(
            query, source=wavelink.TrackSource.YouTube
        )
        if not tracks:
            await ctx.send(
                f"{ctx.author.mention} - Could not find any tracks with that query. Please try again."
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(
                f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue."
            )

        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)

            if not player.playing:
                # Play now since we aren't playing anything...
                await player.play(player.queue.get(), volume=30)
            elif Player.playing:
                embed_queue = discord.Embed(color=config.color_sec)
                embed_queue.set_author(
                    name="Track added in the queue!",
                    url=track.uri,
                    icon_url="https://cdn.discordapp.com/emojis/1226985238891204762.gif?size=96&quality=lossless",
                )
                embed_queue.set_thumbnail(url=track.artwork)
                embed_queue.add_field(
                    name="Track", value=f"[{track.title}]({track.uri})", inline=False
                )
                embed_queue.add_field(name="Track Author", value=f"`{track.author}`")
                embed_queue.add_field(
                    name="Track Length", value=f"{convert_to_minutes(track.length)}"
                )
                embed_queue.set_footer(
                    icon_url=ctx.author.avatar.url,
                    text=f"Requested by {ctx.author.display_name}",
                )
                await ctx.send(embed=embed_queue)

        if not player.playing:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get(), volume=30)


# setup
async def setup(bot: RedHood):
    await bot.add_cog(Music(bot))
