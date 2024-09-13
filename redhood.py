import discord
from discord.ext import commands
import config
import signal
import wavelink
import asyncio
from colorama import Fore

# bot subclass


class RedHood(commands.Bot):
    def __init__(
        self, command_prefix: str, intents: discord.Intents, *args, **kwargs
    ) -> None:
        # Forward all arguments, and keyword-only arguments to commands.Bot
        super().__init__(command_prefix, intents=intents, *args, **kwargs)

    # Here you are overriding the default start method and write your own code.
    async def setup_hook(self) -> None:
        exts = config.cogExt

        # loading cogs
        if not exts:
            print(Fore.RED + "No cogs were provided!")
            return
        else:
            print(Fore.GREEN + "loading cogs...")
            for ext in exts:
                await self.load_extension(ext)
            
            print(Fore.GREEN + "All cogs are loaded successfully!")

        # connecting wavelink
        print(Fore.LIGHTGREEN_EX + "connecting wavelink..")
        nodes = [
            wavelink.Node(
                uri=config.lavalink_url,
                password=config.lavalink_password,
                inactive_player_timeout=10,
            )
        ]  # decalring nodes variable

        # connecting...
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)
        print(Fore.LIGHTGREEN_EX + "Wavelink connected successfully!")

    # on connect event
    async def on_connect(self):
        # switching status
        status_index = 0
        activity_index = 0

        while True:
            await self.change_presence(
                status=config.statuses[status_index],
                activity=config.activities[activity_index],
            )

            status_index = (status_index + 1) % len(config.statuses)
            activity_index = (activity_index + 1) % len(config.activities)

            await asyncio.sleep(10)  # Sleep for 10 seconds (10 seconds)

    # on ready event
    async def on_ready(self):
        # logger
        config.logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        # intro
        print(f"""Logged In As {bot.user}\nID - {bot.user.id}
        {config.botName} Here!
        logged In as {bot.user.name}
        Total servers ~ {len(bot.guilds)}
        Total Users ~ {len(bot.users)}
        Bot is online!
        \nPress Ctrl+C to exit""")


async def prefix(self, message: discord.Message):
    return commands.when_mentioned_or(config.prefix)(self, message)


# bot variable
if __name__ == "__main__":
    bot = RedHood(command_prefix=prefix, intents=discord.Intents.all())

    # logging in with token
    bot.run(config.DISCORD_TOKEN, root_logger=True)

    # printing sigint receiving
    print("\nReceived SIGINT (Ctrl+C), exiting...")

    # signal input
    signal.signal(
        signal.SIGINT,
        lambda sig, frame: bot.close(),
    )
