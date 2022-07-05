import errno
from socket import socket
import struct
from bclient_logger import logger
from torrent_settings import READ_BUFFER_SIZE
from message import HandshakeMessage, Message, WrongMessageException, message_dispatcher
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
    
    def send(self, msg: bytes, type_msg:str):
        try:
            print(f"Intentando enviar {type_msg} con tamagno {len(msg)} :()")
            self.connection.send(msg)
            self.last_call = time.time()
            time.sleep(0.5)
            logger.debug(f"Sending {type_msg} from server to {self.hostaddr}")
        
        except Exception as e:
            logger.error(f"Failed to send {type_msg} message to peer : {self.hostaddr}")
            raise Exception

    def read(self):
        while 1:
            try:
                buff = self.connection.recv(READ_BUFFER_SIZE)
                if not buff:
                    break

                self.read_buffer += buff
            except socket.error as e:
                self.connection_lost = True
                err = e.args[0]
                if err != errno.EAGAIN or err != errno.EWOULDBLOCK:
                    ...
                    # logger.debug(f"Wrong errno {err}")
                
                break
            except Exception:
                logger.exception("Recv failed")
                break
          
        
    
    def get_message(self):
        if len(self.read_buffer) > 4 :
            if not self.handshaked and len(self.read_buffer) >= HandshakeMessage.total_len:
                try:
                    handshake_message = HandshakeMessage.unpack_message(self.read_buffer[:HandshakeMessage.total_len])
                    self.handshaked = True
                    self.read_buffer = self.read_buffer[handshake_message.total_len:]
                    self.peer_id = handshake_message.peer_id
                    return handshake_message

                except Exception:
                    logger.exception("First message should always be a handshake message")
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
        

