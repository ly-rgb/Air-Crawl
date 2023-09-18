# -*- coding: UTF-8 -*-
"""
@Project: phasell_on_python_2
@Author: WJack
@File: test.py
@effect: "DD测试"
@Date: 2022/10/17 11:51
"""

import os
os.chdir("../../")

import unittest
from auto_check.ADD.ADDCheckApi import ADDCheckWeb
from auto_check.ADD.ADDCheckService import ADDCheckService
from utils.AgentDb import select_agent_db
from utils.log import check_DD_logger


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        app = ADDCheckWeb(proxies_type=7)
        app.agent_login()
        # app.agent_login(username="Daran2", password="1qaz@WSX")
        app.check("PUNWITTAYAPHOKIN", "O2PRZQ")
        # app.login1()
        # app.manage_booking(last_name="JIN", first_name="RUN", pnr="A291FI")
        # app.check()
        # print(app.error_code)

    def test_agent_db(self):
        select_agent_db("J7UBG5", check_DD_logger)

    def test_check_service(self):
        os.environ["http_proxy"] = "127.0.0.1:3213"
        os.environ["https_proxy"] = "127.0.0.1:3213"
        app = ADDCheckService()
        result = app.show_check_agent_info("PETCHSAWAT", "K01RWQ")
        print(result)