from threading import Thread, Timer
import time

from requests import request
from block import BlockState
from piece import Piece
from peer import Peer
from torrent_settings import READ_BUFFER_SIZE
import logging
import errno
import socket
from message import *
from piece_manager import PieceManager
from message import HandshakeMessage, PieceMessage, InfoMessage
from torrent_info import TorrentInfo
import random
import time
from bclient_logger import logger
from tools import rpyc_deep_copy

from tracker.tracker_service import TrackerConnection

class TorrentClient(Thread):

    def __init__(self, torrent_info, piece_manager, peer_id, port):
        Thread.__init__(self)
        self.piece_manager: PieceManager = piece_manager
        self.torrent_info: TorrentInfo = torrent_info
        self.peers: list[Peer] = []
        self.__pieces_being_downloaded: dict[int, 'Peer']={} #  dictionary that saves for the piece i that is being downloaded by the peer from which it is obtaining the blocks 
        self.peers_healthy=[]
        self.peers_unreachable=[]
        self.trackers: list[tuple(str, int)] = self.torrent_info.trackers # ip, port of the trackers in the torrent
        self.peer_id = peer_id # peer id
        self.port = port # The port number that the client is listening on
        self.info_hash = self.torrent_info.info_hash

 
        self.rarest = [] # sorted list of the pieces that are rarest 
        self.started = True
        self.first_piece = True
    


    def run(self):
        Timer(1, self.__get_peers_from_tracker, ()).start()
        Timer(1, self.__intent_connect_peers,()).start()
        Timer(5, self.__download_piece,()).start()
        Timer(10, self.__put_peers_not_healthy_to_end,()).start()
        Timer(1, self.__rcv_messages,()).start()
        Timer(5, self.__request_update_bitfield, ()).start()
        Timer(1, self.__show_status, ()).start()

    @property
    def completed(self):
        return self.piece_manager.completed
    
    @property
    def number_of_peers(self):
        return len(self.peers)
       
    def __tracker_request_params(self, event = ''):
        '''
            The parameters used in the client->tracker GET request
        '''
        return {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'port': self.port,
            'left': self.piece_manager.left,
            'event': event
        }
   
    def __put_peers_not_healthy_to_end(self):
        self.peers = sorted(self.peers, key=lambda x: x.healthy, reverse=True)
        Timer(10, self.__put_peers_not_healthy_to_end, ()).start()

    def __connect_tracker(self, ip: str, port: int, event: str):
        '''
            Connects to the tracker and sends the GET request
        '''
        tracker_response = None
        with TrackerConnection(ip, port) as tracker_conn:
            response = tracker_conn.find_peers(self.__tracker_request_params(event))
            response_dc = rpyc_deep_copy(response)
            return response_dc
        
        return tracker_response
        

    def __request_update_bitfield(self, peer: Peer):
        for peer in self.peers:
            if peer.healthy:
                peer.send_msg(InfoMessage("Bitfield").message())

    def __get_peers_from_tracker(self):
        for ip, port in self.trackers:
            print(ip, port)
            event = ''
            if self.started:
                event = 'started'
            if self.completed:
                event = 'completed'
            tracker_response = self.__connect_tracker(ip, port, event)
            peers_dict = tracker_response['peers']
            for peer_dict in peers_dict:
                new_peer = Peer(peer_dict['ip'], peer_dict['port'],  peer_dict['peer_id'])
                # print(new_peer)
                if new_peer not in self.peers:
                    self.peers.append(new_peer)
        
        Timer(10,self.__get_peers_from_tracker, ()).start()


    def __show_status(self):
        new_progession = 0
        for piece in self.piece_manager.pieces:
            for block in piece.blocks:
                if block.state == BlockState.BLOCK_FULL:
                    new_progession += block.block_size
        

        percentage_completed = float((float(new_progession) / self.piece_manager.file_size)*100)
        logger.info(f"Connected peers: {self.number_of_peers} - {percentage_completed} completed | {self.piece_manager.completed_pieces}/{self.piece_manager.number_of_pieces} pieces")
    
    def __intent_connect_peers(self):
        for peer in self.peers:
            if not peer.healthy:
                if not peer.connect():
                    peer.healthy = False
                    peer.unreachable = False
                continue
            if self.__do_handshake(peer):
                peer.healthy = True
            else:
                peer.healthy = False

        
        Timer(5,self.__intent_connect_peers,()).start()


    def __download_piece(self):
        if  not self.piece_manager.completed:
            if len(self.__pieces_being_downloaded) < 4:
                next_piece = self.__give_me_next_piece()
                available_peer = self.__find_available_peer(next_piece)
                if available_peer is not None:
                    self.__pieces_being_downloaded[next_piece] = available_peer
            for piece_index, peer in self.__pieces_being_downloaded.items():
                if peer.healthy:
                    self.__download_piece_from_peer(piece_index, peer)
        Timer(5, self.__download_piece, ()).start()
    
    def __download_piece_from_peer(self, piece_index: int, peer: Peer):
        piece = self.piece_manager.get_piece(piece_index)
        if piece is None:
            return
        begin_block, len_block  = piece.get_empty_block()
        peer.send_msg(RequestMessage(piece_index, begin_block, len_block).message())

    def __find_available_peer(self, piece_index):
        for peer in self.peers:
            if peer.healthy and peer.has_bitfield:
                if peer.have_a_piece(piece_index):
                    return peer
        return None
    
    def __give_me_next_piece(self):
        if self.first_piece:
            self.first_piece = False
            return self.__get_random_piece() 
        else:
            for piece_index,_ in self.rarest:
                if not self.piece_manager.pieces[piece_index].is_completed and piece_index not in self.__pieces_being_downloaded:
                    return piece_index
            


    def __get_random_piece(self):
        left = [piece.piece_index for piece in self.piece_manager.pieces if not piece.is_completed]
        random.shuffle(left)
        return left[0] if left else None
           
    def __do_handshake(self, peer: Peer):
        if not peer.handshaked:
            peer.send_msg(HandshakeMessage(self.info_hash, self.peer_id).message())
            logger.debug("Handshake Message sent")
            time.sleep(0.2)
            buffer = peer.socket.recv(READ_BUFFER_SIZE)
            try:
                handshake = HandshakeMessage.unpack_message(buffer)
                logger.error(f"Handshake message received from peer {handshake.peer_id}")
                if handshake.peer_id != peer.peer_id:
                    logger.error(f"{handshake.peer_id} != {peer.peer_id} Don't match peer_id of de handshake with that the tracker give")
                    peer.send_msg(InfoMessage("Closed Connection").message())
                    # peer.socket.send("Close Connection".encode('utf-8'))
                    peer.healthy = False
                    time.sleep(1)
                    peer.socket.close()
                    return False
                else:
                    peer.handshaked = True
                    peer.healthy = True
                    # peer.send_msg(InfoMessage("Handshake OK").message())  
                    return True
            except Exception as e:
                logging.error(f"Error unpacking handshake message: {e}")
                return False
        return True
            

    
    
    def __rcv_messages(self):
        '''
            Receive messages from peers
        '''
        for peer in self.peers:
            if peer.healthy:
                peer.read()
                msg = peer.get_message()
                if msg:
                    if isinstance(msg, BitfieldMessage):
                        '''
                            If the peer send a bitfield message, we update the bitfield of the peer
                        '''
                        self.logger.debug(f"Bitfield message received from peer {peer.peer_id}")
                        peer.has_bitfield = True
                        peer.bitfield = msg.bitfield
                        self.__update_rarest()
                    elif isinstance(msg, PieceMessage):
                        '''
                            If the peer send a piece message, we write the piece block to the piece manager
                        '''
                        self.logger.debug(f"Piece message of piece {msg.index} received from peer {peer.peer_id} ")
                        self.piece_manager.receive_block_piece(msg.piece_index, msg.begin_block, msg.block)
                    
                    elif isinstance(msg, RequestMessage):
                        ...
                    
                    elif isinstance(msg, ChokeMessage):
                        peer.peer_choking = True
                    
                    elif isinstance(msg, UnchokeMessage):
                        peer.peer_choking = False
                    
                    elif isinstance(msg, InterestedMessage):
                        peer.peer_interested = True
                    
                    elif isinstance(msg, NotInterestedMessage):
                        peer.peer_interested = False
                    
                    else:
                        logger.exception('Is not a valid message')
    # def process_incoming_msg(self, peer: Peer, msg: Message):

    #     if isinstance(msg, HandshakeMessage) and peer.handshaked:
    #         logging.error("Handshake should have already been handled")
    #         return
    #     if isinstance(msg, PieceMessage):
    #         """
    #             :type message: piece message
    #         """
    #         self.piece_manager.receive_block_piece(msg.index, msg.begin, msg.block)
    #     if isinstance(msg, ):...
    
    def __bitfields_sum(self):
        bitfields_sum = [0]*len(self.piece_manager.bitfield)
            
        for peer in self.peers_healthy:
            for index, bitfield in enumerate(peer.bitfield):
                bitfields_sum[index] += bitfield
            
            
        return bitfields_sum 
                
    

    def __update_rarest(self):
        '''
            Update the rarest pieces
        '''
        bitfields_sum = self.__bitfields_sum()
        rarest = [(index, bitfield) for index, bitfield in enumerate(bitfields_sum)]
        self.rarest = sorted(rarest, key=lambda x: x[1])

    
    
    # def select_piece(self,first_time=True, number_of_downloads=4):
    #     result_list=[]
    #     blocked_piece={}
    #     blocked_peer={}
    #     if first_time:
    #         for current_time in number_of_downloads:
                
    #             current_tuple=self.random_piece_selector(blocked_piece,blocked_peer)
    #             result_list.append(current_tuple)
    #             blocked_piece[current_tuple[0]]=current_tuple[0]
    #             blocked_peer[current_tuple[1]]=current_tuple[1]
        
    #         self.rarest_piece_selector(blocked_piece,blocked_peer)
            
    #     else:
            
    #         for item in self.peers_download:
    #             blocked_peer=self.peers_download[item[0]]
    #             blocked_piece=self.peers_download[item[1]]
    #         for _ in range(number_of_downloads):
                
    #             current_tuple=self.rarest_piece_selector(blocked_piece,blocked_peer)
    #             result_list.append(current_tuple)
    #             blocked_piece[current_tuple[0]]=current_tuple[0]
    #             blocked_peer[current_tuple[1]]=current_tuple[1]
            

                
    #     return result_list
    
    # def update_bitfield(self):
    #     have_it_list=[]
        
    #     result_list=TorrentClient.sum_bitfields(self.peers,have_it_list)
        
    #     self.rares_list=result_list
    #     self.have_it_list=have_it_list
    

    # def relay_messages(self, peer: Peer):
    #     socket = peer.socket
    #     if not peer.handshaked:
    #         self.__do_handshake(peer)
    #     else:
    #         pass
            
   


    

