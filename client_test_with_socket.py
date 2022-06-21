# echo-client.py
import pickle
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8002  #1 The port used by the server

sq = [ i*i for i in range(20)]
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(pickle.dumps(sq))
    s.send(pickle.dumps(sq))
    # data = s.recv(1024)

# print(f"Received {data!r}")