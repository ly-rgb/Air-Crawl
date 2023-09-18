from . import execute_select


def get_active_route_by_carrier(carrier):
    sql = f"SELECT dep_city, arr_city from crawl_job_test where  carrier = '{carrier}' and status = '1'"
    return execute_select(sql)



