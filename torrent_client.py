from threading import Thread, Timer
import time
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
from tracker.chord.server_config import RETRY_INTERVAL

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

        self.event_completed = False
        self.rarest = [] # sorted list of the pieces that are rarest 
        self.started = True
        self.first_piece = True
    


    def run(self):
        Timer(1, self.__get_peers_from_tracker, ()).start()
        # Timer(20, self.__timer_intent_connect_peers,()).start()
        Timer(5, self.__download_piece,()).start()
        Timer(10, self.__put_peers_not_healthy_to_end,()).start()
        Timer(1, self.__rcv_messages,()).start()
        #Timer(5, self.__request_update_bitfield, ()).start()
        # Timer(10, self.__show_status, ()).start()

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
        with TrackerConnection(ip, port) as tracker_conn:
            if tracker_conn:
                response = tracker_conn.find_peers(self.__tracker_request_params(event))
                response_dc = rpyc_deep_copy(response)
                return response_dc
            return None
        
        
        

    def __request_update_bitfield(self):
        for peer in self.peers:
            if peer.healthy:
                try:
                    peer.send_msg(InfoMessage("Update Bitfield").message(), "Update Bitfield")
                except:
                    peer.connected = False
                    peer.healthy = False
        
        Timer(5, self.__request_update_bitfield, ()).start()

    def __get_peers_from_tracker(self):
        for ip, port in self.trackers:
            event = ''
            if self.started and not self.completed:
                event = 'started'
            if not self.started  and not self.event_completed and self.completed:
                event = 'completed'
                self.event_completed = True
            
            self.started = False
            tracker_response = self.__connect_tracker(ip, port, event)
            if tracker_response:
                peers_dict = tracker_response['peers']
                new_peers = []
                for peer_dict in peers_dict:
                    new_peer = Peer(peer_dict['ip'], peer_dict['port'],  peer_dict['peer_id'])
                    if new_peer not in self.peers:
                        logger.debug(f"Founded new peer: {new_peer}")
                        self.peers.append(new_peer)
                        new_peers.append(new_peer)
                self.__intent_connect_peers(new_peers)
            else:
                logger.debug(f"Tracker {ip}:{port} unreachable")

        Timer(5,self.__get_peers_from_tracker, ()).start()


    def __show_status(self):
        new_progession = 0
        for piece in self.piece_manager.pieces:
            if piece.is_completed:
                new_progession += piece.piece_size
            else:
                for block in piece.blocks:
                    if block.state == BlockState.BLOCK_FULL:
                        new_progession += block.block_size

        percentage_completed = float((float(new_progession) / self.piece_manager.file_size)*100)
        logger.info(f"Connected peers: {self.number_of_peers} - {percentage_completed} completed | {self.piece_manager.completed_pieces}/{self.piece_manager.number_of_pieces} pieces")
        Timer(10, self.__show_status, ()).start()
    
    def __timer_intent_connect_peers(self):
        self.__intent_connect_peers(self.peers)
        Timer(5,self.__timer_intent_connect_peers,()).start()

    def __intent_connect_peers(self, peers: list['Peer']):
        for peer in peers:
            if not peer.connected:
                #peer.socket.close()
                #peer.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # peer.socket.setblocking(False)
                #time.sleep(1)
                peer.connect()
                time.sleep(1)
                if peer.connected:
                    self.__do_handshake(peer)
                

    def __download_piece(self):
        if  not self.piece_manager.completed:
            if len(self.__pieces_being_downloaded) < 4:
                next_piece = self.__give_me_next_piece()
                
                available_peer = self.__find_available_peer(next_piece)
                if available_peer is not None:
                    self.__pieces_being_downloaded[next_piece] = available_peer
            for piece_index, peer in self.__pieces_being_downloaded.items():
                if peer.healthy:
                    logger.debug(f"Trying to download the piece {piece_index} from {peer.peer_id}")
                    self.__download_piece_from_peer(piece_index, peer)
        Timer(5, self.__download_piece, ()).start()
    
    def __download_piece_from_peer(self, piece_index: int, peer: Peer):
        piece = self.piece_manager.get_piece(piece_index)
        if piece is None:
            return
        begin_block, len_block  = piece.get_empty_block()
        try:
            request_msg = RequestMessage(piece_index, begin_block, len_block)
            time.sleep(1)
            peer.send_msg(request_msg.message(), request_msg.name)
        except:
            logger.debug(f"Error while sending request message to {peer.peer_id}")
            peer.healthy = False
            peer.connected = False

            return

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
            logger.debug(self.rarest)
            for piece_index,_ in self.rarest:
                if not self.piece_manager.pieces[piece_index].is_completed and piece_index not in self.__pieces_being_downloaded:
                    return piece_index
            


    def __get_random_piece(self):
        left = [piece.piece_index for piece in self.piece_manager.pieces if not piece.is_completed]
        random.shuffle(left)
        return left[0] if left else None
           
    def __do_handshake(self, peer: Peer):
        if not peer.handshaked:
            try:
                handshake_msg = HandshakeMessage(self.info_hash, self.peer_id)
                peer.send_msg(handshake_msg.message(), handshake_msg.name)
            except Exception:
                peer.healthy = False
                return False
        return True
            

    
    
    def __rcv_messages(self):
        '''
            Receive messages from peers
        '''
        print(len(self.peers))
        for peer in self.peers:
            if peer.connected:
                # print("ME trabo aqui")
                peer.read()
                msg = peer.get_message()
                if msg:
                    logger.debug(f"{msg.name} message received from client {peer.ip}")
                    if isinstance(msg, HandshakeMessage):
                        if peer.handshaked:
                            logger.debug(f"{peer.ip} already handshaked")
                        if msg.peer_id != peer.peer_id:
                            logger.error(f"{msg.peer_id} != {peer.peer_id} Don't match peer_id of de handshake with that the tracker give")
                            try:
                                time.sleep(1)
                                peer.send_msg(InfoMessage("Closed Connection").message(), "Closed Connection")
                            except Exception:
                                peer.healthy = False
                                peer.handshaked = False
                                
                            time.sleep(0.15)
                            peer.healthy = False
                            peer.socket.close()
                        else:
                            logger.debug(f"Handshake with {peer.ip} OK")
                            peer.handshaked = True
                            peer.healthy = True
                            try:
                                time.sleep(0.1)
                                peer.send_msg(InfoMessage("Handshake OK").message(), "Handshake OK")  
                            except:
                                peer.connected = False
                                peer.healthy = False
                                peer.handshaked = False
                    elif not peer.handshaked:
                        logger.error(f"Expected Handshake Message")
                    
                    elif isinstance(msg, BitfieldMessage):
                        '''
                            If the peer send a bitfield message, we update the bitfield of the peer
                        '''
                        logger.debug(f"Bitfield message received from peer {peer.peer_id}")
                        peer.has_bitfield = True
                        peer.bitfield = msg.bitfield
                        self.__update_rarest()
                    elif isinstance(msg, PieceMessage):
                        '''
                            If the peer send a piece message, we write the piece block to the piece manager
                        '''
                        logger.debug(f"Piece message of piece {msg.index} received from peer {peer.peer_id} ")
                        self.piece_manager.receive_block_piece(msg.index, msg.begin, msg.block)
                    
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
        
        Timer(1,self.__rcv_messages,()).start()
    
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
            
   


    

