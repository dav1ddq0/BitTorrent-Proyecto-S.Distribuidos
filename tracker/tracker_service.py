from typing import Any, Union

import rpyc

import globals_tracker

from .chord.server_config import TRACKER_PORT
from .tracker_logger import logger


class TrackerService(rpyc.Service):
    def on_connect(self, conn):
        self.remote_ip = conn._config["endpoints"][1][0]
        return super().on_connect(conn)

    def get_node(self) -> None:
        self.chord_node = globals_tracker.my_node

    def exposed_find_peers(self, request: dict[str, Any]) -> dict[Any]:
        info_hash = request["info_hash"]
        peer_id = request["peer_id"]
        listeng_port = request["port"]
        event = request["event"]
        left = request["left"]

        stopped = True if event == "stopped" else False
        completed = False
        complete = 0
        incomplete = 0

        if not stopped:
            if event == "completed":
                completed = True
                complete += 1
                incomplete -= 1

            if event == "started":
                if left:
                    incomplete += 1
                    
                else: 
                    complete += 1
                    completed = True

        peer_info = { "ip": self.remote_ip, "port": listeng_port, "peer_id": peer_id, "completed": completed }
        self.chord_node.store_key(info_hash, peer_info, complete, incomplete, stopped)

        info_hash_value = int.from_bytes(info_hash, byteorder='big')
        values = self.chord_node.find_key(info_hash_value)
        filt_peers = [value for key, value in values['peers'].items() if key != peer_id]

        response = {
            'complete': values['complete'],
            'incomplete': values['incomplete'],
            'peers': filt_peers
                }

        logger.info("Tracker response is %s", response)
        return response

class TrackerConnection:
    def __init__(self, node_ip: str, port: int = TRACKER_PORT):
        self.node_ip = node_ip
        self.port = port
        self.conn: Union[rpyc.Connection, None] = None

    def __enter__(self):
        try:
            self.conn = rpyc.connect(self.node_ip, self.port)
            self.conn.root.get_node()
            return self.conn.root

        except:
            logger.error(
                f"address {self.node_ip} is not hosting any tracker-DHT service. Unable to stablish connection"
            )

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
