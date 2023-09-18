from utils.log import spider_FO_logger
from airline.AFO.AFOWeb import AFOWeb
import traceback


def api_search(taskItem, proxies_type=7):
    result = None
    code = 0

    try:
        app = AFOWeb(proxies_type=proxies_type)
        app.search(taskItem)

        result = app.convert_search()
        if not result and isinstance(result, list):
            code = -1
            spider_FO_logger.info("当天无航班")

    except Exception:
        code = -1
        spider_FO_logger.error(f"{traceback.format_exc()}")

    return code, result


