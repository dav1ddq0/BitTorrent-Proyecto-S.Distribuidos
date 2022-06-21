from enum import Enum
from torrent_settings import DEFAULT_BLOCK_SIZE



class State(Enum):
    BLOCK_FREE = 0
    BLOCK_PENDING = 1
    BLOCK_FULL = 2

class Block():
    
    def __init__(self,  data: bytes = b'', block_size: int = BLOCK_SIZE, state: State = State.BLOCK_FREE):
        self.data = data
        self.block_size = block_size
        self.state = state

    def update_block_status(self, new_state: State):
        self.state = new_state
        