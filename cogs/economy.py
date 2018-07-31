import discord
from discord.ext import commands
import os
from copy import deepcopy
from utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import choice as randchoice
from random import randint
from copy import deepcopy
from utils import checks
from enum import Enum
import time
import logging
import datetime
import math
from PIL import Image, ImageDraw, ImageFont
from urllib.request import Request, urlopen
import json
import urllib.request
from utils.PagedResult import PagedResult
from utils.PagedResult import PagedResultData
import random
from random import choice
import asyncio
from difflib import get_close_matches
import requests

endpoint = "https://discordbots.org/api/bots/440996323156819968/check?userId={userId}"


class Economy:
    def __init__(self, bot):
        self.bot = bot
        self.location = 'data/economy/bank.json'
        self.settings = dataIO.load_json(self.location)

    def has_voted(self, userid):
        request = Request(f"https://discordbots.org/api/bots/{self.bot.user.id}/check?userId={userid}")
        request.add_header("Authorization",
                           "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyNzI4OTg5MTM3ODgyMzE2OCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTI0NzA0ODg3fQ.SwouqZy5hd8sltHyQV-hRt0yB-cP9h1aXHtTOw-FFEs")
        request.add_header('User-Agent', 'Mozilla/5.0')

        data = json.loads(urlopen(request).read().decode())
        return data["voted"] == 1

    @commands.command()
    async def register(self, ctx):
        author=ctx.author
        await self._set_bank(author)
        if not self.settings["user"][str(author.id)]["streaktime"]:
            await self._set_bank_user(author)
            self.settings["user"][str(author.id)]["streaktime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + 100
            self.settings["user"][str(author.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
            await ctx.send("You account has been successfully created! You will have $100 to start.")
            dataIO.save_json(self.location, self.settings)
            return
        else:
            await ctx.send("You have already created an account!")

    @commands.command(aliases=["pd", "payday"])
    async def daily(self, ctx):
        """Collect your daily money"""
        author = ctx.author
        if not self.settings["user"][str(author.id)]:
            await ctx.send("You have to create an account using the register command!")
        else:
            m, s = divmod(
                self.settings["user"][str(author.id)]["streaktime"] - ctx.message.created_at.timestamp() + 86400, 60)
            h, m = divmod(m, 60)
            if h == 0:
                time = "%d minutes %d seconds" % (m, s)
            elif h == 0 and m == 0:
                time = "%d seconds" % (s)
            else:
                time = "%d hours %d minutes %d seconds" % (h, m, s)
            if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["streaktime"] <= 86400:
                await ctx.send("You are too early, come collect your money again in {}".format(time))
                return
            elif ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["streaktime"] <= 172800:
                self.settings["user"][str(author.id)]["streaktime"] = ctx.message.created_at.timestamp()
                self.settings["user"][str(author.id)]["streak"] = self.settings["user"][str(author.id)]["streak"] + 1
                if self.settings["user"][str(author.id)]["streak"] == 1:
                    money = 120
                if self.settings["user"][str(author.id)]["streak"] == 2:
                    money = 145
                if self.settings["user"][str(author.id)]["streak"] == 3:
                    money = 170
                if self.settings["user"][str(author.id)]["streak"] == 4:
                    money = 200
                if self.settings["user"][str(author.id)]["streak"] >= 5:
                    money = 250
                self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + money
                dataIO.save_json(self.location, self.settings)
                s = discord.Embed(
                    description="You have collected your daily money! (**+${}**)\nYou had a bonus of ${} for having a {} day streak.".format(
                        money, (money - 100), self.settings["user"][str(author.id)]["streak"]), colour=000000)
                s.set_author(name=author, icon_url=author.avatar_url)
                await ctx.send(embed=s)

                dataIO.save_json(self.location, self.settings)
                return
            else:
                self.settings["user"][str(author.id)]["streaktime"] = ctx.message.created_at.timestamp()
                self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + 100
                self.settings["user"][str(author.id)]["streak"] = 0
                dataIO.save_json(self.location, self.settings)
                s = discord.Embed(description="You have collected your daily money! (**+$100**)", colour=000000)
                s.set_author(name=author, icon_url=author.avatar_url)
                await ctx.send(embed=s)

    @commands.command()
    async def give(self, ctx, user: discord.Member, amount: int):
        """Give someone some money"""
        author = ctx.author
        if user.bot:
            await ctx.send("Bots can't make money :no_entry:")
            return
        await self._set_bank(author)
        await self._set_bank_user(user)
        if user == author:
            await ctx.send("You can't give yourself money :no_entry:")
            return
        if amount > self.settings["user"][str(author.id)]["balance"]:
            await ctx.send("You don't have that much money to give :no_entry:")
            return
        if amount < 1:
            await ctx.send("You can't give them less than a dollar, too mean :no_entry:")
            return
        self.settings["user"][str(user.id)]["balance"] += round(amount * 0.9)
        self.settings["user"][str(author.id)]["balance"] -= amount
        dataIO.save_json(self.location, self.settings)
        s=discord.Embed(description="You have gifted **${}** to **{}**\n\n{}'s new balance: **${}**\n{}'s new balance: **${}**".format(round(amount*0.9), user.name, author.name, self.settings["user"][str(author.id)]["balance"], user.name, self.settings["user"][str(user.id)]["balance"]), colour=author.colour)
        s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://png.kisspng.com/20171216/8cb/5a355146d99f18.7870744715134436548914.png")
        s.set_footer(text="10% Tax is taken per transaction")
        await ctx.send(embed=s)


    @commands.command()
    async def votebonus(self, ctx):
        """Get some extra credits by simply upvoting the bot on DBL"""
        author = ctx.author
        try:
            m, s = divmod(self.settings["user"][str(author.id)]["votetime"] - ctx.message.created_at.timestamp() + 43200, 60)
            h, m = divmod(m, 60)
            if h == 0:
                time = "%d minutes %d seconds" % (m, s)
            elif h == 0 and m == 0:
                time = "%d seconds" % (s)
            else:
                time = "%d hours %d minutes %d seconds" % (h, m, s)
            if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["votetime"] <= 43200:
                await ctx.send("You are too early, come collect your vote bonus again in {}".format(time))
                return
        except:
            pass
        if self.has_voted(author.id) and requests.get("https://discordbots.org/api/weekend").json()["is_weekend"] == False:
            self.settings["user"][str(author.id)]["balance"] += 250
            await ctx.send("Thanks for voting! Here's **$250**. Come back and vote in 12 hours for another **$250**!")
            self.settings["user"][str(author.id)]["votetime"] = ctx.message.created_at.timestamp()
            dataIO.save_json(self.location, self.settings)
        elif self.has_voted(author.id) and requests.get("https://discordbots.org/api/weekend").json()["is_weekend"] == True:
            self.settings["user"][str(author.id)]["balance"] += 500
            await ctx.send("Thanks for voting! As it's double vote weekend here's **$500**. Come back and vote in 12 hours for another **$500**!")
            self.settings["user"][str(author.id)]["votetime"] = ctx.message.created_at.timestamp()
            dataIO.save_json(self.location, self.settings)
        else:
            await ctx.send(f"You need to upvote the bot to use this command you can do that here: https://discordbots.org/bot/{self.bot.user.id}\nIf you have voted please wait up to 5 minutes for it to process and try using the command again.")

    @commands.command(aliases=["bal"])
    async def balance(self, ctx, *, user: discord.Member=None):
        """Check how much money you have"""
        if not user or user == ctx.author:
            user = ctx.author
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Your balance: **${}**".format(self.settings["user"][str(user.id)]["balance"]), colour=000000)
            except:
                s=discord.Embed(description="Your balance: **$0**", colour=000000)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Their balance: **${}**".format(self.settings["user"][str(user.id)]["balance"]), colour=000000)
            except:
                s=discord.Embed(description="Their balance: **$0**", colour=000000)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, page: int=None):
        """Leaderboard for most money"""
        if not page:
            page = 1
        if page - 1 > len([x for x in self.settings["user"].items() if x[1]["balance"] != 0]) / 10:
            await ctx.send("Invalid page :no_entry:")
            return
        if page <= 0:
            await ctx.send("Invalid page :no_entry:")
            return
        msg = ""
        i = page*10-10;
        n = 0;
        sortedbank2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["balance"], reverse=True)
        sortedbank = sorted([x for x in self.settings["user"].items() if x[1]["balance"] != 0], key=lambda x: x[1]["balance"], reverse=True)[page*10-10:page*10]
        for x in sortedbank2:
            n = n + 1
            if str(ctx.author.id) == x[0]:
                break
        for x in sortedbank:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - ${}\n".format(i, user, x[1]["balance"])
        s=discord.Embed(title="Bank Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.author.name, n, page, math.ceil(len([x for x in self.settings["user"].items() if x[1]["balance"] != 0])/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)


    async def _set_bank_user(self, user):
        if user.bot:
            return
        if "user" not in self.settings:
            self.settings["user"] = {}
            dataIO.save_json(self.location, self.settings)
        if str(user.id) not in self.settings["user"]:
            self.settings["user"][str(user.id)] = {}
            dataIO.save_json(self.location, self.settings)
        if "balance" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["balance"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streak" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streaktime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["streaktime"] = None
            dataIO.save_json(self.location, self.settings)
        if "votetime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["votetime"] = None
            dataIO.save_json(self.location, self.settings)

    async def _set_bank(self, author):
        if author.bot:
            return
        if "user" not in self.settings:
            self.settings["user"] = {}
            dataIO.save_json(self.location, self.settings)
        if str(author.id) not in self.settings["user"]:
            self.settings["user"][str(author.id)] = {}
            dataIO.save_json(self.location, self.settings)
        if "balance" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["balance"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streak" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streaktime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["streaktime"] = None
            dataIO.save_json(self.location, self.settings)
        if "votetime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["votetime"] = None
            dataIO.save_json(self.location, self.settings)




def setup(bot):
    print("Economy module loaded")
    bot.add_cog(Economy(bot))
