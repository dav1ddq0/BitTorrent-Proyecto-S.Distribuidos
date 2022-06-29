import socket
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
    SERVER_PORT,
    ChordConnection,
)
from tracker.tracker_logger import logger
from tracker.tracker_service import TrackerConnection


def main():
    creator = TorrentCreator(
        "./test/video_test.mp4",
        PIECE_SIZE_1MB,
        True,
        [f"172.17.0.3:f{SERVER_PORT}"],
        "Torrent para probar",
        "El Javi",
    )
    creator.create_dottorrent_file("./test")

    reader = TorrentReader("./test/video_test.torrent")
    meta_info = reader.build_torrent_info()

    piece_mngr = PieceManager(meta_info)
    peer_id = sha1(("juanito").encode("utf-8")).digest()
    torr_client = TorrentClient(meta_info, piece_mngr, peer_id, "6500")

    for tracker in meta_info.trackers:
        with TrackerConnection(tracker["ip"], tracker["port"]) as tracker_conn:
            tracker_conn.find_peers(torr_client.tracker_request_params("started"))

    # client_ip = socket.gethostbyname(socket.gethostname())
    # client_ip_hunk1, client_ip_hunk2, client_ip_hunk3, _ = client_ip.split('.')

    # connections: list[str] = []

    # host1_ip = None

    # # //\\// Connect Chord Nodes //\\//

    # server_ip = "172.17.0.2"
    # while len(connections) < 2:
    #     with ChordConnection(server_ip) as server_conn:
    #         for ip_last_hunk in range(3, 10):
    #             host1_ip = f"{client_ip_hunk1}.{client_ip_hunk2}.{client_ip_hunk3}.{ip_last_hunk}"
    #             if host1_ip != client_ip:
    #                 with ChordConnection(host1_ip) as chord_conn1:
    #                     if chord_conn1:
    #                         chord_conn1.join(server_ip)
    #                         connections.append(f"{host1_ip} --------------------> {server_ip}")
    #                         logger.info("Tracker with ip %s joined Tracker with ip %s", host1_ip, server_ip)

    #                     else: continue


if __name__ == "__main__":
    main()
