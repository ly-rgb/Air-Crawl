import sys


class DingTalk:
    import requests
    from utils.log import ding_talk_log as log
    WebhookUrl = "https://oapi.dingtalk.com/robot/send"

    def __init__(self, access_token, sign=None, keyword=None):
        self.access_token = access_token
        self.sign = sign
        self.keyword = keyword

    def send_mag(self, msg, at_all=False):
        # if sys.platform == 'darwin':
        #     print(msg)
        #     return
        if self.keyword:
            msg = self.keyword + "\n" + msg

        body = {"msgtype": "text", "text": {"content": msg}, 'at': {"isAtAll": at_all}}
        params = {'access_token': self.access_token, 'sign': self.sign}
        headers = {'Content-Type': 'application/json'}
        rep = self.requests.post(self.WebhookUrl, json=body, headers=headers, params=params)
        if rep.json()['errcode'] != 0:
            self.log.error(rep.text)


ding_talk = DingTalk("3a644ef3e73d1bbbf96f70afd0c69fbed228a7672b834312c3e549d5a8de4cb1", keyword='通知')
ah_ding_talk = DingTalk("16a6014bf91be65538b112ce7b7b23d8cda2b7c14a6327ee5a545d2e96901571", keyword='通知')
f9_order_check_talk = DingTalk('9f072ba6c2cb6742675b15ec5cdf8368f4cfcd32cf7c80b23cc05631724b9371', keyword='通知')
a5J_go_talk = DingTalk('2f82f767fcfa988ec8b7a15848e896681ba5d045f29e6271359fb47b46995a6d', keyword='通知')
u2_talk = DingTalk('04a858b79a0c80835b79a4e9601c50b89de03760cf5531e9a144288e4d23628a', keyword='报警')
if __name__ == '__main__':
    DingTalk("9f072ba6c2cb6742675b15ec5cdf8368f4cfcd32cf7c80b23cc05631724b9371").send_mag("通知测试")
