from datetime import datetime
from pathlib import Path
import time
import flask
from flask import request
import json
from des import DesKey

app = flask.Flask(__name__)
app.config["DEBUG"] = True


class Service:
    SERVICE_KEY = b'{H\x85@\x7fM\xc6\xe4'

    def __init__(self, request: dict) -> None:
        client_request, ticket = request["first_part"], request["service_ticket"]
        ticket = self.decrypt(self.SERVICE_KEY, ticket)
        ticket = json.loads(ticket)
        print(ticket)

        self.client_service_key = ticket["client_service_key"].encode("latin1")

        client_request = self.decrypt(self.client_service_key, client_request)
        client_request = json.loads(client_request)
        print(client_request)
        timeout = float(client_request["timeout"])
        now = datetime.now().timestamp()
        if timeout > now:
            self.response = self.make_response(client_request)
        else:
            self.response = {"msg": "Timeout expirado"}

    def make_response(self, client_request: dict) -> dict:
        print(f"Recebido {client_request}")
        resource = client_request["service_requested"]
        path = Path(__file__).parent.joinpath(resource)
        with open(path, 'r') as file:
            res = file.read()

        response = {
            "data": res,
            "number3": client_request["number3"]
        }
        print(f"Enviando: {response}")
        response_str = json.dumps(response)
        response_encr = self.encrypt(self.client_service_key, response_str)
        return {"response": response_encr}

    def encrypt(self, key_b: bytes, message: str) -> str:
        key = DesKey(key_b)
        message_bytes = message.encode("latin1")
        message_encr_bytes = key.encrypt(message_bytes,
                                         padding=True)
        message_encr = message_encr_bytes.decode("latin1")

        return message_encr

    def decrypt(self, key_b: bytes, message: str) -> str:
        key = DesKey(key_b)
        message_bytes = message.encode("latin1")
        message_encr_bytes = key.decrypt(message_bytes,
                                         padding=True)
        message_decr = message_encr_bytes.decode("latin1")

        return message_decr


@app.route('/', methods=['GET'])
def home():
    server = Service(request.json)
    return server.response


app.run(port=5002)
