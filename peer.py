import errno
import struct
import bitstring
import socket
import logging
import time

from bclient_logger import logger
from message import HandshakeMessage, WrongMessageException, message_dispatcher
from torrent_settings import READ_BUFFER_SIZE

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
        self.has_bitfield = False
        self.unreachable = False
        self.handshaked = False
        self.peer_id = peer_id
        self.choking = False # this peer is choking the client
        self.interested = False # this peer is interested in the client


    def __str__(self):
        return f"PeerID: {self.peer_id} IP:{self.ip} PORT: {self.port}"
    
    
    def _eq__(self, peer:'Peer'):
        return self.peer_id == peer.peer_id
    
    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
            # self.socket.setblocking(False)
            logger.debug(f"Connected to peer ip: {self.ip} - port: {self.port}")

        except Exception as e:
            logger.debug(f"Failed to connect to peer (ip: {self.ip} - port: {self.port} - {str(e)})")
            return False

        return True

    def send_msg(self, msg: bytes):
        try:
            self.socket.send(msg)
            self.last_call = time.time()
        except Exception as e:
            self.healthy = False
            logger.error(f"Failed to send message to peer : {str(e)}")
    
    def have_a_piece(self, index):
        return self.bitfield[index]

    def read(self):
        while 1:
            try:
                buff = self.connection.recv(READ_BUFFER_SIZE)
                if len(buff) <= 0:
                    break

                self.read_buffer += buff
            except socket.error as e:
                self.healthy = False
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    logger.debug("Wrong errno {}".format(err))
                break
            except Exception:
                logger.exception("Recv failed")
                self.healthy = False
                break

    def get_message(self):
        if len(self.read_buffer) > 4 :
            payload_length, = struct.unpack(">I", self.read_buffer[:4])
            total_length = payload_length + 4
            if len(self.read_buffer) < total_length:
                return None
            else:
                payload = self.read_buffer[:total_length]
                self.read_buffer = self.read_buffer[total_length:]
            try:
                received_message = message_dispatcher(payload)
                if received_message:
                    return received_message
                else:
                    return None
            except WrongMessageException as e:
                logger.exception(e.error_info)
                return None
    
    

