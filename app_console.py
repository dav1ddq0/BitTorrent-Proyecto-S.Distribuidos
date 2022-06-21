
import os
from matplotlib import use

from sqlalchemy import false, true
from torrent_creator import TorrentCreator
from torrent_reader import TorrentReader
from torrent_info import TorrentInfo
import os

#(self, path_file: str, piece_size: int, private: bool, trackers_urls: list[str], comments: str, source: str):
def torrent_creator_console():
    userActionRute= ''
    userActionSize = ''
    userActionPrivate = ''
    userActionTrackers = []
    userActionComments = ''
    userActionSource = ''
    
    print("Creando torrent...")
        
    while true:
        print("Escriba la ruta del archivo junto con su nombre./n Si desea cancelar escriba cancel./n")
        userActionRute= input()
        if userActionRute.lower()=="cancel":
            return -1
        if os.path.isfile(userActionRute): 
            break
        print("Ruta o archivo invalido./n")
    while true:
        print("Escriba el tamaño de los pieces./n Si desea cancelar escriba cancel./n")
        userActionSize= input()
        if userActionSize.lower()=="cancel":
            return -1
        try:
            userActionSize=int(userActionSize)
            break
        except:
            print("Numero invalido./n")
    print("Quiere activar el modo privado? (s/n)./n Si desea cancelar escriba cancel./n")
    while True:
        userActionPrivate= input()
        if userActionPrivate.lower()=="cancel":
            return -1
        if userActionPrivate.lower()=="s" :
            userActionPrivate= true
        elif userActionPrivate.lower()=="n":
            userActionPrivate= false
        else :
            print ("Accion invalida./n")
            continue
        break
    
    print("Escriba los trackers(urls)./n Si desea para de añadir trackers escriba 0./n Si desea cancelar escriba cancel./n")
    while True :
        userActionTracker= input()
        if userActionTracker.lower()=="cancel":
            return -1
        if userActionTracker.lower()=="0":
            break
        userActionTrackers.append(userActionTracker)
        
    print("Escriba un comentario./n Si no quiere agregar comentario escriba 0. Si desea cancelar escriba cancel./n")    
    userActionComments= input()
    if userActionComments.lower()=="0":
        userActionComments= ''
        
    print("Escriba la fuente./n Si no quiere agregar fuente escriba 0. Si desea cancelar escriba cancel./n")    
    userActionSource= input()
    if userActionSource.lower()=="0":
        userActionSource= ''
        
    
    torrent_creator = TorrentCreator(userActionRute, userActionSize, userActionPrivate, userActionTrackers, userActionComments, userActionSource)
    torrent_creator.create_dottorrent_file('./')
    
    print("Torrent creado...")

def main():
    
    print("Hola! Esta usando Super-Mytorrent.")
    while True:
        print("\n\n")
        print("Escriba 1 para crear un torrent./n")
        print("Escriba 2 para descargar un torrent./n")
        print("Escriba 3 para salir de Super-Mytorrent./n")
        print("(*-*)/n")
        userAction= input()
        
        print("asdfasdfasd")
        
        match userAction:
            case "1":
                torrent_creator_console()
            case "2":
                pass
            case "3":
                break
            case default:
                print("Esa opción no existe./n")
        print("asdfasdfasd")
main()
print("Finish!!!")