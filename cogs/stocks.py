import discord
from discord.ext import commands
import aiohttp
import inspect
import json


class Stocks:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.command()
    async def stock(self, ctx, symbol: str):
        """Gives the stock price for the stock symbol that you give"""
        if not symbol is None:
            try:
                resp = await self.session.get(
                    f"https://www.alphavantage.co/query?function=BATCH_STOCK_QUOTES&symbols={symbol}&apikey=J80P4GSVQA23VY0D")
                r = await resp.json()
                embed = discord.Embed(title=f'Stock Price for {symbol}', color=000000)
                price = r['Stock Quotes'][0]['2. price']
                price1 = float(price)
                embed.description = f'${price1:.2f}'
                updatetime = r['Stock Quotes'][0]['4. timestamp']
                embed.set_footer(text=f'Last updated {updatetime} US/Eastern')
                await ctx.send(embed=embed)
            except Exception:
                await ctx.send(f"That is not a valid stock symbol!")
        else:
            await ctx.send("You have to include a stock symbol!")


def setup(bot):
    bot.add_cog(Stocks(bot))

