from auto_check.check_server import app as check_app
from auto_check.check_server import task


if __name__ == '__main__':
    check_app.run('0.0.0.0', 5000, threaded=True)