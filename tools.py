from asyncio import ReadTransport
from cgi import test
import os
import re
import random

S512KB = 2 << 18 # 512KB
S1MB = 2 << 19 # 1MB
S16KB = 2 << 13 # 16KB
from piece import Piece

def split_file(filename: str, chunk_size:int  = 2<<13, output_dir: str = './') -> None:
    """
    Split the file into chunks of size chunk_size
    """
    file_number = 1
    with open(f'{filename}', 'rb') as f:
        chunk = f.read(chunk_size)
        while chunk:
            with open(f'{output_dir}/{os.path.basename(filename)}_{str(file_number)}', 'wb') as chunk_file:
                chunk_file.write(chunk)
            file_number += 1
            chunk = f.read(chunk_size)
    

def build_pieces(filename:str, chunk_size:int = 2<<18):
    piece_index = 0
    pieces: list[Piece] = []
    with open(f'{filename}', 'rb') as f:
        chunk = f.read(chunk_size)
        while(chunk):
            piece = Piece(piece_index, chunk_size, '')
            piece.put_data(chunk)
            pieces.append(piece)
            piece_index +=1
            chunk = f.read(chunk_size)
    
    return pieces

        
        # while chunk:
        #     with open(f'{output_dir}/{os.path.basename(filename)}_{str(file_number)}', 'wb') as chunk_file:
        #         chunk_file.write(chunk)
        #     file_number += 1
        #     chunk = f.read(chunk_size)

def build_new_file(pieces: list[Piece], output= './test/all/fedora36.mp4'):
    f = open(output, 'wb')
    for piece in pieces:
       f.seek(piece.piece_index*piece.piece_size)
       f.write(piece.data)
    f.close()

def merge_file(filename:str, output_dir:str = './') -> None:
    """
    Merge the file into one file
    """
    
    f = open(f'{filename}', 'wb')
    path_directory = f'{output_dir}'
    for file in sorted(os.listdir(path_directory), key = lambda x: (int(re.sub('\D','',x)),x)):
        with open(os.path.join(path_directory, file), 'rb') as chunk_file:
            f.write(chunk_file.read())
    f.close()

def create_folder(path)-> None:
    '''
    Create a folder
    '''

    if not os.path.exists(path):
        os.mkdir(path)


def get_split_file(filename, piece_lenght):
    output_dir = f'{os.path.dirname(filename)}/.{os.path.basename(filename)}'
    create_folder(output_dir)
    split_file(filename, output_dir=output_dir, chunk_size=piece_lenght)
    return output_dir

pieces = build_pieces('./test/fedora36.mp4')
random.shuffle(pieces)
build_new_file(pieces)