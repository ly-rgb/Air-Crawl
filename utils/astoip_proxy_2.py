import random
data = [f'209.205.212.36:{x}' for x in range(10000, 10250)]
user = 'daran'
password = '19fe2e-51a6a5-f70027-301237-19f977'


def get_astoip_proxy():
    ip = random.choice(data)
    return f"socks5://{user}:{password}@{ip}"


def get_astoip_http_proxy():
    ip = random.choice(data)
    return f"http://{user}:{password}@{ip}"
