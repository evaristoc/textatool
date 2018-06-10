'use strict';
//this plugin is where connection with PYTHON is being created; it is then a SERVICE
const SocketIO = require('socket.io');
const Stomp = require('stomp-client');
const fs = require('fs');
const Path = require('path');
//console.log(__dirname);
//console.log(process.cwd());
const events = require('events');
const observe = new events.EventEmitter();
var end;

function midware(server, options, next) {
    /////////////////////////
    // Main Var, Const and Setups //
    /////////////////////////

    let itemArray = [];
    const outQueue = '/queue/inPython';
    const inQueue = '/queue/withPython';

    /// Stomp ///
    //pick one of the ports at which Apollo is accepting connections; also the user and its password
    const connectOpt = [process.env.ActiveMQHOST, process.env.ActiveMQPORT, process.env.ActiveMQUSER, process.env.ActiveMQPASS];
    //const sC = new Stomp('localhost', 61613, 'club', 'musichouse');
    const sC = new Stomp(...connectOpt);
    //OBS: the `...` wouldn't unpack for node versions as early as 4.x
    //for that, a ported not-default package called `harmony-spreadcalls should be invoked, just as future package in PYTHON
    //to do that, in package.json --> scripts add a new attribute as so:
    // "start": "node --harmony-spreadcalls index.js

    /// Socket ///
    const io = SocketIO(server.listener);

    //////////////////
    //loading Stomp 1 //
    //////////////////

    //creating the instance is insufficient to open a connection
    //it requires a method that will return a sessionId
    // sC.connect(sessionId => { //callback fired only if successful connection; now moved to stompClient
    //     console.log('Connected to Apache Apollo');
    // });

    //////////////////
    //loading Stomp 3 //
    //////////////////


    function stompClient() {
        return new Promise((resolve, reject) => {
                sC.connect(sessionId => { //callback fired only if successful connection
                    console.log('Connected to Apache Apollo ::', sessionId);
                    sC.subscribe(inQueue, body => { //if connect ok, subscribe
                        itemArray.push(body);
                        observe.emit("set");
                        if (itemArray.length == end) {
                            //https://activemq.apache.org/apollo/documentation/stomp-manual.html
                            //https://stackoverflow.com/questions/2496710/writing-files-in-node-js
                            fs.writeFile('../output/output.json', JSON.stringify(itemArray), function(err) {
                                if (err)
                                    return console.log(err);
                                console.log('Wrote json of itemArray in file output.json, just check it');
                            });
                        }
                    });
                    resolve(sessionId, sC); //finally if connect ok, resolve by passing the subscribed sC and its session to the next step
                });
            },
            error => {
                reject(error);
            }
        )
    };


    ////////////////////
    // Loading Socket 2 //
    ////////////////////

    function ioConnect() {
        io.on('connection', socket => {
            console.log('Connected to SOCKET!');

            /////////////////////
            //managing the button
            /////////////////////
            if (itemArray.length > 0) {
                //Keep button disabled
                socket
                    .emit("buttonState", { //this is verified first
                        state: false,
                    })
                    .emit("allData", { //once the above is done, this one is verified
                        dataArray: itemArray,
                    })
            } else {
                socket.emit("buttonState", {
                    state: true,
                })
            };

            ////////////////////////
            //Publish data to Apollo
            ////////////////////////
            socket.on('begin', () => {
                let forum = Object.keys(options.data).map((k) => {
                        return { "user": k, "data": options.data[k] };
                    }, [])
                    .filter((r) => {
                        return r.data.forum.foundjob_msg.text != "";
                    }, []);
                end = forum.length;
                sC.publish(outQueue, JSON.stringify(forum)); //`options` is recevied by the MAIN aapp !!
            });

            ///////////////////////////////
            //Broadcasting data from Apollo
            ///////////////////////////////
            // Watch the intemArray for changes
            observe.on('set', () => { //this emit doesnt compete with the emit in ~line 132 because this only works when set is available
                //console.log(itemArray[itemArray.length - 1]);
                //console.log(itemArray[itemArray.length - 1]);
                socket.emit('item', {
                    dataArray: itemArray[itemArray.length - 1],
                })
            })
        });
    };

    //////////////////////////////////////////
    // Initiating connections with promises //
    //////////////////////////////////////////

    stompClient()
        .then(ioConnect) //ioConnect doesn't receive anything from stompClient because itemArray is GLOBAL to this scope; it works becase the promise will keep listening until the whole data is brought back from Python
        .catch(err => {
            console.log('An error has ocurred during the connection to Stomp ::', err);
        })


    return next();
};

midware.attributes = {
    name: 'midware',
};

// we will register this `main` plugin into another plugin, the `core` one
module.exports = midware;