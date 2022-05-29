# Bittorrent piece


class Piece:
    def __init__(self, piece_index: int, piece_size: int, piece_hash: str):
        self.piece_index = piece_index
        self.piece_size = piece_size
        self.piece_hash = piece_hash