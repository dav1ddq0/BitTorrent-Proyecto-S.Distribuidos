import hashlib
import re
from threading import Thread, Timer
import time
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
import copy

class TorrentClient(Thread):

    def __init__(self, torrent_info, piece_manager, peer_id):
        Thread.__init__(self)
        self.piece_manager: PieceManager = piece_manager
        self.torrent_info: TorrentInfo = torrent_info
        self.peers: list[Peer] = [Peer('127.0.0.1','4800',self.piece_manager.number_of_pieces, peer_id)]
        self.peers_download={}
        self.peers_healthy=[]
        self.peers_unreachable=[]
        self.trackers = self.torrent_info.trackers
        
        # miss tracker camp
        self.info_hash = self.torrent_info.info_hash
        self.logger: logging.Logger = self._setup_logger()
        # self.peer_id = hashlib.sha1(str(time.time()).encode('utf-8')).digest()
        self.peer_id = peer_id
        self.have_it_list=[]
        self.rares_list=[]
       
        self.run()

        Timer(10, self.check_unreachable_peers_to_reconnect, ()).start()
    

        
    def missing_pieces(self):
        missing_pieces=[]
        for i in range(self.piece_manager.number_of_pieces):
            if not self.piece_manager.pieces[i].is_completed:
                missing_pieces.append(i)
        return missing_pieces

    def get_random_piece(self):
        left = [piece.piece_index for piece in self.piece_manager.pieces if not piece.is_completed]
        random.shuffle(left)
        return left[0] if left else None
    
    def add_peer(self, ip, port, peer_id):
        self.peers.append(Peer(ip, port, self.piece_manager.numer_of_pieces, peer_id))   
   
    
        
    def check_unreachable_peers_to_reconnect(self):
        for peer in self.peers_unreachable:
            if peer.connect():
                if self._do_handshake(peer):
                    peer.healthy = True
                    self.peers_healthy.append(peer)
                    self.peers_unreachable.remove(peer)
                    msg = self.read_message(peer)
                    if msg and isinstance(msg, BitfieldMessage):
                        peer.bitfield = msg.bitfield
                        self.peers_healthy.append(peer)
                    else:
                        self.logger.debug(f'Expected a Bitfield Message from peer {peer.peer_id}')
                        

                else:
                    self.logger.debug(f'Handshake failed')
                    self.peers_unreachable.remove(peer)

            else:
                self.logger.error(f"Error connecting to peer {peer.peer_id}")
        
        Timer(10, self.check_unreachable_peers_to_reconnect, ()).start()

    def _do_handshake(self, peer: Peer):
        peer.send_msg(HandshakeMessage(self.info_hash, self.peer_id))
        buffer = peer.socket.recv(READ_BUFFER_SIZE)
        try:
            handshake = HandshakeMessage.unpack_message(buffer)
            self.logger.error(f"Handshake message received from peer {handshake.peer_id}")
            if handshake.peer_id != peer.peer_id:
                self.logger.error(f"{handshake.peer_id} != {peer.peer_id} Don't match peer_id of de handshake with that the tracker give")
                peer.socket.send("Close Connection".encode('utf-8'))
                time.sleep(4)
                peer.socket.close()
                peer.healthy = False
                return False
            else:
                peer.handshaked = True
                peer.healthy = True
                peer.send_msg("Handshake OK".encode('utf-8'))    
                return True
        except Exception as e:
            logging.error(f"Error unpacking handshake message: {e}")
            return False
            

    
    def read_message(self, peer: Peer)-> bytes:
        '''
        '''
        socket = peer.socket
        buffer = socket.recv(4)
        if len(buffer) < 0:
            return None
        size = struct.unpack('>I', buffer)[0]
        payload = socket.recv(size)
        if len(payload) != size:
            raise Exception(f'size {size}!= payload {payload}')
        try:
            msg = message_dispatcher(payload)
            return msg
        except WrongMessageException as e:
            self.logger(e.error_info)
            return None
    
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
    
    def bitfields_sum(self):

        
        bitfields_sum = [0]*len(self.piece_manager.bitfield)
        
            
        for peer in self.peers_healthy:
            for index, bitfield in enumerate(peer.bitfield):
                bitfields_sum[index] += bitfield
            
            
        return bitfields_sum 
                
    

    def sort_rarest_pieces(self):
        bitfields_sum = self.bitfields_sum()
        rarest = [(index, bitfield) for index, bitfield in enumerate(bitfields_sum) ]
        return sorted(rarest, key=lambda x: x[1])

    
    
    def select_piece(self,first_time=True, number_of_downloads=4):
        result_list=[]
        blocked_piece={}
        blocked_peer={}
        if first_time:
            for current_time in number_of_downloads:
                
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
    

    def relay_messages(self, peer: Peer):
        socket = peer.socket
        if not peer.handshaked:
            self._do_handshake(peer)
        else:
            pass
            
    
    def run(self):
        peers_copy = copy.deepcopy(self.peers)
        for peer in peers_copy:
            if peer.connect():
                if self._do_handshake(peer):
                    msg = self.read_message(peer)
                    if msg and isinstance(msg, BitfieldMessage):
                        peer.bitfield = msg.bitfield
                        self.peers_healthy.append(peer)
                    else:
                        self.logger.debug(f'Expected a Bitfield Message from peer {peer.peer_id}')
                        

                else:
                    self.logger.debug(f'Handshake failed')
                    self.peers.remove(peer)

                    

            else:
                self.logger.error(f"Error connecting to peer {peer.peer_id}")
                self.peers_unreachable.append(peer)
                continue
                
            
            
                    
                    
                
            


                
    
    def _setup_logger(self):
        logger = logging.getLogger(f'Client {self.peer_id}')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
        return logger


    
