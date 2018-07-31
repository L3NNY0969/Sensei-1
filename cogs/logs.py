import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
import logging
import asyncio
import random
from utils.paginator import HelpPaginator, CannotPaginate
import time
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound
from utils.dataIO import fileIO


class Logs:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/general/logs.json"
        self.data = dataIO.load_json(self.JSON)

    @commands.group()
    async def logs(self, ctx):
        """Log actions in your server. This command does nothing. Just a main command"""
        if ctx.invoked_subcommand is None:
            entity=self.bot.get_command("logs")
            p = await HelpPaginator.from_command(ctx, entity)
            await p.paginate()
            server = ctx.message.guild
            if str(server.id) not in self.data:
                self.data[str(server.id)] = {}
                dataIO.save_json(self.JSON, self.data)
            if "channel" not in self.data[str(server.id)]:
                self.data[str(server.id)]["channel"] = {}
                dataIO.save_json(self.JSON, self.data)
            if "toggle" not in self.data[str(server.id)]:
                self.data[str(server.id)]["toggle"] = False
                dataIO.save_json(self.JSON, self.data)
        else:
            server = ctx.message.guild
            if str(server.id) not in self.data:
                self.data[str(server.id)] = {}
                dataIO.save_json(self.JSON, self.data)
            if "channel" not in self.data[str(server.id)]:
                self.data[str(server.id)]["channel"] = {}
                dataIO.save_json(self.JSON, self.data)
            if "toggle" not in self.data[str(server.id)]:
                self.data[str(server.id)]["toggle"] = False
                dataIO.save_json(self.JSON, self.data)

    @logs.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel where you want stuff to be logged"""
        server = ctx.message.guild
        if not channel:
            channel = ctx.message.channel
        self.data[str(server.id)]["channel"] = str(channel.id)
        dataIO.save_json(self.JSON, self.data)
        await ctx.send(f"Logs will be recorded in {channel.mention} if toggled on {self.bot.get_emoji(452709464546476034)}")

    @logs.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def toggle(self, ctx):
        """Toggle logs on or off"""
        server = ctx.message.guild
        if self.data[str(server.id)]["toggle"] == False:
            self.data[str(server.id)]["toggle"] = True
            dataIO.save_json(self.JSON, self.data)
            await ctx.send(f"Logs have been toggled **on** {self.bot.get_emoji(452709464546476034)}")
            return
        if self.data[str(server.id)]["toggle"] == True:
            self.data[str(server.id)]["toggle"] = False
            dataIO.save_json(self.JSON, self.data)
            await ctx.send(f"Logs have been toggled **off** {self.bot.get_emoji(452709464546476034)}")
            return

    async def on_message_delete(self, message):
        author = message.author
        server = message.guild
        channel = message.channel
        s = discord.Embed(description="The message sent by **{}** was deleted in <#{}>".format(author.name, channel.id),
                          color=000000, timestamp=__import__('datetime').datetime.utcnow())
        try:
            s.add_field(name="Message Content", value=message.content)
        except:
            s.add_field(name="Message Content", value="Message was likely an embed.")
        s.set_author(name=author, icon_url=author.avatar_url)
        self.set_embed_image_to_message_image(s, message)
        try:
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        except KeyError or discord.Forbidden:
            pass

    def set_embed_image_to_message_image(self, em, message):
        try:
            if message.content.startswith('https://'):
                em.set_image(url=message.content)
        except:
            pass
        try:
            attach = message.attachments
            em.set_image(url=attach[0].url)
        except:
            pass

    async def on_message_edit(self, before, after):
        author = before.author
        server = before.guild
        channel = before.channel
        if before.content == after.content:
            return
        s = discord.Embed(description="{} edited their message in <#{}>".format(author.name, channel.id),
                          colour=000000, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=author, icon_url=author.avatar_url)
        s.add_field(name="Before", value=before.content, inline=False)
        s.add_field(name="After", value=after.content)
        try:
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        except KeyError or discord.Forbidden:
            pass

    async def on_guild_channel_delete(self, channel):
        server = channel.guild
        deletedby = "Unknown"
        for x in await server.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.channel_delete:
                deletedby = x.user
        if isinstance(channel, discord.TextChannel):
            s = discord.Embed(
                description="The text channel **{}** has just been deleted by **{}**".format(channel, deletedby),
                color=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass
        elif isinstance(channel, discord.VoiceChannel):
            s = discord.Embed(
                description="The voice channel **{}** has just been deleted by **{}**".format(channel, deletedby),
                color=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass
        else:
            s = discord.Embed(
                description="The category **{}** has just been deleted by **{}**".format(channel, deletedby),
                color=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass

    async def on_guild_channel_create(self, channel):
        server = channel.guild
        createdby = "Unknown"
        for x in await server.audit_logs(limit=5).flatten():
            if x.action == discord.AuditLogAction.channel_create:
                createdby = x.user
        if isinstance(channel, discord.TextChannel):
            s = discord.Embed(
                description="The text channel <#{}> has just been created by **{}**".format(channel.id, createdby),
                colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass
        elif isinstance(channel, discord.VoiceChannel):
            s = discord.Embed(
                description="The voice channel **{}** has just been created by **{}**".format(channel, createdby),
                colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass
        else:
            s = discord.Embed(
                description="The category **{}** has just been created by **{}**".format(channel, createdby),
                colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass

    async def on_guild_channel_update(self, before, after):
        server = before.guild
        editedby = "Unknown"
        for x in await server.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.channel_update:
                editedby = x.user
        if isinstance(before, discord.TextChannel):
            s = discord.Embed(
                description="The text channel <#{}> has been renamed by **{}**".format(after.id, editedby),
                colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        elif isinstance(before, discord.VoiceChannel):
            s = discord.Embed(description="The voice channel **{}** has been renamed by **{}**".format(after, editedby),
                              colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        else:
            s = discord.Embed(description="The category **{}** has been renamed by **{}**".format(after, editedby),
                              colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        try:
            if self.data[str(server.id)]["toggle"] == True:
                if before.name != after.name:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        except KeyError or discord.Forbidden:
            pass

    async def on_guild_role_create(self, role):
        server = role.guild
        for x in await server.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.role_delete:
                user = x.user
        s = discord.Embed(description=f'The role **{role.name}** has been created by **{user.name}**', colour=000000, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        try:
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        except KeyError or discord.Forbidden:
            pass

    async def on_guild_role_delete(self, role):
        server = role.guild
        for x in await server.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.role_delete:
                user = x.user
        s = discord.Embed(description="The role **{}** has been deleted by **{}**".format(role.name, user),
                          color=000000, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        try:
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        except KeyError or discord.Forbidden:
            pass

    async def on_guild_role_update(self, before, after):
        server = before.guild
        user = "Unknown"
        for x in await server.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.role_update:
                user = x.user
        s = discord.Embed(description="The role **{}** has been renamed by **{}**".format(before.name, user),
                          colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        s.add_field(name="Before", value=before)
        s.add_field(name="After", value=after)
        try:
            if self.data[str(server.id)]["toggle"] == True:
                if before.name != after.name:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        except KeyError or discord.Forbidden:
            pass

    async def on_member_update(self, before, after):
        server = before.guild
        user1 = "Unknown"
        user2 = "Unknown"
        if before.roles != after.roles:
            for x in await server.audit_logs(limit=1).flatten():
                if x.action == discord.AuditLogAction.member_role_update:
                    if len(x.before.roles) > len(x.after.roles):
                        user1 = x.user
                    else:
                        user2 = x.user
            for role in [x for x in before.roles if x not in after.roles]:
                s = discord.Embed(
                    description="The role `{}` has been removed from **{}** by **{}**".format(role, after.name, user1),
                    color=000000, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
            for role in [x for x in after.roles if x not in before.roles]:
                s = discord.Embed(
                    description="The role `{}` has been added to **{}** by **{}**".format(role, after.name, user2),
                    colour=000000, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass
        if before.nick != after.nick:
            for x in await server.audit_logs(limit=1).flatten():
                if x.action == discord.AuditLogAction.member_update:
                    if before.nick or after.nick:
                        user = x.user
            if not before.nick:
                before.nick = after.name
            if not after.nick:
                after.nick = after.name
            s = discord.Embed(
                description="**{}** has had their nickname changed by **{}**".format(after.name, user),
                colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=after, icon_url=after.avatar_url)
            s.add_field(name="Before", value=before.nick, inline=False)
            s.add_field(name="After", value=after.nick)
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
            except KeyError or discord.Forbidden:
                pass


def setup(bot):
    print("Logs module loaded.")
    bot.add_cog(Logs(bot))