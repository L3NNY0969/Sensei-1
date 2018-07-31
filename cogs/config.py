import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
import os
import discord
from discord.ext import commands
from utils.dataIO import fileIO
import json
from utils.paginator import HelpPaginator, CannotPaginate


class Config:
    """Configuration"""

    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/mod/autorole.json"
        self.antilinkpath = "data/mod/antilink.json"
        self.json = "data/general/starboard.json"
        self.starboardpath = dataIO.load_json(self.json)
        self.settings = dataIO.load_json(self.antilinkpath)
        self.data = dataIO.load_json(self.JSON)
        self._logs_file = "data/mod/modlogs.json"
        self._logs = dataIO.load_json(self._logs_file)


    # @commands.command()
    # @commands.is_owner()
    # @commands.has_permissions(manage_guild=True)
    # async def starboard(self, ctx, *, channel: discord.TextChannel):
    #    server=ctx.guild
    #    if str(server.id) not in self.starboardpath:
    #        self.starboardpath[str(server.id)] = {}
    #        dataIO.save_json(self.json, self.starboardpath)
    #        self.starboardpath[str(server.id)]["channel"] = channel.id
    #        dataIO.save_json(self.json, self.starboardpath)
    #        await ctx.send(f"The starboard channel has been set to {channel.mention} {self.bot.get_emoji(470063310386233344)}")
    #    else:
    #        self.starboardpath[str(server.id)]["channel"] = channel.id
    #        dataIO.save_json(self.json, self.starboardpath)
    #        await ctx.send(f"The starboard channel has been set to {channel.mention} {self.bot.get_emoji(470063310386233344)}")

    async def on_member_join(self, member):
        server = member.guild
        try:
            role = discord.utils.get(server.roles, name=self.data[str(server.id)]["role"])
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await member.add_roles(role, reason="Autorole")
            except AttributeError:
                pass
        except KeyError:
            pass

    # async def on_reaction_add(self, reaction, user):
    #    server=reaction.message.guild
    #    if reaction.message.author == user:
    #        return
    #    if reaction.emoji == '⭐' or reaction.emoji == '🌟':
    #        try:
    #            if self.starboardpath[str(server.id)]['channel']:
    #                chan = self.bot.get_channel(int(self.starboardpath[str(server.id)]['channel']))
    #            if not chan:
    #                return
    #            try:
    #                img_url = reaction.message.attachments[0].url
    #            except IndexError:
    #                img_url = None
    #            if not img_url:
    #                try:
    #                    img_url = reaction.message.embeds[0].url
    #                except IndexError:
    #                    img_url = None
    #            em = discord.Embed(color=000000, title="Starred Message")
    #            em.description = reaction.message.content
    #            em.set_author(name=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
    #            if img_url:
    #                em.set_image(url=str(img_url))
    #            await chan.send(embed=em)
    #        except KeyError:
    #            pass
    #    else:
    #        pass

    @commands.group(pass_context=True)
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
    @commands.has_permissions(manage_guild=True)
    async def role(self, ctx, *, role: discord.Role):
        """Set the role to be added to a user when they join"""
        server = ctx.guild
        self.data[str(server.id)]["role"] = role.name
        dataIO.save_json(self.JSON, self.data)
        await ctx.send(f"The autorole role is now **{role.name}** {self.bot.get_emoji(470063310386233344)}")

    @autorole.command()
    @commands.has_permissions(manage_guild=True)
    async def fix(self, ctx):
        """Has the bot been offline and missed a few users? Use this to add the role to everyone who doesn't have it"""
        server = ctx.guild
        role = discord.utils.get(server.roles, name=self.data[str(server.id)]["role"])
        members = len([x for x in server.members if role not in x.roles])
        if not role:
            await ctx.send("Role is not set or does not exist :no_entry:")
        for user in [x for x in server.members if role not in x.roles]:
            await user.add_roles(role, reason="Autorole fix")
        await ctx.send(f"Added **{role.name}** to **{members}** users {self.bot.get_emoji(470063310386233344)}")

    @autorole.command()
    @commands.has_permissions(manage_guild=True)
    async def toggled(self, ctx):
        """Toggle autorole on or off"""
        server = ctx.guild
        if self.data[str(server.id)]["toggle"] == True:
            self.data[str(server.id)]["toggle"] = False
            await ctx.send(f"Auto-role has been disabled {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.JSON, self.data)
            return
        if self.data[str(server.id)]["toggle"] == False:
            self.data[str(server.id)]["toggle"] = True
            await ctx.send(f"Auto-role has been enabled {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.JSON, self.data)
            return

    @autorole.command()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """View the settings of autorole on your server"""
        if not ctx:
            print('No ctx given')
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

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx):
        """Sets up the bot"""
        with open('data/general/servers.json') as f:
            data = json.loads(f.read())
        server = ctx.guild
        data[str(server.id)] = {}
        await ctx.send('Please enter a prefix (Enter None for default)')
        prefix = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if prefix.content.lower() == 'none':
            prefix.content = ';'
        await ctx.send(f'Prefix set to {prefix.content}')

        await ctx.send('Enable welcome message? (Y/N)')
        msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
            await ctx.send('What should the message say?')
            await ctx.send('The variables you can use are:')
            await ctx.send(
                '```{user} - the user\'s name\n{mention} - mentions the user\n{server} - your server\'s name\n{member_count} - the amount of members in the server```')
            msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            msg = f'{msg.content}'
            await ctx.send('What channel should be the welcome channel?')
            welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            if welc_channel.content.startswith('<#'):
                await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
            else:
                await ctx.send('Invalid channel. Please make sure you mention the channel')
                await ctx.send('What channel should be the welcome channel?')
                welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                if welc_channel.content.startswith('<#'):
                    await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
                else:
                    await ctx.send('Invalid channel. Please make sure you mention the channel')
                    await ctx.send('What channel should be the welcome channel?')
                    welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                    if welc_channel.content.startswith('<#'):
                        await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
                    else:
                        await ctx.send('Invalid channel. Please make sure you mention the channel')
                        await ctx.send('What channel should be the welcome channel?')
                        welc_channel = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                        await ctx.send(f'Welcome channel set to {welc_channel.content} with the message```{msg}```')
        else:
            msg = None
            welc_channel = None
            pass

        await ctx.send('Enable leave message? (Y/N)')
        msg2 = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        if msg2.content.lower() == 'yes' or 'y' == msg2.content.lower():
            await ctx.send('What should the message say?')
            await ctx.send('You can use {user} {server} and {member_count} to use them in your message')
            leave_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
            await ctx.send(f'Leave message set to ```{leave_msg.content}```')
        else:
            leave_msg = None
            pass

        data[str(server.id)]['name'] = server.name
        data[str(server.id)]['prefix'] = prefix.content.strip('"')
        if welc_channel and msg != None:
            data[str(server.id)]['welc_channel'] = welc_channel.content.strip('"')
            data[str(server.id)]['welc_msg'] = msg.strip('"')
        else:
            data[str(server.id)]['welc_channel'] = welc_channel
            data[str(server.id)]['welc_msg'] = msg
        if leave_msg != None:
            data[str(server.id)]['leave_msg'] = leave_msg.content.strip('"')
        else:
            data[str(server.id)]['leave_msg'] = leave_msg

        data = json.dumps(data, indent=4, sort_keys=True)

        with open('data/general/servers.json', 'w') as f:
            f.write(data)
        await ctx.send('Setup complete')

    @commands.group(pass_context=True)
    @commands.has_permissions(manage_guild=True)
    async def antilink(self, ctx):
        """Block out those advertisers"""
        server = ctx.guild
        if str(server.id) not in self.settings:
            self.settings[str(server.id)] = {}
            dataIO.save_json(self.antilinkpath, self.settings)
        if "toggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["toggle"] = False
            dataIO.save_json(self.antilinkpath, self.settings)
        if "modtoggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["modtoggle"] = True
            dataIO.save_json(self.antilinkpath, self.settings)
        if "admintoggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["admintoggle"] = False
            dataIO.save_json(self.antilinkpath, self.settings)
        if "bottoggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["bottoggle"] = True
            dataIO.save_json(self.antilinkpath, self.settings)
        if "channels" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["channels"] = {}
            dataIO.save_json(self.antilinkpath, self.settings)

    @antilink.command()
    @commands.has_permissions(manage_guild=True)
    async def toggle(self, ctx):
        """Toggle antilink on or off"""
        server = ctx.guild
        if self.settings[str(server.id)]["toggle"] == True:
            self.settings[str(server.id)]["toggle"] = False
            await ctx.send(f"Anti-link has been disabled {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return
        if self.settings[str(server.id)]["toggle"] == False:
            self.settings[str(server.id)]["toggle"] = True
            await ctx.send(f"Anti-link has been enabled {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return

    @antilink.command()
    @commands.has_permissions(manage_guild=True)
    async def modtoggle(self, ctx):
        """Choose whether you want your mods to be able to send links or not (manage_message and above are classed as mods)"""
        server = ctx.guild
        if self.settings[str(server.id)]["modtoggle"] == True:
            self.settings[str(server.id)]["modtoggle"] = False
            await ctx.send(f"Mods will now not be affected by anti-link {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return
        if self.settings[str(server.id)]["modtoggle"] == False:
            self.settings[str(server.id)]["modtoggle"] = True
            await ctx.send(f"Mods will now be affected by anti-link {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return

    @antilink.command()
    @commands.has_permissions(manage_guild=True)
    async def admintoggle(self, ctx):
        """Choose whether you want your admins to be able to send links or not (administrator perms are classed as admins)"""
        server = ctx.guild
        if self.settings[str(server.id)]["admintoggle"] == True:
            self.settings[str(server.id)]["admintoggle"] = False
            await ctx.send(f"Admins will now not be affected by anti-link {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return
        if self.settings[str(server.id)]["admintoggle"] == False:
            self.settings[str(server.id)]["admintoggle"] = True
            await ctx.send(f"Admins will now be affected by anti-link {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return

    @antilink.command()
    @commands.has_permissions(manage_guild=True)
    async def togglebot(self, ctx):
        """Choose whether bots can send links or not"""
        server = ctx.guild
        if self.settings[str(server.id)]["bottoggle"] == True:
            self.settings[str(server.id)]["bottoggle"] = False
            await ctx.send(f"Bots will now not be affected by anti-link {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return
        if self.settings[str(server.id)]["bottoggle"] == False:
            self.settings[str(server.id)]["bottoggle"] = True
            await ctx.send(f"Bots will now be affected by anti-link {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return

    @antilink.command()
    @commands.has_permissions(manage_guild=True)
    async def togglechannel(self, ctx, channel: discord.TextChannel = None):
        """Choose what channels you want to count towards antilink"""
        server = ctx.guild
        if not channel:
            channel = ctx.channel
        if self.settings[str(server.id)]["channels"] == None:
            self.settings[str(server.id)]["channels"][str(channel.id)] = {}
            await ctx.send(
                f"Anti-link is now disabled in <#{str(channel.id)}> {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return
        elif str(channel.id) not in self.settings[str(server.id)]["channels"]:
            self.settings[str(server.id)]["channels"][str(channel.id)] = {}
            await ctx.send(
                f"Anti-link is now disabled in <#{str(channel.id)}> {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return
        else:
            del self.settings[str(server.id)]["channels"][str(channel.id)]
            await ctx.send(f"Anti-link is now enabled in <#{str(channel.id)}> {self.bot.get_emoji(470063310386233344)}")
            dataIO.save_json(self.antilinkpath, self.settings)
            return

    @antilink.command()
    async def stats(self, ctx):
        """View the settings of the antilink in your server"""
        serverid = ctx.guild.id
        server = ctx.guild
        s = discord.Embed(color=000000)
        s.set_author(name="Anti-link Settings", icon_url=self.bot.user.avatar_url)
        if self.settings[str(server.id)]["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        if self.settings[str(server.id)]["bottoggle"] == False:
            bottoggle = "Bots **can** send links"
        else:
            bottoggle = "Bots **can't** send links"
        if self.settings[str(serverid)]["modtoggle"] == False:
            mod = "Mods **can** send links"
        else:
            mod = "Mods **can't** send links"
        if self.settings[str(serverid)]["admintoggle"] == False:
            admin = "Admins **can** send links"
        else:
            admin = "Admins **can't** send links"
        s.add_field(name="Status", value=toggle)
        s.add_field(name="Mod Perms", value=mod)
        s.add_field(name="Admin Perms", value=admin)
        s.add_field(name="Bots", value=bottoggle)
        try:
            msg = ""
            for channelid in self.settings[str(server.id)]["channels"]:
                channel = discord.utils.get(server.channels, id=int(channelid))
                msg += channel.name + "\n"
            if msg == "":
                s.add_field(name="Disabled Channels", value="None")
                await ctx.send(embed=s)
                return
            else:
                s.add_field(name="Disabled Channels", value=msg)
        except:
            s.add_field(name="Disabled Channels", value="None")
        await ctx.send(embed=s)

    async def on_message(self, message):
        try:
            serverid = message.guild.id
            author = message.author
            channel = message.channel
            try:
                if self.settings[str(serverid)]["modtoggle"] == False:
                    if channel.permissions_for(author).manage_messages:
                        return
                if self.settings[str(serverid)]["admintoggle"] == False:
                    if channel.permissions_for(author).administrator:
                        return
                if self.settings[str(serverid)]["bottoggle"] == False:
                    if author.bot:
                        return
                try:
                    if str(channel.id) in self.settings[str(serverid)]["channels"]:
                        return
                except:
                    pass
                if self.settings[str(serverid)]["toggle"] == True:
                    if ("http://" in message.content.lower()) or ("https://" in message.content.lower()):
                        await message.delete()
                        await channel.send(
                            "{}, You are not allowed to send links here :no_entry:".format(author.mention), delete_after=10)
                        if self._logs[str(message.guild.id)]["toggle"] == True and channel is not None:
                            channel = self.bot.get_channel(int(self._logs[str(message.guild.id)]["channel"]))
                            embed=discord.Embed(title=f'{message.author} sent an invite link')
                            embed.add_field(name="Channel:", value=f"<#{message.channel.id}>")
                            embed.add_field(name="Message Content:", value=message.content)
                            embed.color = 000000
                            try:
                                await channel.send(embed=embed)
                            except:
                                pass



            except KeyError:
                pass
        except AttributeError:
            pass

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


    async def on_message_edit(self, before, after):
        try:
            serverid = before.guild.id
            author = before.author
            channel = before.channel
            try:
                if self.settings[str(serverid)]["modtoggle"] == False:
                    if channel.permissions_for(author).manage_messages:
                        return
                if self.settings[str(serverid)]["admintoggle"] == False:
                    if channel.permissions_for(author).administrator:
                        return
                if self.settings[str(serverid)]["bottoggle"] == False:
                    if author.bot:
                        return
                try:
                    if str(channel.id) in self.settings[str(serverid)]["channels"]:
                        return
                except:
                    pass
                if self.settings[str(serverid)]["toggle"] == True:
                    if ("http://" in after.content.lower()) or ("https://" in after.content.lower()):
                        await after.delete()
                        await channel.send(
                            "{}, You are not allowed to send links here :no_entry:".format(author.mention))
            except KeyError:
                pass
        except AttributeError:
            pass

    async def on_member_join(self, member):
        server = member.guild
        try:
            role = discord.utils.get(server.roles, name=self.data[str(server.id)]["role"])
            try:
                if self.data[str(server.id)]["toggle"] == True:
                    await member.add_roles(role, reason="Autorole")
            except AttributeError:
                pass
        except KeyError:
            pass


def setup(bot):
    bot.add_cog(Config(bot))
    print("Config module loaded.")

