from socketserver import ThreadingTCPServer, BaseRequestHandler
import requests
from syslog import syslog
import hashlib


class ProxyHandler(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()

        response = self.parse_request(data)
        self.request.sendall(response)

    def parse_request(self, req: bytes) -> bytes:
        text = req.decode("latin-1")
        headers = text.split("\r\n")
        if len(headers) < 2:
            return b""
        syslog(f"IP cliente {self.client_address}. {headers[1]}")
        if "monitorando" in text:
            syslog(f"Acesso bloqueado. Recurso: {headers[0]}")
            return self.error_response()

        try:
            url = headers[0].split(" ")[1]

            original = requests.get(url)
            syslog(f"Status code: {original.status_code}")
            return original.content
        except:
            syslog("Erro interno")
            return b""

    def error_response(self) -> bytes:
        with open("index.html") as f:
            response = f.read()
        return response.encode()


if __name__ == "__main__":
    checksum = hashlib.md5(open('proxy_thread.py', 'rb').read()).hexdigest()
    with open("checksum.txt") as f:
        right_checksum = f.read()

    if checksum != right_checksum:
        msg = "Checksum invalido, o codigo foi alterado!"
        syslog(msg)
        print(msg)
        exit(1)

    PORT = 8081
    with ThreadingTCPServer(("", PORT), ProxyHandler) as server:
        print(f"Servindo rodando na porta {PORT}")
        server.serve_forever()
