import visual.visual_globals as vg
import os
import re



def check_piece_size():
    
    result =match_size()
    return result    


def match_size():
    
    match vg.piece_size:
        case "256Kb":
            return [256,0]
        case "512Kb":
            return [512,0]
        case "1Mb":
            return [1024,0]
        case default:
            return [256,1]
        
def file_location_create():
    if os.path.isfile(vg.file_location):
        return vg.file_location
    return -1

def folder_location_create():
    if os.path.isdir(vg.folder_location):
        return vg.folder_location
    return -1

def creator_name_check():
    return str(vg.creator_name)

def comment_check():
    return str(vg.comment)

def tracker_list_check():
    split_list=re.split(' |\\n',vg.tracker_list) 
    result_list=[]
    error_list=""
    for item in split_list:
        if item=="":
            continue 
        #if re.match("\d+.\d+.\d+.\d+/:dt+",str(item)):
        result_list.append(str(item))
        #else:
        #    error_list+=str(item)+"\n"
    return [result_list,error_list]

def check_create_integrity():
    result=[]
    
    result.append(check_piece_size())
    result.append(file_location_create())
    result.append(folder_location_create())
    result.append(creator_name_check())
    result.append(comment_check())
    result.append(tracker_list_check())
    
    return result

def file_location_download():
    if os.path.isfile(vg.torrent_location):
        temp=vg.torrent_location.split(".")
        if temp[len(temp)-1]=="torrent":
            return vg.torrent_location
    return -1

def folder_location_create():
    if os.path.isdir(vg.folder_location_download):
        return vg.folder_location_download
    return -1

def check_download_integrity():
    result=[]
    
    result.append(file_location_download())
    result.append(folder_location_create())
    
    return result