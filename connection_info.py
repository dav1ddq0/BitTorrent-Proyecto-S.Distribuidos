from socket import socket


import socket
class ConnectionInfo:

    def __init__(self, connection: socket.socket, address , handshaked: bool):
        self.connection = connection
        self.handshaked = handshaked
        self.address = address
        self.peer_id = None
        self.last_call = 0.0
    