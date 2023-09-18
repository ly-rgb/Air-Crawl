import re
import os
import string
import sys
from importlib.util import find_spec
from os.path import join, exists, abspath
from shutil import ignore_patterns, move, copy2, copystat
from stat import S_IWUSR as OWNER_WRITE_PERMISSION
import scrapy
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError

IGNORE = ignore_patterns('*.pyc', '__pycache__', '.svn')


def _make_writable(path):
    current_permissions = os.stat(path).st_mode
    os.chmod(path, current_permissions | OWNER_WRITE_PERMISSION)


def render_templatefile(path, **kwargs):
    with open(path, 'rb') as fp:
        raw = fp.read().decode('utf8')

    content = string.Template(raw).substitute(**kwargs)

    render_path = path[:-len('.tmpl')] + ".py" if path.endswith('.tmpl') else path

    if path.endswith('.tmpl'):
        os.rename(path, render_path)

    with open(render_path, 'wb') as fp:
        fp.write(content.encode('utf8'))


class Command:
    def _is_valid_name(self, project_name):
        if not re.search(r'^[A-Z\d]{2}$', project_name):
            print('Error: 命名语法不规范')
            return True

    def _copytree(self, src, dst):
        """
        Since the original function always creates the directory, to resolve
        the issue a new function had to be created. It's a simple copy and
        was reduced for this case.
        """
        ignore = IGNORE
        names = os.listdir(src)
        ignored_names = ignore(src, names)

        if not os.path.exists(dst):
            os.makedirs(dst)

        for name in names:
            if name in ignored_names:
                continue

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self._copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
                _make_writable(dstname)

        copystat(src, dst)
        _make_writable(dst)

    def run(self):
        args = sys.argv[2:]
        if len(args) not in (1, 2):
            raise UsageError()

        project_name = args[0]
        project_dir = args[0]
        url = args[1]

        project_dir = join("airline", f"A{project_dir}")

        if exists(project_dir):
            print(f'Error: 该航线已经存在！')
            return

        self._copytree(self.templates_dir, abspath(project_dir))  # 移动 templates/project/* 到 当前的绝对路径
        move(join(project_dir, 'module.tmpl'), join(project_dir, f'A{project_name}Web.tmpl'))  # 改名module
        for path in os.listdir(project_dir):
            path = join(project_dir, path)
            render_templatefile(path, flightNumber=project_name, url=url)

    @property
    def templates_dir(self):
        return "./templates/module"


if __name__ == '__main__':
    c = Command()
    c.run(["2Z"], None)
