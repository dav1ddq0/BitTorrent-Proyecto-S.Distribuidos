# Default value of the blocks
from io import DEFAULT_BUFFER_SIZE


DEFAULT_BLOCK_SIZE = 1 << 14 # 16KB

PIECE_SIZE_256KB = 1 << 18 # 256KB
PIECE_SIZE_512KB = 1 << 19 # 512KB
PIECE_SIZE_1MB = 1 << 20 # 1MB

READ_BUFFER_SIZE = 4096 # default recv 
LEN__BUFFER_SIZE = 4 # size of the length of the message

