import discord
from discord.ext import commands
from utils import checks
from urllib.request import Request, urlopen
import json
import urllib
import requests
import aiohttp


class Animals:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.command()
    async def catfact(self, ctx):
        """Gives a cat fact"""
        url = "https://catfact.ninja/fact"
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        s = discord.Embed(description=data["fact"], colour=000000)
        s.set_author(name="Did you know?")
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/134/cat-face_1f431.png")
        await ctx.send(embed=s)

    @commands.command()
    async def catpic(self, ctx):
        res = await self.session.get("https://catapi.glitch.me/random")
        data = await res.json()
        embed=discord.Embed(color=000000).set_footer(text="Powered by CatAPI")
        embed.set_image(url=data["url"])
        await ctx.send(embed=embed)

    @commands.command()
    async def dogfact(self, ctx):
        """Gives a dog fact"""
        url = "https://fact.birb.pw/api/v1/dog"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s = discord.Embed(description=data["string"], color=000000)
        s.set_author(name="Did you know?")
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/134/dog-face_1f436.png")
        await ctx.send(embed=s)

    @commands.command(aliases=["bird"])
    async def birbpic(self, ctx):
        """Shows a random birb picture"""
        url = "http://random.birb.pw/tweet.json/"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s = discord.Embed(description=":bird:", color=000000)
        s.set_image(url="http://random.birb.pw/img/" + data["file"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The birb didn't make it, sorry :no_entry:")

    @commands.command()
    async def dogpic(self, ctx):
        """Shows a random dog picture"""
        url = "https://dog.ceo/api/breeds/image/random"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s = discord.Embed(description=":dog:", color=000000)
        s.set_image(url=data["message"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The dog didn't make it, sorry :no_entry:")

    @commands.command()
    async def duckpic(self, ctx):
        """Shows a random duck picture"""
        url = "https://random-d.uk/api/v1/random"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s = discord.Embed(description=":duck:", color=000000)
        s.set_image(url=data["url"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The duck didn't make it, sorry :no_entry:")

    @commands.command()
    async def foxpic(self, ctx):
        """Shows a random fox picture"""
        url = "https://randomfox.ca/floof/"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s = discord.Embed(description=":fox:", color=000000)
        s.set_image(url=data["image"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The Fox didn't make it, sorry :no_entry:")


def setup(bot):
    print("Animals module loaded.")
    bot.add_cog(Animals(bot))