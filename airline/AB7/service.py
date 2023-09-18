from airline.AB7.AB7Web import AB7Web
from utils.log import spider_B7_logger


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AB7Web(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_B7_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
