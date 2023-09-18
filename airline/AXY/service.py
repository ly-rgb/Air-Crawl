import traceback

from airline.AXY import AXYApp
from utils.log import add_on_XY_logger
from robot.model import AddOnResult, HoldTask
from airline.base import add_on_select_flight


def add_on(holdTask: HoldTask, proxies_type=7):
    code = 0
    result = []
    try:
        app = AXYApp(proxies_type=proxies_type)
        token = app.get_session()
        app.bookingAvailability(holdTask, token)
        flight = app.convert_search()
        add_on_XY_logger.info(f'flight为{flight}')
        add_on_select_flight(holdTask, flight)
        app.selectFlight(holdTask)
        app.get_flight(token)
        app.get_passengers(token)
        bag_list = app.get_bag_list(token)
        result = list(map(lambda x: AddOnResult.from_baggage(holdTask, x, 'XY')
                          .to_dict(), bag_list))
    except Exception:
        add_on_XY_logger.error(traceback.format_exc())
        code = 3
    return code, result
