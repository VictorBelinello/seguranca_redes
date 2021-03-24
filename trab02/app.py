from app_utils import *
from datetime import datetime


def generate_tokens(seed : str) -> list:
    NUM_OF_TOKENS = 3
    tokens = []
    for _ in range(NUM_OF_TOKENS):
        current_min = datetime.now().minute
        minute = f"{current_min:02d}"
        seed += minute
        token = get_hash(seed)
        tokens.append(token)
        seed = token
    return tokens

def validate_token(token:str, possible_tokens:list) -> int:
    for indx, t in enumerate(possible_tokens):
        if t.startswith(token):
            return indx
    return -1

def already_invalidated(token:str, invalid_tokens:list)->bool:
    for t in invalid_tokens:
        if t.startswith(token):
            return True
    return False


def request_loop(seed: str):
    invalid_tokens = []
    while True:
        opt = input("Informe o token. Digite q para sair.")
        if opt == 'q':
            break
        token = opt
        possible_tokens = generate_tokens(seed)
        indx = validate_token(token, possible_tokens)
        if indx != -1 and not already_invalidated(token, invalid_tokens):
                print("Token validado")
                invalid_tokens += possible_tokens[indx:]
        else:
            print("Token inválido")

if __name__ == "__main__":
    arguments = parse_arguments()
    if user_exists(arguments.username):
        seed = get_user_seed(arguments.username)
        request_loop(seed)
    else:
        print("Usuário não encontrado")