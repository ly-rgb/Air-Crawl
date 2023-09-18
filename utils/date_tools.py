from datetime import datetime, timedelta
import time
from typing import *


def make_date_list(day, st: datetime or str = None, offset: str or int = None, ret_fmt=None):
    ret = []
    if st:
        if type(st) == str:
            now = datetime.strptime(st, "%Y-%m-%d")
        else:
            now = st
    else:
        now = datetime.now()
    if offset:
        now += timedelta(days=int(offset))

    if ret_fmt:
        ret.append(now.strftime(ret_fmt))
    else:
        ret.append(now)

    for x in range(day):
        now += timedelta(days=1)
        if ret_fmt:
            ret.append(now.strftime(ret_fmt))
        else:
            ret.append(now)
    return ret


def make_calendar(st: datetime or str or int, et: datetime or str or int, day=1, in_fmt="%Y-%m-%d", ret_fmt="%Y-%m-%d"):
    ret = []
    start = st
    if type(start) == str:
        start = datetime.strptime(start, in_fmt)
    elif type(start) == int:
        start = datetime.now() + timedelta(days=start)
    if type(et) == str:
        et = datetime.strptime(et, in_fmt)
    elif type(et) == int:
        et = start + timedelta(days=et)
    day = timedelta(days=day)
    while True:
        ret.append(start.strftime(ret_fmt))
        start += day
        if start > et:
            return ret


def get_age_by_birthday(birthday, fmt="%Y-%m-%d", now: Union[str, datetime, None] = None, now_fmt="%Y-%m-%d"):
    now = now or datetime.now()
    if not isinstance(birthday, datetime):
        birthday = datetime.strptime(birthday, fmt)
    if not isinstance(now, datetime):
        now = datetime.strptime(now, now_fmt)
    birthday: datetime
    age = now.year - birthday.year
    if birthday.month > now.month:
        age -= 1
    elif birthday.month == now.month:
        if birthday.day > now.day:
            age -= 1
    return age


def time_stamp_to_date(time_stamp, fmt="%Y-%m-%d %H:%M:%S"):
    timeArray = time.localtime(int(time_stamp))
    return time.strftime(fmt, timeArray)


def data_reformat(data, old_fmt, new_fmt):
    return datetime.strptime(str(data), old_fmt).strftime(new_fmt)


if __name__ == '__main__':
    # for x in make_date_list(0, st="2021-06-20", offset=1):
    #     print(x)
    print(get_age_by_birthday("1996-09-25"))
