# -*- coding: utf-8 -*-

"""
wssh.server

This module provides server capabilities of wssh
"""

import gevent
from gevent.socket import wait_read, wait_write
from gevent.select import select
from gevent.event import Event

import paramiko
from paramiko import PasswordRequiredException
from paramiko.dsskey import DSSKey
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import SSHException

import socket

try:
    import simplejson as json
except ImportError:
    import json

from StringIO import StringIO


class WSSHBridge(object):
    """ WebSocket to SSH Bridge Server """

    def __init__(self, websocket):
        """ Initialize a WSSH Bridge

        The websocket must be the one created by gevent-websocket
        """
        self._websocket = websocket
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        self._tasks = []

    def _load_private_key(self, private_key, passphrase=None):
        """ Load a SSH private key (DSA or RSA) from a string

        The private key may be encrypted. In that case, a passphrase
        must be supplied.
        """
        key = None
        last_exception = None
        for pkey_class in (RSAKey, DSSKey):
            try:
                key = pkey_class.from_private_key(StringIO(private_key),
                    passphrase)
            except PasswordRequiredException as e:
                # The key file is encrypted and no passphrase was provided.
                # There's no point to continue trying
                raise
            except SSHException as e:
                last_exception = e
                continue
            else:
                break
        if key is None and last_exception:
            raise last_exception
        return key

    def open(self, hostname, port=22, username=None, password=None,
                    private_key=None, key_passphrase=None,
                    allow_agent=False, timeout=None):
        """ Open a connection to a remote SSH server

        In order to connect, either one of these credentials must be
        supplied:
            * Password
                Password-based authentication
            * Private Key
                Authenticate using SSH Keys.
                If the private key is encrypted, it will attempt to
                load it using the passphrase
            * Agent
                Authenticate using the *local* SSH agent. This is the
                one running alongside wsshd on the server side.
        """
        try:
            pkey = None
            if private_key:
                pkey = self._load_private_key(private_key, key_passphrase)
            self._ssh.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                pkey=pkey,
                timeout=timeout,
                allow_agent=allow_agent,
                look_for_keys=False)
        except socket.gaierror as e:
            self._websocket.send(json.dumps({'error':
                'Could not resolve hostname {0}: {1}'.format(
                    hostname, e.args[1])}))
            raise
        except Exception as e:
            self._websocket.send(json.dumps({'error': e.message or str(e)}))
            raise

    def _forward_inbound(self, channel):
        """ Forward inbound traffic (websockets -> ssh) """
        try:
            while True:
                data = self._websocket.receive()
                if not data:
                    return
                data = json.loads(str(data))
                if 'resize' in data:
                    channel.resize_pty(
                        data['resize'].get('width', 80),
                        data['resize'].get('height', 24))
                if 'data' in data:
                    channel.send(data['data'])
        finally:
            self.close()

    def _forward_outbound(self, channel):
        """ Forward outbound traffic (ssh -> websockets) """
        try:
            while True:
                wait_read(channel.fileno())
                data = channel.recv(1024)
                if not len(data):
                    return
                self._websocket.send(json.dumps({'data': data}))
        finally:
            self.close()

    def _bridge(self, channel):
        """ Full-duplex bridge between a websocket and a SSH channel """
        channel.setblocking(False)
        channel.settimeout(0.0)
        self._tasks = [
            gevent.spawn(self._forward_inbound, channel),
            gevent.spawn(self._forward_outbound, channel)
        ]
        gevent.joinall(self._tasks)

    def close(self):
        """ Terminate a bridge session """
        gevent.killall(self._tasks, block=True)
        self._tasks = []
        self._ssh.close()

    def execute(self, command, term='xterm'):
        """ Execute a command on the remote server

        This method will forward traffic from the websocket to the SSH server
        and the other way around.

        You must connect to a SSH server using ssh_connect()
        prior to starting the session.
        """
        transport = self._ssh.get_transport()
        channel = transport.open_session()
        channel.get_pty(term)
        channel.exec_command(command)
        self._bridge(channel)
        channel.close()

    def shell(self, term='xterm'):
        """ Start an interactive shell session

        This method invokes a shell on the remote SSH server and proxies
        traffic to/from both peers.

        You must connect to a SSH server using ssh_connect()
        prior to starting the session.
        """
        channel = self._ssh.invoke_shell(term)
        self._bridge(channel)
        channel.close()
