// #!/usr/bin/env nodejs
// 
// var http = require('http');
// http.createServer(function (req, res) {
// 	  res.writeHead(200, {'Content-Type': 'text/plain'});
// 	  res.end('Hello World\n');
// }).listen(8080, 'localhost');
// console.log('Server running at http://localhost:8080/');

var express = require('express'),
	app = express(),
	port = 8080;

require('./on')(app);
require('./off')(app);

app.listen(port);
console.log('Server started.');

