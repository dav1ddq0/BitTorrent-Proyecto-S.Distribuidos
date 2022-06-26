from piece_manager import PieceManager
from torrent_creator import TorrentCreator
from torrent_reader import TorrentReader
from torrent_info import TorrentInfo
from torrent_server import TorrentServer
from torrent_client import TorrentClient
import hashlib
import time


def main():
    #torrent_creator = TorrentCreator('./test/fedora36.mp4', 524288, False, ['1www.tracker-run.com', 'www.2h3.xyz'], 'a', 'a')
    # torrent_creator.create_dottorrent_file('./')
    torrent_reader = TorrentReader('./test/fedora36.torrent', './test')
    torrent_info = torrent_reader.build_torrent_info()
    piece_manager = PieceManager(torrent_info)
    peer_id = hashlib.sha1(str(time.time()).encode('utf-8')).digest()
    server = TorrentServer(torrent_info, piece_manager,
                           '127.0.0.1', 4800, peer_id)
    server.start()
    client = TorrentClient(torrent_info, piece_manager, peer_id)
    client.start()
    client.add_peer('127.0.0.1', 4800, peer_id)
    # print(torrent_obj.the_file_is_complete())
    # torrent_obj.check_local_pieces()
    # print(torrent_obj.download_completed)
    # torrent_obj.write_to_disk_test('/home/dquesada/Downloads')

    b = '.'


if __name__ == '__main__':
    main()
