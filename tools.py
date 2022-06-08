from asyncio import ReadTransport
import os
import re


S512KB = 2 << 18 # 512KB
S1MB = 2 << 19 # 1MB
S16KB = 2 << 13 # 16KB


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
