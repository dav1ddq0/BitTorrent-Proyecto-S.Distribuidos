from importlib.metadata import files
from re import A
import bencode 
import datetime
import os

#info dicc que tiene todos los parametros dados abajo... y en el parametro Files, la cantidad de files 


class torrentFile():
    
    def __init__(self,announce,info,md5sum,optional=None,files=None,filesData=None,) -> None:
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

        self.md5sum=md5sum

        #"Listado de diccionarios, uno por archivo (contenido multiarchivo, evidentemente)"
        #self.info["Files"]=[]
        
        
        # for i in range(0,int(files)):
        #    newDicc={}
        #    self.info["Files"].append(newDicc)
        #    #Listado de cadenas de los nombres de los subdirectorios, siendo el final el que dé el nombre verdadero al archivo. 
        #    self.info["Files"][i]["Path"]=filesData[i]["Path"]
        #    
        #    #Una vez más, el número de bytes del archivo.
        #    self.info["Files"][i]["Length"]=filesData[i]["Length"]

        #estas salen como que pueden ser opcionales
        if optional!=None:

            if optional["creationDate"]!=None:
                self.creationDate=optional["creationDate"]
            if optional["comment"]!=None:   
                self.comment["comment"]=optional["comment"]
            if optional["createdBy"]!=None:
                self.createdBy["createdBy"]=optional["createdBy"]
            if optional["updatedBy"]!=None:
                self.updatedBy["updatedBy"]=optional["updatedBy"]
            self.announcelist=optional["announceList"]
            if optional["private"]!=None:
                self.private=optional["private"]
            self.createdBy=optional["createdBy"]
            self.private=optional["private"]
            
            
        
        
            
    def readTorrent(ruteName):
        file = open(ruteName, "w")
        textBytes=file.read()
        file.close()
        decodeData=bencode.decode(textBytes)

        print (decodeData)
        print("a")
        
        announce=decodeData["announce"]
        info=decodeData["info"] 
        announceList=decodeData["announceList"]
        creationDate=decodeData["creationDate"]
        comment=decodeData["comment"]
        createdBy=decodeData["createdBy"]
        private=decodeData["private"]
        md5sum=decodeData["md5sum"]
        
        optional={}
        optional["announceList"]=announceList
        optional["creationDate"]=creationDate
        optional["comment"]=comment 
        optional["createdBy"]=createdBy
        optional["private"]=private
        
        myTorrent=torrentFile(announce,info,md5sum,optional)
        return myTorrent
    
    #def readTorrent(codes):
    #    #file = open(ruteName, "w")
    #    #textBytes=file.read()
    #    #file.close()

    #    decodeData=bencode.decode(codes)
    #    print (decodeData)
    #    
    #    print("a")
        
    def createTorrent(tData):
        resultEncode=None
        
        #parche
        fullDicc={}
        
        fullDicc["announce"]=tData.announce
        fullDicc["info"]=tData.info
        fullDicc["announceList"]=tData.announcelist
        fullDicc["creationDate"]=tData.creationDate
        fullDicc["comment"]=tData.comment
        fullDicc["createdBy"]=tData.createdBy
        fullDicc["private"]=tData.private
        fullDicc["md5sum"]=tData.md5sum
        
        resultEncode=bencode.encode(fullDicc)
        
        #resultEncode=bencode.encode(tData.announce)
        #resultEncode+=bencode.encode(tData.info)
        #resultEncode+=bencode.encode(tData.announcelist)
        #resultEncode+=bencode.encode(tData.creationDate)
        #resultEncode+=bencode.encode(tData.comment)
        #resultEncode+=bencode.encode(tData.createdBy)
        #resultEncode+=bencode.encode(tData.private)
        
        
        #esto arreglarlo
        
        print(resultEncode)
        rute=str(tData.info["Name"])+".torrent"
        print("a")
        print(rute)
        file = open(rute, "wb")
        file.write(resultEncode)
        file.close()
        
        
        return resultEncode
        
        

#test case-------------------------------------------------------------------------------
announce="https://wiki.theory.org/BitTorrentSpecification#Bencoding"

info={}
name="FirstNameTorrent"
pieces=[43,21,324]

info["Name"]=name
info["PieceLength"]=492012
info["Pieces"]=pieces
info["Length"]=8306

#files={}
#filesNames=["/FirstNameTorrent1","/FirstNameTorrent2","/FirstNameTorrent3"]
#filesLength=[4002,4002,302]

optional={}

announceList=["https://wiki.theory.org/BitTorrentSpecification#Bencoding","https://docs.racket-lang.org/bencode/index.html"]
creationDate=str(datetime.datetime.now())
comment="this is a torrentFile"
createdBy="hot-dog create the file using JJD-torrent"
private=0

optional["announceList"]=announceList
optional["creationDate"]=creationDate
optional["comment"]=comment
optional["createdBy"]=createdBy
optional["private"]=private
#--------------------------------------------------------

#testing methods
testFile=torrentFile(announce,info,optional)
bencodeData=torrentFile.createTorrent(testFile)
testTorrent=torrentFile.readTorrent(bencodeData["announce"]) 

print("awesome torrent")        


