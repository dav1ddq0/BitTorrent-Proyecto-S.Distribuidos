from ast import match_case
import hashlib
from operator import index
from threading import Thread
import time

from soupsieve import select
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
                        peer.socket.close()
                        peer.healthy = False
                    else:
                        peer.handshaked = True
                        peer.healthy = True
                        peer.send_msg("Handshake OK".encode('utf-8'))    

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

    
    def random_piece_selector(self):
        select_piece=-1
        for i in range(0, len(self.piece_manager.bitfield-1)):
            if self.piece_manager.bitfield[i] != self.peers.bitfield[i]:
                select_piece=i
                break
        return select_piece
    
    def rarest_piece_selector(self,bitfield_clients,bitfield_peers):
        select_piece=-1
        
    def sum_bitfields(bitfield_peers):
        result_list=[]
        for i in range(bitfield_peers.bitfield):
            result_list.append(0)
        for bitfield in bitfield_peers.bitfield:
            for i in bitfield:
                result_list[i]+=bitfield[i]
                
                
                
        
        
        
        
    
    def select_piece(self, bitfield_client, bitfield_peer, first_time=True):
        
        pass


    
   
