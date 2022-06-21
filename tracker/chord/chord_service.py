import hashlib
from typing import Union
import rpyc
from .peer_info import PeerInfo
from .chord_logger import logger
from .server_config import SERVER_PORT, CHORD_NODE_PORT

class ChordService(rpyc.Service):

    """Our implementation of a chord alg"""

    def on_connect(self, conn):
        if 'initialized' not in self.__dict__:
            server_addr = conn.__dict__["endpoints"][0]
            self.tracker_ip = server_addr[0]
            self.tracker_port = SERVER_PORT
            self.tracker_hash: bytes = hashlib.sha1(f"{self.tracker_ip}:{SERVER_PORT}".encode()).digest()
            self.finger_table = self.__initialize_fingers()
            self.dht: dict[bytes, list[PeerInfo]] = {}
            self.next_to_fix: int = 0
            self.initialized = True
            self.config = {'allow_public_attrs': True}
            self.__create_ring()

        logger.info("Chord node with ip %s joined the ring", conn._config["endpoints"][1])
        return super().on_connect(conn)

    def on_disconnect(self, conn):
        logger.info("Chord node with ip %s left the ring", conn._config["endpoints"][1])
        return super().on_disconnect(conn)

    def exposed_notify(self, new_node_ip: str, new_node_hash: bytes) -> None:
        if not self.predecessor_ip or (self.predecessor_hash and ChordService.in_range_excl(
            int.from_bytes(new_node_hash, "big"),
            int.from_bytes(self.predecessor_hash, "big"),
            int.from_bytes(self.tracker_hash, "big"),
        )):
            self.predecessor_ip = new_node_ip
            self.predecessor_hash = new_node_hash

    def exposed_find_successor(self, identifier: bytes) -> Union[tuple[str, bytes], Exception]:
        if (
            ChordService.in_range_incl(
                int.from_bytes(identifier, "big"),
                int.from_bytes(self.tracker_hash, "big"),
                int.from_bytes(self.successor_hash, "big"),
            )
            or self.tracker_ip == self.successor_ip
        ):
            return self.successor_ip, self.successor_hash

        prev_node_ip = self.__closest_prec_node(identifier)

        try:
            conn = rpyc.connect(prev_node_ip, CHORD_NODE_PORT, config=self.config)
            serv_mngr = conn.root

        except ConnectionError as conn_err:
            logger.exception('Unable to stablish connection with the chord node service with ip %s, host unreachable. Closest preceding node unreachable', prev_node_ip)
            return conn_err

        return serv_mngr.find_successor(identifier)

    def exposed_join(self, new_node_ip: str) -> None:
        self.predecessor_ip = None

        try:
            conn = rpyc.connect(new_node_ip, CHORD_NODE_PORT, config=self.config)
            service_mangr = conn.root
            self.successor_ip, self.successor_hash = conn.find_successor(service_mangr.tracker_hash)
        
        except ConnectionError as conn_err:
            logger.exception('Unable to stablish connection with the chord node service with ip %s, host unreachable. Join operation failed', new_node_ip)

    def __create_ring(self) -> None:
        self.predecessor_ip = None
        self.predecessor_hash = None
        self.successor_ip = self.tracker_ip
        self.successor_hash = self.tracker_hash

    def __closest_prec_node(self, identifier) -> str:
        for i in range(len(self.finger_table) - 1, 0, -1):
            finger_i = self.finger_table[i]
            if ChordService.in_range_excl(
                int.from_bytes(finger_i.node_hash, "big"),
                int.from_bytes(self.tracker_hash, "big"),
                int.from_bytes(identifier, "big"),
            ):
                return finger_i.node_ip
        return self.tracker_ip

    def __initialize_fingers(self):
        table = [FingerTableItem(1, '', b'')]
        hash_int_val = int.from_bytes(self.tracker_hash, "big")
        for i in range(1, 161):
            finger_int = (hash_int_val + 2 ** (i - 1)) % (2**160)
            table.append(FingerTableItem(finger_int, self.tracker_ip, self.tracker_hash))

        return table

    def __stabilize(self) -> None:
        try:
            conn1 = rpyc.connect(self.successor_ip, CHORD_NODE_PORT, config=self.config)
            serv_mngr = conn1.root

        except ConnectionError as conn_err:
            logger.exception('Unable to stablish connection to the chord node service, host unreachable. Stabilize operation failed', self.successor_ip)
            return

        try:
            conn2 = rpyc.connect(serv_mngr.predecessor_ip, CHORD_NODE_PORT, config=self.config)
            serv_mngr = conn2.root
            x = serv_mngr.root

        except:
            logger.exception('Unable to stablish connection to the chord node service, host unreachable. Stabilize operation failed', serv_mngr.predecessor_ip)
            return
           
        if (
            ChordService.in_range_excl(
                int.from_bytes(x.tracker_hash, "big"),
                int.from_bytes(self.tracker_hash, "big"),
                int.from_bytes(self.successor_hash, "big"),
            )
            or self.successor_ip == self.tracker_ip
        ):
            self.successor_ip = x.tracker_ip
            self.successor_hash = x.successor_hash

        if not self.tracker_ip == self.successor_ip:
            try:
                conn = rpyc.connect(self.successor_ip, CHORD_NODE_PORT, config=self.config)
                serv_mngr = conn.root
                serv_mngr.notify(self.tracker_hash)

            except:
                print('Unable to stablish connection to the chord node service, host unreachable. Stabilize operation failed')

    def __fix_fingers(self): 
        self.next_to_fix += 1
        if self.next_to_fix > len(self.finger_table) - 1:
            self.next_to_fix = 1

        hash_int_val = int.from_bytes(self.tracker_hash, "big")
        finger_hash = self.finger_table[self.next_to_fix].start.to_bytes(
            hash_int_val.bit_length(), "big"
        )

        finger_successor = self.exposed_find_successor(finger_hash)
        if isinstance(finger_successor, Exception):
            logger.warning('finger %s of node with hash %s impossible to fix at the moment, retrying later', self.next_to_fix, self.tracker_hash)
            return

        else:
            self.finger_table[self.next_to_fix].node_ip = finger_successor[0] 
            self.finger_table[self.next_to_fix].node_hash = finger_successor[1] 
            logger.info('finger %s of node with hash %s fixed', self.next_to_fix, self.tracker_hash)
    
    def __check_predecessor(self):
        pass

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


class FingerTableItem:

    """Our implementation of a finger table item"""

    def __init__(self, start: int, node_ip: str, node_hash: bytes):
        self.start = start
        self.node_ip = node_ip
        self.node_hash = node_hash
