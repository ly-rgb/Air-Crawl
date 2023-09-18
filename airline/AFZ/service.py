import traceback

from airline.AFZ import AFZApp
from utils.log import add_on_FZ_logger
from robot.model import AddOnResult, HoldTask
from airline.base import add_on_select_flight


def add_on(holdTask: HoldTask, proxies_type=7):
    code = 0
    result = []
    try:
        app = AFZApp(proxies_type=proxies_type)
        #cookies = app.get_home()
        securitytoken = app.bookingAvailability(holdTask)
        flight = app.convert_search()
        add_on_FZ_logger.info(f'flight为{flight}')
        add_on_select_flight(holdTask, flight)
        app.selectFlight(holdTask)
        app.get_addflight(securitytoken)
        bag_list = app.get_bag_list(securitytoken)
        result = list(map(lambda x: AddOnResult.from_baggage(holdTask, x, 'FZ')
                           .to_dict(), bag_list))
    except Exception:
        add_on_FZ_logger.error(traceback.format_exc())
        code = 3
    return code, result