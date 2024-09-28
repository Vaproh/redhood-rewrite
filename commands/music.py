# importing discord modules
import typing
import discord
from discord.ext import commands

# importing bot subclass
from redhood import RedHood

# importing music module
import wavelink
from wavelink import Player
from typing import cast

# importing utility modules
import config
import datetime


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


# checking bot is in vc, user is in vc,etc
async def check_perms(self, ctx: commands.Context):
    if not ctx.voice_client:
        embed = discord.Embed(
            title="Error detected",
            description="<:crosss:1212440602659262505> I am not in any vc.",
            color=config.color_err,
        )
        return await ctx.reply(embed=embed)  # bot is not in vc
    if ctx.voice_client is None:
        embed2 = discord.Embed(
            title="Error detected",
            description="<:crosss:1212440602659262505> You are not in a voice channel.",
            color=config.color_err,
        )
        return await ctx.reply(embed=embed2)  # user is not in vc
    vc: Player = ctx.voice_client
    if not vc.playing:
        embed3 = discord.Embed(
            title="Error detected",
            description="<:crosss:1212440602659262505> I am not playing any song.",
            color=config.color_err,
        )
        return await ctx.reply(embed=embed3)  # bot is not playing songs
    if ctx.author.voice.channel.id != vc.channel.id:
        embed4 = discord.Embed(
            title="Error detected",
            description="<:crosss:1212440602659262505> You are in not the same voice channel.",
            color=config.color_err,
        )
        # user is not in the same channel as bot
        return await ctx.reply(embed=embed4)


time = datetime.datetime.now()


# class starts here
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
                # type: ignore
                player = await ctx.author.voice.channel.connect(cls=Player)
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
        player.autoplay = wavelink.AutoPlayMode.disabled

        # Lock the player to this channel...
        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await ctx.send(
                f"You can only play songs in {
                    player.home.mention}, as the player has already started there."
            )
            return

        # This will handle fetching Tracks and Playlists...
        # Seed the doc strings for more information on this method...
        # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
        # Defaults to YouTube for non URL based queries...
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
                f"Added the playlist **`{
                    tracks.name}`** ({added} songs) to the queue."
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

    # skip command
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def skip(self, ctx: commands.Context) -> None:
        """Skip the current song."""

        # define track
        track: Player = ctx.voice_client

        # embed
        embed_skip = discord.Embed(color=config.color_sec)
        embed_skip.set_author(
            icon_url="https://cdn.discordapp.com/emojis/1227216938078306389.gif?size=96&quality=lossless",
            name="Track Skipped!",
            url=track.current.uri,
        )
        embed_skip.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )
        embed_skip.add_field(
            name="Track",
            value=f"[{track.current.title}]({track.current.uri})",
            inline=False,
        )
        embed_skip.add_field(
            name="Track Author", value=f"`{track.current.author}`", inline=True
        )
        embed_skip.set_thumbnail(url=track.current.artwork)

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = cast(Player, ctx.voice_client)
        if not player:
            return

        # skip current song...
        await player.skip(force=True)

        # add reaction and send embed
        await ctx.message.add_reaction("\u2705")
        await ctx.send(embed=embed_skip)

    # nightcore command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nightcore(self, ctx: commands.Context) -> None:
        """Set the filter to a nightcore style."""

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = cast(Player, ctx.voice_client)
        if not player:
            return

        # apply filter
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)

        # embed
        embed_nightcore = discord.Embed(
            title="Applied!",
            description="Sucessfully applied filter nightcore!",
            color=config.color_main,
        )
        embed_nightcore.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227225866434646016.gif"
        )
        embed_nightcore.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        await ctx.message.add_reaction("\u2705")
        await ctx.send(embed=embed_nightcore)

    # pause_resume command
    @commands.command(name="toggle", aliases=["pause", "resume", "Pause", "Resume"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pause_resume(self, ctx) -> None:
        """Pause or Resume the Player depending on its current state."""

        # define track
        track: Player = ctx.voice_client

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = cast(Player, ctx.voice_client)
        if not player:
            return

        # embed pause
        embed_pause = discord.Embed(
            title="Paused!",
            description=f"Sucessfully paused track [{
                track.current.title}]({track.current.uri}) .",
            color=config.color_sec,
        )
        embed_pause.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227227646262251521.gif?size=48"
        )
        embed_pause.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # embed resume
        embed_resume = discord.Embed(
            title="Resumed!",
            description=f"Sucessfully resumed track [{
                track.current.title}]({track.current.uri}) .",
            color=config.color_sec,
        )
        embed_resume.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227229038553071668.gif?size=48"
        )
        embed_resume.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # pause or resume current track
        await player.pause(not player.paused)
        await ctx.send(embed=embed_pause if player.paused else embed_resume)

    # volume command
    @commands.command(aliases=["vol"])
    async def volume(self, ctx: commands.Context, _volume: typing.Optional[int]):
        """
        Set the volume of the bot.
        {command_prefix}{command_name} volume
        volume(optional): The volume for the music playing. If not provide, return current volume
        {command_prefix}{command_name} 200
        NOTE: max is 100, and makes it inaudible.
        """

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = typing.cast(Player, ctx.voice_client)

        # check volume
        if not _volume:
            # embed
            embed_volume = discord.Embed(
                title="Volume:",
                description=f"**{player.volume}%**",
                color=config.color_main,
            )
            embed_volume.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227234443089936455.gif"
            )
            embed_volume.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # send message
            return await ctx.send(embed=embed_volume)

        elif _volume > 100:  # volume limit
            # embed
            embed_limit = discord.Embed(
                title="Cannot Increase Volume!",
                description="Cannot exceed 100 volume **hard limit**.",
                color=config.color_main,
            )
            embed_limit.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227233754603327562.gif"
            )
            embed_limit.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # send message
            await ctx.send(embed=embed_limit)
        else:  # set volume
            # embed
            embed_in_volume = discord.Embed(
                title="Set volume to",
                description=f"**{_volume}%**",
                color=config.color_main,
            )
            embed_in_volume.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227231707598426234.gif"
            )
            embed_in_volume.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # set volume
            await player.set_volume(_volume)

            # send message
            return await ctx.send(embed=embed_in_volume)

    # Disconnect command
    @commands.command(aliases=["dc", "disconnect"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stop(self, ctx) -> None:
        """Disconnect the Player."""

        # checking bot is in vc, user is in vc,etc
        if not ctx.voice_client:
            embed = discord.Embed(
                title="Error detected",
                description="<:crosss:1212440602659262505> I am not in any vc.",
                color=config.color_err,
            )
            return await ctx.reply(embed=embed)  # bot is not in vc
        if ctx.voice_client is None:
            embed2 = discord.Embed(
                title="Error detected",
                description="<:crosss:1212440602659262505> You are not in a voice channel.",
                color=config.color_err,
            )
            return await ctx.reply(embed=embed2)  # user is not in vc
        vc: Player = ctx.voice_client
        if ctx.author.voice.channel.id != vc.channel.id:
            embed4 = discord.Embed(
                title="Error detected",
                description="<:crosss:1212440602659262505> You are in not the same voice channel.",
                color=config.color_err,
            )
            return await ctx.reply(
                embed=embed4
            )  # user is not in the same channel as bot

        # define player
        player: Player = cast(Player, ctx.voice_client)
        if not player:
            return

        # embed
        embed_ = discord.Embed(
            title="Disconnected!",
            description=f"Successfully disconnected from `{
                player.channel.name}`.",
            color=config.color_main,
        )
        embed_.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227261183015518310.gif"
        )
        embed_.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # disconnect the bot from current vc
        await player.disconnect()
        await ctx.send(embed=embed_)

    # shuffle command
    @commands.command(aliases=["shuf"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shuffle(self, ctx: commands.Context) -> None:
        """Shuffle the queue."""

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = ctx.voice_client

        # shuffle current queue
        player.queue.shuffle()

        # embed shuf
        embed_shuf = discord.Embed(
            title="Queue has been shuffled!", color=config.color_main
        )
        embed_shuf.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227237360165453824.gif?size=96"
        )
        embed_shuf.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # embed queue is empty
        embed_empty = discord.Embed(title="Queue is empty!", color=config.color_main)
        embed_empty.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227237360165453824.gif?size=96"
        )
        embed_empty.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # send message
        if wavelink.Queue.is_empty == True and Player.playing == True:
            await ctx.send(embed=embed_empty)
        else:
            await ctx.send(embed=embed_shuf)

    # now playing command
    @commands.command(aliases=["nowp", "np"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nowplaying(self, ctx: commands.Context) -> None:
        """Show the current playing song."""

        # checking perms...
        await check_perms(self, ctx)

        # define track
        track: Player = ctx.voice_client

        # define player
        vc: Player = ctx.voice_client

        # embed
        embed_play = discord.Embed(color=config.color_main)
        embed_play.set_author(
            name="Now Playing!",
            url=track.current.uri,
            icon_url="https://cdn.discordapp.com/emojis/1226964487572029554.gif?size=96&quality=lossless",
        )
        embed_play.set_image(url=track.current.artwork)
        embed_play.add_field(
            name="Track",
            value=f"[{track.current.title}]({track.current.uri})",
            inline=False,
        )
        embed_play.add_field(
            name="Track Author",
            value=f"`{
                track.current.author}`",
        )
        embed_play.add_field(
            name="Track Length", value=f"{convert_to_minutes(track.current.length)}"
        )
        source = track.current.source
        if source == "spotify":
            embed_play.add_field(
                name="Track Source", value=f"<a:spotify:1226989191150309536> {source}"
            )
        elif source == "youtube":
            embed_play.add_field(
                name="Track Source",
                value=f"<:Youtube_music:1226989661797486634>  {source}",
            )
        else:
            embed_play.add_field(name="Track Source", value=f"{source}")
        embed_play.add_field(name="In channel", value=f"{vc.channel.mention}")
        embed_play.add_field(name="Autoplay", value=f"On (Default)")
        embed_play.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # send message
        await ctx.send(embed=embed_play)

    # queue
    @commands.command(aliases=["q", "que"], help="Look Into The Queue", usage="queue")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        # checking perms...
        await check_perms(self, ctx)

        # define player
        vc: Player = ctx.voice_client

        # define track
        track: Player = ctx.voice_client

        # enumerate current queue
        queue = enumerate(list(vc.queue), start=1)  # queue list

        # retrieve track list
        track_list = "\n".join(
            f"[{num}] {track.title}" for num, track in queue
        )  # track list

        # convert length
        length_seconds = round(vc.current.length) / 1000  # length of song
        hours, remainder = divmod(length_seconds, 3600)  # secs converter.
        minutes, seconds = divmod(remainder, 60)  # another converter..
        # another converter...
        duration_str = f"{int(hours):02d}:{int(minutes):02d}:{
            int(seconds):02d}"

        # embed
        embed5 = discord.Embed(
            description=f"**__Now Playing__**\n  {vc.current.title}・{
                duration_str}\n\n```\n{track_list}```",
            color=config.color_main,
        )  # embed
        embed5.set_author(
            icon_url="https://cdn.discordapp.com/emojis/1226985238891204762.gif?size=96&quality=lossless",
            name="Queue",
            url=track.current.uri,
        )
        embed5.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # send message
        await ctx.reply(embed=embed5, mention_author=False)

    # clear queue command
    @commands.command(aliases=["cq", "cls"], help="Clear The Queue", usage="clearqueue")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clearqueue(self, ctx):
        # checking perms...
        await check_perms(self, ctx)

        # define player
        vc: Player = ctx.voice_client

        # clear queue
        vc.queue.clear()
        embed5 = discord.Embed(
            Title="Successfully Cleared The Queue.", color=config.color_sec
        )
        embed5.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )
        embed5.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227247136970903633.gif?size=96"
        )

        # send message
        await ctx.reply(embed=embed5, mention_author=False)

    # join command
    @commands.command(aliases=["connect", "connect_vc", "join_vc"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def join(self, ctx: commands.Context) -> None:
        """Join the voice channel of the message author."""

        # check perms
        if ctx.author.voice.channel is None:
            embed2 = discord.Embed(
                title="Error detected!",
                description="You are not in a voice channel.",
                color=config.color_err,
            )
            return await ctx.reply(embed=embed2)  # user is not in vc
        vc: Player = ctx.voice_client
        if vc is not None and vc.playing:
            embed3 = discord.Embed(
                title="Error detected!",
                description=f"I am playing songs in another channel named `{
                    vc.channel.name}`",
                color=config.color_err,
            )
            return await ctx.reply(embed=embed3)  # bot is not playing songs

        # join author voice channel
        await ctx.author.voice.channel.connect(
            cls=Player, reconnect=True, self_deaf=True
        )

        # embed
        embed_join = discord.Embed(
            title="Joined!",
            description=f"Successfully connect to {
                ctx.author.voice.channel.mention} .",
            color=config.color_main,
        )
        embed_join.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )
        embed_join.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227248421274910781.gif?size=96"
        )

        # send message
        await ctx.send(embed=embed_join)

    # previous command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def previous(self, ctx: commands.Context) -> None:
        """Play the previous song in the queue."""

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = cast(Player, ctx.voice_client)
        if not player:
            return

        #  embed if track is avail
        embed_play = discord.Embed(
            title="Now Playing Previous Track!",
            description="Playing previous track now!",
            color=config.color_main,
        )
        embed_play.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227262528929661019.gif"
        )
        embed_play.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # embed if track is not avail
        embed_not = discord.Embed(
            title="Error occured",
            description="There is no previous track to play.",
            color=config.color_err,
        )
        embed_not.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227261183015518310.gif?size=96"
        )
        embed_not.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # geeting previous track and play it else send no previous track to play
        if player.queue.history:
            previous_track = player.queue.history[0]
            await player.queue.put_wait(previous_track)
            await player.stop()
            await ctx.send(embed=embed_play)
        else:
            await ctx.send(embed=embed_not)

    # grab command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def grab(self, ctx, *, query: str) -> None:
        """Grab the song info and send it to your DM."""

        # define track
        tracks: wavelink.Search = await wavelink.Playable.search(query)

        # cannot get track
        if not tracks:
            await ctx.send(
                f"{ctx.author.mention} - Could not find any tracks with that query. Please try again."
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            embed = discord.Embed(
                title=f"Playlist: {tracks.name}",
                description=f"**Tracks:**\n{
                    ', '.join([track.title for track in tracks.tracks])}",
                color=config.color_main,
            )
            embed.set_thumbnail(url=tracks.thumbnail)
            await ctx.author.send(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            embed = discord.Embed(
                title=track.title,
                description=f"**Artist:** {track.author}\n**Album:** {
                    track.album.name}\n**Duration:** {convert_to_minutes(track.length)}",
                color=config.color_main,
            )
            embed.set_thumbnail(url=track.artwork)
            await ctx.author.send(embed=embed)

    # loop
    @commands.command(aliases=["repeat"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def loop(self, ctx: commands.Context, mode: str = None) -> None:
        """Loop the current song."""

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = ctx.voice_client

        # loop and other modes
        if mode == None:
            wavelink.QueueMode.loop

            # embed
            embed_loop = discord.Embed(
                title="Loop",
                description=f"Looping is now enabled for track `{
                    player.current.title}`.",
                color=config.color_main,
            )
            embed_loop.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227272974248448011.gif"
            )
            embed_loop.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # send embed
            await ctx.send(embed=embed_loop)

        elif mode == "all":
            wavelink.QueueMode.loop_all

            # embed
            embed_loop = discord.Embed(
                title="Loop",
                description=f"Looping is now enable for the entire queue.",
                color=config.color_main,
            )
            embed_loop.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227272974248448011.gif"
            )
            embed_loop.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # send embed
            await ctx.send(embed=embed_loop)

        elif mode == "off":
            wavelink.QueueMode.normal

            # embed
            embed_loop = discord.Embed(
                title="Loop",
                description=f"Looping is now disabled.`.",
                color=config.color_main,
            )
            embed_loop.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227272974248448011.gif"
            )
            embed_loop.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # send embed
            await ctx.send(embed=embed_loop)

    # remove command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx: commands.Context, index: int) -> None:
        """Remove a song from the queue."""

        # checking perms...
        await check_perms(self, ctx)

        # define player
        player: Player = cast(Player, ctx.voice_client)
        if not player:
            return

        removed_track = player.queue.remove(index - 1)

        embed = discord.Embed(
            title="Remove",
            description=f"Removed **`{removed_track.title}`** from the queue.",
            color=config.color_main,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227275483331428352.gif"
        )
        embed.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # embed invalid
        embed__ = discord.Embed(
            title="Remove", description=f"Invalid Song number.", color=config.color_main
        )
        embed__.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227275483331428352.gif"
        )
        embed__.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        # checking if a valid index
        if index < 1 or index > len(player.queue):
            await ctx.send(embed=embed__)
            return

        # remove track
        removed_track = player.queue.remove(index - 1)
        await ctx.send(embed=embed)

    # skip to command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skipto(self, ctx: commands.Context, position: int) -> None:
        """Skip to a specific song in the queue."""

        # checking perms...
        await check_perms(self, ctx)

        # player
        player: Player = typing.cast(Player, ctx.voice_client)

        # checks index
        if isinstance(position, str):
            position = int(position)
        if len(player.queue) == 0:  # check index
            # embed
            embed1 = discord.Embed(
                title="Skipto",
                description=f"No songs in queue to skip to.",
                color=config.color_main,
            )
            embed1.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227275483331428352.gif"
            )
            embed1.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )

            # send embed
            return await ctx.send(embed=embed1)

        if position:
            if position > len(player.queue):
                # embed
                embed2 = discord.Embed(
                    title="Skipto",
                    description=f"Position exceeds queue count of {
                        len(player.queue)}",
                    color=config.color_main,
                )
                embed2.set_thumbnail(
                    url="https://cdn.discordapp.com/emojis/1227275483331428352.gif"
                )
                embed2.set_footer(
                    icon_url=ctx.author.avatar.url,
                    text=f"Requested by {ctx.author.display_name}",
                )

                # send embed
                return await ctx.send(embed=embed2)
            else:  # plays new track
                new_track = player.queue[position - 1]
                await player.queue.delete(position - 1)
                await player.play(new_track)

        embed = discord.Embed(
            title="Skipto",
            description=f"Skipped to **`{player.current.title}`**.",
            color=config.color_main,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1227275483331428352.gif"
        )
        embed.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by {ctx.author.display_name}",
        )

        await ctx.send(embed=embed)

    # seek command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def seek(self, ctx: commands.Context, position: int):
        """
        Jump to a specific in the current audio playing. Value must be in seconds.
        {command_prefix}{command_name} track_time
        track(required): The time to skip to in seconds
        {command_prefix}{command_name} 120
        """

        # checking perms...
        await check_perms(self, ctx)

        # seeking the position
        if isinstance(position, str):
            position = int(position)
        position * 1000
        player: Player = typing.cast(Player, ctx.voice_client)
        if position >= player.current.length:
            embed = discord.Embed(
                title="Seek",
                description="Position exceeds or equals to song duration",
                color=config.color_main,
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1227275483331428352.gif"
            )
            embed.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}",
            )
            return await ctx.send(embed=embed)

        # seek func
        return await player.seek(position)

    # autoplay command
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def autoplay(self, ctx: commands.Context, input: str):
        """
        Turn autoplay on or off else partial!
        """

        player: Player
        player = cast(Player, ctx.voice_client)

        # checking perms...
        await check_perms(self, ctx)

        thumbnailImage = "https://images-ext-1.discordapp.net/external/\
7QRT3cXpyl7PjWyxDVQDQ6inUaXKHO2vmF4pQ1PhG64/%3Fsize%3D160%26name%\
3Dfuck%2Byou/https/media.discordapp.net/stickers/1124155345728700527.png\
?format=webp&quality=lossless"

        if input == "on":
            player.autoplay = wavelink.AutoPlayMode.enabled

            # embedAutoplay
            embedAutoplay = discord.Embed(
                title="Autoplay",
                color=config.color_main,
                description="Autoplay has been enabled!",
            )
            embedAutoplay.set_thumbnail(url=thumbnailImage)
            embedAutoplay.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}.",
            )

            await ctx.send(embed=embedAutoplay)
        elif input == "off":
            player.autoplay = wavelink.AutoPlayMode.partial

            # embedAutoplay
            embedAutoplay = discord.Embed(
                title="Autoplay",
                color=config.color_main,
                description="Autoplay has been disabled!",
            )
            embedAutoplay.set_thumbnail(url=thumbnailImage)
            embedAutoplay.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}.",
            )

            await ctx.send(embed=embedAutoplay)
        else:
            # embedAutoplay
            embedAutoplay = discord.Embed(
                title="Autoplay",
                color=config.color_main,
                description="Invalid Argument. Only allowed arguments are `on` and `off`.",
            )
            embedAutoplay.set_thumbnail(url=thumbnailImage)
            embedAutoplay.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author.display_name}.",
            )

            await ctx.send(embed=embedAutoplay)


# setup command
async def setup(bot: RedHood) -> None:
    await bot.add_cog(Music(bot))
