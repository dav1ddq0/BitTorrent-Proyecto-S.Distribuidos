from concurrent.futures import ThreadPoolExecutor
from threading import Thread
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


class TorrentServer(Thread):

    def __init__(self, torrent_info, piece_manager, host, port, peer_id):
        Thread.__init__(self)
        self.connections = []
        self.logger = self._setup_logger()
        self.piece_manager: PieceManager = piece_manager
        self.torrent_info = torrent_info
        self.info_hash = torrent_info.info_hash
        self.host = host
        self.port = port
        self.__server_socket: socket.socket = self._setup_server_socket()
        self.peer_id = peer_id
        self._manage_incoming_connections()
        
        
        

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

    def relay_messages(self, connection_info: ConnectionInfo):
        while 1:
            payload = self.read_message(connection_info.connection)
            if payload:
                try:
                    msg = message_dispatcher(payload)
                    if isinstance(msg, RequestMessage):
                        block = self.piece_manager.get_block_piece(msg.index, msg.begin, msg.length)
                        connection_info.connection.send(PieceMessage(msg.index, msg.begin, block).message)
                    if isinstance(msg, KeepAliveMessage):
                        ...
                    
                except:
                    logging.exception('Not is a valid message')

        self.connections.remove(connection_info)
        connection_info.connection.close()
        logging.debug(f"Connection closed:{connection_info.address}")

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

    def read_message(self, connection_info: ConnectionInfo):
        data = b''
        while 1:
            try:
                if connection_info.handshaked:
                    buffer = connection_info.connection.recv(LEN__BUFFER_SIZE)
                    if len(buffer) < 0:
                        break
                    size = struct.unpack('>I', buffer)[0]
                   
                    payload = connection_info.connection.recv(size)
                    if len(payload) == size:
                        data = payload 
                        break
                else:
                    buffer = connection_info.connection.recv(READ_BUFFER_SIZE)
                    try:
                        handshake = HandshakeMessage.unpack_message(buffer)
                        logging.error(f"Handshake message received from peer {handshake.peer_id}")
                        
                    except Exception as e:
                        logging.error(f"Error unpacking handshake message: {e}")
                        break
                    request_handshake_msg = HandshakeMessage(self.info_hash, self.peer_id)
                    connection_info.connection.send(request_handshake_msg.message)
                    ok_recv = connection_info.connection.recv(READ_BUFFER_SIZE)
                    if ok_recv.decode('utf-8') == "Handshake OK":
                        logging.debug('Handshake OK')
                        connection_info.handshaked = True
                        # send bitfield 
                    else:
                        logging.warning('Handshake not OK')
                        break
                    # send bitfield
                    connection_info.connection.send(BitfieldMessage(self.piece_manager.bitfield))

                    
            except socket.error as e:
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    logging.debug("Wrong errno {}".format(err))
                break
            except Exception:
                logging.exception("Recv failed")
                break

        return data

    
    def _setup_logger(self):
        logger = logging.getLogger('chat server')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
        return logger