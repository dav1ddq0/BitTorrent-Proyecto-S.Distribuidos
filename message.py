from abc import abstractclassmethod
import struct
import logging
import bitstring


HANDSHAKE_PSTR_V1 = b'BitTorrent protocol'
HANDSHAKE_PSTRLEN  = 19

class WrongMessageException(Exception):
    @property 
    def error_info(self):
        return self.args[0]

def message_dispatcher(msg_payload):
    try:
        _, msg_id, = struct.unpack(">IB", msg_payload[:5])
    except Exception as e:
        logging.warning(f"Error when unpacking message : {e}")
        return None
    bmap_id_to_msg = {
           0: ChokeMessage,
           1: UnchokeMessage,
           2: InterestedMessage,
           3: NotInterestedMessage,
           4: HaveMessage,
           5: BitfieldMessage,
           6: RequestMessage,
           7: PieceMessage,
           8: CancelMessage,
           12: InfoMessage
        #    9: PortMessage,
    }
    if msg_id not in bmap_id_to_msg:
        raise WrongMessageException(f"Wrong message id. The message with id {msg_id} is not valid in Torrent Protocol")
    return bmap_id_to_msg[msg_id].unpack_message(msg_payload)

class Message:
    name = 'Message'
    @abstractclassmethod
    def unpack_message(self):
        ...
    @abstractclassmethod
    def message(self):
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
        PayloadLenght = len(pstr)=19 + 8 + 20 + 20 = 67
        TotalLenght =  1 + PayloadLenght = 68 
    '''

    total_len = 68
    def __init__(self, info_hash, peer_id):
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.name = 'HandshakeMessage'
    
    @classmethod
    def unpack_message(cls, msg):
        handshake_receive_message = struct.unpack(f">B{HANDSHAKE_PSTRLEN}s8s20s20s", msg[:cls.total_len])
        _, pstr, _, info_hash, peer_id = handshake_receive_message
        if pstr != HANDSHAKE_PSTR_V1:
            raise ValueError("Invalid string identifier of the protocol")

        return HandshakeMessage(info_hash, peer_id)
        

    
    def message(self):
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
    msg_id = 5

    def __init__(self, bitfield: bitstring.BitArray):
        self.bitfield = bitfield
        self.len_bitfield = len(self.bitfield.tobytes())
        self.len =  1 + self.len_bitfield
        self.name = 'BitfieldMessage'

    @classmethod
    def unpack_message(cls, msg):
        len_msg,  = struct.unpack(f">I", msg[:4])
        bitfield_len = len_msg - 1
        msg_id, bitfield = struct.unpack(f">B{bitfield_len}s", msg[4: 4 + len_msg])
        
        if msg_id != cls.msg_id:
            raise Exception("Not a bitField message")

        bitfield = bitstring.BitArray(bytes=bitfield)
        
        return BitfieldMessage(bitfield)


    def message(self):
        bitfield_message = struct.pack(
            f">IB{self.len_bitfield}s",  # 4bytes + 1 bytes + bitfield
            self.len,
            self.msg_id, 
            self.bitfield.tobytes()
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
    msg_id = 6
    def __init__(self, index, begin, length):
        self.index = index
        self.begin = begin
        self.length = length
        self.len = 13
        self.name = 'RequestMessage'
    
    @classmethod
    def unpack_message(cls, msg)->'RequestMessage':
        len_msg, = struct.unpack(f">I", msg[:4])
        msg_id, index, begin, length = struct.unpack(f">BIII", msg[4: 4 + len_msg ])
        if msg_id != cls.msg_id:
            raise Exception("Not a request message")
        
        return RequestMessage(index, begin, length)

    def message(self) -> bytes:
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
    msg_id = 7
    def __init__(self, index, begin, length):
        self.index = index
        self.begin = begin
        self.length = length
        self.len = 13
        self.name = 'CancelMessage'
    
    @classmethod
    def unpack_message(cls, msg):
        _, msg_id, index, begin, length = struct.unpack(f">IBIII", msg)
        if msg_id != cls.msg_id:
            raise Exception("Not a cancel message")

        return CancelMessage(index, begin, length)

    def message(self):
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
    msg_id = 4

    def __init__(self, piece_index):
        self.piece_index = piece_index
        self.len = 5
    
    @classmethod
    def unpack_message(cls, msg):
        _, msg_id, piece = struct.unpack(f">IBI", msg)
        if msg_id != cls.msg_id:
            raise Exception("Not a have message")

        return HaveMessage(piece)

    def message(self):
        have_message = struct.pack(
            f">IBI",
            self.len, # 4bytes + 1 bytes + 4bytes (payload lenght)) 
            self.msg_id, # message id (4)
            self.piece_ # piece index
        )
        return have_message

class ChokeMessage(Message):
    '''
        The choke message is sent by a peer to tell the client that it has stopped sending data.
        #### choke: <len=0001><id=0>
        - length prefix: four byte specifying the length of the message, including self.id
        - id: 1 byte specifying the message type (0)
    '''
    msg_id = 0
    def __init__(self):
        self.len = 1
        self.name = 'ChokeMessage'
    
    @classmethod
    def unpack_message(cls, msg):
        _, msg_id = struct.unpack(f">IB", msg)
        if msg_id != cls.msg_id:
            raise Exception("Not a choke message")

        return ChokeMessage()
    
    def message(self):
        choke_message = struct.pack(
            f">IB",
            self.len, # 4bytes + 1 bytes (payload lenght)) 
            self.msg_id # message id (0)
        )
        return choke_message

class UnchokeMessage(Message):
    '''
        The unchoke message is sent by a peer to tell the client that it can start sending data.
        #### unchoke: <len=0001><id=1>
        - length prefix: four byte specifying the length of the message, including self.id
        - id: 1 byte specifying the message type (1)
    '''

    def __init__(self):
        self.msg_id = 1
        self.len = 1
        self.name = 'UnchokeMessage'
    
    @classmethod
    def unpack_message(cls, msg):
        _, msg_id = struct.unpack(f">IB", msg)
        if msg_id != cls.msg_id:
            raise Exception("Not an unchoke message")

        return UnchokeMessage()
    
    def message(self):
        unchoke_message = struct.pack(
            f">IB",
            self.len, # 4bytes + 1 bytes (payload lenght)) 
            self.msg_id # message id (1)
        )
        return unchoke_message


class InterestedMessage(Message):
    '''
        The interested message is sent by a peer to tell the client that it is interested in receiving data.
        #### interested: <len=0001><id=2>
        - length prefix: four byte specifying the length of the message, including self.id
        - id: 1 byte specifying the message type (2)
    '''
    msg_id = 2
    def __init__(self):
        self.len = 1
        self.name = 'InterestedMessage'
    
    @classmethod
    def unpack_message(cls, msg):
        _, msg_id = struct.unpack(f">IB", msg)
        if msg_id != cls.msg_id:
            raise Exception("Not an interested message")

        return InterestedMessage()
    
    def message(self):
        interested_message = struct.pack(
            f">IB",
            self.len, # 4bytes + 1 bytes (payload lenght)) 
            self.msg_id # message id (2)
        )
        return interested_message

class NotInterestedMessage(Message):
    '''
        The not interested message is sent by a peer to tell the client that it is not interested in receiving data.
        #### not interested: <len=0001><id=3>
        - length prefix: four byte specifying the length of the message, including self.id
        - id: 1 byte specifying the message type (3)
    '''

    msg_id = 3

    def __init__(self):
        self.len = 1
    
    @classmethod
    def unpack_message(cls, msg):
        _, msg_id2 = struct.unpack(f">IB", msg)
        if msg_id2 != cls.msg_id:
            raise Exception("Not an not interested message")

        return NotInterestedMessage()
    
    def message(self):
        not_interested_message = struct.pack(
            f">IB",
            self.len, # 4bytes + 1 bytes (payload lenght)) 
            self.msg_id # message id (3)
        )
        return not_interested_message


class KeepAliveMessage(Message):
    '''
        The keep alive message is sent periodically to let the client know that it is still alive.
        - keep-alive: <len=0000>


    '''

    def __init__(self):
        self.len_prefix = 0
        self.name = 'KeepAliveMessage'
    @classmethod
    def unpack_message(cls, msg):
        len_prefix = struct.unpack(f">I", msg)
        if len_prefix != 0:
            raise Exception("Not a keep alive message")

        return KeepAliveMessage()
    
    def message(self):
        keep_alive_message = struct.pack(
            f">I",
            self.len_prefix, # 4bytes (0)
        )
        return keep_alive_message


class PieceMessage(Message):
    '''
        The piece message is sent by a peer to tell the client that it has a block of data it has not requested.
        #### piece: <len=0009+X><id=7><index><begin><block>
        - length prefix: four byte specifying the length of the message, including self.id and self.block
        - id: 1 byte specifying the message type (7)
        - index: 4 byte specifying the zero-based piece index
        - begin: 4 byte specifying the zero-based byte offset within the piece
        - block: X byte block of data
    '''
    msg_id = 7

    def __init__(self, index, begin, block):
        self.len = 9 + len(block)
        self.index = index
        self.begin = begin
        self.block = block
        self.name = 'PieceMessage'
        
    
    @classmethod
    def unpack_message(cls, msg):
        msg_len, msg_id, index, begin  = struct.unpack(f">IBII", msg[:13])

        if msg_id != cls.msg_id:
            raise Exception("Not a piece message")
        
        block_len = msg_len - 9
        block, = struct.unpack(f"{block_len}s", msg[13: 13 + block_len])
        
        return PieceMessage(index, begin, block)
    
    def message(self):
        piece_message = struct.pack(
            f">IBII{len(self.block)}s",
            self.len, # 4bytes + 1 bytes (payload lenght))
            self.msg_id, # message id (7)
            self.index, # 4 bytes specifying the zero-based piece index
            self.begin, # 4 bytes specifying the zero-based byte offset within the piece
            self.block # X byte block of data
        )
        return piece_message



class InfoMessage(Message):
    '''
        Message to send status information
    '''
    msg_id = 12

    def __init__(self, msg: str):
        
        self.payload_len =  1 + len(msg.encode('utf-8'))
        self.info = msg
        self.name = f'InfoMessage: {self.info}'
        
    
    @classmethod
    def unpack_message(cls, msg):
        len_msg, msg_id= struct.unpack(f">IB", msg[:5])
        if msg_id != cls.msg_id:
            raise Exception("Not a info message")
        try:    
            info = msg[5: 5 + len_msg-1].decode('utf-8')
        except:
            raise Exception("Not valid UTF-8 message")
        return InfoMessage(info)
    
    def message(self):
        msg_encode = self.info.encode('utf-8')
        info_message = struct.pack(
            f">IB{len(msg_encode)}s",
            self.payload_len, # 4bytes + 1 bytes (payload lenght))
            self.msg_id, # message id (7)
            msg_encode # information to send 
        )
        
        return info_message

