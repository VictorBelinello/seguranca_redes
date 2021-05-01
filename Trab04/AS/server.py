from database import users
import flask
from flask import request
import json
from des import DesKey
from secrets import token_bytes

app = flask.Flask(__name__)
app.config["DEBUG"] = True


class AS:
    TGS_KEY = b'4K\xcd\x17\x85\x92\xfc\xd6'

    def __init__(self, request: dict) -> None:
        self.client_id, self.client_message = request["id_c"], request["message"]
        client_key = self.get_user_key()
        if client_key == bytes():
            self.response = json.dumps({"status": "falha"})
        else:
            self.response = self.make_response(client_key)

    def get_user_key(self) -> bytes:
        for user in users:
            if user["id"] == self.client_id:
                return user["key"]
        return bytes()

    def make_response(self, client_key: bytes):
        self.client_message = self.decrypt(client_key, self.client_message)
        print(f"Recebido {self.client_message}")
        try:
            self.client_message = json.loads(self.client_message)
        except Exception as e:
            print(e)
            return {"ERRO": "Não autenticado no AS"}

        client_tgs_key = self.generate_session_key()
        first_part = {"client_tgs_key": client_tgs_key,
                      "number": self.client_message["number"]}

        first_part = json.dumps(first_part)

        first_part_encr = self.encrypt(client_key, first_part)
        # mensagem m2
        response = {
            "first_part": first_part_encr,
            "TGT": self.build_tgt(client_tgs_key)
        }
        return json.dumps(response)

    def generate_session_key(self) -> str:
        return token_bytes(8).decode("latin1")

    def build_tgt(self, client_tgs_key) -> str:
        message = {
            "id_c": self.client_id,
            "timeout": self.client_message["timeout"],
            "client_tgs_key": client_tgs_key
        }
        tgt = json.dumps(message)

        print(f"Enviando TGT: {tgt}")
        tgt_encr = self.encrypt(self.TGS_KEY, tgt)
        return tgt_encr

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
    server = AS(request.json)
    return server.response


app.run()
