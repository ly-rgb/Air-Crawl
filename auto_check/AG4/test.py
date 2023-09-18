# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "请填写用途"
@Date: 2022/12/10 16:31
"""

import os
os.chdir("../../")

import unittest
from auto_check.AG4.AG4CheckService import AG4CheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"



    def test_check_service(self):
        # os.environ["http_proxy"] = "127.0.0.1:3213"
        # os.environ["https_proxy"] = "127.0.0.1:3213"

        result = AG4CheckService.show_check_part_info(last_name="CHEN", pnr="CFFYR2", first_name="NINGYAN")

        print(result)