from typing import Tuple
from flask import json
import requests
from random import randint
from datetime import datetime, timedelta
from des import DesKey


class Client:
    AS_URL = "http://localhost:5000"
    TGS_URL = "http://localhost:5001"
    SERVICE_URL = "http://localhost:5002"

    def __init__(self) -> None:
        self.id = 1
        self.key = b"\xb0\x04\x97\xd8\xb3)#\x1d"
        self.id_service = 10
        self.timeout = self.get_timeout()

    def start(self):
        print(f"Iniciando client {self.id}")
        tgt = self.getTGT()
        first_part, ticket = self.get_ticket(tgt)
        self.client_service_key = first_part["client_service_key"].encode(
            "latin1")
        resource = self.get_service_resource(ticket)
        print(resource)

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

    def getTGT(self):
        print("Obtendo TGT")
        payload, check_number = self.get_tgt_payload()
        response = requests.get(self.AS_URL, json=payload).json()
        if "ERRO" in response:
            print("Falha ao obter TGT")
            print(response["ERRO"])
            exit()
        first_part = response["first_part"]
        self.handle_response(first_part, check_number)
        print("TGT obtido")
        return response["TGT"]

    def get_tgt_payload(self) -> Tuple[dict, int]:
        number = randint(0, 100)
        message = {
            "id_s": self.id_service,
            "timeout": self.timeout,
            "number": number
        }
        print(message)
        message_encr = self.encrypt(self.key, json.dumps(message))
        # mensagem m1
        payload = {
            "id_c": self.id,
            "message": message_encr}
        return payload, number

    def get_timeout(self) -> float:
        now = datetime.now()
        final_date = now + timedelta(seconds=5)
        return final_date.timestamp()

    def handle_response(self, response: str, verification_number: int):
        key = DesKey(self.key)
        response = key.decrypt(response.encode("latin1"),
                               padding=True).decode("latin1")
        response_dict = json.loads(response)
        number = response_dict["number"]

        if number != verification_number:
            print("Número aleatório não bate")
            print(f"Recebeu {number} esperando {verification_number}")
            exit()

        self.client_tgs_key = response_dict["client_tgs_key"].encode("latin1")

    def get_ticket(self, tgt: str) -> tuple:
        print("Pedindo ticket para serviço")
        payload, check_number = self.get_ticket_payload(tgt)
        response = requests.get(self.TGS_URL, json=payload).json()

        if "ERRO" in response:
            print("Erro ao obter Ticket")
            print(response["ERRO"])
            exit()

        first_part = response["first_part"]
        first_part = self.decrypt(self.client_tgs_key, first_part)
        first_part = json.loads(first_part)

        num = first_part["number2"]
        if num != check_number:
            print("O número aleatório recebe é diferente")
            print(f"Esperando {check_number} recebeu {num}")
            exit()

        service_ticket = response["service_ticket"]
        print("Ticket obtido")
        return first_part, service_ticket

    def get_ticket_payload(self, tgt: str) -> Tuple[dict, int]:
        number2 = randint(0, 100)
        first_part = {
            "id_c": self.id,
            "id_s": self.id_service,
            "timeout": self.timeout,
            "number2": number2
        }
        print(first_part)
        first_part_str = json.dumps(first_part)
        first_part_encr = self.encrypt(self.client_tgs_key, first_part_str)
        # mensagem m3
        payload = {
            "first_part": first_part_encr,
            "TGT": tgt
        }

        return payload, number2

    def get_service_resource(self, ticket: str) -> str:
        payload, check_number = self.get_service_resource_payload(ticket)
        response = requests.get(self.SERVICE_URL, json=payload).json()
        response_encr = response["response"]
        response = self.decrypt(self.client_service_key, response_encr)
        response = json.loads(response)
        num = response["number3"]
        if num != check_number:
            print("O número aleatório recebe é diferente")
            print(f"Esperando {check_number} recebeu {num}")
            exit()
        return response["data"]

    def get_service_resource_payload(self, ticket: str):
        number3 = randint(0, 100)
        first_part = {
            "id_c": self.id,
            "timeout": self.timeout,
            "service_requested": "arquivo.txt",
            "number3": number3
        }
        print(first_part)
        first_part_str = json.dumps(first_part)
        first_part_encr = self.encrypt(self.client_service_key, first_part_str)
        # mensagem 5
        payload = {
            "first_part": first_part_encr,
            "service_ticket": ticket
        }
        return payload, number3
