from torrent_creator import TorrentCreator
from torrent_reader import TorrentReader

def main():
    torrent_creator = TorrentCreator('./test/fedora36.mp4', 524288, False, ['1www.tracker-run.com', 'www.2h3.xyz'], 'a', 'a')
    torrent_creator.create_dottorrent_file('./test')
    torrent_reader = TorrentReader('./test/fedora36.torrent', './test')
    torrent_obj = torrent_reader.build_torrent_info()
    print(torrent_obj.the_file_is_complete())
    torrent_obj.check_local_pieces()
    b = '.'

if __name__ == '__main__':
    main()