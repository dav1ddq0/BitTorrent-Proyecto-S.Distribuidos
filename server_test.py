from rpyc.utils.server import ThreadedServer
from tracker.chord import ChordService, ChordNode, CHORD_NODE_PORT  
import socket
import globals_tracker

host_ip = socket.gethostbyname(socket.gethostname())
main_server = ThreadedServer(ChordService, hostname=host_ip, port=CHORD_NODE_PORT, protocol_config={'allow_public_attrs': True})
globals_tracker.my_node = ChordNode(host_ip)
print(f"Bittorrent tracker-DHT service running on {host_ip}:{CHORD_NODE_PORT}")
main_server.start()
