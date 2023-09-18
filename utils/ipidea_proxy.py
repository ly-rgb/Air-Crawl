import requests, time


def get_ipidea_proxy(regions='us'):
    url = f"http://api.proxy.ipidea.io/getProxyIp?num=1&lb=1&sb=0&flow=1&regions={regions}&protocol=http"
    # url = f"http://tiqu.linksocket.com:81/abroad?num=1&type=1&lb=1&sb=0&flow=1&regions={regions}&port=1"
    try:
        response = requests.get(url, timeout=5)
        if '{' in response.text:
            time.sleep(5)
            return get_ipidea_proxy()
        return 'http://' + response.text.replace("\r\n", "")
    except Exception as e:
        return get_ipidea_proxy()


def get_ipidea_proxy_fr():
    url = 'http://api.proxy.ipidea.io/getProxyIp?num=1&return_type=txt&lb=1&sb=0&flow=1&regions=fr&protocol=http'
    try:
        response = requests.get(url, timeout=5)
        if '{' in response.text:
            time.sleep(5)
            return get_ipidea_proxy_fr()
        return 'http://' + response.text.replace("\r\n", "")
    except Exception as e:
        return get_ipidea_proxy_fr()


if __name__ == '__main__':
    print(get_ipidea_proxy())