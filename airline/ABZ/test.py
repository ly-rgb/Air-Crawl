import os
os.chdir("../../")

import unittest

from airline.ABZ.service import api_search
from utils.searchparser import parser_from_task
import os

# os.environ['http_proxy'] = 'http://127.0.0.1:3213'
# os.environ['https_proxy'] = 'http://127.0.0.1:3213'


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_api_search(self):

        task = 'ABZ,TLV,LCA,2022-09-10,,2,,,AFARE,0,,READTIMELCC'
        code, req = api_search(parser_from_task(task), proxies_type=7)
        print(code, req)
        # for x in req:
        #     print(x)
        # self.assert_(req)


if __name__ == '__main__':
    unittest.main()