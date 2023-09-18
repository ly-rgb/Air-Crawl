# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/12/9 14:59
"""

import os
import time

os.chdir("../../")

import unittest
from auto_check.AU2.AU2CheckService import AU2PnrService
from auto_check.AU2.AU2CheckApi import AU2PnrWeb


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_pnr(self):
        AU2PnrService.check_pnr_status()

    def test_api(self):
        app = AU2PnrWeb()
        app.check(last_name="PENG", pnr="K4LPQDS")

    def test_ding_talk(self):
        from utils.dingtalk import f9_order_check_talk
        a = {"123": 123}
        f9_order_check_talk.send_mag(f"{a}")

    def test_redis(self):
        from utils.redis import u2_order_check_cache

        r = u2_order_check_cache
        s = r.get("u2_check_2022-12-13")
        print(s)

