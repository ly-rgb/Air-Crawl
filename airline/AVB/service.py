import traceback

from airline.AVB import AVBApp
from utils.log import add_on_VB_logger
from robot.model import AddOnResult, HoldTask
from airline.base import add_on_select_flight


def add_on(holdTask: HoldTask, proxies_type=7):
    code = 0
    result = []
    try:
        app = AVBApp(proxies_type=proxies_type)
        app.bookingAvailability(holdTask)
        flight = app.convert_search()
        add_on_VB_logger.info(f'flight为{flight}')
        add_on_select_flight(holdTask, flight)
        app.selectFlight(holdTask)
        basket_id = app.get_basket_id()
        app.get_journeys(basket_id)
        bag_list = app.get_bag_list(basket_id)
        if not bag_list:
            return
        result = list(map(lambda x: AddOnResult.from_baggage(holdTask, x, 'VB')
                          .to_dict(), bag_list))
    except Exception:
        add_on_VB_logger.error(traceback.format_exc())
        code = 3
    return code, result