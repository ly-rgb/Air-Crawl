from airline.ABZ.ABZWeb import ABZWeb
from utils.log import spider_BZ_logger
import traceback


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0

    try:
        app = ABZWeb(proxies_type=proxies_type)
        app.currency_choice()
        app.front_search(taskItem)
        app.search()
        result = app.convert_search()
        if not result and isinstance(result, list):
            code = -1
            spider_BZ_logger.info(f"当天没有航班, result: {result}")

    except:
        code = -1
        spider_BZ_logger.error(f"{traceback.format_exc()}")

    return code, result