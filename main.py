from torrent_creator import TorrentCreator

def main():
    torrent_creator = TorrentCreator('./test/fedora36.mp4', 524288, False, ['1www.tracker-run.com', 'www.2h3.xyz'], 'a', 'a')
    torrent_creator.create_dottorrent_file()


if __name__ == '__main__':
    main()