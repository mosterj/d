import discord
import asyncio
import os
import roblox
import time
import inspect
import aiohttp
import json
import datetime
pruning = False

### mostly taken from https://github.com/916253/Kurisu/blob/master/run.py
##dir_path = os.path.dirname(os.path.realpath(__file__))
##os.chdir(dir_path)
##
##os.makedirs("data", exist_ok=True)ti
### create warns.json if it doesn't exist
##if not os.path.isfile("data/warns.json"):
##    with open("data/warns.json", "w") as f:
##        f.write("{}")
##
### create blacklist.json if it doesn't exist
##if not os.path.isfile("data/blacklist.json"):
##    with open("data/blacklist.json", "w") as f:
##        f.write("{}")

with open("data/settings.json", "r") as stnobj:
    settings = json.load(stnobj)

blacklist = settings['shadelists']['word_blacklist']
ublacklist = settings['shadelists']['user_blacklist']
permitted_servers = settings['shadelists']['server_whitelist']
lma_password = settings['tokens_and_logins']['lma_roblox']
fbr_password = settings['tokens_and_logins']['fbr_roblox']

client = discord.Client()
colour = discord.Colour(value=14754329)
roblma = roblox.RobloxSession()
robfbr = roblox.RobloxSession()
session = aiohttp.ClientSession()
print('Loaded discord.py client and loaded ROBLOX account')

@client.event
async def on_ready():
    global permitted_servers
    game = discord.Game(name="-help | Groupblox Bot",url="https://www.roblox.com/",type=1)
    await client.change_presence(game=game,afk=False)
    print('Logged in')
    curr_servers = list(client.servers)[:]
    for i in curr_servers:
        if i.id not in permitted_servers:
            print("Left server {}".format(i.name))
            await client.leave_server(i)
    # blacklist_chnl = client.get_channel("343121616193978369")
    # if blacklist_chnl == None:
    #     return 
    # await client.edit_message(client.get_message(client.get_channel("343121616193978369"), "343129259956764673"), '**Blacklist:** {}'.format(', '.join(blacklist)))
    # msg = client.get_message(blacklist_chnl, "343129259956764673")
    # if msg == None:
    #     return
    # await client.edit_message(msg, '**Blacklist:** {}'.format(', '.join(blacklist)))
    # for server in client.servers:
    #     with os.scandir("data\\") as deer:
    #         ok i quit

verify_server_ids = ['383410524278226944'] # LeMonde, Groupblox, RoCentral, FlyBristol
no_verify_logs = []

@client.event
async def on_message(msg):
    global permitted_servers
    global ublacklist
    global settings
    global blacklist
    global lma_password
    global fbr_password
    server = msg.server

    # people
    owner = discord.utils.get(client.get_all_members(), id="383410524278226944")
    member = msg.author
    if msg.channel.is_private and msg.author != client.user:
        if msg.content.lower().startswith('-'):
            await client.send_message(msg.channel, "Commands must be used in a server.")
        await client.send_message(owner, "**New message sent to bot by " + msg.author.name + "#"+msg.author.discriminator + " (<@"+msg.author.id+">):** " + msg.content)
        if msg.attachments != []:
            for i in msg.attachments:
                await client.send_message(owner, "**An attachment was also sent with the message, which is currently displayed:** " + i['url'])
    elif not msg.channel.is_private:
        if server.unavailable:
            return
        elif msg.author.bot:
            return
        elif server.id not in permitted_servers:
            print("Left server {}".format(server.name))
            await client.leave_server(server)
    if msg.channel.name == 'verify' and not msg.author.bot:
        if msg.content.lower() == '-verify' and server.id in verify_server_ids:
            async def verify():
                verified_role = discord.utils.get(member.server.roles, name="Verified")
                r = await session.get('https://verify.eryn.io/api/user/{}'.format(member.id))
                output = await r.json()
                if output['status'] == 'ok':
                    verified = False
                    try:
                        if msg.server.id == '383410524278226944':
                            user = robfbr.get_user(user_id=output['robloxId'])
                            group = robfbr.get_group(1110714)
                            if group in user.groups():
                                await client.add_roles(member, discord.utils.get(member.server.roles, name="Customers"))
                            else:
                                await client.send_message(msg.channel, "Join the California Pacific Airlines group to join the Discord! https://www.roblox.com/groups/group.aspx?gid=1110714")
                            return
                        await client.change_nickname(member, output['robloxUsername'])
                        await client.add_roles(member, verified_role)
                        verified = True
                    except discord.DiscordException:
                        await client.send_message(msg.channel, "It seems you have a role higher than the bot itself - I can't change your nickname! Please change your nickname to match your ROBLOX username, which is `{}`".format(output['robloxUsername']))
                    finally:
                        if verified:
                            await client.send_message(member, "Hey! We've found your ROBLOX username to be {} and allowed you access to the remainder of the server. Enjoy your stay!".format(output['robloxUsername']))
                            await client.send_message(discord.utils.get(server.channels, name="verify-logs"), "**User verified:** <@{}> as {}".format(msg.author.id, output['robloxUsername']))
                elif output['error'] and output['errorCode'] == 404:
                    await client.send_message(msg.channel, "Hi! You haven't verified yet. Go to http://verify.eryn.io/ to get verified!")
                elif output['error'] and output['errorCode'] == 429:
                    asyncio.sleep(int(output['retryAfterSeconds']))
                    await verify()
                elif output['error']:
                    await client.send_message(msg.channel, "An unknown error occured: `{}`".format(output['error']))
            await verify()
        await client.delete_message(msg)
    elif msg.content.lower() == '-verify' and msg.server.id in verify_server_ids:
        async def verify():
            verified_role = discord.utils.get(member.server.roles, name="Verified")
            r = await session.get('https://verify.eryn.io/api/user/{}'.format(member.id))
            output = await r.json()
            if output['status'] == 'ok':
                await client.add_roles(member, verified_role)
                verified = False
                try:
                    if output['robloxUsername'] != member.display_name:
                        await client.change_nickname(member, output['robloxUsername'])
                    verified = True
                except discord.DiscordException:
                    await client.send_message(msg.channel, "It seems you have a role higher than the bot itself - I can't change your username! Please change your nickname to match your ROBLOX username, which is: `{}`".format(output['robloxUsername']))
                finally:
                    if verified:
                        if output['robloxUsername'] != member.display_name:
                            await client.send_message(member, "Hey! We've found your username currently on record to be {}. Your current nickname is {}, so we've gone and changed it for you.".format(output['robloxUsername'], member.display_name))
                            await client.send_message(discord.utils.get(server.channels, name="verify-logs"), "**User verified:** <@{}> as {}".format(msg.author.id, output['robloxUsername']))
                        else:
                            await client.send_message(msg.channel, "Your ROBLOX username is the same as your current nickname, so we've gone and done nothing.")
            elif output['error'] and output['errorCode'] == 404:
                await client.send_message(msg.channel, "Hi! You haven't verified yet. Go to http://verify.eryn.io/ to get verified!")
            elif output['error'] and output['errorCode'] == 429:
                asyncio.sleep(int(output['retryAfterSeconds']))
                await verify()
            elif output['error']:
                await client.send_message(msg.channel, "An unknown error occured: `{}`".format(output['error']))
        await verify()
    elif msg.content.lower().startswith('-update ') and server.id in verify_server_ids:
        if server.id == '379360947740868608':
            staff_role = discord.utils.get(server.roles, name="High Ranks")
            # if msg.author.id == '143762055457931265':
            #     await client.send_message(msg.channel, "Command disabled for trainana due to abuse.")
            #     return
        else:
            staff_role = discord.utils.get(server.roles, name="Staff")
        if staff_role in member.roles:
            if not member.server.id == '303128948785545216':
                verified_role = discord.utils.get(member.server.roles, name="Verified")
            else:
                verified_role = discord.utils.get(member.server.roles, name="Customers")
            user_id = msg.content.split()[1].strip("<@!>")
            user = discord.utils.get(server.members, id=user_id)
            if not user == None:
                async def verify():
                    r = await session.get('https://verify.eryn.io/api/user/{}'.format(user_id))
                    output = await r.json()
                    if output['status'] == 'ok':
                        await client.add_roles(user, verified_role)
                        verified = False
                        try:
                            if msg.server.id == '255156387997417472':
                                user = robfbr.get_user(user_id=output['robloxId'])
                                group = robfbr.get_group(1110714)
                                if group in user.groups():
                                    await client.add_roles(member, discord.utils.get(member.server.roles, name="Passengers"))
                                return
                            await client.change_nickname(user, output['robloxUsername'])
                            verified = True
                        except discord.DiscordException:
                            await client.send_message(msg.channel, "It seems the player has a role higher than the bot itself - I can't change their username! Please change their nickname to match their ROBLOX username, which is: `{}`".format(output['robloxUsername']))
                        finally:
                            if verified:
                                await client.send_message(msg.channel, "Verified user {} as {}!".format(user.mention, output['robloxUsername']))
                                await client.send_message(discord.utils.get(server.channels, name="verify-logs"), "**User verified:** {} as {}".format(user.mention, output['robloxUsername']))
                    elif output['error'] and output['errorCode'] == 404:
                        await client.send_message(msg.channel, "User {} has not verified.".format(user.mention))
                        await client.remove_roles(user, verified_role)
                    elif output['error'] and output['errorCode'] == 429:
                        asyncio.sleep(int(output['retryAfterSeconds']))
                        await verify()
                    elif output['error']:
                        await client.send_message(msg.channel, "An unknown error occured: `{}`".format(output['error']))
                await verify()
            elif user == None:
                await client.send_message(msg.channel, "Could not find that user on this server. `{}`".format(user_id))
        else:
            if server.id == '379360947740868608':
                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** FlyBristol High Rank")
            else:
                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
    elif msg.author.id in ublacklist:
        if msg.channel.id != '343121616193978369' and msg.server.id != '255156387997417472':
            for i in blacklist:
                if i in msg.content.lower():
                    if i == 'discord.gg/':
                        staff_role = discord.utils.get(server.roles, name="Staff")
                        if not staff_role in member.roles:
                            await client.delete_message(msg)
                    elif msg.server.id != '379360947740868608':
                        await client.delete_message(msg)
                    else:
                        logs = discord.utils.get(msg.server.channels, id="381900428155027459")
                        embed = discord.Embed(color=colour)
                        if msg.author.avatar_url == "":
                            embed.set_author(name="{} ({})".format(str(msg.author), msg.author.id), icon_url=msg.author.default_avatar_url)
                        else:
                            embed.set_author(name="{} ({})".format(str(msg.author), msg.author.id), icon_url=msg.author.avatar_url)
                        embed.add_field(name="Potential Swearing Detected", value=msg.content)
                        await client.send_message(logs, embed=embed)
                        break
        return
    elif msg.content.lower().startswith('-say'):
        if msg.author == discord.utils.get(server.members, id="252154198542647296"):
            await client.send_message(msg.channel, msg.content[5:])
            await client.delete_message(msg)
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-eval '):
        if msg.author == owner:
            code = msg.content[6:]
            code = code.strip('` ')
            python = '```py\n{}\n```'
            result = None

            env = {
                'client': client,
                'msg': msg,
                'member': member,
                'server': server,
                'owner': owner
            }

            env.update(globals())

            if 'token' in code:
                tosend = ":arrow_down: **INPUT:**\n```Python\n{}\n```\n:arrow_up: **OUTPUT:**\n```Python\n\"Nope.\"\n```".format(code)
                await client.send_message(msg.channel, tosend)
                return
            
            try:
                result = eval(code, env)
                if inspect.isawaitable(result):
                    result = await result
            except Exception as ex:
                tosend = ":arrow_down: **INPUT:**\n```Python\n{}\n```\n:arrow_up: **OUTPUT:**\n```Python\n{}\n```".format(code, type(ex).__name__ + ': ' + str(ex))
                await client.send_message(msg.channel, tosend)
                return

            tosend = ":arrow_down: **INPUT:**\n```Python\n{}\n```\n:arrow_up: **OUTPUT:**\n```Python\n{}\n```".format(code, result)
            await client.send_message(msg.channel, tosend)
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-announce') and server.id not in ['379360947740868608', '323127945713549322']:
        staff_role = discord.utils.get(server.roles, name="Staff")
        announcements = discord.utils.get(server.channels, name="announcements")
        if member == discord.utils.get(server.members, id="252154198542647296") or staff_role in member.roles:
            client.send_typing(announcements)
            embed = discord.Embed(colour=colour)
            if not msg.author.avatar_url == '':
                embed.set_author(name=member.name+"#"+member.discriminator,url=embed.Empty,icon_url=member.avatar_url)
            else:
                embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.default_avatar_url)
            embed.add_field(name="Announcement",value=msg.content[9:],inline=False)
            await client.send_message(announcements, embed=embed)
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner, Server Staff")
    # elif msg.content.lower().startswith('-shout') and server.id == '379360947740868608':
    #     await client.send_message(msg.channel, "This command is disabled since **the API is broken.** Thank <@231658954831298560> for this.")
    #     hr_role = discord.utils.get(server.roles, name="High Ranks")
    #     if hr_role in member.roles:
    #         if len(msg.content[6:]) > 255:
    #             await client.send_message(msg.channel, "The new shout is too long.")
    #             return
    #         if not robfbr.verify_session():
    #             try:
    #                 robfbr.logout()
    #             except roblox.errors.BadRequest:
    #                 print('Logging into FlyBristol account')
    #             finally:
    #                 robfbr.login("FBR_Bot", fbr_password)
    #         try:
    #             group = robfbr.get_group(2720616)
    #             shout = group.post_shout(msg.content[6:])
    #             if shout == None:
    #                 await client.send_message(msg.channel, "I posted the shout - however I can't display it because the shout is empty.")
    #                 return
    #             embed = discord.Embed(colour=colour)
    #             if shout.author != None:
    #                 embed.set_author(name=shout.author.username,url=shout.author.absolute_url,icon_url="https://www.roblox.com/Thumbs/Avatar.ashx?x=500&y=500&userId={}".format(shout.author.id))
    #             embed.add_field(name="Latest shout from {}".format(group.name),value=shout.content,inline=False)
    #             if shout.created != None:
    #                 embed.set_footer(text=shout.created.strftime('%A %d %B, %H:%M:%S %Z'))
    #             await client.send_message(msg.channel, embed=embed)
    #         except Exception as ex:
    #             await client.send_message(msg.channel, "Something went wrong! Internal error:\n`{}`".format(type(ex).__name__ + ': ' + str(ex)))
    #     else:
    #         await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** FlyBristol High Rank")
    elif msg.content.lower() == '-getshout' and server.id in ['265962307299835905','379360947740868608']:
        if server.id == '265962307299835905':
            if not roblma.verify_session():
                try:
                   roblma.logout()
                except roblox.errors.BadRequest:
                    print('Logging into LeMonde account')
                finally:
                   roblma.login("LeMondeRankUp", lma_password)
            group = roblma.get_group(1156950)
            shout = group.get_shout
        elif server.id == '379360947740868608':
            if not robfbr.verify_session():
                try:
                   robfbr.logout()
                except roblox.errors.BadRequest:
                    print('Logging into FlyBristol account')
                finally:
                   robfbr.login("FBR_Bot", fbr_password)
            group = robfbr.get_group(2720616)
            shout = group.get_shout
        if shout == None:
            await client.send_message(msg.channel, "The shout is empty, or I don't have permissions to view the shout.")
            return
        embed = discord.Embed(colour=colour)
        if shout.author != None:
            embed.set_author(name=shout.author.username,url=shout.author.absolute_url,icon_url="https://www.roblox.com/Thumbs/Avatar.ashx?x=500&y=500&userId={}".format(shout.author.id))
        embed.add_field(name="Latest shout from {}".format(group.name),value=shout.content,inline=False)
        if shout.created != None:
            embed.set_footer(text=shout.created.strftime('%A %d %B, %H:%M:%S CST/CDT (GMT -6)'))
        await client.send_message(msg.channel, embed=embed)
    elif msg.content.lower().startswith('-prune') and server.id != '323127945713549322':
        if server.id == '379360947740868608':
            staff_role = discord.utils.get(server.roles, name="High Ranks")
        else:
            staff_role = discord.utils.get(server.roles, name="Staff")
        pruning = None
        if staff_role not in member.roles:
            pruning = False
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
        elif staff_role in member.roles:	
            try:
                if int(msg.content[6:]) > 100:
                    await client.send_message(msg.channel, "Could not delete messages. Number is higher than 100.")
                else:
                    await client.purge_from(msg.channel,limit=int(msg.content[6:])+1,check=None)
                    msg2 = await client.send_message(msg.channel, "Pruned" + msg.content[6:] + " messages from <#"+msg.channel.id+">.")
                    await asyncio.sleep(5)
                    await client.delete_message(msg2)
                    pruning = False
            except Exception as e:
                await client.send_message(msg.channel, "Could not delete messages. The following error occured: `{}`".format(e))
                pruning = False
    elif msg.content.lower().startswith('-userprune') and server.id != '323127945713549322':
        if server.id == '379360947740868608':
            staff_role = discord.utils.get(server.roles, name="High Ranks")
        else:
            staff_role = discord.utils.get(server.roles, name="Staff")
        if staff_role not in member.roles:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
        elif staff_role in member.roles:
            try:
                if int(msg.content[10:]) > 100:
                    await client.send_message(msg.channel, "Could not delete messages. Number is higher than 100.")
                else:
                    def check(msg2):
                        if msg2.author == msg.author:
                            return msg2.content.startswith('<@') and msg2.content.endswith('>') or msg2.content == '0'
                        else:
                            client.send_message(msg.channel, "Not a valid user. Please mention the user you would like to delete messages from, or type 0 to cancel.")
                            return False
                    await client.send_message(msg.channel, "Please mention the user you would like to delete messages from, or type 0 to cancel.")
                    msg2 = await client.wait_for_message(timeout=None,check=check)
                    user_id = msg2.content.strip('<@>')
                    if user_id.isnumeric() and not user_id == '0':
                        left = int(msg.content[10:])
                        def check2(msg3):
                            if msg3.author.id == user_id:
                                if left > 0:
                                    left = left - 1
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        await client.purge_from(msg.channel,check=check2)
                        msg4 = await client.send_message(msg.channel, "Pruned" + msg.content[10:] + " messages from <#"+msg.channel.id+">.")
                        await asyncio.sleep(5)
                        await client.delete_message(msg4)
                    elif user_id == '0':
                        await client.send_message(msg.channel, "You cancelled the purge.")
                    else:
                        await client.send_message(msg.channel, "Mention is not a user. Please rerun the command.")
            except Exception as e:
                await client.send_message(msg.channel, "Could not delete messages. The following error occured: {}".format(e))
    elif msg.content.lower().startswith('-kick ') and server.id != '379360947740868608' and server.id != '323127945713549322':
        staff_role = discord.utils.get(server.roles, name="Staff")
        if staff_role not in member.roles:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
        elif staff_role in member.roles:
            try:
                user_id = msg.content[7:].strip('<@!>')
                if not user_id.isnumeric():
                    await client.send_message(msg.channel, "Could not kick user. Did you mention a role or channel? `"+user_id+"`")
                else:
                    def check(msg2):
                        return msg2.author == msg.author
                    await client.send_message(msg.channel, "Please state the reason for kicking, or type 0 to cancel.")
                    msg2 = await client.wait_for_message(timeout=None,check=check)
                    reason = msg2.content
                    deny_list = ['0', 'cancel', 'no']
                    if reason.lower() not in deny_list:
                        naughty = discord.utils.get(server.members, id=user_id)
                        if naughty == None:
                            await client.send_message(msg.channel, "Could not kick user. User is not in this server.")
                        elif staff_role in naughty.roles or naughty.id == '312929842712805376':
                            await client.send_message(msg.channel, "Could not kick user. User is a higher or equal role to the bot.")
                        else:
                            try:
                                await client.send_message(naughty, "You have been kicked by <@{}> for the following reason: `{}` You can rejoin by using the link {}.".format(msg.author.id, reason, client.create_invite(msg.server, max_uses=1)))
                                await client.kick(naughty)
                                await client.send_message(msg.channel, "<@"+msg.author.id+"> kicked <@"+user_id+"> for reason `"+reason+"`.")
                            except Exception as e:
                                await client.send_message(msg.channel, "An unknown error occured. Internal error: `{}`".format(e))
                            finally:
                                await client.send_message(msg.channel, "<@"+msg.author.id+"> kicked <@"+user_id+"> for reason `"+reason+"`.")
                    else:
                        await client.send_message(msg.channel, "You cancelled the action `Kick`.")
            except discord.Forbidden():
                await client.send_message(msg.channel, "Could not kick user. User is a higher or equal role to the bot.")
            except Exception and not discord.Forbidden():
                await client.send_message(msg.channel, "Could not kick user. An unknown error occured.")
    elif msg.content.lower().startswith('-bugreport '):
        if msg.content[10:] != '':
            await client.send_message(owner, ":bug: New bug report by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[10:] + "```")
            await client.send_message(msg.channel, "Your bug report has been submitted.")
        else:
            await client.send_message(msg.channel, "A message is required to submit a bug report.")
    elif msg.content.lower().startswith('-feedback'):
        if msg.content[9:] != '':
            await client.send_message(owner, "New feedback by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[9:] + "```")
            await client.send_message(msg.channel, "Your feedback has been submitted.")
        else:
            await client.send_message(msg.channel, "A message is required to submit feedback.")
    elif msg.content.lower().startswith('-game'):
        if msg.author == discord.utils.get(server.members, id="252154198542647296"):
            game = discord.Game(name=msg.content[5:],url="https://www.roblox.com/",type=1)
            await client.change_presence(game=game,afk=False)
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-leaveserver'):
        if msg.author == owner:
            mserver = discord.utils.get(client.servers, id=msg.content.split()[1])
            try:
                await client.send_message(msg.channel, "Left server `{}`".format(mserver.name))
                await client.leave_server(mserver)
            except Exception as e:
                if mserver == None:
                    await client.send_message(msg.channel, "Error: not in server.")
                else:
                    await client.send_message(msg.channel, "The following error occured: `{}`".format(e))
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower() == '-membercount':
        await client.send_message(msg.channel, "The current member count is {} members.".format(str(msg.server.member_count)))
    elif msg.content.lower() == '-cmds':
        if server.id == '379360947740868608':
            staff_role = discord.utils.get(server.roles, name="High Ranks")
        else:
            staff_role = discord.utils.get(server.roles, name="Staff")
        embed = discord.Embed(title="Commands", description="Commands currently available for use (for the server you ran this from):",colour=colour)
        embed.add_field(name="-membercount",value="Gives you the current member count of the server.",inline=False)
        embed.add_field(name="-feedback text",value="Sends your feedback to the bot owner.",inline=False)
        embed.add_field(name="-bugreport text",value="Sends a bug report to the bot owner.",inline=False)
        if server.id != '379360947740868608' and staff_role in member.roles:
                embed.add_field(name="-announce text",value="Announces in #announcements.",inline=False)
                embed.add_field(name="-kick @mention",value="Kicks a user with a specified reason.",inline=False)
        if staff_role in member.roles:
            embed.add_field(name="-prune number",value="Prunes any amount of messages (up to 100) that you specify.",inline=False)
            embed.add_field(name="-userprune number",value="Prunes any amount of messages from a specific user (up to 100) that you specify.",inline=False)
        if server.id in verify_server_ids:
            embed.add_field(name="-verify",value="Verifies yourself, or changes your ROBLOX username if you've already verified.",inline=False)
            if staff_role in member.roles:
                embed.add_field(name="-update",value="Forcefully (re-)verifies the user mentioned.",inline=False)
        if msg.server.id == '265962307299835905':
            embed.add_field(name="-getshout",value="Gets the latest shout from the group linked to the server.",inline=False)
            if staff_role in member.roles:
                embed.add_field(name="-shout text",value="Only usable by high ranks. Shouts the given text to the group linked to the server.",inline=False)
        embed.add_field(name="-server",value="Sends you a link (in DMs) to the Groupblox server!",inline=False)
        embed.add_field(name="-help",value="Shows a bit of info about the bot",inline=False)
        embed.add_field(name="-cmds",value="Shows commands...the ones you're seeing right now.",inline=False)
        await client.send_message(msg.author, embed=embed)
        if msg.channel.type != discord.ChannelType.private:
            await client.send_message(msg.channel, "<@"+msg.author.id+">, check your DMs!")
    elif msg.content.lower() == '-help':
        embed = discord.Embed(title="Groupblox Bot", description="Created by Ali365Dash#5036, use -cmds for commands, and use -server to join our server",colour=colour)
        embed.add_field(name="Suggestions & Bugs",value="Want to give suggestions? Suggest with -feedback! Alternatively, bugs should be reported with -bugreport.",inline=False)
        await client.send_message(msg.channel, embed=embed)
    elif msg.content.lower() == '-server':
        await client.send_message(msg.author, "https://discord.gg/uCMyPhN")
        if msg.channel.type != discord.ChannelType.private:
            await client.send_message(msg.channel, "<@{}>, check your DMs!".format(msg.author.id))
    elif msg.content.lower().startswith('-wblacklist'):
        if msg.author == owner:
            word = msg.content[11:]
            blacklist.append(word)
            with open("data/settings.json", "a") as f:
                f.write(word)
            await client.delete_message(msg)
            await client.send_message(owner, "Added the following word to the blacklist: `{}`".format(word))
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower() == '-restart':
        if msg.author == owner:
            await client.send_message(msg.channel, "This will restart the bot and update it to the latest version. Continue? `y/n`")
            def check(msg2):
                return msg2.author == msg.author and (msg2.content.lower() == 'y' or msg2.content.lower() == 'n')
            msg2 = await client.wait_for_message(timeout=None,check=check)
            if msg2.content.lower() == 'y':
                await client.send_message(msg.channel, ":wave:")
                await client.logout()
        elif server.id != '379360947740868608':
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-checkstaff'):
        if msg.author == owner:
            staff_role = discord.utils.get(server.roles, name=msg.content[11:])
            try:
                staff_dbanned = []
                other_dbanned = []
                await client.send_message(msg.channel, "I hope you're patient, because this is going to take a while.")
                for i in server.members:
                    payload = {
                        "token": settings['tokens_and_logins']["discord_bans"],
                        "userid": i.id
                    }
                    
                    url = "https://bans.discordlist.net/api"

                    resp = await session.post(url, data=payload)
                    final = await resp.text()
                    if final == 'True':
                        if staff_role in i.roles:
                            staff_dbanned.append(i)
                        else:
                            other_dbanned.append(i)
                    resp.close()
                if staff_dbanned == []:
                    if other_dbanned == []:
                        await client.send_message(msg.channel, "No staff members and no non-staff members are banned by Discord Bans! Good to go!")
                    elif other_dbanned != []:
                        await client.send_message(msg.channel, "No staff members are banned by Discord Bans!")
                elif staff_dbanned != []:
                    content = "The following staff members are in the Discord Bans list:"
                    for i in staff_dbanned:
                        content += "\n<@{}>".format(i.id)
                    await client.send_message(msg.channel, content)
                if other_dbanned != []:
                    content = "The following non-staff members are in the Discord Bans list:"
                    for i in other_dbanned:
                        content += "\n<@{}>".format(i.id)
                    await client.send_message(msg.channel, content)
            except Exception as ex:
                await client.send_message(msg.channel, "Something went wrong! Internal error:\n```{}```".format(type(ex).__name__ + ': ' + str(ex)))
        elif server.id != '379360947740868608':
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-allocation') and server.id == '379360947740868608' and msg.channel.id == '379677934786707460':
        os.chdir('data/379360947740868608')
        if msg.content.lower().startswith('-allocation create'):
            proceed = False
            datestr = msg.content.split()[2]
            yyyymmdd = datestr.split('-')
            try:
                dateobj = datetime.date(int(yyyymmdd[0]), int(yyyymmdd[1]), int(yyyymmdd[2]))
                proceed = True
            except ValueError:
                msg2 = client.send_message(msg.channel, "Use the following syntax: `-allocation create YYYY-MM-DD`")
                asyncio.sleep(10)
                client.delete_message(msg2)
            except Exception as e:
                msg2 = client.send_message(msg.channel, "An error occured: `{}`".format(e))
                asyncio.sleep(10)
                client.delete_message(msg2)
            if proceed:
                dsuff = ''
                if dateobj.day == 1 or dateobj.day == 21 or dateobj.day == 31:
                    dsuff = 'ST'
                elif dateobj.day == 2 or dateobj.day == 22:
                    dsuff = 'ND'
                elif dateobj.day == 3 or dateobj.day == 23:
                    dsuff = 'RD'
                else:
                    dsuff = 'TH'
                msg2 = client.send_message(msg.channel, "**{}{} {}**\n\nAirside (0/3):\nLandside (0/4):\nCabin Crew (0/3):\nSecurity (0/3):\nPilots (0/2):".format(dateobj.strftime('%A %d').upper(), dsuff, dateobj.strftime('').upper()))
        elif msg.content.lower().startswith('-allocation alert'):
            await client.send_message(msg.channel, "Hey! I haven't finished this yet.")
    elif msg.content.lower().startswith('-blacklist'):
        if msg.author == owner:
            mention = msg.content.split()[1]
            member = discord.utils.get(server.members, mention=mention)
            if member != None and member.id not in ublacklist:
                ublacklist.append(member.id)
                with open("data/settings.json", "w") as blkobj:
                    json.dump(settings, blkobj)
                await client.send_message(msg.channel, "Blacklisted user `{}` from the bot.".format(str(member)))
            elif member != None and member.id in ublacklist:
                ublacklist.remove(member.id)
                with open("data/settings.json", "w") as blkobj:
                    json.dump(settings, blkobj)
                await client.send_message(msg.channel, "Unblacklisted user `{}` from the bot.".format(str(member)))
            else:
                await client.send_message(msg.channel, "Could not find user from mention {}.".format(mention))
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-cblacklist'):
        if msg.author == owner:
            mention = msg.content.split()[1]
            member = discord.utils.get(server.members, mention=mention)
            if member != None and member.id not in ublacklist:
                await client.send_message(msg.channel, "User `{}` not blacklisted.".format(str(member)))
            elif member != None and member.id in ublacklist:
                await client.send_message(msg.channel, "User `{}` is blacklisted.".format(str(member)))
            else:
                await client.send_message(msg.channel, "Could not find user from mention {}.".format(mention))
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-updatesettings'):
        if msg.author == owner:
            with open("data/settings.json", "r") as blkobj:
                settings = json.load(blkobj)
            await client.send_message(msg.channel, "Updated user blacklist.")
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-addwhitelist'):
        server_id = msg.content.split()[1]
        if msg.author == owner:
            if server_id.isnumeric():
                permitted_servers.append(server_id)
                with open("data/settings.json", "w") as whtobj:
                    json.dump(settings, whtobj)
                await client.send_message(msg.channel, "Added server ID **{}** to whitelist.".format(server_id))
            else:
                await client.send_message(msg.channel, "{}, **WHAT DO YOU THINK YOU'RE DOING? THAT ISN'T EVEN A NUMBER, YOU NONCE!**".format(msg.author.mention))
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    if msg.channel.type != discord.ChannelType.private and msg.channel.id != '343121616193978369' and msg.server.id != '255156387997417472':
        for i in blacklist:
            if i in msg.content.lower():
                if i == 'discord.gg/':
                    staff_role = discord.utils.get(server.roles, name="Staff")
                    if not staff_role in member.roles:
                        await client.delete_message(msg)
                        await client.send_message(msg.channel, "<@"+msg.author.id+">, no advertising! :no_entry:")
                elif msg.server.id != '379360947740868608':
                    await client.delete_message(msg)
                    await client.send_message(msg.channel, "<@"+msg.author.id+">, one of the words or phrases in your message was on the blacklist! For blacklist-free chat, go into your DMs. :no_entry:")
                else:
                    logs = discord.utils.get(msg.server.channels, id="381900428155027459")
                    embed = discord.Embed(color=colour)
                    if msg.author.avatar_url == "":
                        embed.set_author(name="{} ({})".format(str(msg.author), msg.author.id), icon_url=msg.author.default_avatar_url)
                    else:
                        embed.set_author(name="{} ({})".format(str(msg.author), msg.author.id), icon_url=msg.author.avatar_url)
                    embed.add_field(name="Potential Swearing Detected", value=msg.content)
                    await client.send_message(logs, embed=embed)
                    break

@client.event
async def on_member_join(member):
    if member.server.id in verify_server_ids:
        verified_role = discord.utils.get(member.server.roles, name="Customers")
        r = await session.get('https://verify.eryn.io/api/user/{}'.format(member.id))
        output = await r.json()
        if output['status'] == 'ok':
            await client.send_message(member, "Hey! We've found your username to be {}. If prompted, you'll need to verify your phone number with Discord if you haven't already when typing -verify into <#{}>.".format(output['robloxUsername'], discord.utils.get(member.server.channels, name="verify").id))

@client.event
async def on_message_edit(bmsg, amsg):
    if amsg == None or bmsg == None:
        print("wait wut")
        return
    if bmsg.channel.id != '343121616193978369' and bmsg.server.id != '255156387997417472':
        for i in blacklist:
            if i in amsg.content.lower():
                if i == 'discord.gg/':
                    staff_role = discord.utils.get(server.roles, name="Staff")
                    if not staff_role in member.roles:
                        await client.delete_message(amsg)
                        if bmsg.author.id not in ublacklist:
                            await client.send_message(amsg.channel, "<@"+amsg.author.id+">, no advertising! :no_entry:")
                elif bmsg.server.id != '379360947740868608':
                    await client.delete_message(amsg)
                    if bmsg.author.id not in ublacklist:
                        await client.send_message(amsg.channel, "<@"+amsg.author.id+">, one of the words or phrases in your message was on the blacklist! For blacklist-free chat, go into your DMs. :no_entry:")
                else:
                    logs = discord.utils.get(bmsg.server.channels, id="381900428155027459")
                    embed = discord.Embed(color=colour)
                    if bmsg.author.avatar_url == "":
                        embed.set_author(name="{} ({})".format(str(bmsg.author), bmsg.author.id), icon_url=bmsg.author.default_avatar_url)
                    else:
                        embed.set_author(name="{} ({})".format(str(bmsg.author), bmsg.author.id), icon_url=bmsg.author.avatar_url)
                    embed.add_field(name="Potential Swearing Detected", value=amsg.content)
                    await client.send_message(logs, embed=embed)
                    break

@client.event
async def on_member_update(bmbr, ambr):
    if bmbr.display_name != ambr.display_name and bmbr.server.id in verify_server_ids:
        member = ambr
        verified_role = discord.utils.get(member.server.roles, name="Verified")
        if verified_role in member.roles:
            r = await session.get('https://verify.eryn.io/api/user/{}'.format(member.id))
            output = await r.json()
            if output['status'] == 'ok':
                verified = False
                try:
                    await client.change_nickname(member, output['robloxUsername'])
                    verified = True
                except discord.DiscordException:
                    await client.send_message(member, "It seems you have a role higher than the bot itself after having your nickname/username changed - I can't change your nickname! Please change your nickname to match your ROBLOX username, which is `{}`".format(output['robloxUsername']))
                finally:
                    if verified:
                        await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), "**User reverified:** <@{}> as {}".format(member.id, output['robloxUsername']))
            elif output['error'] and output['errorCode'] == 404:
                try:
                    await client.remove_roles(verified_role)
                except discord.DiscordException:
                    await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), "I do not have permissions to manage the Verified role.")
            elif output['error'] and output['errorCode'] == 429:
                asyncio.sleep(int(output['retryAfterSeconds']))
            elif output['error']:
                await client.send_message(msg.channel, "The following error occured while reverifying <@{}>: `{}`".format(member.id, output['error']))

@client.event
async def on_server_join(server):
    os.mkdir("data/{}".format(server.id))

@client.event
async def on_server_leave(server):
    os.remove("data/{}/*.*".format(server.id))
    os.rmdir("data/{}".format(server.id))

print('Starting client')
client.run(settings['tokens_and_logins']['discord'])
