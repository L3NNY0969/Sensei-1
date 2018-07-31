import Simimport discord
from discord.ext import commands
import json


class Setup:
    """Bot setup"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx):
        """Sets up the bot"""
        with open('servers.json') as f:
            data = json.loads(f.read())
        server = ctx.guild
        data[str(server.id)] = {}
        await ctx.send('Please enter a prefix (Enter None for default)')
        prefix = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if prefix.content.lower() == 'none':
            prefix.content = ';'
        await ctx.send(f'Prefix set to {prefix.content}')

        await ctx.send('Enable welcome message? (Y/N)')
        msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
            await ctx.send('What should the message say?')
            await ctx.send('The variables you can use are:')
            await ctx.send(
                '```{user} - the user\'s name\n{mention} - mentions the user\n{server} - your server\'s name\n{member_count} - the amount of members in the server```')
            msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            msg = f'{msg.content}'
            await ctx.send('What channel should be the welcome channel?')
            welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            if welc_channel.content.startswith('<#'):
                await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
            else:
                await ctx.send('Invalid channel. Please make sure you mention the channel')
                await ctx.send('What channel should be the welcome channel?')
                welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                if welc_channel.content.startswith('<#'):
                    await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
                else:
                    await ctx.send('Invalid channel. Please make sure you mention the channel')
                    await ctx.send('What channel should be the welcome channel?')
                    welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                    if welc_channel.content.startswith('<#'):
                        await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
                    else:
                        await ctx.send('Invalid channel. Please make sure you mention the channel')
                        await ctx.send('What channel should be the welcome channel?')
                        welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                        await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
        else:
            msg = None
            welc_channel = None
            pass

        await ctx.send('Enable leave message? (Y/N)')
        msg2 = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg2.content.lower() == 'yes' or 'y' == msg2.content.lower():
            await ctx.send('What should the message say?')
            await ctx.send('You can use {user} {server} and {member_count} to use them in your message')
            leave_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            await ctx.send(f'Leave message set to ```{leave_msg.content}```')
        else:
            leave_msg = None
            pass

        data[str(server.id)]['name'] = server.name
        data[str(server.id)]['prefix'] = prefix.content.strip('"')
        if welc_channel and msg != None:
            data[str(server.id)]['welc_channel'] = welc_channel.content.strip('"')
            data[str(server.id)]['welc_msg'] = msg.strip('"')
        else:
            data[str(server.id)]['welc_channel'] = welc_channel
            data[str(server.id)]['welc_msg'] = msg
        if leave_msg != None:
            data[str(server.id)]['leave_msg'] = leave_msg.content.strip('"')
        else:
            data[str(server.id)]['leave_msg'] = leave_msg

        data = json.dumps(data, indent=4, sort_keys=True)

        with open('servers.json', 'w') as f:
            f.write(data)
        await ctx.send('Setup complete')


def setup(bot):
    bot.add_cog(Setup(bot))
