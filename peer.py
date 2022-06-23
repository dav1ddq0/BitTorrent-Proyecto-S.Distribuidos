import bitstring
import socket
import logging
import time

class Peer:
    def __init__(self, ip, port, pieces_len):
        self.has_handshaked = False
        self.last_call = 0.0
        self.ip = ip
        self.port = port
        self.read_buffer = b''
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.healthy_status = False
        self.bitfield: bitstring.BitArray = bitstring.BitArray(pieces_len)
        self.pieces_len = pieces_len
    
    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
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
    
    def have_a_piece(self, index):
        return self.bitfield[index]
    
    
    
