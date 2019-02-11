//Requires
const express = require('express');
const app = express();
const path = require('path');
const chalk = require('chalk');
const morgan = require('morgan');

//Static Routes
app.use('/dist', express.static(path.join(__dirname, 'dist')));
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.use('/src', express.static(path.join(__dirname, 'src')));
app.use('/node_modules', express.static(path.join(__dirname, 'node_modules')));

app.use(morgan('dev')) // logging

/*GET REQUESTS*/
const ps = require('python-shell');
app.get('/getDevices', get_devices);
app.post('/getMappings', get_mappings);
app.post('/saveMappings', save_mappings);

/*START GET REQUESTS*/
function get_devices(req, res) {
  ps.PythonShell.run('./dist/get_devices_script.py', null, function(err, resp){
    if(err) throw err;
    res.send(resp);
  })
}
/*END GET REQUESTS*/

/*START POST REQUESTS*/
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
/*END POST REQUESTS*/


//Main App Route
app.get('/', (req, res, next) => res.sendFile(path.join(__dirname, 'index.html')));

//Run Server
const port = 2081;
app.listen(process.env.PORT || port, () => console.log(chalk.blue(`Listening intently on port ${port}`)));
