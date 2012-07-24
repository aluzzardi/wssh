var client = new WSSHClient();

client.connect({
    // Connection and authentication parameters
    username: 'root',
    hostname: 'localhost',
    authentication_method: 'password', // can either be password or private_key
    password: 'secretpassword', // do not provide when using private_key
    key_passphrase: 'secretpassphrase', // *may* be provided if the private_key is encrypted

    // Callbacks
    onError: function(error) {
        // Called upon an error
        console.error(error);
    },
    onConnect: function() {
        // Called after a successful connection to the server
        console.debug('Connected!');

        client.send('ls\n'); // You can send data back to the server by using WSSHClient.send()
    },
    onClose: function() {
        // Called when the remote closes the connection
        console.debug('Connection Reset By Peer');
    },
    onData: function(data) {
        // Called when data is received from the server
        console.debug('Received: ' + data);
    }
});

