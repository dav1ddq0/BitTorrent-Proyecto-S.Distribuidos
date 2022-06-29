from concurrent.futures import ThreadPoolExecutor, thread
from threading import Thread
from typing import Set
from piece import Piece
from peer import Peer
from torrent_settings import READ_BUFFER_SIZE, LEN__BUFFER_SIZE
import logging
import errno
import socket
from message import *
from piece_manager import PieceManager
import struct
from connection_info import ConnectionInfo
from message import HandshakeMessage, message_dispatcher, PieceMessage, BitfieldMessage, KeepAliveMessage
import threading
import time


class TorrentServer(Thread):

    def __init__(self, torrent_info, piece_manager, host, port, peer_id):
        Thread.__init__(self)
        self.peer_id = peer_id
        self.torrent_info = torrent_info
        self.info_hash = torrent_info.info_hash
        self.host = host
        self.port = port
        self.logger = self._setup_logger()
        self.connections = []
       
        # number of peers downloading the piece i
        self.downloading_pieces: list[set]=  []
        self.piece_manager: PieceManager = piece_manager
        
        self.__server_socket: socket.socket = self._setup_server_socket()
            
        new_tread = threading.Thread(self._manage_incoming_connections())
        new_tread.start()
        
        

    def _manage_incoming_connections(self):
        with ThreadPoolExecutor() as executor:
            while 1:
                # accept connections from outside
                connection, address = self.__server_socket.accept()

                # connection.settimeout(20)
                self.logger.debug(f"New connection accepted:{address}")
                connection_info = ConnectionInfo(connection, address, False)
                self.connections.append(connection_info)
                executor.submit(self.relay_messages, connection_info)

    def _do_handshake(self, connection_info: ConnectionInfo):
        socket = connection_info.connection
        buffer = socket.recv(LEN__BUFFER_SIZE)
        if len(buffer) < 0:
            return False
        size = struct.unpack('>I', buffer)[0]

        payload = socket.recv(size)
        if len(payload) != size:
           return False
        else:
            buffer = socket.recv(READ_BUFFER_SIZE)
            try:
                handshake = HandshakeMessage.unpack_message(buffer)
                logging.debug(f"Handshake message received from peer {handshake.peer_id}")
                
            except Exception as e:
                logging.error(f"Error unpacking handshake message: {e}")
                return False
            request_handshake_msg = HandshakeMessage(self.info_hash, self.peer_id)
            socket.send(request_handshake_msg.message())
            ok_recv = connection_info.connection.recv(READ_BUFFER_SIZE)
            if ok_recv.decode('utf-8') == "Handshake OK":
                logging.debug('Handshake OK')
                connection_info.handshaked = True
                connection_info.peer_id = handshake.peer_id
                # send bitfield 
            else:
                logging.warning('Handshake not OK')
                return False
            
            return True

    def _setup_server_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a well-known port
        server_socket.bind((self.host, self.port))
        # become a server socket
        server_socket.listen(5)
        # server_socket.setblocking(False)
        self.logger.debug(f"Server listening on {self.host}:{self.port}")
        return server_socket

    def send_to_socket(self, socket: socket.socket, msg: Message):
        socket.send(msg.message)

    def read_message(self, socket:socket.socket)-> Message | None:
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

    def relay_messages(self, connection_info: ConnectionInfo):
        while 1:
            if not connection_info.handshaked:
                if not self._do_handshake(connection_info):
                    self.logger.warning(f"Handshake failed for {connection_info.address}")
                    # close connection
                    break
                else: 
                    # send bitfield
                    connection_info.connection.send(BitfieldMessage(self.piece_manager.bitfield).message())
            
            else: 
                msg = self.read_message(connection_info.connection)
                if msg:
                    # self.logger.warning(f"Connection closed by {connection_info.address}")
                    # break
                    connection_info.last_call = time.time()
                    self.logger.debug(f"{msg.name} received from {connection_info.address}")
                    # message_dispatcher(msg, self, connection_info)
                    if isinstance(msg, RequestMessage):
                        if connection_info.peer_id not in self.downloading_pieces[msg.piece_index]:
                            self.downloading_pieces[msg.piece_index].add(connection_info.peer_id)
                        block = self.piece_manager.get_block_piece(msg.index, msg.begin, msg.length)
                        connection_info.connection.send(PieceMessage(msg.index, msg.begin, block).message())
                    elif isinstance(msg, KeepAliveMessage):
                        pass
                    elif isinstance(msg, HaveMessage):
                        self.downloading_pieces.remove(connection_info.peer_id)
                        if len(self.downloading_pieces[msg.piece_index]) == 0:
                            self.piece_manager.clean_memory(msg.piece_index)

                        
                else:
                    self.logger.exception('Not is a valid message')
            if time.time() - connection_info.last_call > 20:
                self.logger.warning(f"Connection closed by {connection_info.address}")
                connection_info.connection.send('Close connection'.encode('utf-8'))
                time.sleep(5)
                connection_info.connection.close()
                break
    
    
    

        
    # def read_message(self, connection_info: ConnectionInfo):
    #     data = b''
    #     while 1:
    #         try:
    #             if connection_info.handshaked:
                    

                    
    #         except socket.error as e:
    #             err = e.args[0]
    #             if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
    #                 logging.debug("Wrong errno {}".format(err))
    #             break
    #         except Exception:
    #             logging.exception("Recv failed")
    #             break

    #     return data

    
    def _setup_logger(self):
        logger = logging.getLogger(f'Server {self.peer_id}')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
        return logger