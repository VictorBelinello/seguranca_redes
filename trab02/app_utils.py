import argparse
import hashlib
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('username',type=str,help='Nome de usuario')

    return parser.parse_args()

def user_exists(username : str) -> bool:
    filename = username + ".txt"
    path = Path(filename)
    return path.exists() and path.is_file()

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