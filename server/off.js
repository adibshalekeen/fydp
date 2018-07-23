const { spawn } = require('child_process')

module.exports = function(app) {
	app.get('/off', (req, res) => {
		const path = 'off.py';
		const process = spawn('python3', [path]);
		process.stdout.on('data', (data) => {
			res.send('Done.');
		});
		process.stderr.on('data', (error) => {
			console.log('Script had error.');
		});
	});
};

