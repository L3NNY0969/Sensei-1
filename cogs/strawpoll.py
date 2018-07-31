#import discord
#import asyncio
#import strawpoll
#
#class Strawpoll:
#    def __init__(self, bot):
#        self.bot = bot
#

import asyncio
from strawpoll import API as API


async def main():
    api = API

    p2 = strawpoll.Poll('lol?', ['ha', 'haha', 'hahaha', 'hahahaha', 'hahahahaha'])
    p2 = await api.submit_poll(p2)
    print(p2.url)

asyncio.get_event_loop().run_until_complete(main())
