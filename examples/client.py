#!/usr/bin/env python

if __name__ == '__main__':
    from wssh import client

    client.invoke_shell('ws://localhost:5000/remote?key=secret')
