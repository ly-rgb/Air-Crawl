import os
os.chdir("../../")

import unittest
from auto_check.A6E.A6ECheckApi import A6ECheckWeb
from auto_check.A6E.A6ECheckService import A6ECheckService
from utils.searchparser import parser_from_task


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_check_api(self):
        app = A6ECheckWeb(proxies_type=7, retry_count=3, timeout=60)
        app.index_AEM()
        app.retrieve_AEM("ELVIN CHACKO KOSEPH", "CSUK9H")
        app.view_AEM()

    def test_check_service(self):
        A6ECheckService.show_check_part_info(last_name="MENDIRATTA", pnr="YJH8HL")


if __name__ == '__main__':
    unittest.main()