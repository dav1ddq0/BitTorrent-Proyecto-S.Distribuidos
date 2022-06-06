class FileInfo:

    def __init__(self, path: list[str], lenght, md5sum = None):
        self.path =  path
        self.lenght = lenght
        self.md5sum = md5sum

class MultiFileInfo:
    def __init__(self, name: str, files: dict[str, ] ):
        self.files = files
        self.lenght = sum(f.lenght for f in files)
        self.md5sum = None
        self.name = None