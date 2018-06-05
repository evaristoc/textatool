const helloGET = {
    method: 'GET',
    path: '/hello',
    handler: (request, reply) => {
        reply('<h1>HELLO, hapi!!</h1>');
    }
};

var indexProject = function(options) {
    return {
        method: 'GET',
        path: '/',
        handler: (request, reply) => {
            //reply('<h1>HELLO, hapi!!</h1>');
            reply.view('index', { //using the handlebars template now
                recordCount: () => { return Object.keys(options.data).length; },
            }); // we are creating this AFTER we set the use of data through the `options` attribute
        },
    };
};

//for Hapi, we need to create a route to get the css from public folder(!!!???)
//Comment from the Lesson!!!: it is better to use something like nginx to serve static assets instead, so Hapi doesnt have to do that
const cssProject = {
    method: 'GET',
    path: '/public/{param*}',
    handler: {
        directory: {
            path: 'public'
        }
    }
};

module.exports = function(options) { // we NEED to add an argument `options` so it is available to the `indexProject` router when in the `core` module
    //console.error('THIS IS OPTIONS', options.length);
    //console.error('Arguments ', typeof arguments[0]['data'].length);
    return [
        //helloGET,
        indexProject(options),
        cssProject,
    ]
};