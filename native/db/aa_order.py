from . import execute_select


def get_active_order():
    sql = f"select flight_number as flightNumber,depart_date as departDate from aa_order  where status = 0"
    return execute_select(sql)