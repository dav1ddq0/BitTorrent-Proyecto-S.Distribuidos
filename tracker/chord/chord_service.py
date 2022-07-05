from concurrent.futures import thread
import copy
from hashlib import sha1
from threading import Timer
import threading
from typing import Any, Union

import rpyc

import globals_tracker
from tools import rpyc_deep_copy
from tracker.chord.peer_info import PeerInfo
from tracker.chord.server_config import CHORD_NODE_PORT
from tracker.tracker_logger import logger
import time

class ChordService(rpyc.Service):
    def get_node(self) -> None:
        self.chord_node: ChordNode = globals_tracker.my_node

    def exposed_join(self, node_ip_port: str) -> None:
        self.chord_node.join(node_ip_port)

    def exposed_find_successor(self, node_val: int) -> str:
        return self.chord_node.find_successor(int(node_val))

    def exposed_get_predecessor(self) -> Union[str, None]:
        return self.chord_node.predecessor

    def exposed_notify(self, node_ip_port: str):
        self.chord_node.notify(node_ip_port)

    def exposed_find_key(self, key: bytes) -> list[Any]:
        return self.chord_node.find_key(key)

    def exposed_store_key(
        self, key: bytes, value: Any, complete: int, incomplete: int, stopped: bool
    ):
        return self.chord_node.store_key(key, value, complete, incomplete, stopped)

    def exposed_get_dht(self):
        return self.chord_node.dht

    def exposed_get_replica_dht(self):
        return self.chord_node.replica_dht

    def exposed_get_replica_nodes(self):
        return self.chord_node.replica_nodes

    # retorna la lista de succesores para actualizar el metodo 1 de replicacion
    def exposed_get_successors(self):
        return self.chord_node.successors_list

    # devuelve el hash del nodo
    def exposed_get_hash_val(self):
        return self.chord_node.node_val


class ChordConnection:
    def __init__(self, node_ip_port: str):
        self.node_ip = node_ip_port.split(":")[0]
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
        self.node_ip_port: str = f"{node_ip}:{CHORD_NODE_PORT}"
        self.node_val: int = hash_str(self.node_ip_port)
        self.predecessor: str = ""
        self.successor: str = self.node_ip_port
        self.dht: dict[int, dict[str, Any]] = {}
        self.next_to_fix: int = 0
        self.finger_table: list[str] = [""] * 161
        # news
        self.successors_list = []
        self.replication_factor = 3
        self.replica_dht: dict[int, dict[str, Any]] = {}
        self.replica_nodes = []
        self.start_time=time.time()
        self.run_bg_tasks()
        time.sleep(5)
        self.temporal_succ_check()
        time.sleep(6)
        self.temporal_back_replication()
        time.sleep(7)
        self.temporal_foward_replication()
        self.print_dhts()

    def run_bg_tasks(self):
        self.stabilize()
        self.fix_fingers()
        self.check_predecessor()
            
        Timer(1/200, self.run_bg_tasks, []).start() 

    

        
    def temporal_succ_check(self):
        
        
        print("Entro a revisar predeccesor dentro de temporal_succ_check.")
        self.check_successor()
        Timer(5, self.temporal_succ_check, []).start() 
        
    def temporal_back_replication(self):
        
        print("Entro a revisar predeccesor dentro de temporal_succ_check.")
        self.update_predecessor_dht()
        
        Timer(5, self.temporal_back_replication, []).start()
        
    def temporal_foward_replication(self):
        
        print("Entro a revisar predeccesor dentro de temporal_succ_check.")
        self.replicate_keys()
        
        Timer(5, self.temporal_foward_replication, []).start()

    def find_successor(self, value: int) -> str:
        if (
            ChordNode.in_range_incl(value, self.node_val, hash_str(self.successor))
            or self.node_ip_port == self.successor
        ):
            return self.successor

        else:
            closest_node = self.closest_prec_node(value)

            if closest_node == self.node_ip_port:
                return self.node_ip_port

            with ChordConnection(closest_node) as chord_conn:
                try:
                    successor = chord_conn.find_successor(value)
                    return successor
                except:
                    pass

    def closest_prec_node(self, value: int) -> str:
        for i in range(len(self.finger_table) - 1, 0, -1):
            finger_i = self.finger_table[i]
            if ChordNode.in_range_excl(hash_str(finger_i), self.node_val, value):
                return finger_i

        return self.node_ip_port

    def join(self, other_node_ip: str) -> None:
        logger.info(
            "Node with ip %s will be joining the ring in which the node with ip %s is",
            self.node_ip_port,
            other_node_ip,
        )
        self.predecessor = ""

        with ChordConnection(other_node_ip) as chord_conn:
            if not chord_conn:
                print("El nodo "+str(other_node_ip) +"no esta disponible")
                return
            successor = chord_conn.find_successor(self.node_val)
            logger.info("I will be joining via %s", successor)
            self.successor = successor

    def stabilize(self) -> None:
        if self.successor == self.node_ip_port:
            if self.predecessor:
                # logger.info("My successor is my predecessor %s", self.predecessor)
                self.successor = self.predecessor

                with ChordConnection(self.successor) as chord_conn:
                    if chord_conn:
                        chord_conn.notify(self.node_ip_port)
                        
                        

        else:
            with ChordConnection(self.successor) as chord_conn:
                
                if not chord_conn:
                    return
                successor_predecessor = chord_conn.get_predecessor()
                # logger.info("My successor's predecessor is %s", successor_predecessor)
                if successor_predecessor and successor_predecessor != self.node_ip_port and ChordNode.in_range_excl(
                    hash_str(successor_predecessor),#b
                    self.node_val,#c
                    hash_str(self.successor), #a
                ):

                    # logger.info(
                    #     "My successor is my successor's predecessor %s",
                    #     successor_predecessor,
                    # )
                    self.successor = successor_predecessor
                try:
                    chord_conn.notify(self.node_ip_port)
                except:
                    pass

    def notify(self, node_ip_port: str) -> None:
        if not self.predecessor or ChordNode.in_range_excl(
            hash_str(node_ip_port), hash_str(self.predecessor), self.node_val
        ):

            # logger.info("My predecessor is %s", new_node_ip)
            self.predecessor = node_ip_port

    def fix_fingers(self) -> None:
        self.next_to_fix += 1
        if self.next_to_fix > len(self.finger_table) - 1:
            self.next_to_fix = 1

        finger_val = (self.node_val + (1 << (self.next_to_fix - 1))) % (2 << 160)
        self.finger_table[self.next_to_fix] = self.find_successor(finger_val)
        # logger.info(f"Fixing finger {self.next_to_fix} with value {finger_val} of node {self.node_val}")

    def check_predecessor(self):
        if self.predecessor:
            try:
                rpyc.connect(self.predecessor.split(":")[0], CHORD_NODE_PORT)

            except ConnectionError as conn_err:
                logger.error("Predecessor failed with error message %s", conn_err)
                self.predecessor = ""

    def store_key(
        self,
        key: bytes,
        value: dict[str, Any],
        complete: int,
        incomplete: int,
        stopped: bool,
    ):
        decoded_info_hash = int.from_bytes(key, byteorder="big")
        key_successor = self.find_successor(decoded_info_hash)
        peer_id = value["peer_id"]

        if key_successor == self.node_ip_port:
            logger.info(
                "Storing key %s in node with val %s", decoded_info_hash, self.node_val
            )
            if decoded_info_hash in self.dht:
                if not peer_id in self.dht[decoded_info_hash]:
                    self.dht[decoded_info_hash]["peers"][peer_id] = value

            else:
                self.dht[decoded_info_hash] = {
                    "peers": {peer_id: value},
                    "complete": 0,
                    "incomplete": 0,
                }

            self.dht[decoded_info_hash]["complete"] += complete
            self.dht[decoded_info_hash]["incomplete"] += incomplete

            completed = self.dht[decoded_info_hash]["peers"][peer_id]["completed"]
            if stopped:
                if completed:
                    self.dht[decoded_info_hash]["complete"] -= 1

                else:
                    self.dht[decoded_info_hash]["incomplete"] -= 1

        else:
            with ChordConnection(key_successor) as chord_conn:
                if chord_conn:
                    chord_conn.store_key(key, value, complete, incomplete, stopped)
                else: 
                    #javijavijavijavi
                    print("El nodo mas cercano a "+str(key_successor) +"no esta disponible, se reinviara en unos instantes.")
                    threading.Thread(target=self.fail_store_key, args=(key, value, complete, incomplete, stopped)).start()
                    
    def fail_store_key(
        self,
        key: bytes,
        value: dict[str, Any],
        complete: int,
        incomplete: int,
        stopped: bool,
    ):
        time.sleep(1)
        self.store_key(key,value,complete,incomplete,stopped)
    
    def find_key(self, key: bytes) -> dict[str, dict]:
        decoded_info_hash = int.from_bytes(key, byteorder="big")
        succesor = self.find_successor(decoded_info_hash)

        if succesor == self.node_ip_port:
            if decoded_info_hash in self.dht:
                logger.info("Key %s founded in node %s", key, self.node_ip_port)
                return self.dht[decoded_info_hash]

            else:
                logger.error("Key does not exist, operation failed")

        else:
            with ChordConnection(succesor) as chord_conn:
                if chord_conn:
                    return chord_conn.find_key(key)
                else: 
                    return self.fail_find_key(key)

    def fail_find_key( self, key: bytes,):
        time.sleep(1/100)
        self.find_key(key)

    def print_dhts(self):
        for item in self.dht:
            print(f"\n{item} is stored in {self.node_val} dht")
        
        for item in self.replica_dht:
            print(f"\n{item} is stored in {self.node_val} replica dht ")

        logger.info("%s node successor is %s", self.node_ip_port, self.successor)
        logger.info("%s node predecesor is %s", self.node_ip_port, self.predecessor)

        Timer(10, self.print_dhts, []).start()

    # ffffffffffffffffffffff
    # en este metodo se va a revisar si el succesor existe, de no ser asi se elimina como sucesor y se llaman a los metodos de union al anillo
    def check_successor(self):
        if self.successor == self.node_ip_port:
            print(str(self.node_ip_port)+" is my ip. In my own succesor.")
            return
        with ChordConnection(self.successor) as chord_conn:
            if not chord_conn:
                logger.info(
                    "Node with ip %s is unreacheable.",
                    self.successor,
                )
                print("My succesor fell down. I am calling the union method.")
                self.fix_successor_on_failure()

            else:
                succ_ip_port=chord_conn.get_successors()
                print("My succesor is "+ str(succ_ip_port) + " . I am calling the fix succesor method.")
                self.fix_successors()

    # busca por la lista de sucesores para actualizar su sucesor, si no logra conectarse a ninguno lo busca por la finger table
    def fix_successor_on_failure(self):
        delete_list = []
        for item in self.successors_list:
            with ChordConnection(item) as chord_conn:
                if chord_conn:
                    self.successor = item
                    print("Im"+str(self.node_ip_port) +" succesor is "+ str(item) + " from my succesor-list. ")
                    break
                else:
                    delete_list.append(item)
                    print("This Node is not accesible "+ str(item) +".")

        if len(self.successors_list) == len(delete_list):
            # como la recorremos?
            for i in range(len(self.finger_table)):
                if self.node_ip_port == self.finger_table[i]:
                    continue

                with ChordConnection(self.finger_table[i]) as chord_conn:
                    if not chord_conn:
                        print("This Node is not accesible "+ str(item) +".")
                        continue

                    else:
                        self.successor = self.finger_table[i]
                        print("Im"+str(self.node_ip_port) +" succesor is "+ str(item) + " from my finger. ")
                        break

        for item in delete_list:
            self.successors_list.remove(item)
            logger.info(
                "Node with ip %s is unreacheable. Will be deleted from the successors list.",
                item,
            )
        # aca aplicar la busqueda de succesors mediante la finger table

        self.fix_successors()

    # en este metodo se le pide al succesor su lista de sucesores, y se actualiza la nueva lista
    # fffffffffffffffffff
    def fix_successors(self):
        if self.successor == self.node_ip_port:
            self.successors_list = []
            return

        with ChordConnection(self.successor) as chord_conn:
            succ_list = chord_conn.get_successors()
            real_succ_list = rpyc_deep_copy(succ_list)
            real_succ_list.insert(0, self.successor)

            while len(real_succ_list) > self.replication_factor:
                real_succ_list.pop(len(real_succ_list) - 1)

            self.successors_list = real_succ_list
            
            #borrarte en caso de que estes en la lista
            try:
                self.successors_list.remove(self.node_ip_port)
            except:
                pass
            
            #borrar los caidos
            delete_list = []
            for item in self.successors_list:
                with ChordConnection(self.successor) as chord_conn:
                    if not chord_conn:
                        print("This Node is not accesible "+ str(item) +".")
                        delete_list.append(item)
            
            for item in delete_list:
                self.successors_list.remove(item)

            # logger
            i = 0
            for item in self.successors_list:
                logger.info(
                    "My succesor in %s is %s.",
                    i,
                    item,
                )
                i += 1

    # en los tres metodos el nodo se conecta a su predecessor y le pide la info para guardarla 
    def replicate_keys(self):
        with ChordConnection(self.predecessor) as chord_conn:
            if not chord_conn:
                return
            temp_pred_dht=None
            pred_dht=None
            temp_pred_dht_replic=None
            pred_dht_replica=None
            temp_pred_marks=None
            pred_replica_nodes=None
            temp_pred_hash=None
            pred_hash=None
            
            try:
                # los valores del nodo K-1
                temp_pred_dht = chord_conn.get_dht()
                pred_dht = rpyc_deep_copy(temp_pred_dht)
            except:
                print("No logre copiar de mi sucesor su dht (replicacion hacia delante).")
                return
            try:
                # los valores del los otros predecesores
                temp_pred_dht_replic = chord_conn.get_replica_dht()
                pred_dht_replica = rpyc_deep_copy(temp_pred_dht_replic)
            except:
                print("No logre copiar de mi sucesor su replica dht (replicacion hacia delante)")
                return
            try:
                # la lista de marcas de hash de predecesores
                temp_pred_marks = chord_conn.get_replica_nodes()
                pred_replica_nodes = rpyc_deep_copy(temp_pred_marks)
            except:
                print("No logre copiar de mi sucesor su replica nodes (replicacion hacia delante)")
                return
            try:
                temp_pred_hash = chord_conn.get_hash_val()
                pred_hash = rpyc_deep_copy(temp_pred_hash)
            except:
                print("No logre copiar de mi sucesor su hash_val (replicacion hacia delante)")
                return

            # aca actualizamos la lista de hash de los k predecesores para la replicacion
            pred_replica_nodes.insert(0, pred_hash)
            while self.replication_factor <= len(pred_replica_nodes):
                pred_replica_nodes.pop()

            i = 0
            for item in self.successors_list:
                logger.info(
                    "My predecesor hash-node in %s is %s.",
                    i,
                    item,
                )
                i += 1

            self.replica_nodes = pred_replica_nodes

            if not self.replica_dht:
                self.replica_dht = pred_dht

            else:
                # esto puede manejarse de otra forma quizas
                for item in pred_dht:
                    self.replica_dht[item] = pred_dht[item]

                for item in pred_dht_replica:
                    self.replica_dht[item] = pred_dht_replica[item]

                for item in self.successors_list:
                    logger.info(
                        "Adde in my replica-dht %s.",
                        item,
                    )

                self.delete_remaining_keys()

    def delete_remaining_keys(self):
        delete_list = []
        if not self.replica_nodes:
            return
        
        for item in self.replica_nodes:
            logger.info(
                " %s are my replica nodes.",
                item,
            )
        # arreglar el manejo con la congruencia
        for item in self.replica_dht:
            if not self.in_range_incl(item, self.replica_nodes[-1], self.node_val):
                delete_list.append(item)

        for item in delete_list:
            del self.replica_dht[item]
            logger.info(
                "Delete %s from my replica-dht.",
                item,
            )




        for item in self.dht:
            if item < self.replica_nodes[-1]:
                self.replica_dht[item] = self.replica_dht[item]
                delete_list = item
                logger.info(
                    "Moved %s from my dht to my replica-dht.",
                    item,
                )

            #for item in self.successors_list:
            #    logger.info(
            #        "Moved %s from my dht to my replica-dht.",
            #        item,
            #    )

        for item in delete_list:
            del self.dht[item]

    # este metodo se encarga de actualizar las replicas de los nodos direccion succ->pred
    def update_predecessor_dht(self):
        if self.successor == self.node_ip_port:
            self.successors_list = []
            return

        with ChordConnection(self.successor) as chord_conn:
            if not chord_conn:
                return
            temp_suc_dht_replic=None
            suc_dht_replic = None
            temp_suc_dht=None
            suc_dht=None
            temp_pred_marks=None
            pred_marks=None
            try:
                temp_suc_dht_replic = chord_conn.get_replica_dht()
                suc_dht_replic = rpyc_deep_copy(temp_suc_dht_replic)
            except:
                print("No logre copiar de mi sucesor su replica-dht (replicacion hacia atras)")
                return

            try:
                temp_suc_dht = chord_conn.get_dht()
                suc_dht = rpyc_deep_copy(temp_suc_dht)
            except:
                print("No logre copiar de mi sucesor su dht (replicacion hacia atras)")
                return

            try:
                temp_pred_marks = chord_conn.get_replica_nodes()
                pred_marks = rpyc_deep_copy(temp_pred_marks)
            except:
                print("No logre copiar de mi sucesor su replica nodes (replicacion hacia atras)")
                return

            for item in suc_dht:
                if self.in_range_incl(
                    item,
                    len(
                        self.replica_nodes[len(self.replica_nodes) - 1],
                        self.node_val,
                    ),
                ):
                    if item not in self.dht:
                        self.dht[item] = suc_dht[item]

            for item in suc_dht_replic:
                if self.in_range_incl(
                    item,
                    len(
                        self.replica_nodes[len(self.replica_nodes) - 1],
                        self.node_val,
                    ),
                ):
                    if item not in self.dht:
                        self.dht[item] = suc_dht[item]

                        logger.info(
                            "Added in my dht %s.",
                            item,
                        )

                    elif self.in_range_incl(
                        item, len(self.replica_nodes[0], self.node_val)
                    ):
                        if item not in self.replica_dht:
                            self.replica_dht[item] = suc_dht[item]

                            logger.info(
                                "Added in my dht %s.",
                                item,
                            )

            self.delete_remaining_keys()

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
