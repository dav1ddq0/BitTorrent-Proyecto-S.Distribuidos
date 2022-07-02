import hashlib
from piece import Piece
from torrent_info import TorrentInfo
import bitstring
from disk_io import DiskIO

class PieceManager:

    def __init__(self, torrent_info):
        '''
            Initialize the piece manager
        '''
        self.torrent_info: TorrentInfo = torrent_info # The torrent info
        self.file_size = self.torrent_info.file_size
        self.piece_size = self.torrent_info.piece_size
        self.filename = f'{self.torrent_info.file_path}/{self.torrent_info.file_name}'
        self.file_size = self.torrent_info.file_size
        self.number_of_pieces = self.torrent_info.number_of_pieces
        self.bitfield: bitstring.BitArray = bitstring.BitArray(self.number_of_pieces) # Bitfield of the pieces
        self.completed_pieces: int = 0 # Number of pieces that are completed
        self.dottorrent_pieces = self.torrent_info.dottorrent_pieces
        self.pieces: list[Piece] = self.build_pieces() # List of pieces

    @property
    def downloaded(self):
        '''
            The total amount of bytes downloaded
        '''
        total_downloaded = 0
        for piece in self.pieces:
            if piece.is_completed:
                total_downloaded += self.piece_size
        
        return total_downloaded

    @property
    def completed(self):
        return self.number_of_pieces == self.completed_pieces
    
    @property
    def left(self):
        '''
            The number of bytes needed to download to be 100% complete and 
            get all the included files in the torrent.
        '''
        return self.file_size - self.downloaded
        
    
    

    def get_piece(self, piece_index):
        return self.pieces[piece_index]

    def build_pieces(self):
        pieces = []
        for i in range(self.number_of_pieces):
            piece_offset = self.piece_size*i
            starthash_index = i * 20
            piece_hash = self.dottorrent_pieces[starthash_index: starthash_index+20]
            piece_size = self.file_size % self.piece_size if i == self.number_of_pieces - 1 else self.piece_size
            piece = Piece(i, piece_offset, piece_size, piece_hash)
            pieces.append(piece)
        return pieces
        

    def check_local_pieces(self):
        for piece_index in range(self.numer_of_pieces):
            with open(f'{self.save_at}/{self.torrent_info.file_name}', 'rb') as f:
                chunk = f.read(self.piece_size)
                while(chunk):
                    sha1chunk = hashlib.sha1(chunk).digest()
                    piece: 'Piece' = self.pieces[piece_index]
                    if sha1chunk == piece.piece_hash:  # This piece is already written in the file
                        self.bitfield[piece_index] = True
                        piece.is_completed = True
                        self.completed_pieces += 1
                    chunk = f.read(self.piece_size)

    def receive_block_piece(self, piece_index, block_offset, raw_data):

        if not self.bitfield[piece_index]:
            piece: Piece = self.pieces[piece_index]
            piece.write_block(block_offset, raw_data)
    
            if piece.is_completed:
                self.bitfield[piece_index] = True
                self.complete_pieces += 1
                DiskIO.write_to_disk(self.filename, piece.piece_offset, piece.raw_data)

    def get_block_piece(self, piece_index, block_offset):
        piece: Piece = self.pieces[piece_index]
        if not piece.in_memory:
            piece.load_from_disk()
        
        block = piece.get_block(block_offset)
        return block
    
    def clean_memory(self, piece_index):
        piece: Piece = self.pieces[piece_index]
        if not piece.in_memory:
            piece.clean_memory()
    
    
      