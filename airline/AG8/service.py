import traceback

from airline.AG8 import AG8App
from utils.log import add_on_G8_logger
from robot.model import AddOnResult, HoldTask
from airline.base import add_on_select_flight


def add_on(holdTask: HoldTask, proxies_type=7):
    code = 0
    result = []
    try:
        app = AG8App(proxies_type=proxies_type)
        session_id = app.bookingAvailability(holdTask)
        flight = app.convert_search()
        add_on_select_flight(holdTask, flight)
        app.selectFlight(holdTask)
        app.get_select(session_id)
        BookingInformation = app.get_booking(session_id)
        bag_data, bag_key = app.get_bag_key(session_id, BookingInformation)
        price_list = app.get_bag_price(session_id, bag_key)
        bag_list = app.get_bag_list(bag_data, price_list)
        result = list(map(lambda x: AddOnResult.from_baggage(holdTask, x, 'G8')
                          .to_dict(), bag_list))
    except Exception:
        add_on_G8_logger.error(traceback.format_exc())
        code = 3
    return code, result
