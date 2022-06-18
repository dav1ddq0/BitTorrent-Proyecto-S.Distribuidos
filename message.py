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

class HandshakeMessage(Message):
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
        handshake_receive_message = struct.unpack(f">B{HANDSHAKE_PSTRLEN}s8s20s20s", msg)
        _, pstr, _, info_hash, peer_id = handshake_receive_message
        if pstr != HANDSHAKE_PSTR_V1:
            raise ValueError("Invalid string identifier of the protocol")

        return HandshakeMessage(info_hash, peer_id)
        

    
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

class BitfieldMessage(Message):
    '''
        The bitfield message is sent by the client to tell the tracker which pieces it has.
        #### bitfield: <len=0001+X><id=5><bitfield>
        - length prefix: four byte specifying the length of the message, including self.id and self.bitfield
        - id: 1 byte specifying the message type (5)
        - bitfield: X bytes containing the bitfield.
        
    '''
    def __init__(self, bitfield):
        self.bitfield = bitfield
        self.len_bitfield = len(self.bitfield)
        self.msg_id = 5
        self.len =  1 + self.len_bitfield


    def read_bmessage(self, msg):
        _, msg_id, bitfield = struct.unpack(f">IB{self.len_bitfield}s", msg)
        
        if msg_id != self.msg_id:
            raise Exception("Not a bitField message")

       

        return BitfieldMessage(bitfield)


    def write_bmessage(self):
        bitfield_message = struct.pack(
            f">IB{self.len_bitfield}s",  # 4bytes + 1 bytes + bitfield
            self.payload_len,
            self.msg_id, 
            self.bitfield
        )
        return bitfield_message

class RequestMessage(Message):
    '''
        The request message is sent by a peer to request a block.
        #### request: <len=0013><id=6><index><begin><length>
        - length prefix: four byte specifying the length of the message, including self.id and self.index, self.begin, and self.length
        - id: 1 byte specifying the message type (6)
        - index: 4 byte specifying the zero-based piece index
        - begin: 4 byte specifying the zero-based byte offset within the piece
        - length: 4 byte specifying the requested length
    '''
    def __init__(self, index, begin, length):
        self.index = index
        self.begin = begin
        self.length = length
        self.msg_id = 6
        self.len = 13
    
    def read_bmessage(self, msg):
        _, msg_id, index, begin, length = struct.unpack(f">IBIII", msg)
        if msg_id != self.msg_id:
            raise Exception("Not a request message")

        return RequestMessage(index, begin, length)

    def write_bmessage(self):
        request_message = struct.pack(
            f">IBIII",
            self.len, # 4bytes + 1 bytes + 4bytes + 4bytes + 4bytes (payload lenght)) 
            self.msg_id, # message id (6)
            self.index, # piece index
            self.begin, # block offset
            self.length # block length
        )
        return request_message


class CancelMessage(Message):
    '''
        The cancel message is sent by a peer to cancel a request.
        #### cancel: <len=0013><id=7><index><begin><length>
        - length prefix: four byte specifying the length of the message, including self.id and self.index, self.begin, and self.length
        - id: 1 byte specifying the message type (7)
        - index: 4 byte specifying the zero-based piece index
        - begin: 4 byte specifying the zero-based byte offset within the piece
        - length: 4 byte specifying the requested length
    '''
    def __init__(self, index, begin, length):
        self.index = index
        self.begin = begin
        self.length = length
        self.msg_id = 7
        self.len = 13
    
    def read_bmessage(self, msg):
        _, msg_id, index, begin, length = struct.unpack(f">IBIII", msg)
        if msg_id != self.msg_id:
            raise Exception("Not a cancel message")

        return CancelMessage(index, begin, length)

    def write_bmessage(self):
        cancel_message = struct.pack(
            f">IBIII",
            self.len, # 4bytes + 1 bytes + 4bytes + 4bytes + 4bytes (payload lenght)) 
            self.msg_id, # message id (7)
            self.index, # piece index
            self.begin, # block offset
            self.length # block length
        )
        return cancel_message

class HaveMessage(Message):
    '''
        The have message is sent by a peer to tell the client that it has a piece.
        #### have: <len=0005><id=4><piece index>
        - length prefix: four byte specifying the length of the message, including self.id and self.piece
        - id: 1 byte specifying the message type (4)
        - piece: 4 byte specifying the zero-based piece index
    '''
    def __init__(self, piece_index):
        self.piece_index = piece_index
        self.msg_id = 4
        self.len = 5
    
    def read_bmessage(self, msg):
        _, msg_id, piece = struct.unpack(f">IBI", msg)
        if msg_id != self.msg_id:
            raise Exception("Not a have message")

        return HaveMessage(piece)

    def write_bmessage(self):
        have_message = struct.pack(
            f">IBI",
            self.len, # 4bytes + 1 bytes + 4bytes (payload lenght)) 
            self.msg_id, # message id (4)
            self.piece_ # piece index
        )
        return have_message

