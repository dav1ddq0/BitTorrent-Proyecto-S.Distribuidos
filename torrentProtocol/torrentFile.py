

#info dicc que tiene todos los parametros dados abajo... y en el parametro Files, la cantidad de files 
from numpy import safe_eval


class torrentFile():
    def __init__(self,announce,info,files,filesData,optional=None) -> None:
        #"Es la URL del tracker."
        self.announce=announce
        #"Un diccionario versátil con claves independientes"
        self.info={}
        #"Se sugiere un directorio para guardar el contenido que se descargue."
        self.info["Name"]=info["Name"]
        #"Es el peso, en bytes, de cada pieza"
        self.info["PieceLength"]=info["PieceLength"]
        #"Listado de hash que tiene cada pieza (los hash hacen que las modificaciones sean detectadas, sirviendo para evitarlas)"
        self.info["Pieces"]=info["Pieces"]
        #"Peso, en bytes, del archivo una vez compartido."
        self.info["Length"]=info["Length"]
        #"Listado de diccionarios, uno por archivo (contenido multiarchivo, evidentemente)"
        self.info["Files"]=[]
        for i in range(0,int(files)):
            newDicc={}
            self.info["Files"].append(newDicc)
            #Listado de cadenas de los nombres de los subdirectorios, siendo el final el que dé el nombre verdadero al archivo. 
            self.info["Files"][i]["Path"]=filesData[i]["Path"]
            #Una vez más, el número de bytes del archivo.
            self.info["Files"][i]["Length"]=filesData[i]["Length"]

        #estas salen como que pueden ser opcionales
        if optional!=None:
            self.announce_list=optional["announce_list"]
            self.creationDate=optional["creationDate"]
            self.comment=optional["comment"]
            self.createdBy=optional["createdBy"]
            self.private=optional["private"]




