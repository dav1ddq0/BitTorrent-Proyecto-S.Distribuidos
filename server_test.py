from rpyc.utils.server import ThreadedServer
from tracker import TrackerService
from tracker.chord import SERVER_PORT
import socket

host_ip = socket.gethostbyname(socket.gethostname())
main_server = ThreadedServer(TrackerService, hostname=host_ip, port=SERVER_PORT, protocol_config={'allow_public_attrs': True})
print("Bittorrent tracker service running on 0.0.0.0:8001")
main_server.start()
