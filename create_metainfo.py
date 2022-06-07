'''
    Metainfo file estructure
'''
import os
import hashlib
def create_metainfo(file_name, file_size, announce, announce_list, creation_date, comment, created_by, private, piece_length, pieces, md5sum):
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


def read_file(path):
    file_size = os.path.getsize(path)  # file size in bytes
    md5sum = hashlib.md5(open(path, 'rb').read()).digest() # md5sum of the file calculates and verifies 128-bit MD5 hashes,
    name = os. path. basename(path)
    pointer = ''


read_file('./test/fedora36.mp4')
