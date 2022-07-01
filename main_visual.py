import visual.my_visual as vis
import time
import visual.visual_globals as vg
import threading
import visual.check_visual_integrity as cvi
from dottorrent  import TorrentCreator, TorrentReader

window =vis.sg.Window("My_Torrent",vis.layout,size = (800,630),resizable = True,finalize=True)

def auto_update():
    #vg.download_size+=10
    #window["-DOWNLOAD-SIZE-"].update(str(vg.download_size)+"Kb")
    #vg.upload_size+=10
    #window["-UPLOAD-SIZE-"].update(str(vg.upload_size)+"Kb")
    threading.Timer(1,auto_update,[]).start()
    
def main():
    auto_update()
    while(True):    
        event, values = window.read()   

        window["-DOWNLOAD-SIZE-"].update(str(vg.download_size)+"Kb")
        window["-UPLOAD-SIZE-"].update(str(vg.upload_size)+"Kb")
        
        if event=="Exit" or event == vis.sg.WIN_CLOSED:
            try:
                window.close()
                break
            except:
                pass
        if event=="-CREATE-TORRENT-" :
            try:
                
                vg.piece_size=values["-PIECE-SIZE-"]
                vg.file_location=values["-FILE-LOCATION_CREATE-"]
                vg.folder_location=values["-FOLDER-LOCATION_CREATE-"]
                vg.creator_name=values["-CREATOR-NAME-"]
                vg.comment=values["-CREATOR-COMMENT-"]
                vg.tracker_list=values["-TRACKER_LIST-"]
                
                result_list= cvi.check_create_integrity()
                
                if result_list[1]==-1:
                    vis.sg.popup("Not valid file path.")
                    continue
                
                if result_list[2]==-1:
                    vis.sg.popup("Not valid download folder path.")
                    continue
                
                if result_list[0][1]==1:
                    vis.sg.popup("Not valid size. 256Kb will be used instead.")
                
                if result_list[5][1]!="":
                    vis.sg.popup("These trackers were not in the correct format please fix them or remove them:\n"+result_list[5][1])
                    continue
                
                print("a")
                torrent_creator = TorrentCreator(result_list[1], result_list[0][1], True, result_list[5][0], result_list[4], result_list[3])
                torrent_creator.create_dottorrent_file(result_list[2])
            except:
                pass
            
        if event=="-DOWNLOAD-FILE-" :
            try:
                vg.torrent_location=values["-FILE-LOCATION_DOWNLOAD-"]
                vg.folder_location_download=values["-FOLDER-LOCATION_DOWNLOAD-"]
                
                result_list=cvi.check_download_integrity()
                
                if result_list[0]==-1:
                    vis.sg.popup("Not valid torrent path.")
                    continue
                
                if result_list[1]==-1:
                    vis.sg.popup("Not valid download folder path.")
                    continue
                
                
                torrent_reader = TorrentReader(vg.torrent_location, vg.folder_location_download)
                torrent_info = torrent_reader.build_torrent_info()
            except:
                pass
        
            
            
main()


#102.2.1.4:2012
#103.2.1.4:2042
#104.2.1.4:2032
#105.2.1.4:2022