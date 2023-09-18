import hashlib


def md5(s: str):
    m = hashlib.md5()
    m.update(s.encode())
    return m.hexdigest()


def sha512(s: str):
    m = hashlib.sha512()
    m.update(s.encode())
    return m.hexdigest()


if __name__ == '__main__':
    print(sha512('10077cebuairRwSy$a7q6h1642152085451'))
