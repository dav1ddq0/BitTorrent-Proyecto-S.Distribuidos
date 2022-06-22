# Bittorrent piece
import hashlib
import logging
import math
import os
from block import BLOCK_SIZE, Block, State

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

        if not self.is_completed and not self.blocks[block_index].state == State.FULL:
            self.blocks[block_index].data = data
            self.blocks[block_index].state = State.FULL
    
    def build_blocks(self):
        blocks: list['Block'] = []

        for _ in range(self.number_of_blocks-1):
            blocks.append(Block(block_size = BLOCK_SIZE))
        blocks.append(Block(block_size = self.piece_size%BLOCK_SIZE))
        return blocks
    
    def _merge_blocks(self):
        raw_data = b''
        for block in self.blocks:
            raw_data += block.data
        return raw_data

    def _valid_blocks(self, raw_data):
        hash_raw_data = hashlib.sha1(raw_data).digest()
        if hash_raw_data == self.piece_hash:
            return True
        logging.warning(f'Error Piece Hash : {hash_raw_data} != {self.piece_hash} Piece{self.piece_index}')
        return False
    
            
        
    


        