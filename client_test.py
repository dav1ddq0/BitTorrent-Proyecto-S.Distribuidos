import rpyc
from rpyc.utils.server import ThreadedServer
from tracker import TrackerService
from random import randint
from tracker import SERVER_PORT, CHORD_NODE_PORT, RETRY_INTERVAL, CONNECT_TIMEOUT

def main():

    trackers_amount = 3
    trackers = []

    for i in range(trackers_amount):
        ip_hunk1 = randint(1, 255)
        ip_hunk2 = randint(1, 255)
        ip_hunk3 = randint(1, 255)
        ip_hunk4 = randint(1, 255)
        ip = f"{ip_hunk1}.{ip_hunk2}.{ip_hunk3}.{ip_hunk4}"

        new_tracker_server = ThreadedServer(TrackerService, hostname="0.0.0.1", port=SERVER_PORT, protocol_config={'allow_public_attrs': True})
        new_tracker_server.start()
        trackers.append(new_tracker_server)

    first_to_connect = trackers[1]
    rpyc.connect("0.0.0.0", 8002)

if __name__ == '__main__':
    main()
