import os
from datetime import datetime


def save_msg_file(path: str, filename: str, content, mode='a'):
    if not filename:
        raise Exception('Illegal filename')
    if not path:
        raise Exception('Illegal path')
    if not content:
        content = ""
    if not mode:
        mode = 'a'
    content = f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}]{content}\n'
    root = './files/'
    if path[0] == '/':
        path = path[1:]
    if path[-1] == '/':
        path = path[:-1]
    path = f'{root}{path}/{datetime.now().strftime("%Y-%m-%d")}'
    if not os.path.exists(path):
        os.makedirs(path)
    if '/' in filename:
        raise Exception('Illegal filename')
    with open(f'{path}/{filename}', mode) as f:
        f.write(content)


class MsgFileRecorder:
    """
    单个消息日志文件记录器
    :param domain: 文件保存领域
    :param filename: 文件名
    :param mode: 写入模式
    """

    def __init__(self, domain,  mode='a', suffix='log'):
        self.domain = domain
        self.mode = mode
        self.suffix = suffix

    def msg(self, filename: str, msg: str):
        save_msg_file(self.domain, f'{filename}.{self.suffix}', msg, self.mode)




