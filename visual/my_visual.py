#menu

import PySimpleGUI as sg


sg.theme("Dark Grey 13")

qwery=''
location='' 
#windows 2 columns


#create torrent
location_file= sg.In(size=(25,1), enable_events=True,key="-FILE-LOCATION_CREATE-",background_color="white",text_color="black")
location_folder= sg.In(size=(25,1), enable_events=True,key="-FOLDER-LOCATION_CREATE-",background_color="white",text_color="black")
creator_name = sg.In(size=(25,1), enable_events=True,key="-CREATOR-NAME-",background_color="white",text_color="black")
comment_creator = sg.Multiline(size=(30,15), key="-CREATOR-COMMENT-",background_color="white",text_color="black")
tracker_list = sg.Multiline(size=(30,15), key="-TRACKER_LIST-",background_color="white",text_color="black")\
    


fileListColumn=[
    [
    sg.Text("Create Torrent:",justification="center",text_color="gold" )  ,    
        ],
    
    [
    sg.Text("Piece Size:",justification="right", )  ,
    sg.Text(" (Default: 256KB )",justification="right", ) ,
    sg.Combo(["256kb","512Kb","1Mb"],default_value="256Kb",background_color="white",text_color="black",key="-PIECE-SIZE-") ,
    ],
    [
        
        sg.Text("File Location    "),
        location_file,
        sg.FileBrowse(),
        ],
    [   
        
        sg.Text("Folder Location"),
        location_folder,
        sg.FolderBrowse(),
    
        ],
    [   
        
        sg.Text("Creator name  "),
        creator_name,
    
        ],
    [   
        
        sg.Text("Comment        "),
        comment_creator,
    
        ],
    [   
        
        sg.Text("Tracker list      "),
        tracker_list,
        ],
    [   
        sg.Button('Create Torrent',enable_events=True,key="-CREATE-TORRENT-", button_color=('Grey', 'white'))
        ],
    ]
#-------------------------------------------------------------------------------

location_file_download= sg.In(size=(25,1), enable_events=True,key="-FILE-LOCATION_DOWNLOAD-",background_color="white",text_color="black")
location_folder_download= sg.In(size=(25,1), enable_events=True,key="-FOLDER-LOCATION_DOWNLOAD-",background_color="white",text_color="black")

resultListColumn=[
    [
        sg.Text("Download file from torrent.    ",text_color="gold"),
        ],
    [
        
        sg.Text("Torrent Location    "),
        location_file_download,
        sg.FileBrowse(),
        ],
    [   
        
        sg.Text("Folder Location     "),
        location_folder_download,
        sg.FolderBrowse(),
    
        ],
    [
        sg.Text("Download Size     "),
        sg.Text("0Kb" ,key="-DOWNLOAD-SIZE-"),   
    ],
        [
        sg.Text("Upload Size       "),
        sg.Text("0Kb" ,key="-UPLOAD-SIZE-"),   
    ],
        [
    sg.ProgressBar(100,key="-PROGRESS-BAR-",size=(20,10),visible=True,bar_color=("blue","grey"),style="clam")
    ],
    [   
        sg.Button('Download File',enable_events=True,key="-DOWNLOAD-FILE-", button_color=('Grey', 'white'))
        ],    
    
]





# full layout
layout = [
    [   
        sg.Column(fileListColumn),
        sg.VSeparator(),
        sg.Column(resultListColumn),
        
    ]
]

#window =sg.Window("BV-Search",layout)

#event loop

    
                
#window.Close()