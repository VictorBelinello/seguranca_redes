import socket
from threading import Thread
import requests

HOST = ''
PORT = 8081       # Port to listen on (non-privileged ports are > 1023)


def error_response():
    with open("index.html") as f:
        response = f.read()
    return response.encode()


def parse_request(req: bytes) -> bytes:
    text = req.decode("latin-1")
    if "monitorando" in text:
        return error_response()

    headers = text.split("\r\n")
    url = headers[0].split(" ")[1]

    original = requests.get(url)
    return original.content


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor ouvindo na porta {PORT}")
        while True:
            conn, addr = s.accept()
            print(f"Nova conexão de: {addr}")
            data = conn.recv(1024)
            if not data:
                break
            response = parse_request(data)
            conn.sendall(response)
