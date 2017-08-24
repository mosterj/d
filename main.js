var settings = require('./data/settings.json');
var obj;
var token;
var blacklist;
var colour = 0x14754329;
var fs = require('fs');
var request = require('request');
const ROBLOX = require('roblox-js');
const Eris = require('eris');
fs.readFile('data/settings.json', 'utf8', function (err, data) {
    if (err) throw err;
    obj = JSON.parse(data);
    token = obj[0].token
    blacklist = obj[0].blacklist
    verify_servers = obj[0].verify_servers
});
var bot = new Eris(token)

bot.on('ready', () => {
    console.log('Logged in')
});

bot.on('messageCreate', (msg) => {
    if (!msg.channel.guild && !msg.author.bot) {
        if (msg.content.toLowerCase().startswith('-')) {
            bot.createMessage(msg.author.getDMChannel(), "Commands must be used in a server.")
        }
        bot.createMessage(bot.getDMChannel(252154198542647296), "**New message sent to bot by "+msg.author.username+"#"+msg.author.discriminator+" ("+msg.author.id+"):** " + msg.content)

    }
    else if (msg.channel.name == 'verify' && !msg.author.bot) {
        if (msg.content.toLowerCase() === '-verify' && verify_servers.indexOf(msg.guild.id) !== -1) {
            var verified_role;
            var defined;
            function find(coll) {
                if (coll.name == defined) {
                    return true;
                }
            }
            if (msg.guild.id === '303128948785545216') {
                defined = 'Customers'
                verified_role = msg.guild.roles.find(find)
            } else {
                defined = 'Verified'
                verified_role = msg.guild.roles.find(find)
            };
            request("https://verify.eryn.io/api/user/"+msg.author.id, function (err, resp, body) {
                var parsed = JSON.parse(body);
                if (parsed[0].status === 'ok') {
                    try {
                        msg.channel.guild.editMember(msg.member.id, options.nick = parsed[0].robloxUsername, "User verification")
                    }
                    catch(err) {
                        msg.channel.createMessage("Oops! I don't have the permissions to give you your nickname. Set your nickname as `"+parsed[0].robloxUsername+"` please. Thanks!")
                    }
                    finally {
                        var roles = msg.member.roles
                        for (var i = 0; i < roles.length; i++) {
                            roles[i] = roles[i].id;
                        }
                        roles.push(verified_role.id);
                        msg.channel.guild.editMember(msg.member.id, options.roles, roles, "User verification");
                        msg.author.getDMChannel().createMessage("Hi, "+parsed[0].robloxUsername+"! We've given you access to the rest of the server. Enjoy your stay!")
                    };
                } else if (parsed[0].status === 'error' && parsed[0].errorCode == 404) {
                    msg.channel.createMessage("You haven't verified! Go to https://verify.eryn.io to get yourself verified!");
                } else {
                    msg.channel.createMessage("Oops! I've stumbled upon an API error I don't know of. Contact my owner!");
                }
            });
        };
    };
});

bot.connect();