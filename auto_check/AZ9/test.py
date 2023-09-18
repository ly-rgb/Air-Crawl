# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "test"
@Date: 2022/12/30 12:01
"""

import os
import time

os.chdir("../../")

import unittest
from auto_check.AZ9.AZ9CheckApi import AZ9CheckWeb
from auto_check.AZ9.AZ9CheckService import AZ9CheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
       app = AZ9CheckWeb()
       app.login(pnr="UXQY86")
       app.login2()
       app.check(last_name="WANG", pnr="UXQY85")
       print(app.check_response.text)

    def test_check_service(self):
        app = AZ9CheckService()
        app.show_check_part_info(last_name="WANG", pnr="UXQY85")

