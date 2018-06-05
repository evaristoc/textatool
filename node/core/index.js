'use strict';
const Path = require('path');

//values to the following arguments are passed by Hapi after registering on 
// the highest level index.js script, where core will become a Hapi instance
function core(server, options, next) {
    // Load Routes
    server.route(require('./routes')(options)); //see that we are now passing options; we have made a modification to set options in the main script to use data as an example and see how it is used

    //Configurations
    server.views({
        engines: {
            html: require('handlebars'), //this is a third party middleware for template html
        },
        path: Path.join(__dirname, '../views'),
    });

    //Core Logic

    server.register({
        register: require('./midware'),
        options: {
            data: options.data,
        }
    }, error => { // this error callback is MANDATORY in every register 
        if (error) {
            console.log('There was an error loading the midware plugin');
        }

    });

    return next();
};

core.attributes = {
    name: 'core',
    //sometimes we can just ask Hapi to add the dependencies for certain modules to be loaded from its attribute form
    //dependencies: ['inert','vision']
};

module.exports = core;