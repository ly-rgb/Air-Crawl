import random
data = [f'private.residential.proxyrack.net:{x}' for x in range(10000, 10005)]
user = '981135637'
password = 'a1428b-69092a-187b6e-3ad6ee-00e81a'


def get_astoip_proxy():
    ip = random.choice(data)
    return f"socks5://{user}:{password}@{ip}"


def get_astoip_http_proxy():
    ip = random.choice(data)
    return f"http://{user}:{password}@{ip}"