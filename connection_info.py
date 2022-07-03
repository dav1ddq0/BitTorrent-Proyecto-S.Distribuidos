import errno
from socket import socket
import struct
from bclient_logger import logger
from torrent_settings import READ_BUFFER_SIZE
from message import HandshakeMessage, WrongMessageException, message_dispatcher
import socket
import time
class ConnectionInfo:

    def __init__(self, connection: socket.socket, hostaddr, port):
        self.connection = connection
        self.handshaked = False
        self.hostaddr = hostaddr
        self.port = port
        self.peer_id = None
        self.last_call = 0.0
        self.read_buffer = b''
        self.connection_lost = False
    
    def send(self, msg):
        try:
            self.connection.send(msg)
            self.last_call = time.time()
        except Exception as e:
            logger.error(f"Failed to send message to peer : {self.hostaddr}")

    def read(self):
        # print("AQUI ENRTRO READ1")
        counter = 0
        while 1:
            # print(f"CICLO WHILE{counter}")
            try:
                #print("AQUI ENRTRO READ2")
                buff = self.connection.recv(READ_BUFFER_SIZE)
                print(len(buff))
                if len(buff) <= 0:
                    logger.debug('No buffer')
                    break

                self.read_buffer += buff
                #print(f"Read_buffer {len(self.read_buffer)}")
            except socket.error as e:
                self.connection_lost = True
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    logger.debug(f"Wrong errno {err}")
                
                break
            except Exception:
                logger.exception("Recv failed")
                break
            # counter +=1
        
    
    def get_messages(self):
        if len(self.read_buffer) > 4 :
            if not self.handshaked:
                try:
                    handshake_message = HandshakeMessage.unpack_message(self.read_buffer)
                    self.handshaked = True
                    self.read_buffer = self.read_buffer[handshake_message.total_len:]
                    logger.debug(f'Handshake Message received frorm {self.hostaddr}')
                    self.peer_id = handshake_message.peer_id
                    return handshake_message

                except Exception:
                    logger.exception("First message should always be a handshake message")
                    self.read_buffer = b''
                    return None
            else:
                payload_length, = struct.unpack(">I", self.read_buffer[:4])
                total_length = payload_length + 4

                if len(self.read_buffer) < total_length:
                    return  None
                else:
                    payload = self.read_buffer[:total_length]
                    self.read_buffer = self.read_buffer[total_length:]

                try:
                    received_message = message_dispatcher(payload)
                    if received_message:
                        return received_message
                except WrongMessageException as e:
                    logger.exception(e.error_info)
        return None
        

