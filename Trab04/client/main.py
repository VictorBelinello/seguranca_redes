from utils import get_tgt
def start_client():
    print("Iniciando cliente")
    user = (1, "12345")
    tgt = get_tgt(user)
    send_tgt_to_tgs(tgt)



def send_tgt_to_tgs(tgt):
    print("Enviando TGT para TGS")

if __name__=="__main__":
    start_client()