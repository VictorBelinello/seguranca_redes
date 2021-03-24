from token_gen_utils import *
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

def request_loop(seed : str):
    minute_of_request = -1
    while True:
        opt = input("Pressione ENTER para obter os tokens. Digite q para sair.")
        if opt == 'q':
            break
        tokens = generate_tokens(seed)
        print(tokens)

if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.seed is None:
        if user_exists(arguments.username, arguments.password):
            print("Logando")
            seed = get_user_seed(arguments.username)
            request_loop(seed)
        else:
            print("Login não encontrado:")
            print(arguments.username,arguments.password)
    else:
        save_new_user(arguments.username,arguments.password,arguments.seed)