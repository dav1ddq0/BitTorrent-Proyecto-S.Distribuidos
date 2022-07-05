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
        # self.socket.setblocking(False)
        self.healthy = False
        self.bitfield: bitstring.BitArray = None
        self.unreachable = False
        self.connected = False
        self.handshaked = False
        self.peer_id = peer_id
        self.choking = False # this peer is choking the client
        self.interested = False # this peer is interested in the client

    @property
    def has_bitfield(self):
        return self.bitfield is not None

    def __str__(self):
        return f"PeerID: {self.peer_id} IP:{self.ip} PORT: {self.port}"
    
    
    def __eq__(self, peer:'Peer'):
        return self.peer_id == peer.peer_id
    
    def __ne__(self, peer: 'Peer'):
        return self.peer_id != peer.peer_id
    
    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
            # self.socket.setblocking(False)
            logger.debug(f"Connected to peer ip: {self.ip} - port: {self.port}")
            self.connected = True
            return True

        except socket.error as e:
            err = e.args[0]
            if err == errno.EALREADY:
                logger.error(f"A connection request is already in progress for the specified socket {self.peer.ip} : {self.port}.")
            elif err == errno.EHOSTUNREACH:
                logger.error(f"The destination host {self.ip} : {self.port} cannot be reached (probably because the host is down or a remote router cannot reach it).")
            logger.error(f"Failed to connect to peer (ip: {self.ip} - port: {self.port} - {str(e)})")
            return False
        
        except Exception as e:
            logger.debug(f"Failed to connect to peer (ip: {self.ip} - port: {self.port} - {str(e)})")
            self.connected = False
            return False
        

    def send_msg(self, msg: bytes, type_msg:str):
        try:
            self.socket.send(msg)
            self.last_call = time.time()
            time.sleep(1)
            logger.debug(f"Sending  {type_msg} from client to peer {self.ip} ...")
        except Exception as e:
            self.healthy = False
            logger.error(f"Failed to send {type_msg}  to : {self.ip}")
            raise Exception
    
    def have_a_piece(self, index):
        return self.bitfield[index]

    def read(self):
        while 1:
            try:
                buff = self.socket.recv(READ_BUFFER_SIZE)
                if not buff:
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

            else: break

    def get_message(self):
        
        if len(self.read_buffer) > 4 :
            if not self.handshaked and len(self.read_buffer) >= HandshakeMessage.total_len:
                try:
                    handshake_message = HandshakeMessage.unpack_message(self.read_buffer[:HandshakeMessage.total_len])
                    self.read_buffer = self.read_buffer[HandshakeMessage.total_len:]
                    return handshake_message
                except:
                    logger.exception("First message should always be a handshake message")
                    return None
            else:
                payload_length, = struct.unpack(">I", self.read_buffer[:4])
                total_length = payload_length + 4
                if len(self.read_buffer) < total_length:
                    return None
                else:
                    payload = self.read_buffer[:total_length]
                    print(f"Payload length: {len(payload)}")
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
    
    

