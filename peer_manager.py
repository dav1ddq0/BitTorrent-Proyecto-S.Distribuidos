from ast import match_case
from threading import Thread
from piece import Piece
from peer import Peer
from torrent_settings import READ_BUFFER_SIZE
import logging
import errno
import socket
from message import *
from piece_manager import PieceManager
class PeerManager(Thread):

    def __init__(self, torrent_info, piece_manager):
        Thread.__init__(self)
        self.peers: list[Peer] = []
        self.piece_manager: PieceManager = piece_manager
        self.torrent_info = torrent_info

    
    def read_socket(self, socket: socket.socket):
        data = b''
        while 1:
            try: 
                buffer = socket.recv(READ_BUFFER_SIZE)
                if len(buffer) < 0:
                    break
                data += buffer
            except socket.error as e:
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    logging.debug("Wrong errno {}".format(err))
                break
            except Exception:
                logging.exception("Recv failed")
                break    
    
        return data
    
    def process_incoming_msg(self, peer: Peer, msg: Message):

        if isinstance(msg, HandshakeMessage) and peer.handshaked:
            logging.error("Handshake should have already been handled")
            return
        if isinstance(msg, PieceMessage):
            """
                :type message: piece message
            """
            self.piece_manager.receive_block_piece(msg.index, msg.begin, msg.block)
        if isinstance(msg, ):...


        
        
        


    
   
