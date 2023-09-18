import os
import unittest

os.chdir('../../')

class MyTestCase(unittest.TestCase):

    def test_add_on(self):
        from airline.AFZ.service import add_on
        from robot import HoldTask
        import urllib3
        urllib3.disable_warnings()
        code, result = add_on(HoldTask.from_add_on_task('FFZ,AHB,DXB,baggage,2023-01-28,0'), proxies_type=0)
        for x in result:
            print(x)
        self.assert_(True)
