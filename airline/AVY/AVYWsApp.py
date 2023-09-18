import re
import uuid
from utils.log import refund_VY_logger
from airline.base import AirAgentWebsocket


class AVYWsApp(AirAgentWebsocket):

    def __init__(self, logger=refund_VY_logger, header=None, keep_running=True,
                 get_mask_key=None, cookie=None, subprotocols=None,
                 socket=None):
        super().__init__('wss://endpoint-v4-chatbot.vueling.com/socket.io/?'
                         'EIO=3&transport=websocket', logger, header,
                         keep_running, get_mask_key, cookie, subprotocols,
                         socket)
        self.session_id = uuid.uuid1()

    def get_started(self):
        """
        会话开始
        """
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {
                    "culture": "en-GB",
                    "helpCenterFlow": "RefundAirportTaxes",
                    "type": None,
                    "subType": None,
                    "clientTarget": None
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "GET_STARTED",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'From' in str(msg):
            self.logger.info('退票会话开始')

    def click_code(self):
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {
                    "culture": "en-GB",
                    "helpCenterFlow": "RefundAirportTaxes",
                    "type": None,
                    "subType": None,
                    "clientTarget": None
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "firstFlight",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'booking' in str(msg):
            self.logger.info('点击Code,airport and date正常')

    def send_pnr(self, pnr):
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {
                    "culture": "en-GB",
                    "helpCenterFlow": "RefundAirportTaxes",
                    "type": None,
                    "subType": None,
                    "clientTarget": None
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": pnr,
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'email' in str(msg):
            self.logger.info('发送pnr正常')

    def send_airport(self, airport):
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {"adaptivecards": {"origin": airport}},
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'flight' in str(msg):
            self.logger.info('发送机场正常')

    def send_date(self, date):
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {
                    "adaptivecards": {"date": date}
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'value' in str(msg):
            value_list = re.findall('.*?"value":"(.*?)".*?', str(msg), re.S)
            value_str = ','.join(value_list)
            self.logger.info(f'多位乘客需要退票，value是{value_str}')
            return value_str
        self.logger.info('发送起飞日期正常')

    def send_email(self):
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {
                    "culture": "en-GB",
                    "helpCenterFlow": "RefundAirportTaxes",
                    "type": None,
                    "subType": None,
                    "clientTarget": None
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "nevergiveup17apr05@qq.com",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'phone' in str(msg):
            self.logger.info('发送邮箱正常')

    def send_passenger(self, value_str):
        data = [
            "processInput",
            {
                "URLToken":
                    "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4c4a19b62"
                    "feabcd",
                "channel": "webchat-client",
                "data": {
                    "adaptivecards": {"selectedPassengers": value_str}
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "nevergiveup17apr05@qq.com",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'Remember' in str(msg):
            self.logger.info('发送退票乘客正常')

    def confirm_email(self):
        data = [
            "processInput",
            {
                "URLToken": "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4"
                            "c4a19b62feabcd",
                "channel": "webchat-client",
                "data": {
                    "culture": "en-GB",
                    "helpCenterFlow": "RefundAirportTaxes",
                    "type": None,
                    "subType": None,
                    "clientTarget": None
                },
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "nevergiveup17apr05@qq.com",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        if 'taxes' in str(msg):
            self.logger.info('确认邮箱正常')

    def send_phone(self):
        data = [
            "processInput",
            {
                "URLToken": "cba92de4473675f50885b02f529f57aa0bb5bd878e9e0d65a4"
                            "c4a19b62feabcd",
                "channel": "webchat-client",
                "data": {"adaptivecards": {"phonePrefix": "+86",
                                           "phone": "18611715578"}},
                "passthroughIP": None,
                "reloadFlow": False,
                "resetContext": False,
                "resetFlow": False,
                "resetState": False,
                "sessionId": f"session-{self.session_id}",
                "source": "device",
                "text": "",
                "userId": "27bca16b-15f4-4827-96b4-ec27e559aee7"
            }
        ]
        data = f'42{self.json.dumps(data)}'
        self.send(data)
        msg = self.get_msg(wait=10, timeout=60)
        self.logger.info(msg)
        if 'number' in str(msg):
            self.logger.info('发送手机号为正常')
            describe = re.findall('.*?(\d{8}).*?', str(msg), re.S)[0]
            return describe
