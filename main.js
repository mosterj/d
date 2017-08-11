var fs = require('fs'),
var obj;
var token;
var blacklist;
const ROBLOX = require('roblox-js');
const Eris = require('eris');
fs.readFile('data/settings.json', 'utf8', function (err, data) {
    if (err) throw err;
    obj = JSON.parse(data);
    token = obj[0].token
    blacklist = obj[0].blacklist
});
var bot = new Eris(token)

bot.on('ready', () => {
    console.log('Logged in')
});

bot.on('messageCreate', (msg) => {

});