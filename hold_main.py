import sys

from robot import Runnable
from airline.ADD import PayRobotDD
from multiprocessing import Process
from airline.AVY import RefundTaxRobotVY, RefundTaxRobotVYFull
from airline.A6J import RefundTaxRobot6J, RefundCheckRobot6J
from airline.A6E import RefundTaxRobot6E
from airline.AZ9 import PayRobotZ9


app_map = {
    '6J': [
           (RefundTaxRobot6J, 1, 1, 0),
           (RefundCheckRobot6J, 1, 1, 0)],
    'DD': [(PayRobotDD, 1, 1, 0)],
    'VY': [(RefundTaxRobotVY, 1, 1, 0),
            (RefundTaxRobotVYFull, 1, 1, 0)],
    '6E': [(RefundTaxRobot6E, 1, 1, 0)],
    'Z9': [(PayRobotZ9, 1, 1, 0)]
}


def run_app(app, threads, proxy):
    for _ in range(threads):
        if type(app) == Runnable:
            app.run()
        else:
            app(proxies_type=proxy).run()


def start_app(tag):
    app_cfgs = app_map.get(tag, None)
    if not app_cfgs:
        print('未配置app', tag)
    for app_cfg in app_cfgs:
        app, threads, process, proxy = app_cfg
        for _ in range(process):
            Process(target=run_app, args=(app, threads, proxy)).start()


if __name__ == '__main__':
    start_app(sys.argv[1])

