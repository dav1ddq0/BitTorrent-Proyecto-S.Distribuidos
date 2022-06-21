import hashlib
from threading import Thread

import rpyc
from rpyc.utils.server import ThreadedServer
from .chord.chord_service import ChordService
from .chord.peer_info import PeerInfo
from .chord.server_config import CHORD_NODE_PORT
from .tracker_logger import logger

class TrackerService(rpyc.Service):

    def on_connect(self, conn):
        if 'initialized' not in self.__dict__:
            server_addr = conn._config["endpoints"][0]
            self.ip_addr: str = server_addr[0]
            self.port: str = server_addr[1]
            self.node_hash = hashlib.sha1(f"{self.ip_addr}:{self.port}".encode()).digest()
            self.chord_service = ThreadedServer(ChordService, hostname=self.ip_addr, port=CHORD_NODE_PORT, protocol_config={'allow_public_attrs': True})
            self.chord_thread = Thread(target=self.chord_service.start, args=())
            self.chord_thread.start()
            self.initialized = True

        logger.info("Client node with ip %s connected", conn._config["endpoints"][1])
        return super().on_connect(conn)

    def on_disconnect(self, conn):
        logger.info("Client node with ip %s disconnected", conn._config["endpoints"][1])
        return super().on_disconnect(conn)

    # def exposed_find_peers(self, client_ip_addr: str, info_hash: bytes) -> list[PeerInfo]:
    #     pass
