from hashlib import sha1
import threading
from rpyc.utils.server import ThreadedServer
from tracker.chord import ChordService, ChordNode, CHORD_NODE_PORT  
import socket
import globals_tracker
from tracker.chord.server_config import TRACKER_PORT
from tracker.tracker_service import TrackerService

host_ip = socket.gethostbyname(socket.gethostname())
tracker_service = ThreadedServer(TrackerService, hostname=host_ip, port=TRACKER_PORT, protocol_config={'allow_public_attrs': True})
chord_service = ThreadedServer(ChordService, hostname=host_ip, port=CHORD_NODE_PORT, protocol_config={'allow_public_attrs': True})
t1 = threading.Thread(target=tracker_service.start)
t2 = threading.Thread(target=chord_service.start)
globals_tracker.my_node = ChordNode(host_ip)
print(f"Bittorrent tracker-DHT service running on {host_ip}:{TRACKER_PORT}, with value {globals_tracker.my_node.node_val}")

t1.start()
t2.start()
