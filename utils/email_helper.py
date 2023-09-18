import poplib
import time
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr, mktime_tz
from datetime import datetime
from fnmatch import fnmatch, fnmatchcase
from email.utils import parsedate_tz


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def get_info(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject', 'Date']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                elif header == 'Date':
                    value = decode_str(value)

                    value = datetime.strptime(value, '%d %b %Y %H:%M:%S %z').astimezone().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))
    if msg.is_multipart():
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            get_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))


class EmailReader:

    def __init__(self, address: str, password: str, pop3_server: str, debug=False):
        self.server = None
        self.address = address
        self.password = password
        self.pop3_server = pop3_server
        self.debug = debug
        self.connect()

    def connect(self):
        self.server = poplib.POP3(self.pop3_server)
        if self.debug:
            self.server.set_debuglevel(1)
        self.server.user(self.address)
        self.server.pass_(self.password)

    def close(self):
        if self.server:
            self.server.quit()

    def last_email(self, last_time=time.time(), timeout=60, **header_filter):
        self.connect()
        resp, mails, octets = self.server.list()
        index = len(mails)
        resp, lines, octets = self.server.retr(index)
        top_5 = []
        for i in range(5):
            resp, lines, octets = self.server.retr(index - i)
            top_5.append(lines)
        self.close()
        for lines in top_5:
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            localtime = mktime_tz(parsedate_tz(msg.get('Date')))
            if localtime >= last_time:
                for header in header_filter:
                    if header in ['From', 'To', 'Subject']:
                        _filter = header_filter.get(header)
                        value = msg.get(header, '')
                        if header == 'Subject':
                            value = decode_str(value)
                            if not fnmatch(value, _filter):
                                break
                        else:
                            hdr, addr = parseaddr(value)
                            name = decode_str(hdr)
                            if not fnmatch(addr, _filter):
                                break
                            # value = u'%s <%s>' % (name, addr)
                else:
                    return msg
        else:
            if time.time() - last_time > timeout:
                return None
            return self.last_email(last_time=last_time, timeout=timeout, **header_filter)


if __name__ == '__main__':
    er = EmailReader('zhengquan@darana.cn', 'Zq13883500424', 'pop3.mxhichina.com')
    er.connect()
    email = er.last_email()
    print(email)
