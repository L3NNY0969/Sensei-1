import discord
from discord.ext import commands
import math
import Calculator as calc
import calculator as simplecalc


class Math:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx, num: float, num2: float = None):
        """Adds the two numbers that you give"""
        if num is None:
            await ctx.send("Correct usage: *;add [no.1] [no.2]* (no brackets needed)")
        else:
            await ctx.send(f"{num} plus {num2} is {num+num2}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def multiply(self, ctx, num: float, num2: float = None):
        """Multiplies the two numbers that you give"""
        if num is None:
            await ctx.send("Correct usage: *;multiply [no.1] [no.2]* (no brackets needed)")
        else:
            await ctx.send(f"{num} multiplied by {num2} is {num*num2}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def square(self, ctx, num: float = None):
        """Squares the number that you give"""
        if num is None:
            await ctx.send("Correct usage: *;square [no.1]* (no brackets needed)")
        else:
            await ctx.send(f"The square of {num} is {num*num}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def subtract(self, ctx, num: float, num2: float = None):
        """Subtracts the two numbers that you give"""
        if num is None:
            await ctx.send("Correct usage: *;subtract [no.1] [no.2]* (no brackets needed)")
        else:
            await ctx.send(f"{num} minus {num2} is {num-num2}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def divide(self, ctx, num: float, num2: float = None):
        """Divides the two numbers that you give"""
        if num is None:
            await ctx.send("Correct usage: *;divide [no.1] [no.2]* (no brackets needed)")
        elif num2 == '0':
            await ctx.send("I can't do that!")
        else:
            await ctx.send(f"{num} divided by {num2} is about {float(num/num2):.4f}")

    @commands.command(aliases=['sqrt'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def squareroot(self, ctx, num:float):
        """Gives the square root of the number that you give"""
        if num is None:
            await ctx.send("You have to include a number!")
        else:
            sqrt = math.sqrt(num)
            await ctx.send(f"The square root of {num} is about {sqrt:.4f}")


def setup(bot):
    print("Math module loaded.")
    bot.add_cog(Math(bot))