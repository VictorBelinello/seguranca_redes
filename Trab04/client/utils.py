from random import randint
import json
import requests
from Crypto.Cipher import DES

def pad(text):
    n = 8 - len(text) % 8
    print(n)
    return text + (b' ' * n)

def get_tgt(user):
    partial = {
        "ID_S": 10,
        "T_R": 60,
        "N1": randint(1, 100)
    },
    msg = json.dumps(partial).encode()
    cipher = DES.new(b"FC4BFA51",DES.MODE_ECB)
    msg = pad(msg)
    msg = cipher.encrypt(msg)
    m1 = {
        "ID_C": user[0],
        "msg": msg.decode("latin1")
    }
    resp = requests.get(f"http://localhost:3000", json=m1)
    print(resp.json())
    return
    resp = resp.json()
    if resp["status"] == "ok":
        print("TGT obtido com sucesso.")
        return resp["tgt"]
    else:
        print("Não foi possível obter o tgt, você não está cadastrado no AS.")
        exit()
