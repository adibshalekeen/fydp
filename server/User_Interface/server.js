//Requires
const express = require('express');
const app = express();
const path = require('path');
const chalk = require('chalk');
const morgan = require('morgan');
const http = require('http');

app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

//Static Routes
app.use('/dist', express.static(path.join(__dirname, 'dist')));
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.use('/src', express.static(path.join(__dirname, 'src')));
app.use('/node_modules', express.static(path.join(__dirname, 'node_modules')));

app.use(morgan('dev')) // logging

var hub_ip = "8.8.8.8";

/*GET REQUESTS*/
const ps = require('python-shell');
app.get('/getDevices', get_devices);
app.get('/myIp', get_my_ip);
app.post('/sendMessage', send_message);
app.post('/endPointMessage', end_point_message);
app.post('/getMappings', get_mappings);
app.post('/saveMappings', save_mappings);
app.post('/sendMeMessage', send_me_message);
app.post('/broadcastRx', receive_hub_ip);

/*START GET REQUESTS*/
function get_devices(req, res) {
  // When this get request is triggered, this python script will execute
  // This function gets the ddevices on the network
  ps.PythonShell.run('./dist/get_devices_script.py', null, function(err, resp){
    if(err) throw err;
    res.send(resp);
  })
}

function get_my_ip(req, res){
  let options = {
    args: ["get_ip"]
  };
  ps.PythonShell.run('./dist/IpDeviceDiscovery.py', options, function(err, resp){
    if(err) throw err;
    res.send(resp);
  })
}
/*END GET REQUESTS*/

/*START POST REQUESTS*/
function send_message(req, res) {
  var message = "";
  req.on('data', function (data) {
      message += data;
  });
  req.on('end', function () {
    var options = {
      host: 'localhost',
      port: '2081',
      path: '/myIp'
    };
    var req = http.get(options, function(getResponse) {
      // Buffer the body entirely for processing as a whole.
      var ip_self = "";
      getResponse.on('data', function(chunk) {
        ip_self += chunk;
      }).on('end', function() {
        var self_ip = ip_self.substr(2, ip_self.length - 4);
        // Received message from sender
        let options = {
          args: ['send_message', "act", self_ip + "|" + message]
        };
        // Run mapping check to see if the incoming message is valid and maps to a destination
        // and check what devices to send to
        ps.PythonShell.run('./dist/MappingInterfaceCtrl.py', options, function(err, resp){
          if(err) throw err;
          // send response to free the client
          res.send("Routed to: " + resp);
          if(resp)
          {
            var routed_msg = resp.toString().split(',');

            for(var i = 0; i < routed_msg.length; i++)
            {
              var dest_ip = routed_msg[i].split('|')[0];
              var dest_act = routed_msg[i].split('|')[1];

              // host is the destination of the message and port number is set to our default
              // If we are to send to a third party manufacturer we will have pre-defined settings
              // and will set them here
              var post_options = {
                  host: dest_ip,//dest_ip
                  port: '2081',
                  path: '/endPointMessage',
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/x-www-form-urlencoded',
                      'Content-Length': dest_act.length
                  }
              };
              // Set up the request
              var post_req = http.request(post_options, function(res) {
                  res.setEncoding('utf8');
                  res.on('data', function (chunk) {
                      console.log('Response: ' + chunk);
                  });
              });
              // post the data
              post_req.write(dest_act);
              post_req.end();
            }
          }
        })
      });
    });
  });
}

function end_point_message(req, res) {
  var message = "";
  req.on('data', function (data) {
      message += data;
  });
  req.on('end', function () {
    console.log(message);
    res.send("OK");
  });
}

function get_mappings(req, res) {
  var name = "";
  req.on('data', function (data) {
      name += data;
  });
  req.on('end', function () {
    let options = {
      args: ['get_mappings', name]
    };
    ps.PythonShell.run('./dist/MappingInterfaceCtrl.py', options, function(err, resp){
      if(err) throw err;
      res.send(resp);
    })
  });
}

function save_mappings(req, res) {
  var body = "";
  req.on('data', function (data) {
      body += data;
  });
  req.on('end', function () {
      var table_name = body.substring(body.length - 3, body.length);
      body = body.substring(0, body.length - 3);
      let options = {
        args: ['save_mappings', table_name, body]
      };
      ps.PythonShell.run('./dist/MappingInterfaceCtrl.py', options, function (err, results) {
        if (err) throw err;
        // results is an array consisting of messages collected during execution
        res.send(results);
      });
  });
}

// testing message
function send_me_message(req, res){
  var body = "";
  req.on('data', function (data) {
      body += data;
  });
  req.on('end', function () {
      console.log(body);
      res.send("200 OK: Done");
  });
}

// API to call to receive the IP of hub
function receive_hub_ip(req, res){
  var body = "";
  req.on('data', function (data) {
      body += data;
  });
  req.on('end', function () {
      hub_ip = body;
      res.send("200 OK: Done got " + body);
  });
}
/*END POST REQUESTS*/


//Main App Route
app.get('/', (req, res, next) => res.sendFile(path.join(__dirname, 'index.html')));

//Run Server
const port = 2081;
app.listen(process.env.PORT || port, "0.0.0.0", () => console.log(chalk.blue(`Listening intently on port ${port}`)));
