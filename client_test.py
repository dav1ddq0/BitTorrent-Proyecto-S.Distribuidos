import socket
# from tracker.tracker_service import TrackerService
from tracker.chord import ChordConnection, SERVER_PORT, CHORD_NODE_PORT, RETRY_INTERVAL, CONNECT_TIMEOUT
from tracker.tracker_logger import logger

def main():
    client_ip = socket.gethostbyname(socket.gethostname())
    client_ip_hunk1, client_ip_hunk2, client_ip_hunk3, _ = client_ip.split('.')

    connections: list[str] = []

    host1_ip = None

    # //\\// Connect Chord Nodes //\\//

    server_ip = "172.17.0.2"
    while len(connections) < 2:
        with ChordConnection(server_ip) as server_conn:
            for ip_last_hunk in range(3, 10):
                host1_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
                if host1_ip != client_ip:
                    with ChordConnection(host1_ip) as chord_conn1:
                        if chord_conn1:
                            chord_conn1.join(server_ip)
                            connections.append(f"{host1_ip} --------------------> {server_ip}")
                            logger.info("Tracker with ip %s joined Tracker with ip %s", host1_ip, server_ip)
                        
                        else: continue

if __name__ == '__main__':
    main()
