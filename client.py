from concurrent.futures import ThreadPoolExecutor
import hashlib
import socket
import time
from torrent_reader import TorrentReader
import logging


class ClientBitTorrent:
    
    def __init__(self, ip, lport, sport):
        self.torrents_info = {}
        self.listen_socket = self.setup_lsocket(ip, lport)
        self.send_socket = self.setup_ssocket()
        self.used_ports = []
        self.used_ports.append(lport)
        self.connections = []
        self.peer_id = hashlib.sha1(str(time.time()).encode('utf-8')).digest()


    
    def load_dottorrent(self, path, save_at = '~/Downloads'):
        reader = TorrentReader(path, save_at)
        reader.read()
        torrent_info = reader.build_torrent_info()
        self.torrents_info[torrent_info.info_hash] = torrent_info
    
    def get_torrent_info(self, info_hash):
        return self.torrents_info[info_hash]
    
    def start_listening(self):
        while True:
            self.logger.info("Chat server is running!")
            with ThreadPoolExecutor(max_workers=128) as executor:
                while 1:
                    conn, addr = self.sock.accept()
                    self.logger.debug(f"New connection accpeted:{addr}")
                self.connections.append(conn)
                executor.submit(self.relay_messages, conn, addr)

    def relay_messages(self, conn, addr):
        data =  None
        while True:
            data += conn.recv(1024)
            if not data:
                break
            
            
        conn.close()
        self.connections.remove(conn)
        self.logger.debug(f"Connection closed: {addr}")

    

    def setup_lsocket(self, ip , port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((ip, port))
        sock.listen()
        return sock
    
    def setup_ssocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock
    



        



