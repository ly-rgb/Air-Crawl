from airline.ATL.ATLWeb import ATLWeb
from utils.log import spider_TL_logger
import traceback


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0

    try:
        app = ATLWeb(proxies_type=proxies_type)
        app.front_search(taskItem)
        app.search()
        result = app.convert_search()

        if not result and isinstance(result, list):
            code = -1
            spider_TL_logger.info(f"当天没有航班")

    except Exception:
        spider_TL_logger.error(f"{traceback.format_exc()}")
    finally:
        if result is None:
            code = -1

    return code, result
