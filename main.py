from torrent_creator import TorrentCreator
from torrent_reader import TorrentReader
from torrent_info import TorrentInfo

def main():
    # torrent_creator = TorrentCreator('./test/fedora36.mp4', 524288, False, ['1www.tracker-run.com', 'www.2h3.xyz'], 'a', 'a')
    # torrent_creator.create_dottorrent_file('./test')
    torrent_reader = TorrentReader('./test/fedora36.torrent')
    torrent_info = TorrentInfo(torrent_reader.metainfo, torrent_reader.dottorrent_path)
    # a = torrent_reader.metainfo
    b = '.'

if __name__ == '__main__':
    main()