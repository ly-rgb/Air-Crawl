# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/11/8 15:02
"""

import os
os.chdir("../../")

import unittest
from auto_check.AOD.AODCheckApi import AODCheckWeb
from auto_check.AOD.AODCheckService import AODCheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):

        app = AODCheckWeb(proxies_type=0)
        app.api_check(pnr="TTDUWS")

    def test_check_service(self):
        result = AODCheckService.show_check_part_info(pnr="DRSGJX")