from enum import Enum


# Default value of the blocks
BLOCK_SIZE = 2 << 13 # 16KB


class Block():
    
    def __init__(self,  data: bytes = b''):
        self.data = data

