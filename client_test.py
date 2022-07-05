import socket
import time
from hashlib import sha1

from dottorrent import TorrentCreator, TorrentReader
from piece_manager import PieceManager
from torrent_client import TorrentClient
from torrent_settings import PIECE_SIZE_1MB

# from tracker.tracker_service import TrackerService
from tracker.chord import (
    CHORD_NODE_PORT,
    CONNECT_TIMEOUT,
    RETRY_INTERVAL,
    TRACKER_PORT,
    ChordConnection,
)
from tracker.tracker_logger import logger
from tracker.tracker_service import TrackerConnection


def main():
    # creator = TorrentCreator(
    #     "./test/video_test.mp4",
    #     PIECE_SIZE_1MB,
    #     True,
    #     [f"172.17.0.3:f{TRACKER_PORT}"],
    #     "Torrent para probar",
    #     "El Javi",
    # )
    # creator.create_dottorrent_file("./test")

    # reader = TorrentReader("./test/video_test.torrent")
    # meta_info = reader.build_torrent_info()

    # piece_mngr = PieceManager(meta_info)
    # peer_id = sha1(("juanito").encode("utf-8")).digest()
    # torr_client = TorrentClient(meta_info, piece_mngr, peer_id, "6500")

    # for tracker in meta_info.trackers:
    #     with TrackerConnection(tracker["ip"], tracker["port"]) as tracker_conn:
    #         tracker_conn.find_peers(torr_client.tracker_request_params("started"))

    key_strings = [
        "David",
        "Julio",
        "Javier",
        "Camilo",
        "Timon",
        "Alfonso",
        "Milena",
        "Helena",
        "Eduardo",
        "Juancho",
        "Máximo",
        "Jefferson",
        "Brayan",
        "Antonio",
        "Sergio",
    ]
    data = [
        {
            "ip": "123.0.0.1",
            "port": 123,
            "peer_id": "123ed",
            "completed": False,
        },
        {
            "ip": "123.0.0.22",
            "port": 123,
            "peer_id": "tgar45",
            "completed": False,
        },
        {
            "ip": "123.0.0.4",
            "port": 123,
            "peer_id": "fdyhn35",
            "completed": False,
        },
        {
            "ip": "123.0.0.5",
            "port": 123,
            "peer_id": "guriefh244",
            "completed": False,
        },
        {
            "ip": "123.0.0.6",
            "port": 123,
            "peer_id": "ifeui4",
            "completed": False,
        },
        {
            "ip": "123.0.0.7",
            "port": 123,
            "peer_id": "cxvbh4432",
            "completed": False,
        },
        {
            "ip": "123.0.0.8",
            "port": 123,
            "peer_id": "zncbxnz5",
            "completed": False,
        },
        {
            "ip": "123.0.0.24",
            "port": 123,
            "peer_id": "suidhaih",
            "completed": False,
        },
        {
            "ip": "123.0.0.68",
            "port": 123,
            "peer_id": "yfhnxm8",
            "completed": False,
        },
        {
            "ip": "123.0.0.16",
            "port": 123,
            "peer_id": "thyvdoi7",
            "completed": False,
        },
        {
            "ip": "123.0.0.98",
            "port": 123,
            "peer_id": "8475djb",
            "completed": False,
        },
        {
            "ip": "123.0.0.52",
            "port": 123,
            "peer_id": "8zxc6c7sh",
            "completed": False,
        },
        {
            "ip": "123.0.0.78",
            "port": 123,
            "peer_id": "nvhfyreus7",
            "completed": False,
        },
        {
            "ip": "123.0.0.81",
            "port": 123,
            "peer_id": "7n37bf",
            "completed": False,
        },
        {
            "ip": "123.0.0.97",
            "port": 123,
            "peer_id": "cuvd789wnh",
            "completed": False,
        },
    ]

    dummy_info_hashes = [
        sha1(key_str.encode("utf-8")).digest()
        for key_str in key_strings
    ]

    client_ip = socket.gethostbyname(socket.gethostname())
    client_ip_hunk1, client_ip_hunk2, client_ip_hunk3, _ = client_ip.split('.')

    connections: list[str] = []

    host1_ip = None

    # # //\\// Connect Chord Nodes //\\//

    server_ip = "172.17.0.2:8001"
    while len(connections) < 3:
        with ChordConnection(server_ip) as server_conn:
            for ip_last_hunk in range(3, 6):
                host1_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
                if host1_ip != client_ip:
                    with ChordConnection(host1_ip) as chord_conn1:
                        if chord_conn1:
                            chord_conn1.join(server_ip)
                            connections.append(f"{host1_ip} --------------------> {server_ip}")
                            logger.info("Tracker with ip %s joined Tracker with ip %s", host1_ip, server_ip)
                            time.sleep(5)

                        else: continue


    time.sleep(5)
    logger.info("Storing keys in chord ring")

    for info_hash, value in zip(dummy_info_hashes, data):
        with ChordConnection(server_ip) as server_conn:
            server_conn.store_key(info_hash, value, 0, 0, False)
            logger.info("Key %s stored", info_hash)
            time.sleep(5)

if __name__ == "__main__":
    main()
