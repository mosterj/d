import discord
import asyncio
import os
import sys
import requests
import roblox
import time
import inspect
import aiohttp
#import json
#import time
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

with open("data/token.txt", "r") as tknobj:
    token = tknobj.read()
with open("data/dbans_token.txt", "r") as tknobj:
    dbtoken = tknobj.read()
with open("data/blacklist.txt", "r") as blkobj:
    blacklist = blkobj.read().splitlines()
with open("data/roblox_login.txt", "r") as logobj:
    password = logobj.read()
client = discord.Client()
rob = roblox.RobloxSession()
session = aiohttp.ClientSession()
rob.login("LeMondeRankUp", password)
print('Loaded discord.py client and loaded ROBLOX account')

@client.event
async def on_ready():
    game = discord.Game(name="-help | Groupblox Bot",url="https://www.roblox.com/",type=1)
    await client.change_presence(game=game,afk=False)
    print('Logged in')
    #  blacklist_chnl = client.get_channel("343121616193978369")
    # if blacklist_chnl == None:
    #     return 
#   await client.edit_message(client.get_message(client.get_channel("343121616193978369"), "343129259956764673"), '**Blacklist:** {}'.format(', '.join(blacklist)))
    # msg = client.get_message(blacklist_chnl, "343129259956764673")
    # if msg == None:
    #     return
    # await client.edit_message(msg, '**Blacklist:** {}'.format(', '.join(blacklist)))
##    for server in client.servers:
##        with os.scandir("data\\") as deer:
##            # ok i quit

verify_server_ids = ['265962307299835905', '303128948785545216', '323147682686304256', '339344865978482689', '338238645792407563', '323906250859479040', '293115433182035970'] # LeMonde, Volago, Apple Rail, Groupblox, RoCentral, FlyBristol
no_verify_logs = []

@client.event
async def on_message(msg):
    server = msg.server
    
    # adding some colour
    colour = discord.Colour(value=14754329)
    
    # people
    owner = discord.utils.get(client.get_all_members(), id="252154198542647296")
    member = msg.author
    if msg.channel.is_private and msg.author != client.user:
        await client.send_message(owner, "**New message sent to bot by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"):** " + msg.content)
        if msg.attachments != []:
            for i in msg.attachments:
                await client.send_message(owner, "**An attachment was also sent with the message, which is currently displayed:** " + i['url'])
    if not msg.channel.is_private:
        if server.unavailable:
            return
    elif msg.channel.is_private:
        if msg.content.lower().startswith('-'):
            await client.send_message(msg.channel, "Commands must be used in a server.")
        return
    if msg.channel.name == 'verify' and not msg.author.bot:
        if msg.content.lower() == '-verify' and server.id in verify_server_ids:
            if member.server.id == '303128948785545216':
                verified_role = discord.utils.get(member.server.roles, name="Customers")
            else:
                verified_role = discord.utils.get(member.server.roles, name="Verified")
            r = requests.get('https://verify.eryn.io/api/user/{}'.format(member.id))
            output = r.json()
            if output['status'] == 'ok':
                verified = False
                try:
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
            elif output['error']:
                await client.send_message(msg.channel, "An unknown error occured.")
        await client.delete_message(msg)
    elif msg.content.lower() == '-verify' and msg.server.id in verify_server_ids:
        if not member.server.id == '303128948785545216':
            verified_role = discord.utils.get(member.server.roles, name="Verified")
        else:
            verified_role = discord.utils.get(member.server.roles, name="Customers")
        r = requests.get('https://verify.eryn.io/api/user/{}'.format(member.id))
        output = r.json()
        if output['status'] == 'ok':
            beaned = await client.get_bans(member.server)
            for user in beaned:
                br = requests.get('https://verify.eryn.io/api/user/{}'.format(user.id))
                boutput = br.json()
                if boutput['status'] == 'ok':
                    if boutput['robloxUsername'] == output['robloxUsername']:
                        await client.send_message(member, "You've been banned before with another Discord account - let's ban you with this one too!")
                        await client.ban(member)
                        await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), "**User verified and banned:** {} as {}".format(member.mention, output['robloxUsername']))
                        return
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
    elif msg.content.lower().startswith('-update') and server.id in verify_server_ids:
        if server.id == '323906250859479040':
            staff_role = discord.utils.get(server.roles, name="High Ranks")
        else:
            staff_role = discord.utils.get(server.roles, name="Staff")
        if staff_role in member.roles:
            if not member.server.id == '303128948785545216':
                verified_role = discord.utils.get(member.server.roles, name="Verified")
            else:
                verified_role = discord.utils.get(member.server.roles, name="Customers")
            user_id = msg.content[8:].strip("<@!>")
            user = discord.utils.get(server.members, id=user_id)
            if not user == None:
                r = requests.get('https://verify.eryn.io/api/user/{}'.format(user_id))
                output = r.json()
                if output['status'] == 'ok':
                    beaned = await client.get_bans(server)
                    for guy in beaned:
                        br = requests.get('https://verify.eryn.io/api/user/{}'.format(guy.id))
                        boutput = br.json()
                        if boutput['status'] == 'ok':
                            if boutput['robloxUsername'] == output['robloxUsername']:
                                await client.send_message(user, "You've been banned before with another Discord account - let's ban you with this one too!")
                                await client.ban(user)
                                await client.send_message(discord.utils.get(server.channels, name="verify-logs"), "**User verified and banned:** {} as {}".format(user.mention, output['robloxUsername']))
                                return
                    await client.add_roles(user, verified_role)
                    verified = False
                    try:
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
                elif output['error']:
                    await client.send_message(msg.channel, "An unknown error occured.")
            elif user == None:
                await client.send_message(msg.channel, "Could not find that user on this server. `{}`".format(user_id))
        else:
            if server.id == '323906250859479040':
                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** FlyBristol High Rank")
            else:
                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
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
                tosend = ":arrow_down: **INPUT:**\n```Python\n{}\n```\n:arrow_up: **OUTPUT:**\n```Python\nNope.\n```".format(code)
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
    elif msg.content.lower().startswith('-announce') and server.id != '323906250859479040':
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
    elif msg.content.lower().startswith('-shout') and server.id == '265962307299835905':
##        await client.send_message(msg.channel, "This command is disabled since **the API is broken.** Thank <@231658954831298560> for this.")
        hr_role = discord.utils.get(server.roles, name="High Rank")
        if hr_role in member.roles:
            if len(msg.content[6:]) > 255:
                await client.send_message(msg.channel, "The new shout is too long.")
                return
            try:
                data = {'key': 'lWQ5WoqS1o&Iot*CiuUwrk^7qXT%N3EhA^R^SuBCwaWlnivfQ@r662gnWBJPgc*hKszQxL5%Ch*F0*B2RH5^wRub@t4t*93%R1b3', 'message': msg.content[6:]}
                headers = {'content-type': 'application/json'}
                await session.post('http://lemonde-rank-bot.herokuapp.com/shout/1156950',
                                   data=data,
                                   headers=headers)
                shout = rob.get_group(1156950).get_shout
                embed = discord.Embed(colour=colour)
                embed.set_author(name=shout.author.username,url=shout.author.absolute_url,icon_url="https://www.roblox.com/Thumbs/Avatar.ashx?x=500&y=500&userId={}".format(shout.author.id))
                if shout == None:
                    embed.add_field(name="Latest shout",value="*Shout empty.*",inline=False)
                else:
                    embed.add_field(name="Latest shout",value=shout.content,inline=False)
                await client.send_message(msg.channel, "Posted shout:", embed=embed)
            except Exception as ex:
                await client.send_message(msg.channel, "Something went wrong! Internal error:\n```{}```".format(type(ex).__name__ + ': ' + str(ex)))
##            if not rob.verify_session():
##                try:
##                    rob.logout()
##                finally:
##                    rob.login("LeMondeRankUp", password)
##            try:
##                rob.get_group(1156950).post_shout(msg.content[6:])
##                await client.send_message(msg.channel, "Posted shout.")
##            except Exception as ex:
##                await client.send_message(msg.channel, "Something went wrong! Internal error:\n```{}```".format(type(ex).__name__ + ': ' + str(ex)))
        else:
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** LeMonde High Rank")
    elif msg.content.lower() == '-getshout' and (server.id == '265962307299835905' or server.id == '293115433182035970'):
        if server.id == '265962307299835905':
            shout = rob.get_group(1156950).get_shout
        elif server.id == '293115433182035970':
            shout = rob.get_group(3049155).get_shout
        if shout == None:
            await client.send_message(msg.channel, "The shout is empty.")
            return
        embed = discord.Embed(colour=colour)
        embed.set_author(name=shout.author.username,url=shout.author.absolute_url,icon_url="https://www.roblox.com/Thumbs/Avatar.ashx?x=500&y=500&userId={}".format(shout.author.id))
        embed.add_field(name="Latest shout",value=shout.content,inline=False)
        await client.send_message(msg.channel, embed=embed)
    elif msg.content.lower().startswith('-prune'):
        staff_role = discord.utils.get(server.roles, name="Staff")
        pruning = True
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
            except Exception:
                await client.send_message(msg.channel, "Could not delete messages. Did you enter a number?")
                pruning = False
    elif msg.content.lower().startswith('-userprune') and server.id != '323906250859479040':
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
            except Exception:
                await client.send_message(msg.channel, "Could not delete messages. Did you enter a number?")
    elif msg.content.lower().startswith('-kick ') and server.id != '323906250859479040':
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
                    if not reason == '0':
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
                            except discord.Forbidden():
                                await client.send_message(msg.channel, "Hmm...that's odd. I'm not allowed to kick that person. Maybe they have a higher role than me?")
                            except discord.NotFound():
                                await client.send_message(msg.channel, "Oh no, I've been 404'd! In all seriousness, I can't perform this action right now. No idea why.")
                            finally:
                                await client.send_message(msg.channel, "<@"+msg.author.id+"> kicked <@"+user_id+"> for reason `"+reason+"`.")
                    elif reason == '0':
                        await client.send_message(msg.channel, "You cancelled the action `Kick`.")
            except discord.Forbidden():
                await client.send_message(msg.channel, "Could not kick user. User is a higher or equal role to the bot.")
            except Exception and not discord.Forbidden():
                await client.send_message(msg.channel, "Could not kick user. An unknown error occured.")
    elif msg.content.lower().startswith('-bugreport') and server.id != '323906250859479040':
##        bl = open("blacklist.json", "r")
##        if msg.author.id not in blacklist:
        await client.send_message(owner, "<@252154198542647296> :bug: New bug report by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[10:] + "```")
        await client.send_message(msg.channel, "Your bug report has been submitted.")
##        elif msg.author.id in blacklist:
##        await client.send_message(msg.channel, "Bug reports and feedback are disabled as you are on the blacklist.")
##        bl.close()
    elif msg.content.lower().startswith('-feedback') and server.id != '323906250859479040':
##        bl = open("blacklist.json", "r")
##        if msg.author.id not in blacklist:
        await client.send_message(owner, "New feedback by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[9:] + "```")
        await client.send_message(msg.channel, "Your feedback has been submitted.")
##        elif msg.author.id in blacklist:
##            await client.send_message(msg.channel, "Bug reports and feedback are disabled as you are on the blacklist.")
##    elif msg.content.startswith('-blacklist'):
##        bl = open("blacklist.txt", "w")
##        if msg.author == discord.utils.get(server.members, id="252154198542647296"):
##            bl.write(msg.content[10:])
##            await client.send_message(msg.channel, "User with ID "+msg.content[10:]+" has been added to the blacklist.")
##        else:
##            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
##        bl.close()
##    elif msg.content.startswith('-warn'):
##        # mostly taken from https://github.com/916253/Kurisu/blob/master/addons/mod_warn.py
##        issuer = msg.author
##        if staff_role in issuer.roles:
##            try:
##                member = msg.mentions[0]
##            except IndexError:
##                await client.send_message(msg.channel, "Please mention a user.")
##                return
##            for i in msg.raw_mentions:
##                count = count + len(i)
##            reason = 
##            if staff_role in member.roles:
##                await client.send_message(msg.channel, "You can't warn another high rank!")
##                return
##            with open("data/warns.json", "r") as f:
##                warns = json.load(f)
##            if member.id not in warns:
##                warns[member.id] = {"warns": {}}
##            warns[member.id]["name"] = member.name + "#" + member.discriminator
##            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
##            warns[member.id]["warns"][len(warns[member.id]["warns"]) + 1] = {"issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp}
##            with open("data/warns.json", "w") as f:
##                json.dump(warns, f)
##            msg = "You were warned on {}.".format(server.name)
##            if reason != "":
##                # much \n
##                msg += " The given reason is: " + reason
##            msg += "\n\nPlease read the rules in #rules. This is warn #{}.".format(len(warns[member.id]["warns"]))
##            warn_count = len(warns[member.id]["warns"])
##            if warn_count == 2:
##                msg += " __The next warn will automatically kick.__"
##            if warn_count == 3:
##                msg += "\n\nYou were kicked because of this warning. You can join again right away. Two more warnings will result in an automatic ban."
##            if warn_count == 4:
##                msg += "\n\nYou were kicked because of this warning. This is your final warning. You can join again, but **one more warn will result in a ban**."
##            if warn_count == 5:
##                msg += "\n\nYou were automatically banned due to five warnings."
##            try:
##                await client.send_message(member, msg)
##            except discord.Forbidden:
##                pass
##            if warn_count == 3 or warn_count == 4:
##                await client.kick(member)
##            if warn_count >= 5: # stuff happens sometimes
##                await client.ban(member)
##            await client.send_message(msg.channel, "{} warned. User has {} warning(s)".format(member.mention, len(warns[member.id]["warns"])))
##            msg = "⚠️ **Warned**: {} warned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, len(warns[member.id]["warns"]), member.name, member.discriminator)
##            if reason != "":
##                msg += "\n✏️ __Reason__: " + reason
##            await client.send_message(logs, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `!warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))            
##        else:
##            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
##            
    elif msg.content.lower().startswith('-game'):
        if msg.author == discord.utils.get(server.members, id="252154198542647296"):
            game = discord.Game(name=msg.content[5:],url="https://www.roblox.com/",type=1)
            await client.change_presence(game=game,afk=False)
        elif server.id != '323906250859479040':
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower().startswith('-leaveserver'):
        if msg.author == owner:
            mserver = discord.utils.get(client.servers, id=msg.content[12:])
            try:
                await client.leave_server(mserver)
                await client.send_message(msg.channel, "Left server `{}`".format(mserver.name))
            except Exception:
                await client.send_message(msg.channel, "Error: not in server.")
        elif server.id != '323906250859479040':
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
##    elif msg.content.lower().startswith('-abuse'):
##        server2 = discord.utils.get(client.servers, id="323127945713549322")
##        staff_chnl = discord.utils.get(server2.channels, id="323127945713549322")
##        await client.send_message(staff_chnl, "New abuse report by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[7:] + "```")
##        await client.send_message(msg.channel, "Your abuse report has been submitted.")
##        await client.send_message(msg.channel, "This command is currently disabled until ")
    elif msg.content.lower() == '-membercount' and server.id != '323906250859479040':
        await client.send_message(msg.channel, "The current member count is "+str(object=msg.server.member_count)+" members.")
##    elif msg.content.startswith('-banhammer'):
##        staff_role = discord.utils.get(server.roles, name="Staff")
##        print('Attempting to ban user with ID '+msg.content[10:])
##        to_ban = discord.utils.get(server.members, id=msg.content[10:])
##        if not to_ban == None:
##            if staff_role not in msg.author.roles:
##                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** JZ Studios Staff")
##            elif staff_role in msg.author.roles:
##                await client.send_message(msg.channel, "The ban hammer (<:ban_hammer:301083705634455552>) is coming down on <@"+to_ban.id+">! Look out!")
##                asyncio.sleep(5)
##                await client.send_message(msg.channel, "The ban hammer (<:ban_hammer:301083705634455552>) has swung on <@"+to_ban.id+">.")
##                await client.ban(to_ban, 7)
##                print('Ban success for user with ID '+msg.content[10:])
##        elif to_ban == None:
##            print('Ban failed for user with ID '+msg.content[10:])
##            await client.send_message(msg.channel, "Could not find member with that ID. Did you type in the right ID? Is the user in the server?")
    elif msg.content.lower() == '-cmds':
        if server.id == '323906250859479040':
            staff_role = discord.utils.get(server.roles, name="High Ranks")
        else:
            staff_role = discord.utils.get(server.roles, name="Staff")
        embed = discord.Embed(title="Commands", description="Commands currently available for use (for the server you ran this from):",colour=colour)
        if server.id != '323906250859479040':
            embed.add_field(name="-membercount",value="Gives you the current member count of the server.",inline=False)
            embed.add_field(name="-feedback text",value="Sends your feedback to the bot owner.",inline=False)
            embed.add_field(name="-bugreport text",value="Sends a bug report to the bot owner.",inline=False)
            if staff_role in member.roles:
                embed.add_field(name="-prune number",value="Prunes any amount of messages (up to 100) that you specify.",inline=False)
                embed.add_field(name="-userprune number",value="Prunes any amount of messages from a specific user (up to 100) that you specify.",inline=False)
                embed.add_field(name="-announce text",value="Announces in #announcements.",inline=False)
                embed.add_field(name="-kick @mention",value="Kicks a user with a specified reason.",inline=False)
##        if staff_role in member.roles:
##            embed.add_field(name="-lock",value="Locks server to staff only.",inline=False)
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
        await client.send_message(msg.author, "https://discord.gg/d8BWzmW")
        if msg.channel.type != discord.ChannelType.private:
            await client.send_message(msg.channel, "<@{}>, check your DMs!".format(msg.author.id))
    elif msg.content.lower().startswith('-wblacklist'):
        if msg.author == owner:
            word = msg.content[11:]
            with open("data/blacklist.txt", "a") as f:
                f.write(word)
            blacklist.append(word)
            await client.delete_message(msg)
            await client.send_message(owner, "Added the following word to the blacklist: `{}`".format(word))
        elif server.id != '323906250859479040':
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.lower() == '-restart':
        if msg.author == owner:
            await client.send_message(msg.channel, "This will restart the bot and update it to the latest version. Continue? `y/n`")
            def check(msg2):
                return msg2.author == msg.author and (msg2.content.lower() == 'y' or msg2.content.lower() == 'n')
            msg2 = await client.wait_for_message(timeout=None,check=check)
            if msg2.content.lower() == 'y':
                await client.send_message(msg.channel, ":wave:")
                sys.exit("Restarting bot - the other fail-safe script should pick this up")
        elif server.id != '323906250859479040':
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
                        "token": dbtoken,
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
        elif server.id != '323906250859479040':
            await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
##    elif msg.content.lower() == '-lock':
##        if server.id != '323906250859479040':
##            staff_role = discord.utils.get(server.roles, name="Staff")
##        else:
##            staff_role = discord.utils.get(server.roles, name="High Ranks")
##        if staff_role in member.roles:
##            channel = msg.channel
##            if not member.server.id == '303128948785545216':
##                verified_role = discord.utils.get(member.server.roles, name="Verified")
##            else:
##                verified_role = discord.utils.get(member.server.roles, name="Customers")
##            if verified_role != None:
##                staff_override = channel.overwrites_for(staff_role)
##                verified_override = channel.overwrites_for(verified_role)
##                if staff_override.send_messages != True:
##                    staff_override.send_messages = True
##                if verified_override.read_messages != True:
##                    await client.send_message(msg.channel, "Error: Can only lock public channels.")
##                    return
##                verified_override.send_messages = False
##                if staff_role.name == 'High Ranks':
##                    await client.send_message(msg.channel, ":lock: Channel locked. Only high ranks may talk.")
##                else:
##                    await client.send_message(msg.channel, ":lock: Channel locked. Only staff can talk.")
##            else:
##                staff_override = channel.overwrites_for(staff_role)
##                all_override = channel.overwrites_for(server.default_role)
##                if staff_override.send_messages != True:
##                    staff_override.send_messages = True
##                if all_override.read_messages != True:
##                    await client.send_message(msg.channel, "Error: Can only lock public channels.")
##                    return
##                all_override.send_messages = False
##                await client.send_message(msg.channel, ":lock: Channel locked. Only staff can talk.")
##        else:
##            if staff_role.name == 'High Ranks':
##                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** FlyBristol High Rank")
##            else:
##                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
##    elif msg.content.lower() == '-unlock':
##        if server.id != '323906250859479040':
##            staff_role = discord.utils.get(server.roles, name="Staff")
##        else:
##            staff_role = discord.utils.get(server.roles, name="High Ranks")
##        if staff_role in member.roles:
##            channel = msg.channel
##            if not member.server.id == '303128948785545216':
##                verified_role = discord.utils.get(member.server.roles, name="Verified")
##            else:
##                verified_role = discord.utils.get(member.server.roles, name="Customers")
##            if verified_role != None:
##                verified_override = channel.overwrites_for(verified_role)
##                if verified_override.send_messages != True:
##                    verified_override.send_messages = True
##                    await client.send_message(msg.channel, ":unlock: Channel unlocked. Everybody can now talk.")
##                else:
##                    await client.send_message(msg.channel, "Error: Channel is not locked.")
##            else:
##                all_override = channel.overwrites_for(server.default_role)
##                if all_override.send_messages == False:
##                    all_override.send_messages = True
##                    await client.send_message(msg.channel, ":unlock: Channel unlocked. Everybody can now talk.")
##                else:
##                    await client.send_message(msg.channel, "Error: Channel is not locked.")
##        else:
##            if staff_role.name == 'High Ranks':
##                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** FlyBristol High Rank")
##            else:
##                await client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Server Staff")
    if msg.channel.type != discord.ChannelType.private:
        if server.id == '323147682686304256': # apple rail
            people = [discord.utils.get(server.members, id="227451765618900992"), owner] # wee, me
            roles = [discord.utils.get(server.roles, name="High Rank"), discord.utils.get(server.roles, name="Staff")]
            for person in people:
                if person in msg.mentions:
                    if not msg.author.bot and not member in people:
                        await client.kick(msg.author)
                        await client.send_message(msg.channel, "<@"+msg.author.id+"> was kicked for pinging "+person.display_name+". Don't ping anybody on the list, or you'll be kicked too!")
            for role in roles:
                if role in msg.role_mentions:
                    if not msg.author.bot:
                        await client.kick(msg.author)
                        await client.send_message(msg.channel, "<@"+msg.author.id+"> was kicked for pinging the {} role. Don't ping anybody on the list, or you'll be kicked too!".format(role.name))
        elif msg.channel.id != '343121616193978369' and server.id != '323906250859479040':
            for i in blacklist:
                if i in msg.content.lower():
                    if i == 'discord.gg/':
                        staff_role = discord.utils.get(server.roles, name="Staff")
                        if not staff_role in member.roles:
                            await client.delete_message(msg)
                            await client.send_message(msg.channel, "<@"+msg.author.id+">, no advertising! :no_entry:")
                    else:
                        await client.delete_message(msg)
                        await client.send_message(msg.channel, "<@"+msg.author.id+">, one of the words or phrases in your message was on the blacklist! For blacklist-free chat, go into your DMs. :no_entry:")

@client.event
async def on_member_join(member):
    if member.server.id in verify_server_ids:
        if not member.server.id == '303128948785545216':
            verified_role = discord.utils.get(member.server.roles, name="Verified")
        else:
            verified_role = discord.utils.get(member.server.roles, name="Customers")
        r = requests.get('https://verify.eryn.io/api/user/{}'.format(member.id))
        output = r.json()
        if member.server.id == '303128948785545216':
            if output['status'] == 'ok':
                if not member.avatar_url == '':
                    embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.avatar_url)
                    embed.set_image(url=member.avatar_url)
                else:
                    embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.default_avatar_url)
                    embed.set_image(url=member.default_avatar_url)
                embed.add_field(name="Member Joined",value="{}#{}, with ROBLOX username {}".format(member.name, member.discriminator, output['robloxUsername']),inline=False)
                await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), embed=embed)
            else:
                if not msg.author.avatar_url == '':
                    embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.avatar_url)
                    embed.set_image(url=member.avatar_url)
                else:
                    embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.default_avatar_url)
                    embed.set_image(url=member.default_avatar_url)
                embed.add_field(name="Member Joined",value="{}#{}, not verified yet".format(member.name, member.discriminator),inline=False)
                await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), embed=embed)
        if output['status'] == 'ok':
            beaned = await client.get_bans(member.server)
            for user in beaned:
                br = requests.get('https://verify.eryn.io/api/user/{}'.format(user.id))
                boutput = br.json()
                if boutput['status'] == 'ok':
                    if boutput['robloxUsername'] == output['robloxUsername']:
                        await client.send_message(member, "You've been banned before with another Discord account - let's ban you with this one too!")
                        await client.ban(member)
                        await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), "**User banned:** {} as {}".format(member.mention, output['robloxUsername']))
                        return
            await client.send_message(member, "Hey! We've found your username to be {}. For security reasons, you'll need to verify your phone number with Discord if you haven't already and type -verify into <#{}>.".format(output['robloxUsername'], discord.utils.get(member.server.channels, name="verify").id))

@client.event
async def on_message_edit(bmsg, amsg):
    if amsg == None or bmsg == None:
        print("wait wut")
        return
    if bmsg.channel.id != '343121616193978369' and bmsg.server.id != '323906250859479040':
        for i in blacklist:
            if i in amsg.content.lower():
                if i == 'discord.gg/':
                    staff_role = discord.utils.get(server.roles, name="Staff")
                    if not staff_role in member.roles:
                        await client.delete_message(amsg)
                        await client.send_message(amsg.channel, "<@"+amsg.author.id+">, no advertising! :no_entry:")
                else:
                    await client.delete_message(amsg)
                    await client.send_message(amsg.channel, "<@"+amsg.author.id+">, one of the words or phrases in your message was on the blacklist! For blacklist-free chat, go into your DMs. :no_entry:")

@client.event
async def on_member_remove(member):
    if member.server.id == '303128948785545216':
        r = requests.get('https://verify.eryn.io/api/user/{}'.format(member.id))
        output = r.json()
        if output['status'] == 'ok':
            if not msg.author.avatar_url == '':
                embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.avatar_url)
                embed.set_image(url=member.avatar_url)
            else:
                embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.default_avatar_url)
                embed.set_image(url=member.default_avatar_url)
            embed.add_field(name="Member Left",value="{}#{}, with ROBLOX username {}".format(member.name, member.discriminator, output['robloxUsername']),inline=False)
            await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), embed=embed)
        else:
            if not msg.author.avatar_url == '':
                embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.avatar_url)
                embed.set_image(url=member.avatar_url)
            else:
                embed.set_author(name="{}#{}".format(member.name, member.discriminator),url=embed.Empty,icon_url=member.default_avatar_url)
                embed.set_image(url=member.default_avatar_url)
            embed.add_field(name="Member Left",value="{}#{}, not verified".format(member.name, member.discriminator),inline=False)
            await client.send_message(discord.utils.get(member.server.channels, name="verify-logs"), embed=embed)

@client.event
async def on_server_join(server):
    os.mkdir("data/{}".format(server.id))

@client.event
async def on_server_leave(server):
    os.remove("data/{}/*.*".format(server.id))
    os.rmdir("data/{}".format(server.id))

@client.event
async def on_member_ban(member):
    if member.id == '157558469354979328' and server.id == '265962307299835905':
        await client.unban(member.server, member)
        await client.send_message(member, "http://discord.gg/qGshqNS")

print('Starting client with token ' + token)
client.run(token)
