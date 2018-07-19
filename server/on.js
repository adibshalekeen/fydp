const { spawn } = require('child_process')

module.exports = function(app) {
	app.get('/on', (req, res) => {
		const path = 'on.py';
		const process = spawn('python3', [path]);
		process.stdout.on('data', (data) => {
			res.send('Done.');
		});
		process.stderr.on('data', (error) => {
			console.log('Script had error.');
		});
	});
};

