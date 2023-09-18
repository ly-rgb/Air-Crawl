import base64
from spider.model import Segment


def decode_key(ciphertext):
    key = base64.b64decode(ciphertext.replace('-', '=').encode(), altchars='_-'.encode()).decode()
    return key


if __name__ == '__main__':
    j = decode_key("Sjl_IDI1Mn4gfn5BTU1_MDkvMjIvMjAyMiAxMDo1NX5LV0l_MDkvMjIvMjAyMiAxMzowMH5_Xko5fiA3MzN_IH5_S1dJfjA5LzIyLzIwMjIgMTg6NDV_Q0FJfjA5LzIyLzIwMjIgMjA6MzB_fg--")
    f = decode_key('RmxpZ2h0SW5mbzp7ImZsaWdodE5vIjo1MDE2LCJkZXBhcnR1cmVEYXRlIjoiMjAyMi0wOS0yOFQxNzowNTowMC4wMDAtMDM6MDAiLCJpZCI6MTEwMjcyLCJsZklkIjoxMTAyNzIsIm9yaWdpbiI6IkFFUCIsImRlc3RpbmF0aW9uIjoiQ09SIiwic3RvcHMiOjB9')
    print(f)