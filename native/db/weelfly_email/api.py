from . import execute_select, execute_select_first
import datetime


def find_email_by_recv_address_and_subject(recvAddress, subject):
    sql = f"SELECT body from flight_emails_{datetime.datetime.now().strftime('%Y_%m_%d')} where recvAddress='{recvAddress}' and subject='{subject}'"
    return execute_select_first(sql)

