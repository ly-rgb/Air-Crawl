import traceback

from airline.A5J.A5JApp import A5JApp
from airline.base import add_on_select_flight
from robot import HoldTask
from robot.model import AddOnResult
from utils.log import add_on_5j_logger


def add_on(holdTask: HoldTask, proxies_type=7):
    code = 0
    result = []
    try:
        app = A5JApp(proxies_type=proxies_type)
        app.init()
        app.bookingAvailability(holdTask, ["MAFI"])
        flight = app.convert_search(is_booking=True)
        add_on_select_flight(holdTask, flight)
        app.selectFlight(holdTask, check_class=False)
        app.trip(holdTask)
        app.guestdetails(holdTask)
        bag_list = app.get_bag_list()
        result = list(map(lambda x: AddOnResult.from_baggage(holdTask, x, '5J').to_dict(), bag_list))
    except Exception:
        add_on_5j_logger.error(traceback.format_exc())
        code = 3
    return code, result
