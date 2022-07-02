from concurrent.futures import ThreadPoolExecutor, thread
from threading import Thread, Timer
from typing import Set
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
        self.connections = []
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
        print("RUN SERVER ....")
        self.__manage_incoming_connections()
        Timer(20, self.__cleaner, ()).start()

    def __manage_incoming_connections(self):
        # with ThreadPoolExecutor(128) as executor:
        while 1:
            print("DENTRO DEL WHILE INCOMING CONNECTIONS")
            # accept connections from outside
            connection, address = self.__server_socket.accept()
            # connection.settimeout(20)
            logger.debug(f"New connection accepted:{address}")
            connection_info = ConnectionInfo(connection, address[0], address[1])
            self.connections.append(connection_info)
            Thread(target = self.relay_messages, args = (connection_info,)).start()
            # executor.submit(self.relay_messages, connection_info)

    # def _do_handshake(self, connection_info: ConnectionInfo):
    #     socket = connection_info.connection
    #     buffer = socket.recv(LEN__BUFFER_SIZE)
    #     if len(buffer) < 0:
    #         return False
    #     size = struct.unpack('>I', buffer)[0]
    #     logger.debug("Message")
    #     payload = socket.recv(size)
    #     logger.debug(f"{len(payload)}")
    #     if len(payload) != size:
    #         logger.debug(f"EL payload tiene size distinto al {size}")
    #         return False
    #     else:
    #         buffer = socket.recv(READ_BUFFER_SIZE)
    #         try:
    #             handshake = HandshakeMessage.unpack_message(buffer)
    #             logger.debug(f"Handshake message received from peer {handshake.peer_id}")

    #         except Exception as e:
    #             logger.error(f"Error unpacking handshake message: {e}")
    #             return False
    #         request_handshake_msg = HandshakeMessage(
    #             self.info_hash, self.peer_id)
    #         socket.send(request_handshake_msg.message())
    #         ok_recv = connection_info.connection.recv(READ_BUFFER_SIZE)
    #         if ok_recv.decode('utf-8') == "Handshake OK":
    #             logger.debug('Handshake OK')
    #             connection_info.handshaked = True
    #             connection_info.peer_id = handshake.peer_id
    #             # send bitfield
    #         else:
    #             logging.warning('Handshake not OK')
    #             return False

    #         return True

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

    # def send_to_socket(self, socket: socket.socket, msg: Message):
    #     socket.send(msg.message)

    # def read_message(self, socket: socket.socket) -> Message | None:
    #     buffer = socket.recv(READ_BUFFER_SIZE)
    #     if len(buffer) < 0:
    #         return None
    #     size = struct.unpack('>I', buffer)[0]
    #     payload = socket.recv(size)
    #     if len(payload) != size:
    #         raise Exception(f'size {size}!= payload {payload}')
    #     try:
    #         msg = message_dispatcher(payload)
    #         return msg
    #     except WrongMessageException as e:
    #         logger(e.error_info)
    #         return None

    def relay_messages(self, connection_info: ConnectionInfo):
        while 1:
            print("DENTRO DEL WHILE 1")
            connection_info.read()
            print('2DANTE')
            msg =  connection_info.get_messages()
            print("ENTRE AQUI")
            connection_info.last_call = time.time()
            logger.debug(f"{msg.name} received from {connection_info.address}")
            if isinstance(msg, HandshakeMessage):
                connection_info.send(BitfieldMessage(self.piece_manager.bitfield).message())
            if isinstance(msg, RequestMessage): 
                if connection_info.peer_id not in self.downloading_pieces[msg.piece_index]:
                    self.downloading_pieces[msg.piece_index].add(connection_info.peer_id)
                    block = self.piece_manager.get_block_piece(msg.index, msg.begin, msg.length)
                    connection_info.send(PieceMessage(msg.index, msg.begin, block).message())
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
                    time.sleep(0.8)
                    self.connections.remove(connection_info)
                    break
                if msg.info == "Update Bitfield":
                    connection_info.send(BitfieldMessage(self.piece_manager.bitfield).message())
            
            else:
                logger.exception('Is not a valid message')
            # mg = connection_info.get_messages
            #    if msg:
                # self.logger.warning(f"Connection closed by {connection_info.address}")
                # break
                # connection_info.last_call = time.time()
               
                # message_dispatcher(msg, self, connection_info)
                
            
            if time.time() - connection_info.last_call > 20:
                logger.warning(f"Connection closed {connection_info.address}")
                connection_info.send(InfoMessage("Closed connection").message())
                time.sleep(5)
                connection_info.connection.close()
                break
    
