from collections import namedtuple, defaultdict, deque
import box
import fortniteapi
from .utilites.SimplePaginator import SimplePaginator
import asyncio
import discord
from discord.ext import commands
import aiohttp
import random
import requests
import json
import pprint
from utils.dataIO import dataIO
from random import randint

rps_settings = {"rps_wins": 0, "rps_draws": 0, "rps_losses": 0}


class Fun:
    """This is the fun stuff"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.answers = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely',
                        'You may rely on it',
                        'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                        'Reply hazy try again', 'Very doubtful',
                        'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                        "Don't count on it", 'My reply is no', 'My sources say no', 'Outlook not so good']
        self.JSON = 'data/general/rpssettings.json'
        self.settings = dataIO.load_json(self.JSON)
        self.rpssettings = defaultdict(lambda: rps_settings, self.settings)
        self.fnheaders = {'TRN-Api-Key': '52f2fbde-018d-47b5-9c7d-99990c0d3507'}

    @commands.command(aliases=['badjoke', 'dumbjoke', 'suckyjoke'])
    async def horriblejoke(self, ctx):
        """Give a really bad joke"""
        resp = await self.session.get('https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke')
        r = await resp.json()
        em = discord.Embed(title=r['setup'], color=000000, timestamp=ctx.message.created_at)
        em.description = r['punchline']
        await ctx.send(embed=em)

    @commands.command()
    async def pokemon(self, ctx):
        """Try to guess the pokemon"""
        try:
            num = random.randint(1, 800)
            async with self.session.get(f'https://pokeapi.co/api/v2/pokemon-form/{num}/') as resp:
                data = await resp.json()
            embed = discord.Embed(title="Who's that pokemon?", color=000000, timestamp=ctx.message.created_at)
            embed.set_image(url=data['sprites']['front_default'])
            await ctx.send(embed=embed)
            answer = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            if answer.content.lower() == data['name']:
                await ctx.send(f'Correct! That pokemon is {data["name"]}')
            else:
                await ctx.send(f'Incorrect! That pokemon is {data["name"]}')
        except:
            await ctx.send("An error occured with pokeapi. Try again later.")

    @commands.command(aliases=['8ball', 'eightball'])
    async def ball(self, ctx, *, question: str = None):
        """Answers a question like an 8ball would"""
        if question is None:
            await ctx.send("You have to include a question!")
        else:
            author = ctx.author
            avatar = author.avatar_url
            timestamp = ctx.message.created_at
            embed = discord.Embed(title="8ball", color=000000, timestamp=timestamp)
            embed.add_field(name='Question', value=f"{question}")
            embed.add_field(name="Answer :8ball:", value=random.choice(self.answers))
            embed.set_footer(text="Asked")
            embed.set_thumbnail(url='http://legomenon.com/images/magic-8ball-first-white.jpg')
            embed.set_author(name=author, icon_url=avatar)
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def coinflip(self, ctx):
        """Flips a coin"""
        randomcoin = random.choice(['1', '2'])
        if randomcoin == "1":
            embed = discord.Embed(title="You flipped a heads!", color=000000, timestamp=ctx.message.created_at)
            embed.set_thumbnail(url="http://www.virtualcointoss.com/img/quarter_front.png")
            await ctx.send(embed=embed)
        elif randomcoin == "2":
            embed = discord.Embed(title="You flipped a tails!", color=000000, timestamp=ctx.message.created_at)
            embed.set_thumbnail(url="http://www.virtualcointoss.com/img/quarter_back.png")
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def diceroll(self, ctx, num: int, num2: int):
        """Rolls a dice from your specified numbers"""
        if num is None or num2 is None:
            ctx.send("Correct usage: *;diceroll [no.1] [no.2]* (no brackets needed, least to greatest)")
        else:
            await ctx.send("You rolled a " + str(random.randint(num, num2)) + "!")

    @commands.command()
    async def kill(self, ctx, user: discord.Member):
        """Kills a user"""
        if user == self.bot.user:
            await ctx.send("Do you really think that I would commit suicide?")
        else:
            msg = await ctx.send(f"{user.mention} will be dead in 3...")
            await asyncio.sleep(1)
            await msg.edit(content=f"{user.mention} will be dead in 2...")
            await asyncio.sleep(1)
            await msg.edit(content=f"{user.mention} will be dead in 1...")
            await asyncio.sleep(1)
            await msg.edit(content=f"{user.mention} is dead!")

    @commands.command()
    async def yomama(self, ctx):
        """Gives a yomama joke """
        resp = await self.session.get("http://api.yomomma.info/")
        resp = await resp.json(content_type=None)
        await ctx.send(embed=discord.Embed(title=resp['joke'], color=000000, timestamp=ctx.message.created_at))

    @commands.command(aliases=["pick"])
    async def choose(self, ctx, *, choices):
        """Chooses from the choices that you give. Separate choices with ,"""
        split = choices.split(",")
        if len(split) < 2:
            return await ctx.send("Not enough choices to pick from.")
        await ctx.send(f"I choose `{random.choice(split)}`")

    @commands.command()
    async def meme(self, ctx):
        """Gives a terrible meme"""
        num = random.randint(1, 10001)
        url = f'https://memegenerator.net/img/images/{num}.jpg'
        await ctx.send(embed=discord.Embed(title="A meme", color=000000).set_image(url=url))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def textmojify(self, ctx, *, msg: str):
        """Makes your text into emojis"""
        out = msg.lower()
        text = out.replace(' ', '  ').replace('10', '\u200B:keycap_ten:') \
            .replace('ab', '\u200B🆎').replace('cl', '\u200B🆑') \
            .replace('0', '\u200B:zero:').replace('1', '\u200B:one:') \
            .replace('2', '\u200B:two:').replace('3', '\u200B:three:') \
            .replace('4', '\u200B:four:').replace('5', '\u200B:five:') \
            .replace('6', '\u200B:six:').replace('7', '\u200B:seven:') \
            .replace('8', '\u200B:eight:').replace('9', '\u200B:nine:') \
            .replace('!', '\u200B❗').replace('?', '\u200B❓') \
            .replace('vs', '\u200B🆚').replace('.', '\u200B.') \
            .replace(',', '🔻').replace('a', '\u200B🇦') \
            .replace('b', '\u200B🇧').replace('c', '\u200B🇨') \
            .replace('d', '\u200B🇩').replace('e', '\u200B🇪') \
            .replace('f', '\u200B🇫').replace('g', '\u200B🇬') \
            .replace('h', '\u200B🇭').replace('i', '\u200B🇮') \
            .replace('j', '\u200B🇯').replace('k', '\u200B🇰') \
            .replace('l', '\u200B🇱').replace('m', '\u200B🇲') \
            .replace('n', '\u200B🇳').replace('ñ', '\u200B🇳') \
            .replace('o', '\u200B🇴').replace('p', '\u200B🇵') \
            .replace('q', '\u200B🇶').replace('r', '\u200B🇷') \
            .replace('s', '\u200B🇸').replace('t', '\u200B🇹') \
            .replace('u', '\u200B🇺').replace('v', '\u200B🇻') \
            .replace('w', '\u200B🇼').replace('x', '\u200B🇽') \
            .replace('y', '\u200B🇾').replace('z', '\u200B🇿')
        await ctx.send(text)

    @commands.command(pass_context=True)
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def rip(self, ctx, tombuser, *, tombtext: str):
        """ RIPs a user """
        rip = discord.Embed(color=000000)
        tombtext = tombtext.split(" ")
        tombtext = "+".join(tombtext)
        rip.set_image(
            url=f"http://www.tombstonebuilder.com/generate.php?top1={tombuser}&top2={tombtext}&top3=&top4=&sp=")
        await ctx.send(embed=rip)

    @commands.command(aliases=["fn", "fnprofile"])
    async def fortnite(self, ctx, platform: str, *, username: str):
        """Gets your fortnite stats"""
        res = await self.session.get(f"https://api.fortnitetracker.com/v1/profile/{platform.lower()}/{username}",
                                     headers=self.fnheaders)
        data = await res.json()
        try:
            if data.get('error', '') == "Player Not Found":
                return await ctx.send(f"{username} was not found!")
            else:
                embed = discord.Embed(color=000000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/460894620545449986/461579014394609665/IMG_20180627_200804.png")
                embed.title = f"{str(data['epicUserHandle'])} on {data['platformNameLong']}"
                embed.add_field(name="Lifetime Stats", value=f"Total Wins: {data['lifeTimeStats'][8]['value']}\n"
                                                             f'Total Games: {data["lifeTimeStats"][7]["value"]}\n'
                                                             f'Total Kills: {data["lifeTimeStats"][10]["value"]}\n'
                                                             f'Kill/Death Ratio: {data["lifeTimeStats"][11]["value"]}\n'
                                                             f'Win Percentage: {data["lifeTimeStats"][9]["value"]}\n'
                                                             f'Total Score: {data["lifeTimeStats"][6]["value"]}')
                try:
                    embed.add_field(name="Solo Stats", value=f'Wins: {data["stats"]["p2"]["top1"]["value"]}\n'
                                                             f'Games Played: {data["stats"]["p2"]["matches"]["value"]}\n'
                                                             f'Kills: {data["stats"]["p2"]["kills"]["value"]}\n'
                                                             f'Kill/Death Ratio: {data["stats"]["p2"]["kd"]["value"]}\n'
                                                             f'Win Percentage: {data["stats"]["p2"]["winRatio"]["value"]}%\n'
                                                             f'Score: {data["stats"]["p2"]["score"]["displayValue"]}')
                except:
                    embed.add_field(name="Solo Stats", value="No Solos Played")
                try:
                    embed.add_field(name="Duos Stats", value=f'Wins: {data["stats"]["p10"]["top1"]["value"]}\n'
                                                             f'Games Played: {data["stats"]["p10"]["matches"]["value"]}\n'
                                                             f'Kills: {data["stats"]["p10"]["kills"]["value"]}\n'
                                                             f'Kill/Death Ratio: {data["stats"]["p10"]["kd"]["value"]}\n'
                                                             f'Win Percentage: {data["stats"]["p10"]["winRatio"]["value"]}%\n'
                                                             f'Score: {data["stats"]["p10"]["score"]["displayValue"]}')
                except:
                    embed.add_field(name="Duos Stats", value="No Duos Played")
                try:
                    embed.add_field(name="Squads Stats", value=f'Wins: {data["stats"]["p9"]["top1"]["value"]}\n'
                                                               f'Games Played: {data["stats"]["p9"]["matches"]["value"]}\n'
                                                               f'Kills: {data["stats"]["p9"]["kills"]["value"]}\n'
                                                               f'Kill/Death Ratio: {data["stats"]["p9"]["kd"]["value"]}\n'
                                                               f'Win Percentage: {data["stats"]["p9"]["winRatio"]["value"]}%\n'
                                                               f'Score: {data["stats"]["p9"]["score"]["displayValue"]}')
                except:
                    embed.add_field(name="Squads Stats", value="No Squads Played")
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occured! More details: ```{e}```")

    @commands.command(pass_context=True)
    async def rps(self, ctx, your_choice):
        """Play rock paper scissors with the bot"""
        author = ctx.message.author
        if your_choice == "rock" or your_choice == "scissors" or your_choice == "paper" or your_choice == "r" or your_choice == "s" or your_choice == "p":
            if your_choice == "rock" or your_choice == "r":
                your_choice = 1
            if your_choice == "paper" or your_choice == "p":
                your_choice = 2
            if your_choice == "scissors" or your_choice == "s":
                your_choice = 3
        else:
            await ctx.send("You have to choose rock, paper or scissors :no_entry:")
            return
        bot_choice = randint(1, 3)
        if bot_choice == your_choice:
            end = "Draw, let's go again!"
        if bot_choice == 1 and your_choice == 2:
            end = "You win! :trophy:"
        if bot_choice == 1 and your_choice == 3:
            end = "You lose, better luck next time."
        if bot_choice == 2 and your_choice == 1:
            end = "You lose, better luck next time."
        if bot_choice == 2 and your_choice == 3:
            end = "You win! :trophy:"
        if bot_choice == 3 and your_choice == 1:
            end = "You win! :trophy:"
        if bot_choice == 3 and your_choice == 2:
            end = "You lose, better luck next time."
        if bot_choice == 1:
            bot_choice = f"**Rock {self.bot.get_emoji(469959614583013386)}**"
        if bot_choice == 2:
            bot_choice = "**Paper :page_facing_up:**"
        if bot_choice == 3:
            bot_choice = "**Scissors :scissors:**"
        if your_choice == 1:
            your_choice = f"**Rock {self.bot.get_emoji(469959614583013386)}**"
        if your_choice == 2:
            your_choice = "**Paper :page_facing_up:**"
        if your_choice == 3:
            your_choice = "**Scissors :scissors:**"
        await ctx.send("{}: {}\nSensei: {}\n\n{}".format(author.name, your_choice, bot_choice, end))
        if end == "You lose, better luck next time.":
            self.rpssettings[str(author.id)]["rps_losses"] = self.rpssettings[str(author.id)]["rps_losses"] + 1
        if end == "Draw, let's go again!":
            self.rpssettings[str(author.id)]["rps_draws"] = self.rpssettings[str(author.id)]["rps_draws"] + 1
        if end == "You win! :trophy:":
            self.rpssettings[str(author.id)]["rps_wins"] = self.rpssettings[str(author.id)]["rps_wins"] + 1
        dataIO.save_json(self.JSON, self.rpssettings)

    @commands.command(pass_context=True, aliases=["rpss"])
    async def rpsstats(self, ctx, *, user: discord.Member = None):
        """Check your rps win/loss record"""
        author = ctx.message.author
        if not user:
            user = author
        s = discord.Embed(color=user.color)
        s.set_author(name="{}'s RPS Stats against Me".format(user.name), icon_url=user.avatar_url)
        s.add_field(name="Wins", value=self.rpssettings[str(author.id)]["rps_wins"])
        s.add_field(name="Draws", value=self.rpssettings[str(author.id)]["rps_draws"])
        s.add_field(name="Losses", value=self.rpssettings[str(author.id)]["rps_losses"])
        await ctx.send(embed=s)


def setup(bot):
    print("Fun module loaded.")
    bot.add_cog(Fun(bot))
