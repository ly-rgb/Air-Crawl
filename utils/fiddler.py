def headers_parser(hstr: str):
    hstr = hstr.strip().split('\n')
    headers = {}
    for line in hstr:
        line = line.strip()
        if ": " in line:
            k, v = line.split(': ', 1)
            headers[k] = v
    return headers



