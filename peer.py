import socket
import logging
import time

class Peer:
    def __init__(self, ip, port=6881):
        self.last_call = 0.0
        self.ip = ip
        self.port = port
        self.socket =  None
        self.healthy_status = False
    
    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port), timeout=1)
            self.socket.setblocking(False)
            logging.debug(f"Connected to peer ip: {self.ip} - port: {self.port}")
            self.healthy_status = True

        except Exception as e:
            print(f"Failed to connect to peer (ip: {self.ip} - port: {self.port} - {str(e)})")
            return False

        return True

    def send_msg(self, msg):
        try:
            self.socket.send(msg)
            self.last_call = time.time()
        except Exception as e:
            self.healthy_status = False
            logging.error(f"Failed to send message to peer : {str(e)}")
    