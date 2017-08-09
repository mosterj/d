var fs = require('fs'),
var obj;
var token;
fs.readFile('data/settings.json', 'utf8', function (err, data) {
    if (err) throw err;
    obj = JSON.parse(data);
    token = obj[0].token
});
var bot = new Eris(token)