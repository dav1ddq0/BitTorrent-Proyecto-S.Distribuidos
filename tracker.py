import hashlib

import rpyc
from chord_node import ChordNode
from peer_info import PeerInfo
# from tracker_node import TrackerNode


class Tracker(rpyc.Service):

    """Bit-torrent tracker implementation"""

    def __init__(self, ip_addr: str, port: str):
        self.ip_addr: str = ip_addr
        self.port: str = port
        self.node_hash = self.__hash_node()
        self.chord_node = ChordNode(self.node_hash, self.ip_addr, self.port)

    def __hash_node(self) -> bytes:
        hash_object = hashlib.sha1(f"{self.ip_addr}:{self.port}".encode())
        return hash_object.digest()

    def on_connect(self, conn):
        return super().on_connect(conn)

    def on_disconnect(self, conn):
        return super().on_disconnect(conn)

    def exposed_find_peers(self, client_ip_addr: str, info_hash: bytes) -> list[PeerInfo]:
        pass

