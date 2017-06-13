import discord
import asyncio
import os
import json
import time
pruning = False
blacklist = ['porn', 'discord.gg/', 'naked', 'dick', 'pussy', 'sex', 'penis', 'vagina', 'fuck', 'shit', 'intercourse', 'bitch', 'cock']

### mostly taken from https://github.com/916253/Kurisu/blob/master/run.py
##dir_path = os.path.dirname(os.path.realpath(__file__))
##os.chdir(dir_path)
##
##os.makedirs("data", exist_ok=True)
### create warns.json if it doesn't exist
##if not os.path.isfile("data/warns.json"):
##    with open("data/warns.json", "w") as f:
##        f.write("{}")
##
### create blacklist.json if it doesn't exist
##if not os.path.isfile("data/blacklist.json"):
##    with open("data/blacklist.json", "w") as f:
##        f.write("{}")

with open("token.txt", "r") as tknobj:
    token = tknobj.read()
client = discord.Client()
print('Loaded discord.py client')

@client.event
@asyncio.coroutine
def on_ready():
    game = discord.Game(name="-help | LeMonde Bot",url="https://www.roblox.com/",type=0)
    yield from client.change_presence(game=game,afk=False)
    print('Logged in')

@client.event
@asyncio.coroutine
def on_message(msg):
    if not msg.channel.type == discord.ChannelType.text:
        if not msg.content.lower() == '-help' and not msg.content.lower() == '-cmds':
            yield from client.send_message(msg.channel, "Sorry, but commands can only be used in a server.")
            return
    server = msg.server
    
    # adding some colour
    colour = discord.Colour(value=16290304)

    # people
    owner = discord.utils.get(server.members, id="252154198542647296")
    dan = discord.utils.get(server.members, id="253246604377718784")
    member = msg.author

    # roles
    staff_role = discord.utils.get(server.roles, name="Staff")
    staff_role = discord.utils.get(server.roles, name="High Ranks || Manager+")
    lmalive_role = discord.utils.get(server.roles, name="LeMondeLive Staff")

    # channels
    announcements = discord.utils.get(server.channels, id="323133480605188096")
    logs = discord.utils.get(server.channels, id="312334072607145995")
    if msg.content.startswith('-say'):
        if msg.author == owner:
            yield from client.send_message(msg.channel, msg.content[5:])
            yield from client.delete_message(msg)
        else:
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.startswith('-eval '):
        if msg.author == owner:
            exec(msg.content[6:])
        else:
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.startswith('-announce'):
        if member == owner or staff_role in member.roles or lmalive_role in member.roles:
            client.send_typing(announcements)
            embed = discord.Embed(colour=colour)
            if not msg.author.avatar_url == '':
                embed.set_author(name=member.name+"#"+member.discriminator,url=embed.Empty,icon_url=member.avatar_url)
            else:
                embed.set_author(name=member.name+"#"+member.discriminator,url=embed.Empty,icon_url=member.default_avatar_url)
            embed.add_field(name="Announcement",value=msg.content[9:],inline=False)
            yield from client.send_message(announcements, embed=embed)
        else:
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner, LeMonde High Rank or Founder")
    elif msg.content.startswith('-prune'):
        pruning = True
        if staff_role not in member.roles:
            pruning = False
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** LeMonde Staff")
        elif staff_role in member.roles:
            try:
                if int(msg.content[6:]) > 100:
                    yield from client.send_message(msg.channel, "Could not delete messages. Number is higher than 100.")
                else:
                    yield from client.purge_from(msg.channel,limit=int(msg.content[6:])+1,check=None)
                    yield from client.send_message(msg.channel, "Pruned" + msg.content[6:] + " messages from <#"+msg.channel.id+">.")
                    pruning = False
            except Exception:
                yield from client.send_message(msg.channel, "Could not delete messages. Did you enter a number?")
                pruning = False
    elif msg.content.startswith('-userprune'):
        if staff_role not in member.roles:
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** LeMonde Staff")
        elif staff_role in member.roles:
            try:
                if int(msg.content[10:]) > 100:
                    yield from client.send_message(msg.channel, "Could not delete messages. Number is higher than 100.")
                else:
                    def check(msg2):
                        if msg2.author == msg.author:
                            return msg2.content.startswith('<@') and msg2.content.endswith('>') or msg2.content == '0'
                        else:
                            client.send_message(msg.channel, "Not a valid user. Please mention the user you would like to delete messages from, or type 0 to cancel.")
                            return False
                    yield from client.send_message(msg.channel, "Please mention the user you would like to delete messages from, or type 0 to cancel.")
                    msg2 = yield from client.wait_for_message(timeout=None,check=check)
                    user_id = msg2.content.strip('<@>')
                    if user_id.isnumeric() and not user_id == '0' and not user_id == '252154198542647296':
                        def check2(msg3):
                            return msg3.author.id == user_id
                        yield from client.purge_from(msg.channel,limit=int(msg.content[10:]),check=check2)
                        yield from client.send_message(msg.channel, "Pruned" + msg.content[10:] + " messages from <#"+msg.channel.id+">.")
                    elif user_id == '0':
                        yield from client.send_message(msg.channel, "You cancelled the purge.")
                    elif user_id == '252154198542647296':
                        yield from client.send_message(msg.channel, "<@"+msg.author.id+">, you know you can't trick me. Don't try and deleting the bot owner's messages.")
                    else:
                        yield from client.send_message(msg.channel, "Mention is not a user. Please rerun the command.")
            except Exception:
                yield from client.send_message(msg.channel, "Could not delete messages. Did you enter a number?")
    elif msg.content.startswith('-kick'):
        if staff_role not in member.roles:
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** LeMonde High Rank")
        elif staff_role in member.roles:
            try:
                user_id = msg.content[7:].strip('<@>')
                if not user_id.isnumeric():
                    yield from client.send_message(msg.channel, "Could not kick user. Did you mention a role or channel? `"+user_id+"`")
                else:
                    def check(msg2):
                        return msg2.author == msg.author
                    yield from client.send_message(msg.channel, "Please state the reason for kicking, or type 0 to cancel.")
                    msg2 = yield from client.wait_for_message(timeout=None,check=check)
                    reason = msg2.content
                    if not reason == '0':
                        naughty = discord.utils.get(server.members, id=user_id)
                        if naughty == None:
                            yield from client.send_message(msg.channel, "Could not kick user. User is not in this server.")
                        elif staff_role in naughty.roles or naughty.id == '312929842712805376':
                            yield from client.send_message(msg.channel, "Could not kick user. User is a higher or equal role to the bot.")
                        else:
                            yield from client.send_message(msg.channel, "<@"+msg.author.id+"> kicked <@"+user_id+"> for reason `"+reason+"`.")
                            yield from client.send_message(naughty, "You have been kicked by <@"+msg.author.id+"> for the following reason: `"+reason+"`")
                            yield from client.kick(naughty)
                    elif reason == '0':
                        yield from client.send_message(msg.channel, "You cancelled the action `Kick`.")
            except discord.Forbidden():
                yield from client.send_message(msg.channel, "Could not kick user. User is a higher or equal role to the bot.")
            except Exception and not discord.Forbidden():
                yield from client.send_message(msg.channel, "Could not kick user. An unknown error occured.")
    elif msg.content.startswith('-blamedan'):
        yield from client.send_message(msg.channel, "This command has been discontinued after Dan **finally** removed the Staff Member role.")
    elif msg.content.startswith('-bugreport'):
##        bl = open("blacklist.json", "r")
##        if msg.author.id not in blacklist:
        yield from client.send_message(owner, "<@252154198542647296> :bug: New bug report by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[10:] + "```")
        yield from client.send_message(msg.channel, "Your bug report has been submitted.")
##        elif msg.author.id in blacklist:
        yield from client.send_message(msg.channel, "Bug reports and feedback are disabled as you are on the blacklist.")
##        bl.close()
    elif msg.content.startswith('-feedback'):
##        bl = open("blacklist.json", "r")
##        if msg.author.id not in blacklist:
        yield from client.send_message(owner, "New feedback by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[9:] + "```")
        yield from client.send_message(msg.channel, "Your feedback has been submitted.")
##        elif msg.author.id in blacklist:
##            yield from client.send_message(msg.channel, "Bug reports and feedback are disabled as you are on the blacklist.")
##    elif msg.content.startswith('-blacklist'):
##        bl = open("blacklist.txt", "w")
##        if msg.author == owner:
##            bl.write(msg.content[10:])
##            yield from client.send_message(msg.channel, "User with ID "+msg.content[10:]+" has been added to the blacklist.")
##        else:
##            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
##        bl.close()
##    elif msg.content.startswith('-warn'):
##        # mostly taken from https://github.com/916253/Kurisu/blob/master/addons/mod_warn.py
##        issuer = msg.author
##        if staff_role in issuer.roles:
##            try:
##                member = msg.mentions[0]
##            except IndexError:
##                yield from client.send_message(msg.channel, "Please mention a user.")
##                return
##            for i in msg.raw_mentions:
##                count = count + len(i)
##            reason = 
##            if staff_role in member.roles:
##                yield from client.send_message(msg.channel, "You can't warn another high rank!")
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
##                yield from client.send_message(member, msg)
##            except discord.Forbidden:
##                pass
##            if warn_count == 3 or warn_count == 4:
##                yield from client.kick(member)
##            if warn_count >= 5: # stuff happens sometimes
##                yield from client.ban(member)
##            yield from client.send_message(msg.channel, "{} warned. User has {} warning(s)".format(member.mention, len(warns[member.id]["warns"])))
##            msg = "⚠️ **Warned**: {} warned {} (warn #{}) | {}#{}".format(issuer.mention, member.mention, len(warns[member.id]["warns"]), member.name, member.discriminator)
##            if reason != "":
##                msg += "\n✏️ __Reason__: " + reason
##            yield from client.send_message(logs, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `!warn <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))            
##        else:
##            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** LeMonde High Rank")
##            
    elif msg.content.startswith('-game'):
        if msg.author == owner:
            game = discord.Game(name=msg.content[5:],url="https://www.roblox.com/",type=0)
            yield from client.change_presence(game=game,afk=False)
        else:
            yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** Bot Owner")
    elif msg.content.startswith('-abuse'):
        server2 = discord.utils.get(client.servers, id="323127945713549322")
        staff_chnl = discord.utils.get(server2.channels, id="323127945713549322")
        yield from client.send_message(staff_chnl, "New abuse report by " + msg.author.name + "#"+msg.author.discriminator + " ("+msg.author.id+"): ```" + msg.content[7:] + "```")
        yield from client.send_message(msg.channel, "Your abuse report has been submitted.")
    elif msg.content == '-membercount':
        yield from client.send_message(msg.channel, "The current member count is "+str(object=msg.server.member_count)+" members.")
##    elif msg.content.startswith('-banhammer'):
##        staff_role = discord.utils.get(server.roles, name="Staff")
##        print('Attempting to ban user with ID '+msg.content[10:])
##        to_ban = discord.utils.get(server.members, id=msg.content[10:])
##        if not to_ban == None:
##            if staff_role not in msg.author.roles:
##                yield from client.send_message(msg.channel, "You do not have the permissions required to run this command. **Permissions required:** JZ Studios Staff")
##            elif staff_role in msg.author.roles:
##                yield from client.send_message(msg.channel, "The ban hammer (<:ban_hammer:301083705634455552>) is coming down on <@"+to_ban.id+">! Look out!")
##                asyncio.sleep(5)
##                yield from client.send_message(msg.channel, "The ban hammer (<:ban_hammer:301083705634455552>) has swung on <@"+to_ban.id+">.")
##                yield from client.ban(to_ban, 7)
##                print('Ban success for user with ID '+msg.content[10:])
##        elif to_ban == None:
##            print('Ban failed for user with ID '+msg.content[10:])
##            yield from client.send_message(msg.channel, "Could not find member with that ID. Did you type in the right ID? Is the user in the server?")
    elif msg.content == '-cmds':
        embed = discord.Embed(title="Commands", description="Commands currently available for this bot:",colour=colour)
        embed.add_field(name="-membercount",value="Gives you the current member count of the server.",inline=False)
        embed.add_field(name="-abuse",value="Sends an abuse report to staff.",inline=False)
        embed.add_field(name="-feedback",value="Sends your feedback to the bot owner.",inline=False)
        embed.add_field(name="-bugreport",value="Sends a bug report to the bot owner.",inline=False)
        embed.add_field(name="-prune",value="Only usable by staff. Prunes any amount of messages (up to 100) that you specify.",inline=False)
        embed.add_field(name="-userprune",value="Only usable by staff. Prunes any amount of messages from a specific user (up to 100) that you specify.",inline=False)
        embed.add_field(name="-announce",value="Only usable by staff. Announces in #information.",inline=False)
        embed.add_field(name="-kick",value="Only usable by staff. Kicks a user with a specified reason.",inline=False)
        yield from client.send_message(msg.author, embed=embed)
        yield from client.send_message(msg.channel, "<@"+msg.author.id+">, check your DMs!")
    elif msg.content == '-help':
        embed = discord.Embed(title="LeMonde Airlines Bot", description="Created by Ali365Dash#5036, use -cmds for commands",colour=colour)
        embed.add_field(name="Suggestions & Bugs",value="Want to give suggestions? Suggest with -feedback! Alternatively, bugs should be reported with -bugreport.",inline=False)
        yield from client.send_message(msg.channel, embed=embed)
    elif msg.channel.id == '313263471762604042' and not msg.author.id == "298796807323123712":
        yield from client.delete_message(msg)
    else:
        for i in blacklist:
            if i in msg.content.lower():
                if i == 'discord.gg/':
                    if staff_role in member.roles:
                        yield from client.delete_message(msg)
                        yield from client.send_message(msg.channel, "<@"+msg.author.id+">, no advertising! :no_entry:")
                else:
                    yield from client.delete_message(msg)
                    yield from client.send_message(msg.channel, "<@"+msg.author.id+">, one of the words or phrases in your message was on the blacklist! For blacklist-free chat, go into your DMs. :no_entry:")

print('Starting client with token ' + token)
client.run(token)
