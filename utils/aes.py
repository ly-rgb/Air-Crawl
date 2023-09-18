import base64
import binascii
import re
from Crypto.Cipher import AES


class AESCBC:
    def __init__(self, key, vi):
        self.key = key  # 定义key值
        self.vi = vi
        self.mode = AES.MODE_CBC
        self.bs = 16  # block size
        self.PADDING = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def encrypt(self, text):
        generator = AES.new(self.key, self.mode, self.vi)  # 这里的key 和IV 一样 ，可以按照自己的值定义
        crypt = generator.encrypt(self.PADDING(text).encode())
        crypted_str = base64.b64encode(crypt)   #输出Base64
        # crypted_str = binascii.b2a_hex(crypt)  # 输出Hex
        result = crypted_str.decode()
        return result

    def decrypt(self, text):
        generator = AES.new(self.key, self.mode, self.vi)
        text += (len(text) % 4) * '='
        decrpyt_bytes = base64.b64decode(text)           #输出Base64
        # decrpyt_bytes = binascii.a2b_hex(text)  # 输出Hex
        meg = generator.decrypt(decrpyt_bytes)
        # 去除解码后的非法字符
        try:
            result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', meg.decode())
        except Exception:
            result = '解码失败，请重试!'
        return result


if __name__ == '__main__':
    aes = AESCBC()

    to_encrypt = '123456'
    to_decrypt = 'sN00C5okGvSnd0rK+X2hYOL2Cwpxuu0y1Lf0lakBXbmMZDjewXElC8ppP4n+NskVge5IG6qVBzk9p1N3E1oUng=='

    print("\n加密前:{0}\n加密后：{1}\n".format(to_encrypt, aes.encrypt(to_encrypt)))
    print("解密前:{0}\n解密后：{1}".format(to_decrypt, aes.decrypt(to_decrypt)))
