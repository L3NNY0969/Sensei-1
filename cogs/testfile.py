import discord
from discord.ext import commands
import asyncio
import asyncpg
from

async def run():
    description = "A bot written in Python that uses asyncpg to connect to a postgreSQL database."

    # NOTE: 127.0.0.1 is the loopback address. If your db is running on the same machine as the code, this address will work
    credentials = {"user": "avik", "password": "21407fire", "database": "Local Disc (D:)", "host": "127.0.0.1"}
    db = await asyncpg.create_pool(**credentials)

    # Example create table code, you'll probably change it to suit you
    await db.execute("CREATE TABLE IF NOT EXISTS users(id bigint PRIMARY KEY, data text);")

    bot = Bot(description=description, db=db)
    try:
        await bot.start("NDI4MzU1NTI4OTE0MjM5NDg4.DhrvoA.3tUAvQTyuFbGeovFg3DXzjey80s")
    except KeyboardInterrupt:
        # Make sure to do these steps if you use a command to exit the bot
        await db.close()
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            command_prefix="?"
        )

        self.db = kwargs.pop("db")

    async def on_ready(self):
        # .format() is for the lazy people who aren't on 3.6+
        print("Username: {0}\nID: {0.id}".format(self.user))


## Example commands, don't use them
#@bot.command()
#async def query(ctx):
#    query = "SELECT * FROM users WHERE id = $1;"
#
#    # This returns a asyncpg.Record object, which is similar to a dict
#    row = await bot.db.fetchrow(query, ctx.author.id)
#    await ctx.send("{}: {}".format(row["id"], row["data"]))
#
#@bot.command()
#async def update(ctx, *, new_data: str):
#    # Once the code exits the transaction block, changes made in the block are committed to the db
#
#    connection = await bot.db.acquire()
#    async with connection.transaction():
#        query = "UPDATE users SET data = $1 WHERE id = $2"
#        await bot.db.execute(query, new_data, ctx.author.id)
#    await bot.db.release(connection)
#
#    await ctx.send("NEW:\n{}: {}".format(ctx.author.id, new_data))

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
