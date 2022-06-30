from hashlib import sha1
from threading import Timer
from typing import Any, Union

import rpyc

import globals_tracker
from tracker.chord.peer_info import PeerInfo
from tracker.chord.server_config import CHORD_NODE_PORT
from tracker.tracker_logger import logger


class ChordService(rpyc.Service):
    def get_node(self) -> None:
        self.chord_node: ChordNode = globals_tracker.my_node

    def exposed_join(self, node_ip: str) -> None:
        self.chord_node.join(node_ip)

    def exposed_find_successor(self, node_val: int) -> str:
        return self.chord_node.find_successor(int(node_val))

    def exposed_get_predecessor(self) -> Union[str, None]:
        return self.chord_node.predecessor

    def exposed_notify(self, node_ip: str):
        self.chord_node.notify(node_ip)

    def exposed_find_key(self, key: str) -> list[Any]:
        return self.chord_node.find_key(key)

    def exposed_store_key(self, key: str, value: Any):
        return self.chord_node.store_key(key, value)


class ChordConnection:
    def __init__(self, node_ip: str):
        self.node_ip = node_ip
        self.conn: Union[rpyc.Connection, None] = None

    def __enter__(self):
        try:
            self.conn = rpyc.connect(self.node_ip, CHORD_NODE_PORT)
            self.conn.root.get_node()
            return self.conn.root

        except:
            logger.error(
                f"address {self.node_ip} is not hosting any tracker-DHT service. Unable to stablish connection"
            )

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()


def hash_str(val: str):
    hashed = sha1(val.encode("utf-8")).digest()
    return int.from_bytes(hashed, byteorder="big")


class ChordNode:

    """Our implementation of a chord node"""

    def __init__(self, node_ip: str):
        self.node_ip: str = node_ip
        self.node_val: int = hash_str(self.node_ip)
        self.predecessor: str = ""
        self.successor: str = node_ip
        self.dht: dict[int, dict[str, Any]] = {}
        self.next_to_fix: int = 0
        self.finger_table: list[str] = [""] * 161
        self.run_bg_tasks()

    def run_bg_tasks(self):
        self.stabilize()
        self.fix_fingers()
        self.check_predecessor()
        Timer(1, self.run_bg_tasks, []).start()

    # def log_info(self):
    #     logger.info(
    #         "Current succesor's ip is %s and current predecessor's ip is %s",
    #         self.successor,
    #         self.predecessor,
    #     )

    def find_successor(self, node_val: int) -> str:
        if (
            ChordNode.in_range_incl(node_val, self.node_val, hash_str(self.successor))
            or self.node_ip == self.successor
        ):
            return self.successor

        else:
            closest_node = self.closest_prec_node(node_val)
            if closest_node == self.node_ip:
                return self.node_ip

            with ChordConnection(closest_node) as chord_conn:
                successor = chord_conn.find_successor(node_val)

            return successor

    def closest_prec_node(self, identifier) -> str:
        for i in range(len(self.finger_table) - 1, 0, -1):
            finger_i = self.finger_table[i]
            if ChordNode.in_range_excl(hash_str(finger_i), self.node_val, identifier):
                return finger_i

        return self.node_ip

    def join(self, other_node_ip: str) -> None:
        logger.info(
            "Node with ip %s will be joining the ring in which the node with ip %s is",
            self.node_ip,
            other_node_ip,
        )
        self.predecessor = ""

        with ChordConnection(other_node_ip) as chord_conn:
            successor = chord_conn.find_successor(self.node_val)

        self.successor = successor

    def stabilize(self) -> None:
        logger.info("Stabilizing %s", self.node_ip)
        if self.successor == self.node_ip:
            if self.predecessor:
                self.successor = self.predecessor

        else:
            with ChordConnection(self.successor) as chord_conn:
                successor_predecessor = chord_conn.get_predecessor()
                if successor_predecessor and ChordNode.in_range_excl(
                    hash_str(successor_predecessor),
                    self.node_val,
                    hash_str(self.successor),
                ):
                    self.successor = successor_predecessor

                logger.info("Notifying %s about %s", self.successor, self.node_ip)
                chord_conn.notify(self.node_ip)

    def notify(self, new_node_ip: str) -> None:
        if not self.predecessor or ChordNode.in_range_excl(
            hash_str(new_node_ip), hash_str(self.predecessor), self.node_val
        ):
            self.predecessor = new_node_ip

    def fix_fingers(self) -> None:
        self.next_to_fix += 1
        if self.next_to_fix > len(self.finger_table) - 1:
            self.next_to_fix = 1

        self.finger_table[self.next_to_fix] = self.find_successor(
            self.node_val + (1 << (self.next_to_fix - 1))
        )

    def check_predecessor(self):
        if self.predecessor:
            try:
                rpyc.connect(self.predecessor, CHORD_NODE_PORT)

            except ConnectionError as conn_err:
                logger.error("Predecessor failed with error message %s", conn_err)
                self.predecessor = ""

    def store_key(self, key: bytes, value: dict[str, Any], complete: int, incomplete: int, stopped: bool):
        decoded_info_hash = int.from_bytes(key, byteorder="big")
        succesor = self.find_successor(decoded_info_hash)
        peer_id = value["peer_id"]

        if succesor == self.node_ip:
            logger.info("Storing key %s in node %s", key, self.node_ip)
            if decoded_info_hash in self.dht:
                if not peer_id in self.dht[decoded_info_hash]:
                    self.dht[decoded_info_hash]["peers"][peer_id] = value

            else:
                self.dht[decoded_info_hash] = {
                    "peers": { peer_id: value },
                    "complete": 0,
                    "incomplete": 0,
                }

            self.dht[decoded_info_hash]["complete"] += complete
            self.dht[decoded_info_hash]["incomplete"] += incomplete

            completed = self.dht[decoded_info_hash]["peers"][peer_id]["completed"]
            if stopped:
                if completed:
                    self.dht[decoded_info_hash]["complete"] -= 1

                else: self.dht[decoded_info_hash]["incomplete"] -= 1

        else:
            with ChordConnection(succesor) as chord_conn:
                chord_conn.store_key(key, value, complete, incomplete, stopped)

    def find_key(self, key: bytes) -> dict[str, dict]:
        decoded_info_hash = int.from_bytes(key, byteorder="big")
        succesor = self.find_successor(decoded_info_hash)

        if succesor == self.node_ip:
            if decoded_info_hash in self.dht:
                logger.info("Key %s founded in node %s", key, self.node_ip)
                return self.dht[decoded_info_hash]

            else:
                logger.error("Key does not exist, operation failed")

        else:
            with ChordConnection(succesor) as chord_conn:
                return chord_conn.find_key(key)

    @staticmethod
    def in_range_excl(val: int, lower_b: int, upper_b: int):
        return lower_b < val < upper_b or (
            lower_b > upper_b and (val > lower_b or val < upper_b)
        )

    @staticmethod
    def in_range_incl(val: int, lower_b: int, upper_b: int):
        return lower_b < val <= upper_b or (
            lower_b > upper_b and (val > lower_b or val <= upper_b)
        )
