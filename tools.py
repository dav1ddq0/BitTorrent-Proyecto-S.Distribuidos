import os
import re

def split_file(filename: str, chunk_size:int  = 2<<13, output_dir: str = './') -> None:
    """
    Split the file into chunks of size chunk_size
    """
    file_number = 1
    with open(f'{filename}', 'rb') as f:
        chunk = f.read(chunk_size)
        while chunk:
            with open(f'{output_dir}', 'wb') as chunk_file:
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
