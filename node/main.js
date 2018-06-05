'use strict';
const Path = require('path');
require('dotenv').config({ path: Path.dirname(process.cwd()) }); //environment variables managed by 3rd party package
const Hapi = require('hapi');

const server = new Hapi.Server();

server.connection({
    port: process.env.port || 3000
});

// when Hapi registers the core module into one of its servers, 
// it immediately assigns values to the parameters of the 'core' function of the 'core' plugin we just created;
// those parameters are (server, options, next)
server.register([
    { register: require('inert') }, //this is a third party middleware for reading static files
    { register: require('vision') }, //this is a third party middleware for rendering support for templates
    {
        register: require('./core'),
        options: { // this is done here to demonstrate the use of the `option` attribute
            data: require('../data/jobproject_forum.json'), // OBS: `data` is just a custom variable
        },
    }
], error => {
    if (error) {
        console.log('Error: ', error);
    } else {
        //Start the server 
        server.start(() => {
            console.log('Hapi Server running at: ', server.info.uri);
        })
    }
})