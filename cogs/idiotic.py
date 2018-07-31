import discord
from discord.ext import commands
import idioticapi
import json


with open("apikeys.json") as f:
    x = json.load(f)


class Idiotic:
    def __init__(self, bot):
        self.bot = bot
        self.token = x['keys']['idiotickey']
        self.client = idioticapi.Client(self.token, dev=True)

    @commands.command()
    async def blame(self, ctx, *, text=None):
        """Blame someone for doing something"""
        try:
            await ctx.send(file=discord.File(await self.client.blame(str(text)), "blame.png"))
        except Exception as e:
            await ctx.send(f"An error occurred with the API! \nMore details: \n```{e}```")

    @commands.command()
    async def invert(self, ctx, user: discord.Member = None):
        """Inverts the color of the specified user"""
        await ctx.trigger_typing()
        user = user if user is not None else ctx.author
        try:
            await ctx.send(f"**{user.name}** has inverted color!", file=discord.File(await self.client.invert(user.avatar_url), "invert.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n```{e}```")

    @commands.command()
    async def cursive(self, ctx, *, text=None):
        """Turns your text into cursive"""
        try:
            await ctx.send(await self.client.cursive(text, 'normal'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n```{e}```")

    @commands.command()
    async def wanted(self, ctx, user: discord.Member = None):
        """Someone is WANTED!"""
        await ctx.trigger_typing()
        user = ctx.author if user is None else user
        try:
            await ctx.send(f"**{user.name}** is wanted!", file=discord.File(await self.client.wanted(user.avatar_url), "wanted.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n```{e}```")

    @commands.command()
    async def gay(self, ctx, user: discord.Member = None):
        """Someone is gay!"""
        await ctx.trigger_typing()
        user = ctx.author if user is None else user
        try:
            await ctx.send(f"**{user.name}** is gay!", file=discord.File(await self.client.rainbow(user.avatar_url), 'gay.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n```{e}```")

    @commands.command()
    async def tiny(self, ctx, *, text=None):
        """Send your text in really small letters."""
        await ctx.send(await self.client.tiny(text, 'subscript'))

    def format_avatar(self, avatar_url):
        if avatar_url.endswith(".gif"):
            return avatar_url + "?size=2048"
        return avatar_url.replace("webp", "png")

    @commands.command(aliases=['trigger'])
    async def triggered(self, ctx, user: discord.Member = None):
        """TRIGGER someone"""
        if user is None:
            user = ctx.author
        try:
            await ctx.trigger_typing()
            av = self.format_avatar(user.avatar_url)
            await ctx.send(f"**{user.name}** is triggered.", file=discord.File(await self.client.triggered(av), "triggered.gif"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def slap(self, ctx, user: discord.Member = None):
        """Slap someone."""
        await ctx.trigger_typing()
        if user is None:
            return await ctx.send("Please tag the person that you wanna slap.")
        try:
            await ctx.send(f"**{ctx.author.name}** slapped **{user.name}** hard. \n{self.bot.get_emoji(450867669772533760)}", file=discord.File(await self.client.batslap(ctx.author.avatar_url, user.avatar_url), "spank.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def tattoo(self, ctx, user: discord.Member = None):
        """Tattoos the mentioned user's profile picture"""
        person=ctx.author if user is None else user
        await ctx.trigger_typing()
        try:
            await ctx.send(f"**{person.display_name}** has been tattooed!", file=discord.File(await self.client.tattoo(person.avatar_url), 'tattoo.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def greyscale(self, ctx, user: discord.Member = None):
        person=ctx.author if user is None else user
        await ctx.trigger_typing()
        try:
            await ctx.send(f"**{person.display_name}** has been greyscaled!", file=discord.File(await self.client.greyscale(person.avatar_url), 'greyscale.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def brighten(self, ctx, user: discord.Member = None):
        """Brightens the mentioned users profile picture"""
        person=ctx.author if user is None else user
        await ctx.trigger_typing()
        try:
            await ctx.send(f"**{person.display_name}** has been brightened!", file=discord.File(await self.client.brightness(person.avatar_url, 50), 'greyscale.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def darken(self, ctx, user: discord.Member = None):
        """Darkens the mentioned users profile picture"""
        person=ctx.author if user is None else user
        await ctx.trigger_typing()
        try:
            await ctx.send(f"**{person.display_name}** has been darkened!", file=discord.File(await self.client.darkness(person.avatar_url, 50), 'greyscale.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def sepia(self, ctx, user: discord.Member = None):
        """Make someone's profile picture redder"""
        person=ctx.author if user is None else user
        await ctx.trigger_typing()
        try:
            await ctx.send(f"**{person.display_name}** has been reddened!", file=discord.File(await self.client.sepia(person.avatar_url), 'sepia.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def like(self, ctx, user: discord.Member):
        """Like a user"""
        if user == ctx.author:
            await ctx.send("Are you *actually* that lonely? Ping someone!")
        elif user is None:
            await ctx.send("Ping someone, *please*!")
        else:
            await ctx.trigger_typing()
            try:
                await ctx.send(f'{ctx.author.name} has a crush on {user.display_name}', file=discord.File(await self.client.crush(user.avatar_url, ctx.author.avatar_url), 'crush.png'))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command(aliases=['owo'])
    async def owoify(self, ctx, text: str = None):
        if text is None:
            await ctx.send("Please give text")
        await ctx.trigger_typing()
        try:
            await ctx.send(await self.client.owoify(text))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def mock(self, ctx, *, text: str = None):
        if text is None:
            await ctx.send("Please give text")
        await ctx.trigger_typing()
        try:
            await ctx.send(await self.client.mock(text))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


    @commands.command()
    async def vapor(self, ctx, *, text: str):
        """Vaporwaves your text"""
        if text is None:
            await ctx.send("Please give text")
        else:
            await ctx.trigger_typing()
            try:
                await ctx.send(await self.client.vapor(text))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def thesearch(self, ctx, *, text: str, user: discord.Member = None):
        if text is None:
            await ctx.send("Please include text!")
        else:
            person = user if not user is None else ctx.author
            await ctx.trigger_typing()
            try:
                await ctx.send(file = discord.File(await self.client.thesearch(person.avatar_url, text), 'thesearch.png'))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def beautiful(self, ctx, avatar:discord.Member = None):
        person=ctx.author if avatar is None else avatar
        await ctx.trigger_typing()
        try:
            await ctx.send(file=discord.File(await self.client.beautiful(person.avatar_url), 'beautiful.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def rejected(self, ctx, avatar:discord.Member = None):
        person=ctx.author if avatar is None else avatar
        await ctx.trigger_typing()
        try:
            await ctx.send(file=discord.File(await self.client.rejected(person.avatar_url), 'rejected.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def approved(self, ctx, avatar:discord.Member = None):
        person=ctx.author if avatar is None else avatar
        await ctx.trigger_typing()
        try:
            await ctx.send(file=discord.File(await self.client.approved(person.avatar_url), 'approved.png'))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def achievement(self, ctx, text:str = None, avatar:discord.Member=None):
        if text is None:
            await ctx.send("Please include text!")
        else:
            person=ctx.author if avatar is None else avatar
            await ctx.trigger_typing()
            try:
                await ctx.send(file=discord.File(await self.client.achievement(person.avatar_url, text), 'achievement.png'))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def snapchat(self, ctx, *, text:str):
        if text is None:
            await ctx.send("Please include text!")
        else:
            await ctx.trigger_typing()
            try:
                await ctx.send(file=discord.File(await self.client.snapchat(text), 'snapchat.png'))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def time(self, ctx, user: discord.Member = None):
        """Inverts the color of the specified user"""
        await ctx.trigger_typing()
        user = user if user is not None else ctx.author
        try:
            await ctx.send(f"The time is... **{user.display_name}**?",
                           file=discord.File(await self.client.time(user.avatar_url), "time.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n```{e}```")

    @commands.command()
    async def suggestion(self, ctx, text: str, user: discord.Member = None):
        """Inverts the color of the specified user"""
        await ctx.trigger_typing()
        user = user if user is not None else ctx.author
        try:
            await ctx.send(f"Your suggestion was sent to the company suggestion box.",
                           file=discord.File(await self.client.suggestion(user.avatar_url, text), "suggestion.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n```{e}```")


def setup(bot):
    print("Idiotic module loaded.")
    bot.add_cog(Idiotic(bot))
