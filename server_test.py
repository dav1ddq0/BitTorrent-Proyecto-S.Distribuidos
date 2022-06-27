from rpyc.utils.server import ThreadedServer
from tracker.chord import ChordService, CHORD_NODE_PORT  
import socket

host_ip = socket.gethostbyname(socket.gethostname())
main_server = ThreadedServer(ChordService, hostname=host_ip, port=CHORD_NODE_PORT, protocol_config={'allow_public_attrs': True})
print(f"Bittorrent tracker-DHT service running on {host_ip}:{CHORD_NODE_PORT}")
main_server.start()
