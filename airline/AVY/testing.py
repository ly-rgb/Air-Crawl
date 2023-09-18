import os
import unittest

os.chdir("../../")


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    @staticmethod
    def test_ws(pnr, airport, date):
        from airline.AVY.AVYWsApp import AVYWsApp
        from utils.log import booking_VY_logger
        # WebSocketApp

        app = AVYWsApp(booking_VY_logger)
        app.start(timeout=10, ping_interval=60, ping_timeout=5)
        app.get_started()
        app.click_code()
        app.send_pnr(pnr)
        app.send_airport(airport)
        app.send_date(date)
        app.send_email()
        describe = app.send_phone()
        print(describe)
        app.close()
        # app.close()
        # app.get_started()

    @staticmethod
    def test_describe(pnr='INKING', airport='BIO', date='2022-10-11'):
        from airline.AVY.AVYWsApp import AVYWsApp
        from utils.log import booking_VY_logger
        # WebSocketApp

        app = AVYWsApp(booking_VY_logger)
        app.start(timeout=10, ping_interval=60, ping_timeout=5)
        app.get_started()
        app.click_code()
        app.send_pnr(pnr)
        app.send_airport(airport)
        value_str = app.send_date(date)
        if value_str:  # 回复的消息中存在乘客号码的话，需要走另一条线路
            app.send_passenger(value_str)
            app.send_email()
            describe = app.send_phone()
            print(describe)
        app.send_email()
        describe = app.send_phone()
        print(describe)


if __name__ == '__main__':
    unittest.main()

