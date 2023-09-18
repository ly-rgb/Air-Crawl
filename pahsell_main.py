from config import config
from manager import init, run
import urllib3
from api import app
import sys
import threading
from auto_check.check_server import app as check_app

urllib3.disable_warnings()


if __name__ == '__main__':
    argv = sys.argv
    port = 10241
    if len(argv) > 1:
        config.proxy_type = int(argv[1])
        port = int(argv[2])
    threading.Thread(target=app.run, args=("0.0.0.0",), kwargs={'port': port, "threaded": True}).start()
    #threading.Thread(target=check_app.run, args=("0.0.0.0",), kwargs={'port': 5000, "threaded": True}).start()
    init()
