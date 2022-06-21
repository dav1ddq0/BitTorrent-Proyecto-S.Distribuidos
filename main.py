from torrent_creator import TorrentCreator
from torrent_reader import TorrentReader
from torrent_info import TorrentInfo

def main():
    torrent_creator = TorrentCreator('./test/fedora36.mp4', 524288, False, ['1www.tracker-run.com', 'www.2h3.xyz'], 'a', 'a')
    torrent_creator.create_dottorrent_file('./')
    # torrent_reader = TorrentReader('./test/fedora36.torrent', './test')
    # torrent_obj = torrent_reader.build_torrent_info()
    # print(torrent_obj.the_file_is_complete())
    # torrent_obj.check_local_pieces()
    # print(torrent_obj.download_completed)
    # torrent_obj.write_to_disk_test('/home/dquesada/Downloads')
    
    b = '.'

if __name__ == '__main__':
    main()