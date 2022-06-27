<<<<<<< Updated upstream
import hashlib
import re
from threading import Thread
import time
=======
from operator import index
from threading import Thread
import time
from cv2 import haveImageReader, sort
from numpy import result_type

from soupsieve import select
from sqlalchemy import false, true
>>>>>>> Stashed changes
from piece import Piece
from peer import Peer
from torrent_settings import READ_BUFFER_SIZE
import logging
import errno
import socket
from message import *
from piece_manager import PieceManager
from message import HandshakeMessage, PieceMessage
from torrent_info import TorrentInfo
import random
import time

class TorrentClient(Thread):

    def __init__(self, torrent_info, piece_manager, peer_id):
        Thread.__init__(self)
        self.peers: list[Peer] = []
        self.peers_download={}
        self.peers_healthy={}
        self.peers_unreachable={}
        
        self.piece_manager: PieceManager = piece_manager
        self.torrent_info: TorrentInfo = torrent_info
        self.info_hash = self.torrent_info.info_hash
        # self.peer_id = hashlib.sha1(str(time.time()).encode('utf-8')).digest()
        self.peer_id = peer_id
        self.have_it_list=[]
        self.rares_list=[]
        
        

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

    
    def random_piece_selector(self,blocked_piece,blocked_peer):
        select_piece=-1
        select_peer=-1
        
        for actual_peer in len(self.peers):
            #revisando si no se debe usar a ese peer:
            if blocked_peer[actual_peer]:
                continue
            
            
            for pos_bitfield in actual_peer.bitfield:
                
                #revisando si no se debe usar a ese piece:
                if blocked_piece[pos_bitfield]:
                    continue
                
                if actual_peer.bitfield[pos_bitfield] != self.piece_manager.bitfield[pos_bitfield]:
                    select_peer=actual_peer
                    select_piece=pos_bitfield
                    break
                
        return (select_piece,select_peer)
    
    def rarest_piece_selector(self,blocked_piece,blocked_peer):
        select_piece=-1
        select_peer=-1
        have_it_list=[]
        
        if len(have_it_list)==0:
            result_list=TorrentClient.sum_bitfields(self.peers,have_it_list)
        else:
            result_list=self.rares_list
            have_it_list=self.have_it_list
        
        for piece in result_list:
            if blocked_piece[piece]:
                continue
            
            for peer in have_it_list[piece]:
                if blocked_peer[peer]:
                    continue
                if peer.bitfield[piece] != self.piece_manager.bitfield[piece]:
                    select_peer=peer
                    select_piece=piece
                    break
                    
        return (select_piece,select_peer)
        
        
        
        #returns sorted rarest pieces and in have_it_list returns who has each piece
<<<<<<< Updated upstream
    
=======
    @staticmethod
>>>>>>> Stashed changes
    def sum_bitfields(peers,have_it_list):
        result_list=[]
        have_it_list=[]
        
        for i in range(peers.bitfield):
            result_list.append(0)
            have_it_list.append([])
            
        for bitfield in peers.bitfield:
            for i in bitfield:
                if bitfield[i]:
                    result_list[i]+=int(bitfield[i])
                    have_it_list[i].append(peers[i].peer_id)
            
        return sorted(result_list) 
                
                
        
        
    
    def select_piece(self,first_time=True, number_of_downloads=4):
        result_list=[]
        blocked_piece={}
        blocked_peer={}
<<<<<<< Updated upstream
        if first_time == True:
            for _ in range(number_of_downloads):
=======
        if first_time:
            for current_time in number_of_downloads:
>>>>>>> Stashed changes
                
                current_tuple=self.random_piece_selector(blocked_piece,blocked_peer)
                result_list.append(current_tuple)
                blocked_piece[current_tuple[0]]=current_tuple[0]
                blocked_peer[current_tuple[1]]=current_tuple[1]
        
            self.rarest_piece_selector(blocked_piece,blocked_peer)
            
        else:
            
            for item in self.peers_download:
                blocked_peer=self.peers_download[item[0]]
                blocked_piece=self.peers_download[item[1]]
            for _ in range(number_of_downloads):
                
                current_tuple=self.rarest_piece_selector(blocked_piece,blocked_peer)
                result_list.append(current_tuple)
                blocked_piece[current_tuple[0]]=current_tuple[0]
                blocked_peer[current_tuple[1]]=current_tuple[1]
            

                
        return result_list
    
    def update_bitfield(self):
        have_it_list=[]
        
        result_list=TorrentClient.sum_bitfields(self.peers,have_it_list)
        
        self.rares_list=result_list
        self.have_it_list=have_it_list
                
                


    

