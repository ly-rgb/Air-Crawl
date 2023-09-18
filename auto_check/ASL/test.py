# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/12/15 15:25
"""

import os
import time

os.chdir("../../")

import unittest
import json
from auto_check.ASL.ASLCheckService import ASLCheckService
from auto_check.ASL.ASLCheckApi import ASLCheckWeb

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_service(self):
        with open("auto_check/ASL/111.html", "r") as f:
            flight_text = f.read()
        app = ASLCheckWeb(otaid="916716969246784801")
        app.pay_order_name_birthday()
        app.extract_birthday_form(text=flight_text)


