import os
os.chdir("../../")

import unittest
from auto_check.AUO.AUOCheckApi import AUOCheckWeb
from auto_check.AUO.AUOCheckService import AUOCheckService
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        app = AUOCheckWeb(proxies_type=0)
        app.agent_check("T8LUWJ")
        # app.manage_booking(last_name="JIN", first_name="RUN", pnr="A291FI")
        # app.check()
        # print(app.error_code)

    def test_check_service(self):
        app = AUOCheckService()
        # result = app.show_check_part_info(last_name="YU", first_name="WING YI", pnr="BY1P8N")
        # print(result)
        app.show_check_agent_info("Q9FG5D")



