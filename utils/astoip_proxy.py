import random
data = [f'usa.rotating.proxyrack.net:{x}' for x in range(10000, 10999)]


def get_astoip_proxy():
    ip = random.choice(data)
    return f"socks5://{ip}"


def get_astoip_http_proxy():
    ip = random.choice(data)
    return f"http://{ip}"
