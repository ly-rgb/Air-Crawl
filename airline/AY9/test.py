import os
os.chdir("../../")

import unittest

from airline.AY9.service import api_search
from utils.searchparser import parser_from_task
import os

# os.environ['http_proxy'] = 'http://127.0.0.1:3213'
# os.environ['https_proxy'] = 'http://127.0.0.1:3213'


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_api_search(self):
        task = 'AY9,YHZ,YHM,2022-09-18,,1,,,AFARE,0,,CRAWlLCC'
        code, req = api_search(parser_from_task(task), proxies_type=7)
        print(code, req)
        for x in req:
            print(x)
        self.assert_(req)


if __name__ == '__main__':
    unittest.main()

