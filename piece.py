# Bittorrent piece
import math

from block import BLOCK_SIZE, Block

class Piece:


    def __init__(self, piece_index: int, piece_size: int, piece_hash: str):
        """
        Initialize a piece
        """
        self.piece_index = piece_index
        self.piece_size = piece_size
        self.piece_hash = piece_hash
        self.number_of_blocks: int = int(math.ceil(float(piece_size) / BLOCK_SIZE))
        self.blocks: list['Block'] = []
        self.completed: bool = False 
        self.data : bytes = b''

    
    def put_data(self, data):
        self.data = data
    
    
    def write_block(self, offset, data):
        block_index = int(offset/BLOCK_SIZE)
        


        