import base64

import traceback
import random


def decode(ciphertext: str) -> str:
    try:
        return base64.b64decode(ciphertext.replace('-', '=').encode(), altchars='_-'.encode()).decode()
    except:
        traceback.print_exc()
        return ""


def encode(text: str) -> str:
    try:
        if len(text) < 5:
            return None
        return base64.b64encode(text.encode(), altchars='_-'.encode()).decode().replace('=', '-')
    except:
        return ""


if __name__ == '__main__':
    proxy_list = [12, 11, 10, 39]
    proxies_type = random.choice(proxy_list)
    print(proxies_type)
    print(encode('1~G~ ~NK~GA7NR~0001~~0~8~~^2~N~ ~NK~N7CLUBZ5~9FCL~~0~5~~X!0'))
    print(decode(encode('1~G~ ~NK~GA7NR~0001~~0~8~~^2~N~ ~NK~N7CLUBZ5~9FCL~~0~5~~X!0')))

