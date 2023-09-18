import os

os.chdir("../../")

import unittest

from airline.AB7.service import api_search
from utils.searchparser import parser_from_task


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_api_search(self):
        import urllib3
        urllib3.disable_warnings()
        task = 'AB7,TSA,HUN,2023-01-24,,1,,,AFARE,0,,READTIMELCC'
        code, req = api_search(parser_from_task(task), proxies_type=0)
        print(code, req)
        for x in req:
            print(x)
        self.assert_(req)


if __name__ == '__main__':
    unittest.main()
