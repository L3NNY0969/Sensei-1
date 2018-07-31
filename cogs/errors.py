import discord
from discord.ext import commands
import asyncio


class Errors:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        em = discord.Embed(color=discord.Color.red(), title='An error occurred.')
        if isinstance(error, commands.NotOwner):
            em.description = 'This command is for the owner only.'
            return
            x = await ctx.send(embed=em)
            await asyncio.sleep(5)
            await x.delete()

        elif isinstance(error, commands.MissingPermissions):
            missing = ""
            perms = {
                "ban_members": "Ban Members",
                "kick_members": "Kick Members",
                "manage_messages": "Manage Messages",
                "manage_emojis": "Manage Emojis",
                "mute_members": "Mute Members",
                "administrator": "Administrator",
                "manage_guild": "Manage Server"
            }
            for x in error.missing_perms:
                missing += f"{perms[x]} \n"
            em.description = f'You do not have enough permissions! You are missing the following permissions required to run this command:\n\n{missing}'
            x = await ctx.send(embed=em)
            await asyncio.sleep(5)
            await x.delete()
        elif isinstance(error, commands.CommandOnCooldown):
            retry_time = error.retry_after
            if retry_time < 60:
                actual_time = "{} seconds".format(int(retry_time))
            elif retry_time >= 60 and retry_time < 3600:
                actual_time = "{} minutes".format(int(retry_time / 60))
            elif retry_time >= 3600 and retry_time < 86400:
                actual_time = "{} hours".format(int(retry_time / 3600))
            elif retry_time >= 86400:
                actual_time = "{} days".format(int(retry_time / 86400))
            em.description = 'The command is on a cool down! You can use it again in {}.'.format(actual_time)
            return
            x = await ctx.send(embed=em)
            await asyncio.sleep(5)
            await x.delete()
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have enough permissions to do that!")
        else:
            await ctx.send(f'{error}')
            print(f"An error occurred in {ctx.author.guild.name}: {error}")


def setup(bot):
    bot.add_cog(Errors(bot))