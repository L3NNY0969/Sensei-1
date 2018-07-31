import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
import os
import discord
from discord.ext import commands
from utils.dataIO import fileIO
from utils.paginator import HelpPaginator, CannotPaginate


class AutoRole:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/mod/autorole.json"
        self.data = dataIO.load_json(self.JSON)

    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def autorole(self, ctx):
        """Allows a role to be added to a user when they join the server"""
        if ctx.invoked_subcommand is None:
            entity = self.bot.get_command("autorole")
            p = await HelpPaginator.from_command(ctx, entity)
            await p.paginate()
            server = ctx.guild
            if str(server.id) not in self.data:
                self.data[str(server.id)] = {}
                dataIO.save_json(self.JSON, self.data)
            if "role" not in self.data[str(server.id)]:
                self.data[str(server.id)]["role"] = {}
                dataIO.save_json(self.JSON, self.data)
            if "toggle" not in self.data[str(server.id)]:
                self.data[str(server.id)]["toggle"] = True
                dataIO.save_json(self.JSON, self.data)
        else:
            server = ctx.guild
            if str(server.id) not in self.data:
                self.data[str(server.id)] = {}
                dataIO.save_json(self.JSON, self.data)
            if "role" not in self.data[str(server.id)]:
                self.data[str(server.id)]["role"] = {}
                dataIO.save_json(self.JSON, self.data)
            if "toggle" not in self.data[str(server.id)]:
                self.data[str(server.id)]["toggle"] = True
                dataIO.save_json(self.JSON, self.data)

    @autorole.command()
    async def role(self, ctx, *, role: discord.Role):
        """Set the role to be added to a user when they join"""
        server = ctx.guild
        self.data[str(server.id)]["role"] = role.name
        dataIO.save_json(self.JSON, self.data)
        await ctx.send("The autorole role is now **{}** :white_check_mark:".format(role.name))

    @autorole.command()
    async def fix(self, ctx):
        """Has the bot been offline and missed a few users? Use this to add the role to everyone who doesn't have it"""
        server = ctx.guild
        role = discord.utils.get(server.roles, name=self.data[str(server.id)]["role"])
        members = len([x for x in server.members if role not in x.roles])
        if not role:
            await ctx.send("Role is not set or does not exist :no_entry:")
        for user in [x for x in server.members if role not in x.roles]:
            await user.add_roles(role, reason="Autorole fix")
        await ctx.send("Added **{}** to **{}** users :white_check_mark:".format(role.name, members))

    @autorole.command()
    async def toggle(self, ctx):
        """Toggle autorole on or off"""
        server = ctx.guild
        if self.data[str(server.id)]["toggle"] == True:
            self.data[str(server.id)]["toggle"] = False
            await ctx.send("Auto-role has been **Disabled**")
            dataIO.save_json(self.JSON, self.data)
            return
        if self.data[str(server.id)]["toggle"] == False:
            self.data[str(server.id)]["toggle"] = True
            await ctx.send("Auto-role has been **Enabled**")
            dataIO.save_json(self.JSON, self.data)
            return

    @autorole.command()
    async def stats(self, ctx):
        """View the settings of autorole on your server"""
        server = ctx.guild
        s = discord.Embed(colour=000000)
        s.set_author(name="Auto-role Settings", icon_url=self.bot.user.avatar_url)
        if self.data[str(server.id)]["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        s.add_field(name="Status", value=toggle)
        if self.data[str(server.id)]["role"] == {}:
            s.add_field(name="Auto-role role", value="Role not set")
        else:
            s.add_field(name="Auto-role role", value=self.data[str(server.id)]["role"])
        await ctx.send(embed=s)

    async def on_member_join(self, member):
        server = member.guild
        try:
            role = discord.utils.get(server.roles, name=self.data[str(server.id)]["role"])
            if self.data[str(server.id)]["toggle"] == True:
                await member.add_roles(role, reason="Autorole")
        except KeyError:
            pass


def check_files():
    s = "settings/autorole.json"
    if not dataIO.is_valid_json(s):
        print("Creating default mod's autorole.json...")
        dataIO.save_json(s, {})


def setup(bot):
    check_files()
    bot.add_cog(AutoRole(bot))
