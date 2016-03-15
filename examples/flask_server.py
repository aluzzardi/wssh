#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()

from flask import Flask, request
from werkzeug.exceptions import BadRequest, Unauthorized
import wssh


app = Flask(__name__)


@app.route('/remote')
def index():
    # Abort if this is not a websocket request
    if not request.environ.get('wsgi.websocket'):
        app.logger.error('Abort: Request is not WebSocket upgradable')
        raise BadRequest()

    # Here you can perform authentication and sanity checks
    if request.args.get('key') != 'secret':
        raise Unauthorized

    # Initiate a WSSH Bridge and connect to a remote SSH server
    bridge = wssh.WSSHBridge(request.environ['wsgi.websocket'])
    try:
        bridge.open(
            hostname='localhost',
            username='root',
            password='my password'
            )
    except Exception as e:
        app.logger.exception('Error while connecting: {0}'.format(
            e.message))
        request.environ['wsgi.websocket'].close()
        return str()

    # Launch a shell on the remote server and bridge the connection
    # This won't return as long as the session is alive
    bridge.shell()

    # Alternatively, you can run a command on the remote server
    # bridge.execute('/bin/ls -l /')

    # We have to manually close the websocket and return an empty response,
    # otherwise flask will complain about not returning a response and will
    # throw a 500 at our websocket client
    request.environ['wsgi.websocket'].close()
    return str()


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler

    app.debug = True
    http_server = WSGIServer(('localhost', 5000), app,
        log=None,
        handler_class=WebSocketHandler)
    print 'Server running on ws://localhost:5000/remote'
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
