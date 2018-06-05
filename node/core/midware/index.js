'use strict';
//this plugin is where connection with PYTHON is being created; it is then a SERVICE
const SocketIO = require('socket.io');
const Stomp = require('stomp-client');
const events = require('events');
const observe = new events.EventEmitter();

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
    sC.connect(sessionId => { //callback fired only if successful connection; now moved to stompClient
        console.log('Connected to Apache Apollo');
    });

    return next();
};

midware.attributes = {
    name: 'midware',
};

// we will register this `main` plugin into another plugin, the `core` one
module.exports = midware;