import bitstring
import socket
import logging
import time

class Peer:
    def __init__(self, ip, port, pieces_len):
        self.last_call = 0.0
        self.ip = ip
        self.port = port
        self.socket =  None
        self.healthy_status = False
        self.bitarray = bitstring.BitArray(pieces_len)
        self.pieces_len = pieces_len
    
    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port), timeout=1)
            self.socket.setblocking(False)
            logging.debug(f"Connected to peer ip: {self.ip} - port: {self.port}")
            self.healthy_status = True

        except Exception as e:
            print(f"Failed to connect to peer (ip: {self.ip} - port: {self.port} - {str(e)})")
            return False

        return True

    def send_msg(self, msg):
        try:
            self.socket.send(msg)
            self.last_call = time.time()
        except Exception as e:
            self.healthy_status = False
            logging.error(f"Failed to send message to peer : {str(e)}")
    