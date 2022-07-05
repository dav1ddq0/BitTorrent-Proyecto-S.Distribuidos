from concurrent.futures import ThreadPoolExecutor, thread
from threading import Thread, Timer
from typing import Set
from block import Block
from piece import Piece
from peer import Peer
from torrent_settings import READ_BUFFER_SIZE, LEN__BUFFER_SIZE
import logging
import errno
from threading import Thread
import socket
from message import *
from piece_manager import PieceManager
import struct
from connection_info import ConnectionInfo
from message import HandshakeMessage, message_dispatcher, PieceMessage, BitfieldMessage, KeepAliveMessage
import time
from bclient_logger import logger


class TorrentServer(Thread):

    def __init__(self, torrent_info, piece_manager, ip, port, peer_id):
        Thread.__init__(self)
        self.peer_id = peer_id
        self.torrent_info = torrent_info
        self.info_hash = torrent_info.info_hash
        self.host = ip
        self.port = port
        self.connections: list['ConnectionInfo'] = []
        self.piece_manager = piece_manager

        # number of peers downloading the piece i
        self.downloading_pieces: list[set] = [set() for _ in range(self.piece_manager.number_of_pieces)]
        self.piece_manager: PieceManager = piece_manager

        self.__server_socket: socket.socket = self.__setup_server_socket()

        # self._manage_incoming_connections()


    def __cleaner(self):
        for i in range(self.piece_manager.number_of_pieces):
            if len(self.downloading_pieces[i]) == 0:
                self.piece_manager.clean_memory(i)

    def run(self):
        logger.info("RUN SERVER ....")
        self.__manage_incoming_connections()
        Timer(20, self.__cleaner, ()).start()

    def __manage_incoming_connections(self):
        while 1:
            # accept connections from outside
            connection, address = self.__server_socket.accept()
            # accept returns a new socket and, "initially all sockets are in blocking mode."
            # So you need to add a connection.setblocking(0) right after the accept call returns.
            connection.setblocking(False)
            # connection.settimeout(20):
            logger.debug(f"New connection accepted:{address}")
            connection_info = ConnectionInfo(connection, address[0], address[1])
            self.connections.append(connection_info)
            Thread(target = self.relay_messages, args = (connection_info,)).start()

    

    def __setup_server_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a well-known port
        server_socket.bind((self.host, self.port))
        # become a server socket
        server_socket.listen(5)
        # server_socket.setblocking(False)
        logger.debug(f"Server  listening on {self.host}:{self.port}")
        return server_socket

    def relay_messages(self, connection_info: ConnectionInfo):
        
        while 1:            
            connection_info.read()
            # if connection_info.connection_lost:
            #     connection_info.connection.close()
            #     self.connections.remove(connection_info)
            #     break
            
            msg =  connection_info.get_message()
            if msg: 
                connection_info.last_call = time.time()
                logger.debug(f"{msg.name} received from server {connection_info.hostaddr}")
                if isinstance(msg, HandshakeMessage):
                    try:
                        handshake_msg = HandshakeMessage(self.info_hash, self.peer_id)
                        connection_info.send(handshake_msg.message(), handshake_msg.name)
                    except:
                        connection_info.connection_lost = True
                        connection_info.connection.close()

                elif isinstance(msg, RequestMessage): 
                    if connection_info.peer_id not in self.downloading_pieces[msg.index]:
                        self.downloading_pieces[msg.index].add(connection_info.peer_id)
                    block: 'Block' = self.piece_manager.get_block_piece(msg.index, msg.begin)
                    try:
                        print("Pepito vende tomales")
                        piece_msg = PieceMessage(msg.index, msg.begin, block.data)
                        print("Se le acabaron los tamales a Pepito")
                        connection_info.send(piece_msg.message(), piece_msg.name)
                    except:
                        pass
                        # connection_info.connection_lost = True
                        # connection_info.connection.close()
                elif isinstance(msg, KeepAliveMessage):
                    pass
                elif isinstance(msg, BitfieldMessage):
                    pass
                elif isinstance(msg, PieceMessage):
                    pass
                elif isinstance(msg, HaveMessage):
                    self.downloading_pieces.remove(connection_info.peer_id)
                    if len(self.downloading_pieces[msg.piece_index]) == 0:
                        self.piece_manager.clean_memory(msg.piece_index)
                elif isinstance(msg, CancelMessage):
                    pass
                elif isinstance(msg, InfoMessage):
                    if msg.info == "Closed connection":
                        connection_info.connection.close()
                        time.sleep(0.15)
                        self.connections.remove(connection_info)
                        break
                    elif msg.info == "Update Bitfield":
                        bitfield_msg = BitfieldMessage(self.piece_manager.bitfield)
                        try:
                            connection_info.send(bitfield_msg.message(), bitfield_msg.name)
                        except:
                            connection_info.connection_lost = True
                            connection_info.connection.close()
                            
                    elif msg.info == "Handshake OK":
                        connection_info.handshaked = True
                        bitfield_msg = BitfieldMessage(self.piece_manager.bitfield)
                        connection_info.send(bitfield_msg.message(), bitfield_msg.name)
                else:
                    logger.exception('Is not a valid message')
                
            # else:
            #     logger.exception('Is not a valid message')
            # if time.time() - connection_info.last_call > 20:
            #     logger.warning(f"Connection closed {connection_info.hostaddr}")
            #     connection_info.send(InfoMessage("Closed connection").message(), "Connection closed")
            #     time.sleep(5)
            #     connection_info.connection.close()
            #     break
    
