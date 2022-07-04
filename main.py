from piece_manager import PieceManager
from dottorrent  import TorrentCreator, TorrentReader
from torrent_info import TorrentInfo
from torrent_server import TorrentServer
from torrent_settings import PIECE_SIZE_1MB
#from torrent_server import TorrentServer
from torrent_client import TorrentClient
import hashlib
import time
import socket
import sys
from tools import next_free_port, get_mac_address


def main():
    # torrent_creator = TorrentCreator('./test/fedora36.mp4',PIECE_SIZE_1MB, False, ['172.17.0.2:8001'], 'a', 'a')
    # torrent_creator.create_dottorrent_file('./')
    torrent_reader = TorrentReader('./fedora36.torrent', './test')
    torrent_info = torrent_reader.build_torrent_info()
    # print(torrent_creator.filename)
    # print(torrent_creator.file_size)
    piece_manager = PieceManager(torrent_info)
    peer_id = hashlib.sha1(get_mac_address().encode()).digest()
    # print(peer_id)
    # print(get_mac_address())
    # server = TorrentServer(torrent_info, piece_manager,'127.0.0.1', 4800, peer_id)
    # server.start()
    listening_port = next_free_port(6200, 6999)
    host = socket.gethostbyname(socket.gethostname())
    server = TorrentServer(torrent_info, piece_manager, host, listening_port, peer_id)
    server.start()
    client = TorrentClient(torrent_info, piece_manager, peer_id, listening_port)
    client.start()
    #print(torrent_obj.the_file_is_complete())
    # torrent_obj.check_local_pieces()
    # print(torrent_obj.download_completed)
    # torrent_obj.write_to_disk_test('/home/dquesada/Downloads')
    


if __name__ == '__main__':
    main()
