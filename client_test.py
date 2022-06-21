import rpyc
import socket
from rpyc.utils.server import ThreadedServer
from tracker import TrackerService
from random import randint
from tracker import SERVER_PORT, CHORD_NODE_PORT, RETRY_INTERVAL, CONNECT_TIMEOUT
from testing_logger import logger

def main():
    client_ip = socket.gethostbyname(socket.gethostname())
    client_ip_hunk1, client_ip_hunk2, client_ip_hunk3, _ = client_ip.split('.')

    first_server_last_hunk = 0
    second_server_last_hunk = 0

    connections: list[str] = []

    host1_ip = None
    host2_ip = None
    
    while len(connections) < 4:
        for ip_last_hunk in range(1, 256):
            host1_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
            if host1_ip != client_ip:
                try:
                    conn1 = rpyc.connect(host1_ip, CHORD_NODE_PORT)
                    server1 = conn1.root
                    first_server_last_hunk = ip_last_hunk
                    logger.info(f"Connection with tracker service hosted at {host1_ip} stablished")
                    break
                except:
                    logger.error(f"address {host1_ip} is not hosting any tracker service. Unable to stablish connection")

        for ip_last_hunk in range(1, 256):
            host2_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
            if host2_ip != client_ip and host1_ip and host1_ip != host2_ip:
                try:
                    conn2 = rpyc.connect(host2_ip, CHORD_NODE_PORT)
                    server2 = conn2.root
                    second_server_last_hunk = ip_last_hunk
                    logger.info(f"Connection with tracker service hosted at {host2_ip} stablished")
                    break
                except:
                    logger.error(f"address {host2_ip} is not hosting any tracker service. Unable to stablish connection")
        connections.append(f'{host1_ip}-{host2_ip}')
            
if __name__ == '__main__':
    main()
