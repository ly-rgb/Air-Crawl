import requests


def get_ip_idea():
    url = "http://tiqu.ipidea.io:2330/getProxyIp?num=1&return_type=json&lb=1&sb=0&flow=1&regions=us&protocol=http"
    res = requests.get(url)
    print(res.text)
    data = res.json()['Data'][0]
    proxyHost = data['ip']
    proxyPort = data['port']
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }
    return proxyMeta


if __name__ == '__main__':
    print(get_ip_idea())
