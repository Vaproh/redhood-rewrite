import discord
from discord.ext import commands
import time
import config
import signal
import os
import wavelink
import asyncio

# bot subclass


class CustomBot(commands.Bot):
    def __init__(
        self, command_prefix: str, intents: discord.Intents, *args, **kwargs
    ) -> None:
        # Forward all arguments, and keyword-only arguments to commands.Bot
        super().__init__(command_prefix, intents=intents, *args, **kwargs)

    # Here you are overriding the default start method and write your own code.
    async def setup_hook(self) -> None:
        print("loading cogs...")
        # loading cogs
        for ext in config.cogExt:
            await self.load_extension(ext)
        print("All cogs are loaded successfully!")
        print("Syncing slash commands...")

        # connecting wavelink
        print("connecting wavelink...")
        time.sleep(0.1)
        print("connecting wavelink..")
        nodes = [
            wavelink.Node(
                uri=config.lavalink_url,
                password=config.lavalink_password,
                inactive_player_timeout=10,
            )
        ]  # decalring nodes variable
        time.sleep(0.1)
        print("connecting wavelink.")
        # connecting...
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)
        time.sleep(0.1)
        print("Wavelink connected successfully!")

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
    return commands.when_mentioned_or("::")(self, message)


# bot variable
if __name__ == "__main__":
    bot = CustomBot(command_prefix=prefix, intents=discord.Intents.all())

    # logging in with token
    bot.run(config.DISCORD_TOKEN, root_logger=True)

    # clearing the screen and proceeding
    os.system("cls" if os.name == "nt" else "clear")
    # printing sigint receiving
    print("Received SIGINT (Ctrl+C), exiting...")
    time.sleep(2.5)
    # signal input
    signal.signal(
        signal.SIGINT,
        lambda sig, frame: print("Received SIGINT (Ctrl+C), exiting...") or bot.close(),
    )
