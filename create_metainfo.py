'''
    Metainfo file estructure
'''
from copyreg import pickle
import datetime
import os
import hashlib
import tools
import re

def create_metainfo(file_name, file_size, announce, announce_list, creation_date, comment, created_by, private, piece_length, pieces, md5sum):
    '''
    Create a metainfo file
    '''
    
    metainfo = {}
    metainfo["announce"] = announce
    metainfo["announce-list"] = announce_list
    metainfo["info"] = {}
    metainfo["info"]["name"] = file_name
    metainfo["info"]["length"] = file_size
    metainfo["info"]["piece length"] = piece_length
    metainfo["info"]["pieces"] = pieces
    metainfo["info"]["private"] = private
    # a 32-character hexadecimal string corresponding to the MD5 sum of the file
    metainfo["info"]["md5sum"] = md5sum
    metainfo["creation date"] = creation_date
    metainfo["comment"] = comment
    metainfo["created by"] = created_by
    return metainfo


def get_hash_pieces(pieces_dir):
    pieces_sha1 = b''
    for file in sorted(os.listdir(pieces_dir), key = lambda x: (int(re.sub('\D','',x)),x)):
        with open(os.path.join(pieces_dir, file), 'rb') as piece:
            pieces_sha1 += hashlib.sha1(piece.read()).digest()
    return pieces_sha1


def read_file_to_upload(path):
    file_size = os.path.getsize(path)  # file size in bytes
    md5sum = hashlib.md5(open(path, 'rb').read()).digest() # md5sum of the file calculates and verifies 128-bit MD5 hashes,
    name = os. path.basename(path)
    piece_lenght = tools.S512KB
    pieces_dir = tools.get_split_file(path, tools.S512KB)
    pieces = get_hash_pieces(pieces_dir)
    private = 0
    announce = "https://wiki.theory.org/BitTorrentSpecification#Bencoding"
    announce_list=["https://wiki.theory.org/BitTorrentSpecification#Bencoding","https://docs.racket-lang.org/bencode/index.html"]
    creation_date=str(datetime.datetime.now())
    comment="this is a test"
    created_by="DQ"
    return create_metainfo(name, file_size, announce, announce_list, creation_date, comment, created_by, private, piece_lenght, pieces, md5sum)
    




media_info = read_file_to_upload('./test/fedora36.mp4')
print(media_info)
