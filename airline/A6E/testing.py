import os
import unittest

from airline.A6E.A6EWeb import A6EWeb

os.chdir("../../")


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    @staticmethod
    def test_ws(pnr, email):
        from utils.log import booking_6E_logger

        app = A6EWeb()
        session_id = app.get_session_id
        app.get_amount(session_id)

if __name__ == '__main__':
    unittest.main()
