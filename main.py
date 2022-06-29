from piece_manager import PieceManager
from dottorrent  import TorrentCreator, TorrentReader
from torrent_info import TorrentInfo
from torrent_settings import PIECE_SIZE_1MB
# from torrent_server import TorrentServer
# from torrent_client import TorrentClient
import hashlib
import time
import socket






def main():
    torrent_creator = TorrentCreator('./test/fedora36.mp4',PIECE_SIZE_1MB, False, ['192.168.10.1:8080'], 'a', 'a')
    torrent_creator.create_dottorrent_file('./')
    torrent_reader = TorrentReader('./fedora36.torrent', './test')
    torrent_info = torrent_reader.build_torrent_info()
    print(torrent_creator.filename)
    print(torrent_creator.file_size)
    #piece_manager = PieceManager(torrent_info)
    # peer_id = hashlib.sha1(str(time.time()).encode('utf-8')).digest()
    # server = TorrentServer(torrent_info, piece_manager,'127.0.0.1', 4800, peer_id)
    # server.start()
    # client = TorrentClient(torrent_info, piece_manager, peer_id)
    # client.start()
    # print(torrent_obj.the_file_is_complete())
    # torrent_obj.check_local_pieces()
    # print(torrent_obj.download_completed)
    # torrent_obj.write_to_disk_test('/home/dquesada/Downloads')
    

    b = '.'


if __name__ == '__main__':
    main()
