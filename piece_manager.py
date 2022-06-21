from piece import Piece
import bitstring
class PieceManager:
    
    def __init__(self, torrent_info):
        '''
            Initialize the piece manager
        '''
        self.torrent_info = torrent_info
        self.dottorent_pieces = self.torrent_info.dottorent_pieces
        self.pieces = self.build_pieces()
        self.save_at = self.torrent_info.file_path
        self.numer_of_pieces = self.torrent_info.number_of_pieces
        
        self.bitfield: bitstring.BitArray = bitstring.BitArray(self.number_of_pieces)
        self.completed_pieces:int = 0


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
    
    