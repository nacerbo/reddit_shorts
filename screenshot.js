const Pageres = require('pageres');
// console.log(process.argv);
(async () => {
	await new Pageres({delay: 2, filename: './audio/' + process.argv[3]  + "/" + process.argv[4] + '/' + process.argv[5] })
        .src(process.argv[2], ['Nexus 10'])
		.dest(__dirname)
		.run();

	console.log('Finished generating screenshots!');
})();