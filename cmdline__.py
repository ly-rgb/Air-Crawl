import importlib
import sys


def excute():
    lib = importlib.import_module(f"commands.{sys.argv[1]}")
    lib.Command().run()


if __name__ == '__main__':
    excute()
