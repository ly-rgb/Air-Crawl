from airline.AN0.AN0Web import AN0Web
from utils.log import spider_N0_logger
import traceback


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0

    try:
        app = AN0Web(proxies_type=proxies_type)
        app.get_token()
        app.search(taskItem)
        result = app.convert_search()
        if not result and isinstance(result, list):
            code = -1
            spider_N0_logger.info(f"当天没有航班")

    except:
        code = -1
        spider_N0_logger.error(f"{traceback.format_exc()}")

    return code, result
