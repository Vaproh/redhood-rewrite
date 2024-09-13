# importing discord modules
import discord
from discord.ext import commands

# importing utility modules
import config
import datetime

# improting main bot class
from main import CustomBot

        # if isinstance(error, commands.MissingRequiredArgument):
        #     embed = discord.Embed(title="Error", description="You are missing a required argument!", color=config.color_main)
        #     embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        #     embed.set_footer(icon_url=ctx.bot.user.avatar_url,text=config.footer_text)

# cog starts here
class ErrorHandler(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
    
    # event listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        
        # try webhook
        webhook = discord.SyncWebhook.from_url("https://discord.com/api/webhooks/1226888630363226112/Emhykx-k_OSGhVKmETneToctptCkzdGwX35eZ6q0fRJLxHnOOisnC_xsERPD2fmO9mQY")
        try:
            emb = discord.Embed(title=f"Command runned in {ctx.guild.name}", description=f"Command name: `{ctx.command.qualified_name}`\nAuthor Name: {str(ctx.author)}\nGuild Id: {ctx.guild.id}\nCommand executed: `{ctx.message.content}`\nChannel name: {ctx.channel.name}\nChannel Id: {ctx.channel.id}\nJump Url: [Jump to]({ctx.message.jump_url})\nCommand runned without error: False", timestamp=ctx.message.created_at, color=config.color_err)
        except:
            return
        emb.set_thumbnail(url=ctx.author.display_avatar.url) # set set_thumbnail for webhook
        
        
        if isinstance(error, commands.BotMissingPermissions):
            permissions = ", ".join([f"{permission.capitalize()}" for permission in error.missing_permissions]).replace("_", " ")
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  Unfortunately I am missing **`{permissions}`** permissions to run the command `{ctx.command}`", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Bot Missing {permissions} permissions to run the command", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.MissingPermissions):
            permissions = ", ".join([f"{permission.capitalize()}" for permission in error.missing_permissions]).replace("_", " ")
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  You lack `{permissions}` permissions to run the command `{ctx.command}`.", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"User Missing {permissions} permissions to run the command", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.MissingRole):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  You need `{error.missing_role}` role to use this command.", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Missing role", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  This command is on cooldown. Please retry after `{round(error.retry_after, 1)} Seconds` .", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Command On Cooldown", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  You missed the `{error.param.name}` argument.\nDo it like: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Argument missing", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.EmojiNotFound):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  The Emoji Cannot be found", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Emoji not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.RoleNotFound):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  The Role Cannot be found", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Role not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.GuildNotFound):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  The Guild Cannot be found", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Guild not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.UserNotFound):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  The User Cannot be found", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"User not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.MemberNotFound):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  The Member Cannot be found", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"Member not found", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return
        
        if isinstance(error, commands.NSFWChannelRequired):
            em = discord.Embed(title="Error detected", description=f"<:crosss:1212440602659262505>  The Channel is required to be NSFW to execute this command", color=config.color_err)
            await ctx.send(embed=em, delete_after=10, mention_author=True)
            await ctx.message.delete(delay=10)
            emb.add_field(name="Error:", value=f"NSFW Channel disabled", inline=False)
            webhook.send(embed=emb, username=f"{str(self.bot.user)} | Error Command Logs", avatar_url=self.bot.user.avatar.url)
            return

        # add more from https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.PrivateMessageOnly
# setup
async def setup(bot: CustomBot):
    await bot.add_cog(ErrorHandler(bot))
