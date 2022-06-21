import socket
import pickle

HOST = 'localhost'
PORT=8002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = b''
            chunk = conn.recv(1024)
            if not chunk:
                break
            # while(chunk):
            #     data += chunk
            #     chunk = 0
            data += chunk
            print(pickle.loads(data))
            if not data:
                break
            # conn.sendall(chunk)