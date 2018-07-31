from utils.context import Context
import asyncpg
import pymongo
import asyncio
import datetime
import io
import json
import logging
import platform
import textwrap
import traceback
from contextlib import redirect_stdout
from motor.motor_asyncio import AsyncIOMotorClient


import aiohttp
import discord
import psutil
from discord.ext import commands




async def get_pre(bot, message):
    with open('data/general/servers.json') as f:
            data = json.load(f)
    try:
        if str(message.guild.id) not in data:
            return ";"
    except:
        pass
    else:
        return data[str(message.guild.id)]['prefix']

with open("apikeys.json") as f:
    x = json.load(f)

bot = commands.Bot(command_prefix=get_pre, owner_id=392151500929105920, description="A simple discord bot")
token = x['keys']['token']

bot._last_result = None
bot.load_extension('cogs.util')
bot.load_extension('cogs.fun')
bot.load_extension('cogs.math')
bot.load_extension('cogs.mod')
bot.load_extension('cogs.config')
bot.load_extension('cogs.idiotic')
bot.load_extension('cogs.stocks')
bot.load_extension('cogs.giveaway')
bot.load_extension('cogs.music')
bot.load_extension('cogs.help')
bot.load_extension('cogs.logs')
bot.load_extension('cogs.connectfour')
bot.load_extension('cogs.animals')
bot.load_extension('cogs.hangman')
bot.load_extension('cogs.economy')
bot.commands_run = 0


bot.start_time = datetime.datetime.now()


async def send_stats():
    tokens = (
        ('https://discordbots.org/api/bots/%s/stats', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyNzI4OTg5MTM3ODgyMzE2OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTI0NzA0ODg3fQ.SwouqZy5hd8sltHyQV-hRt0yB-cP9h1aXHtTOw-FFEs"),
        ('https://bots.discord.pw/api/bots/%s/stats', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiIzOTIxNTE1MDA5MjkxMDU5MjAiLCJyYW5kIjo2ODYsImlhdCI6MTUyNDM1NTk4OH0.0mXtgI90nTP1Std8B622588K8Rz5t8_kmy0wLYd5U4c"),
        ('https://botsfordiscord.com/api/v1/bots/%s', "bb0c0f933f3b2113babc3329271dbf736c266a0de51d3a504722c2c549c5f818e1554fc30037e936af6c8753c9d148014401c440e7b877babc9911cdb0aa6ad6")
    )
    payload = {'Content-Type': 'application/json', 'server_count': len(bot.guilds)}
    for url, token in tokens:
        headers = {'Authorization': token}
        await bot.session.post(url % bot.user.id, json=payload, headers=headers)


async def vote_check(id: int):
    headers = {'Authorization': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyNzI4OTg5MTM3ODgyMzE2OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTI0NzA0ODg3fQ.SwouqZy5hd8sltHyQV-hRt0yB-cP9h1aXHtTOw-FFEs"}
    resp = await bot.session.get("https://discordbots.org/api/bots/427289891378823168/votes", headers=headers)
    upvoters = resp.json()
    if id in upvoters['id']:
        return True
    else:
        return False


def cleanup_code(content):
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')


@bot.event
async def on_ready():
    separator = '━' * 44
    print(separator)
    print("Your bot is online and connected as:")
    print(bot.user.name)
    print("ID: " + str(bot.user.id))
    print("Discord Version: %s" % discord.__version__)
    server = len(bot.guilds)
    print(f"Playing in {server} servers")
    print(separator)
    bot.session = aiohttp.ClientSession()
    await send_stats()
    while True:
        server1 = len(bot.guilds)
        await bot.change_presence(game=discord.Game(name=f'{server1} servers', type=3))
        await asyncio.sleep(10)
        await bot.change_presence(game=discord.Game(name=f'{str(len(set(bot.get_all_members())))} users', type=3))
        await asyncio.sleep(10)
        await bot.change_presence(game=discord.Game(name=';help'))
        await asyncio.sleep(10)
        await bot.change_presence(game=discord.Game(name='on https://sensei-bot.glitch.me'))
        await asyncio.sleep(10)
        await bot.change_presence(game=discord.Game(name='with fire1234#6302', url="https://www.twitch.tv/#", type=1))
        await asyncio.sleep(10)


@bot.event
async def on_guild_join(guild):
    message = (
        f"Hi! My name is **{bot.user.name}**, and I am a bot that someone you trust added to your server, **{guild.name}**. My command prefix is **;**. For the list of available commands, use **;help**. If you have any feedback, you can use my **;feedback** command to send a message to my developer.")
    servers = len(bot.guilds)
    embed = discord.Embed(title="New Server! :grinning: ", color=discord.Colour.green())
    embed.add_field(name="Server Number:", value=servers)
    embed.add_field(name="Name:", value=guild.name)
    embed.add_field(name="Server Owner:", value=guild.owner)
    embed.add_field(name="Server ID:", value=guild.id)
    if guild.icon_url:
        embed.set_thumbnail(url=guild.icon_url)
    else:
        embed.set_thumbnail(url='https://cdn.discordapp.com/embed/avatars/0.png')
    embed.add_field(name="Total Users: ", value=len(set(bot.get_all_members())))
    channel = bot.get_channel(431992896225542154)
    await channel.send(embed=embed)
    print(f"New Server: {guild.name}")
    await send_stats()
    try:
        await guild.owner.send(message)
    except discord.Forbidden:
        pass


@bot.event
async def on_command(ctx):
    bot.commands_run += 1


@bot.event
async def on_guild_remove(guild):
    servers = len(bot.guilds)
    embed = discord.Embed(title="Removed Server :sob:", color=discord.Colour.red())
    embed.add_field(name='Server Number:', value=servers)
    embed.add_field(name="Server Name:", value=guild.name)
    embed.add_field(name="Server Owner:", value=guild.owner)
    embed.add_field(name="Server ID:", value=guild.id)
    embed.set_thumbnail(url=guild.icon_url)
    channel = bot.get_channel(431992896225542154)
    await channel.send(embed=embed)
    await send_stats()
    print(f"Left Server: {guild.name}")


@bot.event
async def on_member_join(member):
    with open("data/general/servers.json") as f:
        data = json.load(f)
    try:
        guild = member.guild
        member_count = len(guild.members)
        user = member
        server = guild.name
        mention = user.mention
        welc_channel = str(data[str(guild.id)]['welc_channel'])
        if welc_channel is not None:
            welc_channel = welc_channel.replace('<', '')
            welc_channel = welc_channel.replace('#', '')
            welc_channel = welc_channel.replace('>', '')
            msg = str(data[str(guild.id)]['welc_msg'])
            if '{user}' in msg:
                msg = msg.replace('{user}', user.name)
            if '{server}' in msg:
                msg = msg.replace('{server}', server)
            if '{member_count}' in msg:
                msg = msg.replace('{member_count}', str(member_count))
            if '{mention}' in msg:
                msg = msg.replace('{mention}', mention)

            if msg is not None:
                try:
                    channel = int(welc_channel)
                    channel = bot.get_channel(channel)
                    await channel.send(msg)
                except:
                    pass
            else:
                pass
        else:
            pass
    except KeyError:
        pass


@bot.event
async def on_member_remove(member):
    with open('data/general/servers.json') as f:
        data = json.load(f)
    try:
        guild = member.guild
        user = member
        server = guild.name
        member_count = len(guild.members)
        welc_channel = str(data[str(guild.id)]['welc_channel'])
        if welc_channel is not None:
            welc_channel = welc_channel.replace('<', '')
            welc_channel = welc_channel.replace('#', '')
            welc_channel = welc_channel.replace('>', '')
            msg = str(str(data[str(guild.id)]['leave_msg']))
            if '{user}' in msg:
                msg = msg.replace('{user}', user.name)
            if '{server}' in msg:
                msg = msg.replace('{server}', server)
            if '{member_count}' in msg:
                msg = msg.replace('{member_count}', str(member_count))
            if msg is not None:
                try:
                    channel = int(welc_channel)
                    channel = bot.get_channel(channel)
                    await channel.send(msg)
                except:
                    pass
            else:
                return
        else:
            return
    except KeyError:
        pass


@bot.event
async def on_message_edit(old_msg, new_msg):
    """Runs a command if someone mistypes a command.
    If the old message equals the new message the bot will ignore it same thing if the author is a bot.
    Else the bot will process the command.
    """
    if old_msg.author.bot and new_msg.author.bot:
        return  # Ignore bots
    if old_msg.content == new_msg.content:
        return  # Ignore the same content
    else:
        # Run the command
        await bot.process_commands(new_msg)


@bot.event
async def on_message(message):
    if not message.author.bot:
        if isinstance(message.channel, discord.abc.PrivateChannel) and message.content.startswith(";"):
            await message.channel.send(f"You can't use commands in private messages {bot.get_emoji(452709542485295125)}")
            return
        else:
            try:
                await bot.process_commands(message)
            except Exception:
                pass
            if message.content.upper().startswith(";SERVERPREFIX"):
                x = await get_pre(bot, message)
                await message.channel.send(f"The prefix for this server is **{x}**")
    else:
        pass


@bot.command()
async def invite(ctx):
    """Invite the bot to your server"""
    await ctx.send(f"<{discord.utils.oauth_url(bot.user.id)}>")


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
    f"""Gives {bot.user.name}'s speed"""
    embed = discord.Embed(timestamp=ctx.message.created_at,
                          title=f"My speed is: {bot.latency * 1000:.0f} milliseconds")
    await ctx.send(embed=embed)


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, *, extension: str):
    try:
        if extension.lower() == 'all':
            msg = await ctx.send(f"Updating {bot.get_emoji(403035325242540032)}")
            await asyncio.sleep(5)
            bot.unload_extension('cogs.util')
            bot.unload_extension('cogs.fun')
            bot.unload_extension('cogs.math')
            bot.unload_extension('cogs.mod')
            bot.unload_extension('cogs.config')
            bot.unload_extension('cogs.idiotic')
            bot.unload_extension('cogs.stocks')
            bot.unload_extension('cogs.giveaway')
            bot.unload_extension('cogs.music')
            bot.unload_extension('cogs.help')
            bot.unload_extension('cogs.logs')
            bot.unload_extension('cogs.connectfour')
            bot.unload_extension('cogs.animals')
            bot.load_extension('cogs.util')
            bot.load_extension('cogs.fun')
            bot.load_extension('cogs.math')
            bot.load_extension('cogs.mod')
            bot.load_extension('cogs.config')
            bot.load_extension('cogs.idiotic')
            bot.load_extension('cogs.stocks')
            bot.load_extension('cogs.giveaway')
            bot.load_extension('cogs.music')
            bot.load_extension('cogs.help')
            bot.load_extension('cogs.logs')
            bot.load_extension('cogs.connectfour')
            bot.load_extension('cogs.animals')

            await ctx.message.add_reaction("✅")
            await msg.edit(content="All cogs have been reloaded!")
        else:
            msg = await ctx.send(f'Updating {bot.get_emoji(403035325242540032)}')
            await asyncio.sleep(3)
            bot.unload_extension(f'cogs.{extension}')
            bot.load_extension(f'cogs.{extension}')
            await ctx.message.add_reaction("✅")
            await msg.edit(content=f'cogs.{extension} has been reloaded')
    except Exception as e:
        await ctx.send(f'An error occurred! More details:```{e}```')


@bot.command(name='eval')
@commands.is_owner()
async def _eval(ctx, *, body):
    """Evaluates python code"""
    env = {
        'ctx': ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
        '_': bot._last_result,
    }

    env.update(globals())

    body = cleanup_code(body)
    stdout = io.StringIO()
    err = out = None

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    def paginate(text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text) - 1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    try:
        exec(to_compile, env)
    except Exception as e:
        err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        return await ctx.message.add_reaction('\u2049')

    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        if ret is None:
            if value:
                try:

                    out = await ctx.send(f'```py\n{value}\n```')
                except:
                    paginated_text = paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')
        else:
            bot._last_result = ret
            try:
                out = await ctx.send(f'```py\n{value}{ret}\n```')
            except:
                paginated_text = paginate(f"{value}{ret}")
                for page in paginated_text:
                    if page == paginated_text[-1]:
                        out = await ctx.send(f'```py\n{page}\n```')
                        break
                    await ctx.send(f'```py\n{page}\n```')

    if out:
        await ctx.message.add_reaction('\u2705')  # tick
    elif err:
        await ctx.message.add_reaction('\u2049')  # x
    else:
        await ctx.message.add_reaction('\u2705')


@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def info(ctx):
    '''Gives info about the bot'''
    embed = discord.Embed(title=f"{bot.user.name}'s Information", timestamp=ctx.message.created_at,
                          color=000000)
    server = len(bot.guilds)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name="Creator", value=f'{bot.get_user(392151500929105920)}')
    embed.add_field(name="Server Count", value=f"{server} servers")
    embed.add_field(name=":link: Links",
                    value="[Invite link](https://discordapp.com/oauth2/authorize?client_id=427289891378823168&permissions=8&scope=bot)\nhttps://discord.gg/3EDgbbG.\n:arrow_up_small: Upvote Sensei [here](https://discordbots.org/bot/427289891378823168/vote)\n Coding Language:\n\t[Python 3.6.5](https://www.python.org/downloads/release/python-365/)\n\t[discord.py](https://github.com/Rapptz/discord.py/tree/rewrite/discord)")
    embed.add_field(name="Users:", value=str(len(set(bot.get_all_members()))))
    embed.add_field(name='Uptime:', value=botuptime())
    embed.add_field(name='Operating System:', value=platform.system())
    embed.add_field(name="Connected Voice Channels", value=len(bot.voice_clients))
    RAM = psutil.virtual_memory()
    used = RAM.used >> 20
    percent = RAM.percent
    embed.add_field(name='Memory Usage', value=f"{used} MB ({percent}%)")
    embed.add_field(name="Shard Count", value=bot.shard_count)
    embed.add_field(name='This Shard', value=bot.shard_id)
    embed.set_footer(text="Powered by discord.py v.1.0.0a | Requested by %s" % (ctx.message.author))
    await ctx.send(embed=embed)

@bot.command()
async def update(ctx):
    embed=discord.Embed(title="Latest Update", color=000000)
    emoji = bot.get_emoji(470075737513394185)
    embed.description=f"""Update `1.0.4`

{emoji} `New register command. Create a bank account`

{emoji} `New daily command. Get your daily credit for your bank account`

{emoji} `New votebonus command. Get your voting bonus for your bank account`

{emoji} `New balance command. Check how much money you have`

{emoji} `New give command. Give some of your money to someone else`

{emoji} `New leaderboard command. Check your place in the global bank leaderboard`"""
    await ctx.send(embed=embed)


bot.uptime_ = datetime.datetime.utcnow()


def botuptime():
    delta = datetime.datetime.utcnow() - bot.uptime_
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    values = [f'{days} days', f'{hours} hours', f'{minutes} minutes', f'{seconds} seconds']
    return ', '.join(v for v in values if str(v)[0] != '0')


@bot.command()
async def uptime(ctx):
    embed=discord.Embed(title="Bot Uptime", description=botuptime(), color=000000)
    await ctx.send(embed=embed)


@bot.command()
async def restart(ctx):
    msg = await ctx.send("Restarting")
    bot.logout()
    bot.login(token=token, bot=bot)
    await msg.edit(content="Restarted")


@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(color=discord.Color.red(), title='An error occurred.')
    if isinstance(error, commands.NotOwner):
        em.description = 'This command is for the owner only.'
        return await ctx.send(embed=em, delete_after=10)
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
        await ctx.send(embed=em, delete_after=10)
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
        return await ctx.send(embed=em, delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have enough permissions to do that!")
    elif isinstance(error, (commands.MissingRequiredArgument, commands.TooManyArguments)):
        embed=discord.Embed(title="Incorrect Usage", color=discord.Color.red())
        embed.description = f"Correct Usage: **{ctx.prefix}{ctx.command.signature}**"
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'{error}')
        print(f"An error occurred in {ctx.author.guild.name}: {error}")


@bot.command()
@commands.is_owner()
async def runas(ctx, user: discord.Member, *, command):
    """Calls a command on behalf of another person"""
    msg = ctx.message
    msg.content = f"{ctx.prefix}{command}"
    msg.author = user
    context = await bot.get_context(msg, cls=Context)
    if not context.command:
        return await ctx.send(f"Command does not exist")
    await bot.invoke(context)

@bot.command()
async def requestcmd(ctx, *, request:str):
    channel=bot.get_channel(473353077202747392)
    server = ctx.message.author.guild
    embed1 = discord.Embed(title="Your request has been sent!", color=000000)
    await ctx.send(embed=embed1)
    embed2 = discord.Embed(title=f"{ctx.message.author} sent you this request from {server}:",
                           description=f"{request}",
                           color=000000, timestamp=ctx.message.created_at)
    embed2.set_footer(text="Sent at", icon_url=ctx.author.avatar_url)
    await channel.send(embed=embed2)


@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def feedback(ctx, *, feedback: str ):
    """Sends feedback to the support server"""
    server = ctx.message.author.guild
    embed1 = discord.Embed(title="Your feedback has been sent!", color=000000)
    await ctx.send(embed=embed1)
    embed2 = discord.Embed(title=f"{ctx.message.author} sent you this feedback from {server}:",
                           description=f"{feedback}",
                           color=000000, timestamp=ctx.message.created_at)
    embed2.set_footer(text="Sent at", icon_url=ctx.author.avatar_url)
    channel = bot.get_channel(431997383270858773)
    await channel.send(embed=embed2)




bot.run(token)
