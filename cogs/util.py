import unicodedata
import discord
from discord.ext import commands
import aiohttp
import inspect
import json
import datetime
import time
import platform
import asyncio
import wikipedia
import lyricwikia
import requests
import urbandict
from pygoogling.googling import GoogleSearch
from urllib.parse import quote as uriquote
from lxml import etree
import googletrans


class Utils:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=000000)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').replace('guild', 'server').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def permissions(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        """Shows a member's permissions in a specific channel.
        If no channel is given then it uses the current one.
        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = channel or ctx.channel
        if member is None:
            member = ctx.author

        await self.say_permissions(ctx, member, channel)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timer(self, ctx, timer: float):
        """Sets a timer for the given amount of minutes"""
        if timer > 60:
            await ctx.send("I can only set a timer for 60 minutes or less!")
        else:
            await ctx.send(f"Your timer for {timer} minute(s) has been set")
            time = timer * 60
            await asyncio.sleep(time)
            await ctx.send(f"Your timer has rung, {ctx.message.author.mention}!")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sendmessage(self, ctx, user: discord.Member, *, message):
        """Sends a message to the given user."""
        try:
            if user is None:
                await ctx.send("You have to mention a user!")
            else:
                await ctx.send("Your message has been sent!")
                em = discord.Embed(title=f'{ctx.message.author} has sent you a message from **{ctx.guild}**:')
                em.description = f'\n {message}'
                await user.send(embed=em)
        except discord.Forbidden:
            await ctx.send("I do not have permissions to send messages to this user!")

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """Shows info about a member.
        This cannot be used in private messages. If you don't specify
        a member then the info returned will be yours.
        """

        if member is None:
            member = ctx.author

        e = discord.Embed()
        roles = [role.name.replace('@', '@\u200b') for role in member.roles]
        shared = sum(1 for m in self.bot.get_all_members() if m.id == member.id)
        voice = member.voice
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
        else:
            voice = 'Not connected.'

        e.set_author(name=str(member))
        e.set_footer(text='Member since').timestamp = member.joined_at
        e.add_field(name='ID', value=member.id)
        e.add_field(name='Servers', value=f'{shared} shared')
        e.add_field(name='Created', value=member.created_at)
        e.add_field(name='Voice', value=voice)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        e.colour = member.colour

        if member.avatar:
            e.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=e)

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, message: commands.clean_content()):
        """Says the message that you give."""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(f"{message}")

    @commands.command(aliases=['btc'])
    async def bitcoin(self, ctx, currency: str = None):
        """Finds the current bitcoin price"""
        if currency is None:
            resp = await self.session.get('https://blockchain.info/ticker')
            r = await resp.json()
            em = discord.Embed(title='Bitcoin Price', color=000000)
            price = float(r['USD']['last'])
            em.description = f"${price:.2f}"
            await ctx.send(embed=em)
        else:
            try:
                site = await self.session.get('https://blockchain.info/ticker')
                data = await site.json()
                currency1 = currency.upper()
                em = discord.Embed(title="Bitcoin Price", color=000000)
                symbol = str(data[currency1]['symbol'])
                price = float(data[currency1]['last'])
                em.description = f'{symbol}{price:.2f}'
                await ctx.send(embed=em)
            except Exception:
                currencies = "\tUSD\n\tAUD\n\tBRL\n\tCAD\n\tCHF\n\tCLP\n\tCNY\n\tDKK\n\tEUR\n\tGBP\n\tHKD\n\tINR\n\tISK\n\tJPY\n\tKRW\n\tNZD\n\tPLN\n\tRUB\n\tSEK\n\tSGD\n\tTHB\n\tTWD\n\t"
                await ctx.send(embed=discord.Embed(title="That is not a valid currency",
                                                   description=f"Valid Currencies:\n{currencies}",
                                                   color=000000).set_footer(text="Powered by Block Chain"))

    @commands.command()
    @commands.is_owner()
    async def source(self, ctx, *, command: str):
        cmd = self.bot.get_command(command)

        if cmd:
            resp = await self.session.post("https://hastebin.com/documents", data=str(inspect.getsource(cmd.callback)))
            resp = await resp.json()
            color = discord.Color(value=000000)
            em = discord.Embed(color=color, title=f'Source for {cmd}')
            em.description = f"https://hastebin.com/{resp['key']}.py"
            await ctx.send(embed=em)
        else:
            await ctx.send("Please enter a valid command")

    @commands.command()
    async def dbl(self, ctx, bot_user: discord.Member):
        """Searches a bot up in DBL's database"""
        async with self.session.get(f'http://discordbots.org/api/bots/{bot_user.id}') as resp:
            data = await resp.json()
        if 'server_count' in data:
            server_count = data['server_count']
        else:
            server_count = None
        if 'error' not in data:
            embed = discord.Embed(title=f'{bot_user.name} DBL Info', color=00000)
            embed.add_field(name="Short Description", value=data['shortdesc'])
            embed.add_field(name="Github", value="None" if data['github'] == "" else data['github'])
            embed.add_field(name="Website", value="None" if data['website'] == "" else data['website'])
            embed.add_field(name="Invite", value=f"[Here]({data['invite']})")
            embed.add_field(name='Prefix', value=data['prefix'])
            embed.add_field(name='Library', value=data['lib'])
            embed.add_field(name='Server Count', value=server_count)
            embed.add_field(name='Upvotes', value=data['points'])
            embed.add_field(name="Upvotes this Month", value=str(data['monthlyPoints']))
            embed.add_field(name="DBL Website", value=f"[Here](https://discordbots.org/bot/{bot_user.id})")
            embed.set_thumbnail(url=bot_user.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{bot_user.mention} was not found in DBL's database!")

    @commands.command()
    async def ascii(self, ctx, *, text = None):
        if text is None:
            await ctx.send("You have to include text")
        else:
            resp = await self.session.get(f"http://artii.herokuapp.com/make?text={text}")
            message = await resp.text()
            if len(f"```{message}```") > 2000:
                return await ctx.send('Your ASCII is too long!')
            await ctx.send(f"```{message}```")

    async def get_google_entries(self, query):
        url = f'https://www.google.com/search?q={uriquote(query)}'
        params = {
            'safe': 'on',
            'lr': 'lang_en',
            'hl': 'en'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) Gecko/20100101 Firefox/53.0'
        }

        # list of URLs and title tuples
        entries = []

        # the result of a google card, an embed
        card = None

        async with self.session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                log.info('Google failed to respond with %s status code.', resp.status)
                raise RuntimeError('Google has failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())

            # for bad in root.xpath('//style'):
            #     bad.getparent().remove(bad)

            # for bad in root.xpath('//script'):
            #     bad.getparent().remove(bad)

            # with open('google.html', 'w', encoding='utf-8') as f:
            #     f.write(etree.tostring(root, pretty_print=True).decode('utf-8'))


            card_node = root.xpath(".//div[@id='rso']/div[@class='_NId']//"
                                   "div[contains(@class, 'vk_c') or @class='g mnr-c g-blk' or @class='kp-blk']")

            if card_node is None or len(card_node) == 0:
                card = None
            else:
                card = self.parse_google_card(card_node[0])

            search_results = root.findall(".//div[@class='rc']")
            # print(len(search_results))
            for node in search_results:
                link = node.find("./h3[@class='r']/a")
                if link is not None:
                    # print(etree.tostring(link, pretty_print=True).decode())
                    entries.append((link.get('href'), link.text))

        return card, entries

    @commands.command(aliases=['google'])
    async def g(self, ctx, *, query):
        """Searches google and gives you top result."""
        await ctx.trigger_typing()
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await ctx.send(str(e))
        else:
            if card:
                value = '\n'.join(f'[{title}]({url.replace(")", "%29")})' for url, title in entries[:3])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await ctx.send(embed=card)

            if len(entries) == 0:
                return await ctx.send('No results found... sorry.')

            next_two = [x[0] for x in entries[1:3]]
            first_entry = entries[0][0]
            if first_entry[-1] == ')':
                first_entry = first_entry[:-1] + '%29'

            if next_two:
                formatted = '\n'.join(f'<{x}>' for x in next_two)
                msg = f'{first_entry}\n\n**See also:**\n{formatted}'
            else:
                msg = first_entry

            await ctx.send(msg)


def setup(bot):
    bot.add_cog(Utils(bot))
