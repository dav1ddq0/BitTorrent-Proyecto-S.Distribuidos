import os
import hashlib
import math
import bencode
from piece import Piece

class TorrentInfo:
    def __init__(self, metainfo, save_at: str):
        '''
            Representation of the Torrent File
            to Download File
        '''
        self.metainfo = metainfo
        self.file_path = save_at
        self.file_md5sum = self.metainfo['info']['md5sum']
        self.file_name = self.metainfo['info']['name']
        self.file_size = self.metainfo['info']['length']
        self.piece_size = self.metainfo['info']['piece length']
        self.number_of_pieces = math.ceil(self.file_size/self.piece_size)
        self.dottorrent_pieces = self.metainfo['info']['pieces']
        #  urlencoded 20-byte SHA1 hash of the value of the info key from the Metainfo file. Note that the value will be a bencoded dictionary, given the definition of the info key above.
        self.info_hash = hashlib.sha1(bencode.encode(self.metainfo['info'])).digest()
        self.pieces = self.build_pieces()
        
    def build_pieces(self):
        pieces = []
        for i in range(self.number_of_pieces):
            piece_offset = self.piece_size*i
            starthash_index = i *20 
            piece_hash = self.dottorrent_pieces[starthash_index: starthash_index+20]
            piece_size = self.file_size % self.piece_size if i == self.number_of_pieces - 1  else self.piece_size 
            piece = Piece(i,piece_offset, piece_size, piece_hash)
            pieces.append(piece)
        return pieces

    # def 
    def file_exists(self):

        return os.path.isfile(f'{self.file_path}/{self.file_name}')

    def the_file_is_complete(self):
        if self.file_exists():
            f =  open(f'{self.file_path}/{self.file_name}','wb')
            f_md5sum = hashlib.sha1(f.read()).digest()
            f.close() 
            return f_md5sum == self.file_md5sum
        return False
    

        

