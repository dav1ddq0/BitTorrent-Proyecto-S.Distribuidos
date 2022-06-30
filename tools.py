import socket


def next_free_port( min_port=1024, max_port=65535 ):

    '''
        Give me available free port for listening
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while min_port <= max_port:
        try:
            sock.bind(('', min_port))
            sock.close()
            return min_port
        except OSError:
            min_port += 1
    raise IOError('no free ports')

def rpyc_deep_copy(obj):
    if (isinstance(obj, list)):
        copied_list = []
        for value in obj: copied_list.append(rpyc_deep_copy(value))
        return copied_list
    elif (isinstance(obj, dict)):
        copied_dict = {}
        for key in obj: copied_dict[key] = rpyc_deep_copy(obj[key])
        return copied_dict
    else:
        return obj
