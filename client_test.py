import rpyc
import socket
# from tracker.tracker_service import TrackerService
from tracker.chord import SERVER_PORT, CHORD_NODE_PORT, RETRY_INTERVAL, CONNECT_TIMEOUT
from testing_logger import logger

def main():
    client_ip = socket.gethostbyname(socket.gethostname())
    client_ip_hunk1, client_ip_hunk2, client_ip_hunk3, _ = client_ip.split('.')

    connections: list[str] = []

    host1_ip = None
    host2_ip = None

    server1 = None
    server2 = None

    # //\\// Connect Chord Nodes //\\//

    while len(connections) < 1:
        for ip_last_hunk in range(1, 256):
            host1_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
            if host1_ip != client_ip:
                try:
                    chord_conn1 = rpyc.connect(host1_ip, CHORD_NODE_PORT, config={'allow_public_attrs': True})
                    server1 = chord_conn1.root
                    logger.info(f"Connection with tracker-DHT service hosted at {host1_ip} stablished")
                    break
                except:
                    logger.error(f"address {host1_ip} is not hosting any tracker-DHT service. Unable to stablish connection")

        for ip_last_hunk in range(1, 256):
            host2_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
            if host2_ip != client_ip and host1_ip and host1_ip != host2_ip:
                try:
                    chord_conn2 = rpyc.connect(host2_ip, CHORD_NODE_PORT, config={'allow_public_attrs': True})
                    server2 = chord_conn2.root
                    logger.info(f"Connection with tracker-DHT service hosted at {host2_ip} stablished")
                    break
                except:
                    logger.error(f"address {host2_ip} is not hosting any tracker-DHT service. Unable to stablish connection")

        if server1 and server2:
            server1.register(host1_ip)
            server2.register(host2_ip)
            server1.join(host2_ip)
            connections.append(f'{host1_ip}-{host2_ip}')

if __name__ == '__main__':
    main()
