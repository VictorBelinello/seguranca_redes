import argparse
import hashlib
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('username',type=str,help='Nome de usuario')
    parser.add_argument('password',type=str,help='Senha de usuario')
    parser.add_argument('-seed',type=str,help='Senha semente')

    return parser.parse_args()

def save_new_user(username : str, password : str, seed : str):
    filename = username + ".txt"
    with open(filename,'w') as file:
        hashed = get_hash(password)
        file.write(hashed)

        file.write("\n")
        
        hashed = get_hash(seed)
        file.write(hashed)

def user_exists(username : str, password : str) -> bool:
    filename = username + ".txt"
    path = Path(filename)
    if path.exists() and path.is_file():
        hashed = get_hash(password)
        with path.open() as f:
            saved_hashed = f.readline().strip()
        return hashed == saved_hashed
    else:
        return False

def get_user_seed(username : str) -> str:
    filename = username + ".txt"
    lines = []
    with open(filename) as f:
        lines = f.readlines()
    return lines[1]

def get_hash(text : str) -> str:
    m = hashlib.md5()
    text_bytes = text.encode('utf-8')
    m.update(text_bytes)
    hashed = m.hexdigest()
    return hashed