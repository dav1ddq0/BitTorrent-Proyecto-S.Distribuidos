from abc import abstractclassmethod
import struct

HANDSHAKE_PSTR_V1 = b'BitTorrent protocol'
HANDSHAKE_PSTRLEN  = 19

class Message:
    @abstractclassmethod
    def read_bmessage(self):
        ...
    @abstractclassmethod
    def write_bmessage(self):
        ...

class Handshake(Message):
    '''
        The handshake is a required message and must be the first message transmitted by the client
        #### handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
        - pstrlen: string length of <pstr>, as a single raw byte (1 byte)
        - pstr: string identifier of the protocol (in this case, "BitTorrent protocol") (19 bytes)
        - reserved: eight bytes of reserved data  (8 bytes)
        - info_hash: 20-byte SHA1 hash of the info key from the metainfo file (20 bytes)
        - peer_id: 20-byte string used as a unique ID for the client.

        In version 1.0 of the BitTorrent protocol, pstrlen = 19, and pstr = "BitTorrent protocol".
    '''

    def __init__(self, info_hash, peer_id):
        self.info_hash = info_hash
        self.peer_id = peer_id
    
    def read_bmessage(self, msg):
        
        

    
    def write_bmessage(self):
        '''
            message in bytes format handshake message
        '''
        reserved = b'\x00' * 8 # 8 bytes of reserved data
        handshake_message = struct.pack(
            f">B{HANDSHAKE_PSTRLEN}s8s20s20s",
            HANDSHAKE_PSTRLEN,
            HANDSHAKE_PSTR_V1,
            reserved,
            self.info_hash,
            self.peer_id
        )
        

        return handshake_message 
    