import asyncio
import discord
import random
import operator
from discord.ext import commands


class MathGame:
    def __init__(self, bot):
        self.bot = bot
        self.gamestate = 0
        self.max_round = 5

        self._players = None
        self.players = None
        self.round = None
        self.msg = None
        self.ctx = None

    @commands.command()
    @commands.guild_only()
    async def math(self, ctx):
        """Starts the game"""
        self.ctx = ctx
        self.round = 1
        if self.gamestate == 0:
            self.gamestate = 1
            self._players = set()
            self.msg = await ctx.send(content='Game is starting in 20 seconds. Now waiting for players.\n'
                                              'Click on the reaction to participate!')
            await self.msg.add_reaction('▶')
            await asyncio.sleep(20)
            await MathGame.check_players(self)
        else:
            await self.ctx.send('Theres already a game on going!\n'
                                'Wait for it to finish to start another one.')

    async def on_reaction_add(self, reaction, user):
        if self.gamestate == 1 and reaction.message.id == self.msg.id \
                and reaction.emoji == '\U000025B6' and not user.bot:
            self._players.add(user.name)

    async def check_players(self):
        self.gamestate = 2
        if len(self._players) > 1:
            self.players = dict.fromkeys(self._players, 0)
            await self.ctx.send('**The game started! Number of rounds: {}\n'
                                'Be the first to answer to win each round.**'.format(self.max_round))
            await asyncio.sleep(3)
            await MathGame.start_game(self)
            await MathGame.leaderboard(self)
        else:
            await self.ctx.send('You need at least 2 players to start the MathGame.')
        self.gamestate = 0
        await self.ctx.send('`Game ended`')

    async def start_game(self):
        while True:
            x = random.randrange(4, 9)
            y = random.randrange(4, 9)
            z = random.randrange(3, 6)
            a = str((x + y) * z)
            await self.ctx.send(f'**Round {self.round}:**\n**`({x}+{y})*{z}`**')
            await MathGame.answer(self, a)
            if self.round >= self.max_round:
                break
            await self.ctx.send('Next round in 10 seconds.')
            await asyncio.sleep(10)
            self.round += 1

    async def answer(self, a):
        def check(m):
            return m.content == a and m.author.name in self.players

        try:
            msg = await self.bot.wait_for('message', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.ctx.send('Round timed out')
        else:
            await self.ctx.send(f'**{msg.author.name} won round {self.round}!** :tada:')
            self.players[msg.author.name] += 1

    async def leaderboard(self):
        s_players = sorted(self.players.items(), key=lambda kv: kv[1], reverse=True)
        colw = max(len((s_players[x])[0]) for x in range(len(s_players))) + 2
        p_players = ([(i, *r) for i, r in enumerate(s_players, 1)])
        p_players.insert(0, ('#:', 'Name:', 'Pts:'))
        ploys = []
        for m, n, p in p_players:
            ploys.append(f' {m:<3} {n.ljust(colw)} {p:<8} ')

        syolp = "\n".join(x for x in ploys)

        leader_b = f'**Leaderboard:**\n```{syolp}\n\n {(p_players[1])[1]} wins!```'

        embed = discord.Embed(Title='**Leaderboard**', description=leader_b, colour=0x06B3F9)
        embed.set_image(url='https://i.imgur.com/r1ks0Ek.png')

        await self.ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MathGame(bot))
