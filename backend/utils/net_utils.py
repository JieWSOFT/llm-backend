import socket

def get_host_ip():
    res = socket.gethostbyname(socket.gethostname())
    return res
