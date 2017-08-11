var fs = require('fs'),
var obj;
var token;
var blacklist;
var colour = 0x14754329;
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
/*     if (msg.content.toLowerCase().startsWith('-')) {
        
    } */
});

bot.connect();