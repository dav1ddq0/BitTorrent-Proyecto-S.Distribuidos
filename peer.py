import bitstring
import socket
import logging
import time

class Peer:
    def __init__(self, ip, port, peer_id):
        self.has_handshaked = False
        self.last_call = 0.0
        self.ip = ip
        self.port = port
        self.read_buffer = b''
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.healthy = False
        self.bitfield: bitstring.BitArray = None
        self.unreachable = False
        self.handshaked = False
        self.peer_id = peer_id
        self.am_choking = False # this client is choking the peer
        self.am_interested = False # this client is interested in the peer
        self.peer_choking = False # this peer is choking the client
        self.peer_interested = False # this peer is interested in the client
        self.logger = self._setup_logger()

    
    
    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
            # self.socket.setblocking(False)
            logging.debug(f"Connected to peer ip: {self.ip} - port: {self.port}")

        except Exception as e:
            logging.debug(f"Failed to connect to peer (ip: {self.ip} - port: {self.port} - {str(e)})")
            return False

        return True

    def send_msg(self, msg: bytes):
        try:
            self.socket.send(msg)
            self.last_call = time.time()
        except Exception as e:
            self.healthy = False
            self.logger.error(f"Failed to send message to peer : {str(e)}")
    
    def have_a_piece(self, index):
        return self.bitfield[index]
    
    def _setup_logger(self):
        logger = logging.getLogger(f'Peer {self.peer_id}')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
        return logger
    
