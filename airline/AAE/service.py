from airline.AAE.AAEWeb import AAEWeb
from utils.log import spider_AE_logger


def api_search(taskItem, proxies_type=8):
    result = None
    code = 0
    try:
        app = AAEWeb(proxies_type=proxies_type)
        app.search(taskItem)
        result = app.convert_search()
        if not result:
            code = 2
    except Exception:
        import traceback
        spider_AE_logger.error(f"{taskItem} {traceback.format_exc()}")
        code = 3
    return code, result
