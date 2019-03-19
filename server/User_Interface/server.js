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
var zig_hub_ip = "1.1.1.1";
var portNum = "2080";
var currSongIndex = 0;
var currentVolume = 70;
var zigbeeToken = "not_found";

/*GET REQUESTS*/
const ps = require('python-shell');
app.get('/myIp', get_my_ip);
app.post('/getDevices', get_devices);
app.post('/sendMessage', send_message);
app.post('/hubPointMessage', hub_point_message)
app.post('/endPointMessage', end_point_message);
app.post('/getMappings', get_mappings);
app.post('/saveMappings', save_mappings);
app.post('/sendMeMessage', send_me_message);
app.post('/broadcastRx', receive_hub_ip);
app.post('/connectBT', connect_bt);
app.post('/btSongAction', bt_song_action);
app.post('/connectZigbee', connect_zigbee);
app.post('/zigbeeAction', zigbee_action);


/*START GET REQUESTS*/
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
function get_devices(req, res) {
  var message = "";
  req.on('data', function (data) {
      message += data;
  });
  req.on('end', function () {
    if(message === "zigbee")
    {
      if(zig_hub_ip === "1.1.1.1" || zigbeeToken === "not_found")
      {
        message = "Initialize zigbee first";
        console.log(message);
        res.send(message);
        return;
      }
    }

    let options = {
      args: [message, zig_hub_ip, zigbeeToken]
    };
    console.log(message + " " + zig_hub_ip + " " + zigbeeToken);
    // When this get request is triggered, this python script will execute
    // This function gets the ddevices on the network
    ps.PythonShell.run('./dist/get_devices_script.py', options, function(err, resp){
      if(err) throw err;
      res.send(resp);
    });
  });
}

// Devices will send packet of format "sourceIP|action"
function send_message(req, res) {
  if(hub_ip === "8.8.8.8"){
    console.log("Broadcast IP from hub first");
    res.send("Need broadcast");
    return;
  }
  var message = "";
  req.on('data', function (data) {
      message += data;
  });
  req.on('end', function () {
    var options = {
      host: 'localhost',
      port: portNum,
      path: '/myIp'
    };
    var req = http.get(options, function(getResponse) {
      // Buffer the body entirely for processing as a whole.
      var ip_self = "";
      getResponse.on('data', function(chunk) {
        ip_self += chunk;
      }).on('end', function() {
        // Calculate my own IP to send with the packet
        var self_ip = ip_self.substr(2, ip_self.length - 4);
        var packet_to_send = self_ip + "|" + message;

        // Construct the post message to the central hub
        // Make sure to broadcast IP before this!
        var post_options = {
            host: hub_ip,//dest_ip
            port: portNum,
            path: '/hubPointMessage',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': packet_to_send.length
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
        post_req.write(packet_to_send);
        post_req.end();
      });
    });
  });
}

// Post a message "192.168.0.54|RIGHT" being "sourceIP|action"
function hub_point_message(req, res){
  var message = "";
  req.on('data', function (data) {
      message += data;
  });
  req.on('end', function () {
    // Received message from sender
    message = message.toUpperCase();
    console.log(message);
    let options = {
      args: ['send_message', "act", message]
    };
    // Run mapping check to see if the incoming message is valid and maps to a destination
    // and check what devices to send to
    ps.PythonShell.run('./dist/MappingInterfaceCtrl.py', options, function(err, resp){
      if(err) throw err;
      // send response to free the client
      res.send("Routed to: " + resp);
      if(resp){
        var routed_msg = resp.toString().split(',');

        for(var i = 0; i < routed_msg.length; i++){
          var dest_addr = "";
          var dest_act = "";
          var dest_name = "";
          var second_field = routed_msg[i].split('|')[1];

          if(second_field != "BLUETOOTH" && second_field != "ZIGBEE"){
            continue;
            // handle the http calls
          }
          else{
            dest_act = routed_msg[i].replace("BLUETOOTH|", "");
            dest_act = dest_act.replace("ZIGBEE|", "");
            console.log(dest_act + "hubPtMessage");

            var path = (second_field === "BLUETOOTH") ? "/btSongAction" : "/zigbeeAction";
            // host is the destination of the message and port number is set to our default
            // If we are to send to a third party manufacturer we will have pre-defined settings
            // and will set them here
            var post_options = {
                host: "localhost", //dest_ip
                port: portNum,
                path: path,
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
      }
    })
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

function connect_bt(req, res){
  var bt_mac = "";
  req.on('data', function (data) {
      bt_mac += data;
  });
  req.on('end', function () {
      let options = {
        args: ['connect', bt_mac]
      };
      ps.PythonShell.run('./dist/handle_bluetooth_actions.py', options, function (err, results) {
        if (err) throw err;
        // results is an array consisting of messages collected during execution
        res.send(results);
        console.log("Finished connectBT");
      });
  });
}

// Post data will be like "AA:11:AA:11:AA:11|playsong|1"
// next and previous song: UE BOOM 2|2C:41:A1:07:71:E0|VOLUMEUP
// Only stop song doesnt need mac address
function bt_song_action(req, res){
  var bt_song_act = "";
  req.on('data', function (data) {
      bt_song_act += data;
  });
  req.on('end', function () {
    let options = {
      args: ["getsonglistlength"]
    };
    ps.PythonShell.run('./dist/handle_bluetooth_actions.py', options, function (err, listLength) {
      if (err) throw err;
      var action = bt_song_act.split("|")[2].split("-")[0].toLowerCase();
      var mac = bt_song_act.split("|")[1];
      var name = bt_song_act.split("|")[0].replace(/_/g, " ");
      var variable = bt_song_act.split("|")[2].split("-")[1];

      console.log(bt_song_act + " Action BT");
      var variable = 0;
      if(action.includes("song"))
      {
        if(action === "prevsong")
          variable = (currSongIndex - 1 >= 0) ? currSongIndex - 1 :  listLength - 1;
        else if(action === "nextsong")
          variable = (currSongIndex + 1 < listLength) ? currSongIndex + 1 : 0;
        currSongIndex = variable;
      }
      else if (action.includes("volume"))
      {
        if(action === "volumeup")
        {
          variable = currentVolume + 10
          variable = (variable > 100) ? 100 : variable;

        }
        else if(action === "volumedown")
        {
          variable = currentVolume - 10;
          variable = (variable < 50) ? 50 : variable;
        }
        mac = name;
        currentVolume = variable;
      }

      let options_inr = {
        args: [action, variable, mac]
      };

      console.log(options_inr);
      ps.PythonShell.run('./dist/handle_bluetooth_actions.py', options_inr, function (err, results_inr) {
        if (err) throw err;
      });
      // results is an array consisting of messages collected during execution
      res.send(listLength);
    });
  });
}

function connect_zigbee(req, res){
  var zighub_ip = "";
  req.on('data', function (data) {
      zighub_ip += data;
  });
  req.on('end', function () {
      zig_hub_ip = zighub_ip;
      let options = {
        args: ['getapikey', zighub_ip]
      };
      ps.PythonShell.run('./dist/handle_zigbee_actions.py', options, function (err, results) {
        if (err) throw err;
        // results is an array consisting of messages collected during execution
        res.send(results);
        zigbeeToken = results[0];
        console.log("Finished zigbee auth");
      });
  });
}

// name|action-variable
// action, ip, key, id, brightness
function zigbee_action(req, res){
  var zigbee_act = "";
  req.on('data', function (data) {
      zigbee_act += data;
  });
  req.on('end', function () {
    if(zig_hub_ip === "1.1.1.1")
    {
      console.log("Initialize the hub and zigbee devices");
      res.send("Failed to init zigbee");
      return;
    }
    var action = zigbee_act.split("|")[1].split("-")[0].toLowerCase();
    var variable = zigbee_act.split("|")[1].split("-")[1];
    var name = zigbee_act.split("|")[0].replace(/_/g, " ");

    let options_inr = {
      args: [action, zig_hub_ip, zigbeeToken, name, variable]
    };

    console.log(options_inr);
    ps.PythonShell.run('./dist/handle_zigbee_actions.py', options_inr, function (err, results_inr) {
      if (err) throw err;
      res.send(results_inr);
    });
  });
}
/*END POST REQUESTS*/


//Main App Route
app.get('/', (req, res, next) => res.sendFile(path.join(__dirname, 'index.html')));

//Run Server
app.listen(portNum, "0.0.0.0", () => console.log(chalk.blue(`Listening intently on port ${portNum}`)));
