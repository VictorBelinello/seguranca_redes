import flask
from flask import request
import json
from des import DesKey
from secrets import token_bytes

app = flask.Flask(__name__)
app.config["DEBUG"] = True


class TGS:
    TGS_KEY = b'4K\xcd\x17\x85\x92\xfc\xd6'
    SERVICE_KEY = b'{H\x85@\x7fM\xc6\xe4'

    ALLOWED = {
        10: [1, 2]
    }

    def __init__(self, request: dict) -> None:
        client_request, self.tgt = request["first_part"], request["TGT"]
        tgt = self.decrypt_tgt()
        session_key = tgt["client_tgs_key"].encode("latin1")
        client_request = self.decrypt(session_key, client_request)
        try:
            client_request = json.loads(client_request)
            self.response = self.make_response(client_request, session_key)
        except json.decoder.JSONDecodeError:
            self.response = {
                "msg": "Não foi possível converter a requisição para JSON, provavelmente a chave de sessão está errada."}

    def decrypt_tgt(self) -> dict:
        tgt = self.decrypt(self.TGS_KEY, self.tgt)
        return json.loads(tgt)

    def make_response(self, client_request: dict, client_tgs_key: bytes):
        print(f"Recebido {client_request}")
        target_service = client_request["id_s"]
        clients_allowed = self.ALLOWED[target_service]
        client_id = client_request["id_c"]
        if client_id not in clients_allowed:
            return {"ERRO": "Você não tem permissão de acessar esse serviço"}

        client_service_key = self.generate_session_key()
        timeout = client_request["timeout"]
        first_part = {
            "client_service_key": client_service_key,
            "timeout": timeout,
            "number2": client_request["number2"]

        }
        first_part_str = json.dumps(first_part)
        first_part_encr = self.encrypt(client_tgs_key, first_part_str)

        service_ticket = {
            "id_c": client_request["id_c"],
            "timeout": timeout,
            "client_service_key": client_service_key
        }

        service_ticket_str = json.dumps(service_ticket)
        service_ticket_encr = self.encrypt(
            self.SERVICE_KEY, service_ticket_str)

        print(f"Para cliente: {first_part}")
        print(f"Ticket: {service_ticket}")

        # Mensagem m4
        response = {
            "first_part": first_part_encr,
            "service_ticket": service_ticket_encr
        }
        return response

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

    def generate_session_key(self) -> str:
        return token_bytes(8).decode("latin1")


@app.route('/', methods=['GET'])
def home():
    server = TGS(request.json)
    return server.response


app.run(port=5001)
