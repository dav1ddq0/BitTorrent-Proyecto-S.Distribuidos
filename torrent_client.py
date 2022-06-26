from ast import match_case
import hashlib
from threading import Thread
import time
from piece import Piece
from peer import Peer
from torrent_settings import READ_BUFFER_SIZE
import logging
import errno
import socket
from message import *
from piece_manager import PieceManager
from message import HandshakeMessage, PieceMessage, BitfieldMessage
from torrent_info import TorrentInfo
import random
import time

class TorrentClient(Thread):

    def __init__(self, torrent_info, piece_manager, peer_id):
        Thread.__init__(self)
        self.peers: list[Peer] = []
        self.piece_manager: PieceManager = piece_manager
        self.torrent_info: TorrentInfo = torrent_info
        self.info_hash = self.torrent_info.info_hash
        # self.peer_id = hashlib.sha1(str(time.time()).encode('utf-8')).digest()
        self.peer_id = peer_id
        

    def get_random_piece(self):
        left = [piece.piece_index for piece in self.piece_manager.pieces if not piece.is_completed]
        random.shuffle(left)
        return left[0] if left else None
        
    
    def run(self):
        self.connect_to_peers()
        for peer in self.peers:
            socket = peer.socket
            if not peer.handshaked:
                peer.send_msg(HandshakeMessage(self.info_hash, self.peer_id))
                buffer = socket.recv(READ_BUFFER_SIZE)
                try:
                    handshake = HandshakeMessage.unpack_message(buffer)
                    logging.error(f"Handshake message received from peer {handshake.peer_id}")
                    if handshake.peer_id != peer.peer_id:
                        logging.error(f"{handshake.peer_id} != {peer.peer_id} Don't match peer_id of de handshake with that the tracker give")
                        peer.socket.send("Shutdown Connection".encode('utf-8'))
                        time.sleep(4)
                        peer.socket.close()
                        peer.healthy = False
                        break
                    else:
                        peer.handshaked = True
                        peer.healthy = True
                        peer.send_msg("Handshake OK".encode('utf-8'))    
                    buffer = socket.connection.recv(4)
                    if len(buffer) < 0:
                        break
                    size = struct.unpack('>I', buffer)[0]
                    
                    payload = socket.connection.recv(size)
                    try:
                        msg = message_dispatcher(payload)
                    except:
                        logging.debug('Mensaje No Valido')
                    if isinstance(msg, BitfieldMessage):
                        peer.bitfield = msg.bitfield
                    
                except Exception as e:
                    logging.error(f"Error unpacking handshake message: {e}")
                    break
            
            else:
                peer.send_msg(BitfieldMessage())
                payload = self.read_message(peer)
                if payload:
                    msg = message_dispatcher(payload)
                    if isinstance(msg, PieceMessage):
                        self.piece_manager.receive_block_piece(msg.index, msg.begin, msg.block)




            
                    




    def add_peer(self, ip, port, peer_id):
        self.peers.append(Peer(ip, port, self.piece_manager.numer_of_pieces, peer_id))   
    def connect_to_peers(self):
        for peer in self.peers:
            peer.connect()
        




    
    def read_message(self, peer: Peer)-> bytes:
        data = b''
        while 1:
            try:
                if peer.handshaked:
                    buffer = peer.socket.recv(4)
                    if len(buffer) < 0:
                        break
                    size = struct.unpack('>I', buffer)[0]

                    payload = peer.socket.recv(size)
                    if len(payload) == size:
                        data = payload 
                        break

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


        
        
        


    
   
