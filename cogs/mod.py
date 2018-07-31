from utils.paginator import HelpPaginator, CannotPaginate
import math
import datetime
import discord
from discord.ext import commands
from utils.dataIO import dataIO
import os
import discord
from discord.ext import commands
from utils.dataIO import fileIO
import json
import asyncio


class Mod:
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop().create_task(self.check_mute())
        self._logs_file = "data/mod/modlogs.json"
        self._logs = dataIO.load_json(self._logs_file)
        self.JSON = "data/mod/warns.json"
        self.data = dataIO.load_json(self.JSON)
        self.file = "data/mod/mutes.json"
        self.d = dataIO.load_json(self.file)
        self._time_file = "data/general/time.json"
        self._time = dataIO.load_json(self._time_file)

    async def check_mute(self):
        while not self.bot.is_closed():
            for serverid in list(self.d)[:len(self.d)]:
                server = self.bot.get_guild(int(serverid))
                if server != None:
                    role = discord.utils.get(server.roles, name="Muted - Sensei")
                    if role != None:
                        if self.d[str(server.id)] != None:
                            for userid in [x for x in self.d[serverid] if x != "channel"]:
                                user = discord.utils.get(server.members, id=int(userid))
                                if user != None:
                                    if self.d[str(server.id)][str(user.id)]["toggle"] != False and self.d[str(server.id)][str(user.id)]["time"] != None and self.d[str(server.id)][str(user.id)]["amount"] != None:
                                        time2 = self.d[str(server.id)][str(user.id)]["time"] - datetime.datetime.utcnow().timestamp() + self.d[str(server.id)][str(user.id)]["amount"]
                                        if time2 <= 0:
                                            if role in user.roles:
                                                await user.remove_roles(role)
                                                s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=datetime.datetime.now())
                                                s.add_field(name="Moderator", value="{} ({})".format(self.bot.user, self.bot.user.id), inline=False)
                                                s.add_field(name="Reason", value="Time Served", inline=False)
                                                try:
                                                    await user.send(embed=s)
                                                except:
                                                    pass
                                                action = "Unmute (Automatic)"
                                                author = self.bot.user
                                                reason = "Time limit served"
                                                try:
                                                    await self._log(author, server, action, reason, user)
                                                except:
                                                    pass
                                            self.d[str(server.id)][str(user.id)]["time"] = None
                                            self.d[str(server.id)][str(user.id)]["toggle"] = False
                                            self.d[str(server.id)][str(user.id)]["amount"] = None
                                            dataIO.save_json(self.file, self.d)
            await asyncio.sleep(20)

    @commands.command(no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = None):
        """Warns a user in pm, a reason is also optional."""
        author = ctx.message.author
        server = ctx.message.guild
        channel = ctx.message.channel
        if user == author:
            await ctx.send("You can not warn yourself :no_entry:")
            return
        if user.top_role.position >= author.top_role.position:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not warn someone higher than your own role :no_entry:")
                return
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if str(user.id) not in self.d[str(server.id)]:
            self.d[str(server.id)][str(user.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "muted" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["toggle"] = False
            dataIO.save_json(self.file, self.d)
        if "time" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["time"] = None
            dataIO.save_json(self.file, self.d)
        if "amount" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["amount"] = None
            dataIO.save_json(self.file, self.d)
        role = discord.utils.get(server.roles, name="Muted - Sensei")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            role = await server.create_role(name="Muted - Sensei")
            for channels in server.text_channels:
                await channels.set_permissions(role, overwrite=overwrite)
            for channels in server.voice_channels:
                await channels.set_permissions(role, overwrite=perms)
        await self._create_warn(server, user)
        if reason:
            if reason not in self.data[str(server.id)]["user"][str(user.id)]["reasons"]:
                self.data[str(server.id)]["user"][str(user.id)]["reasons"][reason] = {}
        self.data[str(server.id)]["user"][str(user.id)]["warnings"] = self.data[str(server.id)]["user"][str(user.id)][
                                                                          "warnings"] + 1
        dataIO.save_json(self.JSON, self.data)
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 1:
            await ctx.send("**{}** has been warned :warning:".format(user))
            s = discord.Embed(colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been warned in {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Mute")
            action = "Warn"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 2:
            try:
                await user.add_roles(role)
                self.d[str(server.id)][str(user.id)]["toggle"] = True
                self.d[str(server.id)][str(user.id)]["amount"] = 600
                self.d[str(server.id)][str(user.id)]["time"] = ctx.message.created_at.timestamp()
                dataIO.save_json(self.file, self.d)
            except:
                await ctx.send("I cannot add the mute role to the user :no_entry:")
                return
            await ctx.send("**{}** has been muted due to their second warning :white_check_mark:".format(user))
            s = discord.Embed(colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been muted in {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Kick")
            action = "Mute"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
            await asyncio.sleep(600)
            if role in user.roles:
                try:
                    await user.remove_roles(role)
                except:
                    pass
                self.d[str(server.id)][str(user.id)]["toggle"] = False
                dataIO.save_json(self.file, self.d)
                action = "Unmute"
                try:
                    await self._log(author, server, action, reason, user)
                except:
                    pass
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 3:
            try:
                await server.kick(user, reason="Kick made by {}".format(author))
            except:
                await ctx.send("I'm not able to kick that user :no_entry:")
                return
            await ctx.send("**{}** has been kicked due to their third warning :white_check_mark:".format(user))
            s = discord.Embed(colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been kicked from {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Ban")
            action = "Kick"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] >= 4:
            try:
                await server.ban(user, reason="Ban made by {}".format(author))
            except:
                await ctx.send("I'm not able to ban that user :no_entry:")
                del self.data[str(server.id)]["user"][str(user.id)]
                dataIO.save_json(self.JSON, self.data)
                return
            await ctx.send("**{}** has been banned due to their fourth warning :white_check_mark:".format(user))
            await server.ban(user, reason="Ban made by {}".format(author))
            s = discord.Embed(colour=000000, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been banned from {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="None")
            del self.data[str(server.id)]["user"][str(user.id)]
            dataIO.save_json(self.JSON, self.data)
            action = "Ban"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        try:
            await user.send(embed=s)
        except:
            pass

    async def _create_warn(self, server, user):
        if str(server.id) not in self.data:
            self.data[str(server.id)] = {}
            dataIO.save_json(self.JSON, self.data)
        if "user" not in self.data[str(server.id)]:
            self.data[str(server.id)]["user"] = {}
            dataIO.save_json(self.JSON, self.data)
        if str(user.id) not in self.data[str(server.id)]["user"]:
            self.data[str(server.id)]["user"][str(user.id)] = {}
            dataIO.save_json(self.JSON, self.data)
        if "warnings" not in self.data[str(server.id)]["user"][str(user.id)]:
            self.data[str(server.id)]["user"][str(user.id)]["warnings"] = 0
            dataIO.save_json(self.JSON, self.data)
        if "reasons" not in self.data[str(server.id)]["user"][str(user.id)]:
            self.data[str(server.id)]["user"][str(user.id)]["reasons"] = {}
            dataIO.save_json(self.JSON, self.data)

    async def _list_warns(self, server, page):
        msg = ""
        s = discord.Embed(colour=000000)
        s.set_author(name=server.name, icon_url=server.icon_url)
        sortedwarn = sorted(self.data[str(server.id)]["user"].items(), key=lambda x: x[1]["warnings"], reverse=True)[
                     page * 20 - 20:page * 20]
        for x in sortedwarn:
            users = discord.utils.get(server.members, id=int(x[0]))
            if users and self.data[str(server.id)]["user"][x[0]]["warnings"] != 0:
                msg += "\n`{}`: Warning **#{}**".format(users, self.data[str(server.id)]["user"][x[0]]["warnings"])
        s.add_field(name="Users on Warnings", value=msg)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(self.data[str(server.id)]["user"]) / 20)))
        return s

    @commands.command()
    async def warnlist(self, ctx, page: int = None):
        """View everyone who has been warned and how many warning they're on"""
        server = ctx.message.guild
        if not page:
            page = 1
        if page < 0:
            await ctx.send("Invalid page :no_entry:")
            return
        try:
            if page > math.ceil(len(self.data[str(server.id)]["user"]) / 20):
                await ctx.send("Invalid page :no_entry:")
                return
        except:
            await ctx.send("No one has been warned in this server :no_entry:")
            return
        s = await self._list_warns(server, page)
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("There are no users with warnings in this server :no_entry:")

    @commands.command()
    async def warnings(self, ctx, user: discord.Member):
        """Check how many warnings a specific user is on"""
        server = ctx.message.guild
        try:
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 1:
                action = "Mute"
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 2:
                action = "Kick"
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] >= 3:
                action = "Ban"
            if not self.data[str(server.id)]["user"][str(user.id)]["reasons"]:
                reasons = "None"
            else:
                reasons = ", ".join([x for x in self.data[str(server.id)]["user"][str(user.id)]["reasons"]])
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 1:
                s = discord.Embed(description="{} is on 1 warning".format(user), colour=user.colour)
                s.set_author(name=str(user), icon_url=user.avatar_url)
                s.add_field(name="Next Action", value=action, inline=False)
                s.add_field(name="Reasons", value=reasons, inline=False)
                await ctx.send(embed=s)
            else:
                try:
                    s = discord.Embed(description="{} is on {} warnings".format(user, self.data[str(server.id)]["user"][
                        str(user.id)]["warnings"]), colour=user.colour)
                    s.set_author(name=str(user), icon_url=user.avatar_url)
                    s.add_field(name="Next Action", value=action, inline=False)
                    s.add_field(name="Reasons", value=reasons, inline=False)
                    await ctx.send(embed=s)
                except:
                    await ctx.send("That user has no warnings :no_entry:")
        except:
            await ctx.send("That user has no warnings :no_entry:")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def setwarns(self, ctx, user: discord.Member, warnings: int = None):
        """Set the warn amount for a specific user"""
        server = ctx.message.guild
        await self._create_warn(server, user)
        dataIO.save_json(self.JSON, self.data)
        if not warnings:
            del self.data[str(server.id)]["user"][str(user.id)]
            dataIO.save_json(self.JSON, self.data)
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings == 0:
            del self.data[str(server.id)]["user"][str(user.id)]
            dataIO.save_json(self.JSON, self.data)
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings <= 0:
            await ctx.send("You can set warnings to 1-4 only :no_entry:")
            return
        if warnings >= 5:
            await ctx.send("You can set warnings to 1-4 only :no_entry:")
            return
        self.data[str(server.id)]["user"][str(user.id)]["warnings"] = warnings
        dataIO.save_json(self.JSON, self.data)
        await ctx.send("**{}'s** warnings have been set to **{}**".format(user.name, warnings))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):
        """Kicks a user."""
        author = ctx.message.author
        server = author.guild
        channel = ctx.message.channel
        destination = user
        action = "Kick"
        can_ban = channel.permissions_for(ctx.me).kick_members
        if not can_ban:
            await ctx.send("I need the `KICK_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not going to kick myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await ctx.send("Why would you want to kick yourself, just leave.")
            return
        if user.top_role.position >= author.top_role.position:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not kick someone higher than your own role :no_entry:")
                return
        try:
            await server.kick(user, reason="Kick made by {}".format(author))
            await ctx.send("**{}** has been kicked ".format(user))
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to kick that user :no_entry:")
            return
        try:
            u = discord.Embed(title="You have been kicked from {}".format(server.name), colour=0xfff90d,
                              timestamp=__import__('datetime').datetime.utcnow())
            u.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
            u.set_thumbnail(url=server.icon_url)
            if not reason:
                u.add_field(name="Reason", value="No reason specified")
            else:
                u.add_field(name="Reason", value=reason)
            try:
                await user.send(embed=u)
            except discord.errors.HTTPException:
                pass
        except Exception as e:
            print(e)

    @commands.command(no_pm=True, )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = None):
        """Bans a user."""
        author = ctx.message.author
        server = author.guild
        channel = ctx.message.channel
        action = "Ban"
        destination = user
        can_ban = channel.permissions_for(ctx.me).ban_members
        if str(server.id) not in self._time:
            self._time[str(server.id)] = {}
            dataIO.save_json(self._time_file, self._time)
        if "bantime" not in self._time[str(server.id)]:
            self._time[str(server.id)]["bantime"] = 0
            dataIO.save_json(self._time_file, self._time)
        if not can_ban:
            await ctx.send("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not going to ban myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await ctx.send("Why would you want to ban yourself, just leave.")
            return
        if user.top_role.position >= author.top_role.position:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not ban someone higher than your own role :no_entry:")
                return
        try:
            await server.ban(user, reason="Ban made by {}".format(author))
            self._time[str(server.id)]["bantime"] = datetime.datetime.utcnow().timestamp()
            dataIO.save_json(self._time_file, self._time)
            await ctx.send("**{}** has been banned :white_check_mark:".format(user))
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to ban that user :no_entry:")
            return
        try:
            u = discord.Embed(title="You have been banned from {}".format(server.name), colour=0xfff90d,
                              timestamp=__import__('datetime').datetime.utcnow())
            u.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
            u.set_thumbnail(url=server.icon_url)
            if not reason:
                u.add_field(name="Reason", value="No reason specified")
            else:
                u.add_field(name="Reason", value=reason)
            try:
                await user.send(embed=u)
            except discord.errors.HTTPException:
                pass
        except Exception as e:
            print(e)

    @commands.command(no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = None):
        """unbans a user by ID and will notify them about the unbanning in pm"""
        author = ctx.message.author
        server = ctx.message.guild
        channel = ctx.message.channel
        action = "Unban"
        if str(server.id) not in self._time:
            self._time[str(server.id)] = {}
            dataIO.save_json(self._time_file, self._time)
        if "unbantime" not in self._time[str(server.id)]:
            self._time[str(server.id)]["unbantime"] = 0
            dataIO.save_json(self._time_file, self._time)
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await ctx.send("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await ctx.send("The ID specified does not exist :no_entry:")
            return
        can_ban = channel.permissions_for(ctx.me).ban_members
        if not can_ban:
            await ctx.send("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        ban_list = await server.bans()
        invite = await channel.create_invite(max_age=86400, max_uses=1)
        s = discord.Embed(title="You have been unbanned from {}".format(server.name),
                          description="Feel free to join back whenever.", colour=000000,
                          timestamp=__import__('datetime').datetime.utcnow())
        s.set_thumbnail(url=server.icon_url)
        s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
        s.add_field(name="Invite", value="{} (This will expire in 1 week)".format(str(invite)))
        if user == author:
            await ctx.send("You can't unban yourself :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not even banned ¯\_(ツ)_/¯")
            return
        i = 0
        n = 0
        if user in [x.user for x in ban_list]:
            pass
        else:
            await ctx.send("That user is not banned :no_entry:")
            return
        try:
            await server.unban(user, reason="Unban made by {}".format(author))
            self._time[str(server.id)]["unbantime"] = datetime.datetime.utcnow().timestamp()
            dataIO.save_json(self._time_file, self._time)
        except discord.errors.Forbidden:
            await ctx.send("I need the **Ban Members** permission to unban :no_entry:")
            return
        await ctx.send("**{}** has been unbanned :white_check_mark:".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        try:
            await user.send(embed=s)
        except:
            pass

    @commands.command()
    async def mutedlist(self, ctx):
        """Check who is muted in the server and for how long"""
        server = ctx.message.guild
        msg = ""
        i = 0
        try:
            for userid in self.d[str(server.id)]:
                if self.d[str(server.id)][userid]["toggle"] == True:
                    i = i + 1
        except:
            await ctx.send("No one is muted in this server :no_entry:")
            return
        if i == 0:
            await ctx.send("No one is muted in this server :no_entry:")
            return
        for userid in self.d[str(server.id)]:
            if self.d[str(server.id)][userid]["time"] == None or self.d[str(server.id)][userid]["time"] - ctx.message.created_at.timestamp() + self.d[str(server.id)][userid]["amount"] <= 0:
                time = "Infinite"
            else:
                m, s = divmod(self.d[str(server.id)][userid]["time"] - ctx.message.created_at.timestamp() +
                              self.d[str(server.id)][userid]["amount"], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                if d == 0:
                    time = "%d hours %d minutes %d seconds" % (h, m, s)
                if h == 0 and d == 0:
                    time = "%d minutes %d seconds" % (m, s)
                elif h == 0 and m == 0:
                    time = "%d seconds" % (s)
                else:
                    time = "%d days %d hours %d minutes %d seconds" % (d, h, m, s)
            if self.d[str(server.id)][userid]["toggle"] == True:
                user = discord.utils.get(server.members, id=int(userid))
                if user:
                    msg += "{} - {} (Till mute ends)\n".format(user, time)
        if not msg:
            await ctx.send("No one is muted in this server :no_entry:")
            return
        s = discord.Embed(description=msg, colour=0xfff90d, timestamp=datetime.datetime.utcnow())
        s.set_author(name="Mute List for {}".format(server), icon_url=server.icon_url)
        await ctx.send(embed=s)

    async def on_member_update(self, before, after):
        try:
            server = before.guild
            user = after
            role = discord.utils.get(server.roles, name="Muted - Sensei")
            if role in before.roles:
                if role not in after.roles:
                    self.d[str(server.id)][before.id]["toggle"] = False
                    self.d[str(server.id)][str(user.id)]["time"] = None
                    self.d[str(server.id)][str(user.id)]["amount"] = None
                    dataIO.save_json(self.file, self.d)
                    return
            if role in after.roles:
                if role not in before.roles:
                    self.d[str(server.id)][before.id]["toggle"] = True
                    self.d[str(server.id)][str(user.id)]["time"] = None
                    self.d[str(server.id)][str(user.id)]["amount"] = None
                    dataIO.save_json(self.file, self.d)
                    return
        except KeyError or AttributeError:
            pass

    async def on_guild_channel_create(self, channel):
        try:
            server = channel.guild
            role = discord.utils.get(server.roles, name="Muted - Sensei")
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            perms = discord.PermissionOverwrite()
            perms.speak = False
            if not role:
                return
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(role, overwrite=overwrite)
            if isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(role, overwrite=perms)
        except KeyError or AttributeError:
            pass

    @commands.command(aliases=["hb"])
    @commands.has_permissions(ban_members=True)
    async def hackban(self, ctx, user_id: int, *, reason: str = None):
        """Ban a user before they even join the server, make sure you provide a user id"""
        author = ctx.message.author
        server = ctx.message.guild
        channel = ctx.message.channel
        action = "Ban"
        if str(server.id) not in self._time:
            self._time[str(server.id)] = {}
            dataIO.save_json(self._time_file, self._time)
        if "bantime" not in self._time[str(server.id)]:
            self._time[str(server.id)]["bantime"] = 0
            dataIO.save_json(self._time_file, self._time)
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await ctx.send("The user was not found, check if the ID specified is correct :no_entry:")
            return
        except discord.errors.HTTPException:
            await ctx.send("The ID specified does not exist :no_entry:")
            return
        ban_list = await server.bans()
        can_ban = channel.permissions_for(ctx.me).ban_members
        if user in server.members:
            await ctx.send("Use the ban command to ban people in the server :no_entry:")
            return
        if not can_ban:
            await ctx.send("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not going to ban myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await ctx.send("Why would you want to ban yourself, just leave.")
            return
        if user in [x.user for x in ban_list]:
            await ctx.send("That user is already banned :no_entry:")
            return
        try:
            await self.bot.http.ban(user_id, server.id, reason="Ban made by {}".format(author))
            self._time[str(server.id)]["bantime"] = datetime.datetime.utcnow().timestamp()
            dataIO.save_json(self._time_file, self._time)
        except:
            await ctx.send("I'm not able to ban that user :no_entry:")
            return
        await ctx.send(f"**{user}** has been banned by ID {self.bot.get_emoji(470063310386233344)}")
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass

    @commands.group()
    async def modlog(self, ctx):
        """Have Have logs for all mod actions. This command give the sub commands."""
        if ctx.invoked_subcommand is None:
            entity=self.bot.get_command("modlog")
            p = await HelpPaginator.from_command(ctx, entity)
            await p.paginate()
            server = ctx.guild
            if str(server.id) not in self._logs:
                self._logs[str(server.id)] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if "channel" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["channel"] = None
                dataIO.save_json(self._logs_file, self._logs)
            if "toggle" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["toggle"] = False
                dataIO.save_json(self._logs_file, self._logs)
            if "case#" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["case#"] = 0
                dataIO.save_json(self._logs_file, self._logs)
            if "case" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["case"] = {}
                dataIO.save_json(self._logs_file, self._logs)
        else:
            server = ctx.guild
            if str(server.id) not in self._logs:
                self._logs[str(server.id)] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if "channel" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["channel"] = None
                dataIO.save_json(self._logs_file, self._logs)
            if "toggle" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["toggle"] = False
                dataIO.save_json(self._logs_file, self._logs)
            if "case#" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["case#"] = 0
                dataIO.save_json(self._logs_file, self._logs)
            if "case" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["case"] = {}
                dataIO.save_json(self._logs_file, self._logs)

    @modlog.command()
    @commands.has_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """Toggle modlogs on or off"""
        server = ctx.guild
        if self._logs[str(server.id)]["toggle"] == True:
            self._logs[str(server.id)]["toggle"] = False
            dataIO.save_json(self._logs_file, self._logs)
            await ctx.send("Modlogs are now disabled.")
            return
        if self._logs[str(server.id)]["toggle"] == False:
            self._logs[str(server.id)]["toggle"] = True
            dataIO.save_json(self._logs_file, self._logs)
            await ctx.send(f"Modlogs are now enabled {self.bot.get_emoji(470063310386233344)}")
            return

    @modlog.command()
    @commands.has_permissions(manage_roles=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where you want modlogs to be posted"""
        server = ctx.guild
        self._logs[str(server.id)]["channel"] = str(channel.id)
        dataIO.save_json(self._logs_file, self._logs)
        await ctx.send(f"<#{str(channel.id)}> has been set as the modlog channel {self.bot.get_emoji(470063310386233344)}")

    @modlog.command()
    @commands.has_permissions(manage_roles=True)
    async def case(self, ctx, case_number, *, reason):
        """Edit a modlog case"""
        author = ctx.author
        server = ctx.guild
        try:
            self._logs[str(server.id)]["case"][case_number]
        except:
            await ctx.send("Invalid case number :no_entry:")
            return
        if self._logs[str(server.id)]["case"][case_number]["mod"] is not None and \
                self._logs[str(server.id)]["case"][case_number]["mod"] != str(author.id):
            await ctx.send("You do not have ownership of that log :no_entry:")
            return
        try:
            channel = self.bot.get_channel(int(self._logs[str(server.id)]["channel"]))
        except:
            await ctx.send("The modlog channel no longer exists :no_entry:")
            return
        try:
            message = await channel.get_message(int(self._logs[str(server.id)]["case"][case_number]["message"]))
        except:
            await ctx.send("I am unable to find that case :no_entry:")
            return
        s = discord.Embed(color=000000,
                          title="Case {} | {}".format(case_number, self._logs[str(server.id)]["case"][case_number]["action"]))
        s.add_field(name="User",
                    value=await self.bot.get_user_info(int(self._logs[str(server.id)]["case"][case_number]["user"])))
        s.add_field(name="Moderator", value=author, inline=False)
        self._logs[str(server.id)]["case"][case_number]["mod"] = str(author.id)
        s.add_field(name="Reason", value=reason)
        self._logs[str(server.id)]["case"][case_number]["reason"] = reason
        dataIO.save_json(self._logs_file, self._logs)
        try:
            await message.edit(embed=s)
            await ctx.send(f"Case #{case_number} has been updated {self.bot.get_emoji(470063310386233344)}")
        except:
            await ctx.send("I am unable to edit that case or it doesn't exist :no_entry:")

    @modlog.command()
    @commands.has_permissions(manage_roles=True)
    async def viewcase(self, ctx, case_number):
        """Has someone delete their modlog case in your modlog channel? Use this command to view it"""
        server = ctx.guild
        try:
            if self._logs[str(server.id)]["case"][case_number]["reason"] is None:
                reason = "None (Update using `;modlog case {} <reason>`)".format(case_number)
            else:
                reason = self._logs[str(server.id)]["case"][case_number]["reason"]
            if self._logs[str(server.id)]["case"][case_number]["mod"] is None:
                author = "Unknown"
            else:
                author = await self.bot.get_user_info(self._logs[str(server.id)]["case"][case_number]["mod"])
            user = await self.bot.get_user_info(int(self._logs[str(server.id)]["case"][case_number]["user"]))
            s = discord.Embed(
                title="Case {} | {}".format(case_number, self._logs[str(server.id)]["case"][case_number]["action"]))
            s.add_field(name="User", value=f'{user}(<@{user.id}>)')
            s.add_field(name="Moderator", value=author, inline=False)
            s.add_field(name="Reason", value=reason)
            await ctx.send(embed=s)
        except:
            await ctx.send("Invalid case number :no_entry:")

    @modlog.command()
    @commands.has_permissions(manage_roles=True)
    async def resetcases(self, ctx):
        """Reset all the cases in the modlog"""
        server = ctx.guild
        self._logs[str(server.id)]["case#"] = 0
        del self._logs[str(server.id)]["case"]
        dataIO.save_json(self._logs_file, self._logs)
        await ctx.send(f"All cases have been reset {self.bot.get_emoji(470063310386233344)}")

    async def _log(self, author, server, action, reason, user):
        if "case" not in self._logs[str(server.id)]:
            self._logs[str(server.id)]["case"] = {}
            dataIO.save_json(self._logs_file, self._logs)
        channel = self.bot.get_channel(int(self._logs[str(server.id)]["channel"]))
        if self._logs[str(server.id)]["toggle"] == True and channel is not None:
            self._logs[str(server.id)]["case#"] += 1
            number = str(self._logs[str(server.id)]["case#"])
            if number not in self._logs[str(server.id)]["case"]:
                self._logs[str(server.id)]["case"][number] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if "action" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["action"] = action
                dataIO.save_json(self._logs_file, self._logs)
            if "user" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["user"] = str(user.id)
                dataIO.save_json(self._logs_file, self._logs)
            if "mod" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["mod"] = str(author.id)
                dataIO.save_json(self._logs_file, self._logs)
            if "reason" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["reason"] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if not reason:
                reason = "None (Update using `;modlog case {} <reason>`)".format(number)
                self._logs[str(server.id)]["case"][number]["reason"] = None
            else:
                self._logs[str(server.id)]["case"][number]["reason"] = reason
            s = discord.Embed(title="Case {} | {}".format(number, action), color=000000)
            s.add_field(name="User", value=f"{user}(<@{user.id}>)")
            s.add_field(name="Moderator", value=author, inline=False)
            s.add_field(name="Reason", value=reason)
            message = await channel.send(embed=s)
            if "message" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["message"] = str(message.id)
                dataIO.save_json(self._logs_file, self._logs)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a members and deletes their messages."""
        await member.ban(reason=f'Softban - {reason}')
        await member.unban(reason='Softban unban.')
        await ctx.send(f'Done. {member.name} was softbanned.')

    @commands.command(aliases=['clear'])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def purge(self, ctx, num: int):
        """Deletes the number of messages"""
        try:
            if num is None:
                await ctx.send("How many messages would you like me to delete? Usage: *;purge [number of msgs]*")
            else:
                try:
                    float(num)
                except ValueError:
                    return await ctx.send(
                        "The number is invalid. Make sure it is valid! Usage: *;purge [number of msgs]*")
                await ctx.message.delete()
                await ctx.channel.purge(limit=num, before=ctx.message)
                msg = await ctx.send("The purge was successful!", delete_after=3)
                await asyncio.sleep(3)
                await msg.delete()
        except discord.Forbidden:
            await ctx.send("Uh oh! The purge didn't work! I don't have the **Manage Messages** permission.", delete_after=5.0)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lockdown(self, ctx, action=None):
        """Doesn't let anyone talk in the channel"""
        try:
            if not action:
                return await ctx.send("Lockdown command:\n*;lockdown [on/off]*")
            if action.lower() == 'on':
                msg = await ctx.send("Locking down the channel...")
                for x in ctx.guild.members:
                    await ctx.channel.set_permissions(x, send_messages=False)
                return await msg.edit(content="The channel has been successfully locked down. :lock: ")
            elif action.lower() == 'off':
                msg = await ctx.send("Unlocking the channel...")
                for x in ctx.guild.members:
                    await ctx.channel.set_permissions(x, send_messages=True)
                return await msg.edit(content="The channel has been successfully unlocked. :unlock: ")
            else:
                return await ctx.send("Lockdown command:\n*;lockdown [on/off]*")
        except discord.Forbidden:
            await ctx.send("I need to have the permission: Manage Server")

    @commands.command(aliases=['giverole'])
    @commands.has_permissions(manage_roles = True)
    async def addrole(self, ctx, user: discord.Member=None, *, role=None):
        """Gives the user a role"""
        if user is None or role is None:
            return await ctx.send("Incorrect usage! *;addrole @user role*")
        r = discord.utils.get(ctx.guild.roles, name=str(role))
        if r is None:
            return await ctx.send(f'{role} was not found')
        try:
            await user.add_roles(r)
            return await ctx.send(f"**{str(user)}** has been given the role of **{role}** {self.bot.get_emoji(470063310386233344)}")
        except discord.Forbidden:
            return await ctx.send("Bot does not have enough permissions to give roles.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member, time_and_unit=None, *, reason: str = None):
        """Mute a user for a certain amount of time
        Example: ;mute @fire1234#6302 20m (this will mute the @fire1234#6302 for 20 minutes)"""
        server = ctx.message.guild
        channel = ctx.message.channel
        author = ctx.message.author
        if channel.permissions_for(user).administrator:
            await ctx.send("That user has administrator perms, why would I even try :no_entry:")
            return
        if user.top_role.position >= author.top_role.position:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not mute someone higher than your own role :no_entry:")
                return
        if not time_and_unit:
            time2 = 600
            time = "10"
            unit = "minutes"
        else:
            try:
                unit = time_and_unit[len(time_and_unit) - 1:len(time_and_unit)]
            except ValueError:
                await ctx.send("Invalid time unit :no_entry:")
                return
            try:
                time = time_and_unit[0:len(time_and_unit) - 1]
            except ValueError:
                await ctx.send("Invalid time unit :no_entry:")
                return
            if unit == "s":
                try:
                    time2 = int(time)
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "second"
                else:
                    unit = "seconds"
            elif unit == "m":
                try:
                    time2 = int(time) * 60
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "minute"
                else:
                    unit = "minutes"
            elif unit == "h":
                try:
                    time2 = int(time) * 3600
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "hour"
                else:
                    unit = "hours"
            elif unit == "d":
                try:
                    time2 = int(time) * 86400
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "day"
                else:
                    unit = "days"
            else:
                await ctx.send("Invalid time unit :no_entry:")
                return
        action = "Mute ({} {})".format(time, unit)
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if str(user.id) not in self.d[str(server.id)]:
            self.d[str(server.id)][str(user.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["toggle"] = False
            dataIO.save_json(self.file, self.d)
        if "time" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["time"] = None
            dataIO.save_json(self.file, self.d)
        if "amount" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["amount"] = None
            dataIO.save_json(self.file, self.d)
        role = discord.utils.get(server.roles, name="Muted - Sensei")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            role = await server.create_role(name="Muted - Sensei")
            for channels in ctx.guild.text_channels:
                await channels.set_permissions(role, overwrite=overwrite)
            for channels in ctx.guild.voice_channels:
                await channels.set_permissions(role, overwrite=perms)
        if role in user.roles:
            await ctx.send("**{}** is already muted :no_entry:".format(user))
            return
        try:
            await user.add_roles(role)
        except:
            await ctx.send("I cannot add the mute role to the user :no_entry:")
            return
        await ctx.send(f"**{user}** has been muted for {time} {unit} {self.bot.get_emoji(470063310386233344)}")
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        self.d[str(server.id)][str(user.id)]["toggle"] = True
        self.d[str(server.id)][str(user.id)]["amount"] = time2
        self.d[str(server.id)][str(user.id)]["time"] = ctx.message.created_at.timestamp()
        dataIO.save_json(self.file, self.d)
        try:
            s = discord.Embed(title="You have been muted in {} :speak_no_evil:".format(server.name), colour=0xfff90d,
                              timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
            s.add_field(name="Time", value="{} {}".format(time, unit), inline=False)
            if reason:
                s.add_field(name="Reason", value=reason, inline=False)
            await user.send(embed=s)
        except:
            pass

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member, *, reason: str = None):
        """Unmute a user who is muted"""
        server = ctx.message.guild
        channel = ctx.message.channel
        author = ctx.message.author
        action = "Unmute"
        role = discord.utils.get(server.roles, name="Muted - Sensei")
        if not role:
            await ctx.send("No-one is muted in this server :no_entry:")
            return
        if role not in user.roles:
            await ctx.send("**{}** is not muted :no_entry:".format(user))
            return
        try:
            await user.remove_roles(role)
        except:
            await ctx.send("I cannot remove the mute role from the user :no_entry:")
            return
        await ctx.send(f"**{user}** has been unmuted {self.bot.get_emoji(470063310386233344)}")
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        self.d[str(server.id)][str(user.id)]["toggle"] = False
        self.d[str(server.id)][str(user.id)]["time"] = None
        self.d[str(server.id)][str(user.id)]["amount"] = None
        dataIO.save_json(self.file, self.d)
        try:
            s = discord.Embed(title="You have been unmuted early in {}".format(server.name), colour=000000,
                              timestamp=datetime.datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)))
            await user.send(embed=s)
        except:
            pass

    async def on_member_ban(self, guild, user):
        author = None
        for x in await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten():
            author = x.user
            if x.reason != "":
                reason = x.reason
            else:
                reason = None
        action = "Ban"
        server = guild
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass

    async def on_member_unban(self, guild, user):
        author = None
        for x in await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten():
            author = x.user
            if x.reason != "":
                reason = x.reason
            else:
                reason = None
        action = "Unban"
        server = guild
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass


def setup(bot):
    bot.add_cog(Mod(bot))
    print("Mod module loaded.")






