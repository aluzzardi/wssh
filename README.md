wssh
====

wssh is a SSH to WebSockets Bridge that lets you invoke a remote shell using nothing but HTTP.

The client connecting to wssh doesn't need to speak the SSH protocol - rather, the SSH connection is terminated
at the bridge level and the pty is wrapper through a thin layer of JSON and sent back to the client.

This means you can implement a WSSH client in just a few lines of code, even for a web browser.

Usage
-----

Even though `wssh` primary purpose is to be used as a library in your applications,
it ships with two command line tools: `wsshd` (the server) and `wssh` (the client).

```
$ wsshd 
wsshd/0.1.0 running on 0.0.0.0:5000
```

```
$ wssh aluzzardi@mba -p
Password: 
Last login: Mon Jul 23 23:20:27 2012 from localhost
aluzzardi@mba:~$ 
```

Web Interface
-------------

wsshd provides a web interface giving you access to a Javascript client

![wssh: shell](https://github.com/aluzzardi/wssh/raw/master/misc/shell_screenshot.png)

![wssh: vim](https://github.com/aluzzardi/wssh/raw/master/misc/vim_screenshot.png)

Creating your own server
------------------------

`wsshd` is just a simple server implementation to demonstrate the wssh library.

You can actually integrate wssh into your own Python web application in order to provide terminal access.
For instance, you may want to provide shell access to clients authenticated through OAuth to a special user account.
The client doesn't need to know where the SSH server is located nor its credentials.

An example using the Flask framework is provided in `examples/flask_server.py`

Creating your own client
------------------------

Beside the command line tool, `wssh` comes bundled with both a Python and a Javascript client library for the wssh bridge.

There are examples available in the `examples/` directory for both languages.

You can write your own library in another language in just a few lines of code.