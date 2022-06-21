# Bittorrent piece
import math
import os
from block import BLOCK_SIZE, Block

class Piece:


    def __init__(self, piece_index: int, piece_offset, piece_size: int, piece_hash: str):
        """
        Initialize a piece
        """
        self.piece_index = piece_index
        self.piece_offset = piece_offset
        self.piece_size = piece_size
        self.piece_hash = piece_hash
        self.number_of_blocks: int = int(math.ceil(float(piece_size) / BLOCK_SIZE))
        self.blocks: list['Block'] = self.build_blocks()
        self.is_completed: bool = False 
        self.raw_data : bytes = b''

    
    def put_data(self, data):
        self.raw_data = data
        self.is_completed = True
        
    
    
    def write_block(self, offset, data):
        block_index = offset//BLOCK_SIZE
    
    def build_blocks(self):
        blocks: list['Block'] = []

        for _ in range(self.number_of_blocks-1):
            blocks.append(Block(block_size = BLOCK_SIZE))
        blocks.append(Block(block_size = self.piece_size%BLOCK_SIZE))
        return blocks
        
    def write_to_disk(self, path):
        new_file = open(path, 'r+b')
        new_file.seek(self.piece_offset)
        new_file.write(self.raw_data)
        new_file.close()


        