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

    def build_new_file(self):
        f = open(self.file_path,"wb")
        f.seek(self.file_size-1)
        f.write(b"\0")
        f.close()

    
    def check_local_pieces(self):
        piece_index = 0
        with open(f'{self.file_path}/{self.file_name}', 'rb') as f:
            chunk = f.read(self.piece_size)
            while(chunk):
                sha1chunk = hashlib.sha1(chunk).digest()
                piece_i: 'Piece' = self.pieces[piece_index]

                if sha1chunk == piece_i.piece_hash: # Esta pieza ya esta escrita en el file
                    piece_i.put_data(chunk)
                piece_index +=1
                chunk = f.read(self.piece_size)
                
    
    def file_exists(self):

        return os.path.isfile(f'{self.file_path}/{self.file_name}')

    def the_file_is_complete(self):
        if self.file_exists():
            f =  open(f'{self.file_path}/{self.file_name}','rb')
            f_md5sum = hashlib.md5(f.read()).digest()
            f.close() 
            return f_md5sum == self.file_md5sum
        return False
    

        

