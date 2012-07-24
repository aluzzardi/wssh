wssh
====

wssh is a SSH to WebSockets Bridge that lets you invoke a remote shell using nothing but HTTP.

The client connecting to wssh doesn't need to speak the SSH protocol - rather, the SSH connection is terminated
at the bridge level and the pty is wrapper through a thin layer of JSON and sent back to the client.

This means you can implement a WSSH client in just a few lines of code, even for a web browser.

