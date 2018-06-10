const helloGET = {
    method: 'GET',
    path: '/hello',
    handler: (request, reply) => {
        reply('<h1>HELLO, hapi!!</h1>');
    }
};


//https://gist.github.com/joyrexus/0c6bd5135d7edeba7b87
var indexProject = function(options) {
    return {
        method: 'GET',
        path: '/',
        handler: (request, reply) => {
            //reply('<h1>HELLO, hapi!!</h1>');
            reply.view('index', { //using the handlebars template now
                recordCount: () => {
                    let forum = Object.keys(options.data).filter((k) => { return options.data[k].forum.foundjob_msg.text != "" }, [])
                    return forum.length;
                },
            }); // we are creating this AFTER we set the use of data through the `options` attribute
        },
    };
};

// const singProject =

//     {
//         method: 'GET',
//         path: '/edit/{id}',
//         handler: (request, reply) => {
//             let id = request.params.id;
//             //let id = 'World';
//             reply('<h1>HELLO, hapi!!' + id + '</h1>');
//             //reply.view('sing', { //using the handlebars template now
//             //    record: () => {
//             //        return indexArray;
//             //    },
//             //    edit: true,
//             //}); // we are creating this AFTER we set the use of data through the `options` attribute
//         },
//     };



const singProjectGet = {
    method: 'GET',
    path: '/edit/{id}',
    handler: (request, reply) => {
        let id = request.params.id;
        //let record = JSON.parse(require('../../../output/output.json')).filter((d) => { return d.id == id });
        let record = JSON.parse(JSON.stringify(require('../../../output/output.json'))).filter((d) => {
            return JSON.parse(d).id == id;
        }, {});
        //let id = 'World';
        reply.view('edit', {
            record: record,
        });
        //reply.view('sing', { //using the handlebars template now
        //    record: () => {
        //        return indexArray;
        //    },
        //    edit: true,
        //}); // we are creating this AFTER we set the use of data through the `options` attribute
    },

};

//for Hapi, we need to create a route to get the css from public folder(!!!???)
//Comment from the Lesson!!!: it is better to use something like nginx to serve static assets instead, so Hapi doesnt have to do that
const cssProject = {
    method: 'GET',
    path: '/public/{param*}',
    handler: {
        directory: {
            path: 'public',
            redirectToSlash: true,
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
        singProjectGet,
    ]
};