from rpyc.utils.server import ThreadedServer
from tracker import TrackerService
from tracker.chord import SERVER_PORT

main_server = ThreadedServer(TrackerService, hostname="0.0.0.0", port=SERVER_PORT, protocol_config={'allow_public_attrs': True})
print("Bittorrent tracker service running on 0.0.0.0:8001")
main_server.start()
