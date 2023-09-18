import os

os.chdir("../../")

import unittest
from airline.AHD.service import api_search
from utils.searchparser import parser_from_task



# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here
#
#     def test_api_search(self):
#         task = 'AHD,MMB,HND,2022-09-27,,1,,,AFARE,0,,CRAWlLCC'
#         code, req = api_search(parser_from_task(task), proxies_type=7)
#         print(code, req)
#         for x in req:
#             print(x)
#         self.assert_(req)


def test_api_search():
    task = 'AHD,HND,MMB,2022-09-29,,1,,,AFARE,0,,CRAWlLCC'
    code, req = api_search(parser_from_task(task), proxies_type=7)
    print(code, req)
    for x in req:
        print(x)


if __name__ == '__main__':
    # unittest.main()
    test_api_search()


