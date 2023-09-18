import json
import os
import unittest
from datetime import datetime

os.chdir('../../')


class MyTestCase(unittest.TestCase):

    def test_add_on(self):
        from airline.A5J.service import add_on
        from robot import HoldTask
        code, result = add_on(HoldTask.from_add_on_task('F5J,CEB,DVO,MNL,baggage,2023-01-16,0'), proxies_type=8889)
        for x in result:
            print(x)
        self.assert_(True)
