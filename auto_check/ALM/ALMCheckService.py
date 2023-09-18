# -*- coding: UTF-8 -*-
from datetime import datetime
from utils.log import check_LM_logger
from auto_check.ALM.ALMCheckApi import ALMCheckWeb
from lxml import etree
import traceback


class ALMCheckService(object):
    """

    """

    @classmethod
    def show_check_all_info(cls, last_name: str, pnr: str):
        """
        返回所有数据
        （该数据未解析）
        :param last_name:
        :param pnr:
        :return:
        """
        result = None
        app = ALMCheckWeb(proxies_type=7)
        try:
            app.check(last_name, pnr)
            if app.error_code == "1":
                result = app.check_response
            elif app.error_code == "0":
                result = {
                    "code": app.error_code,
                    "isFind": "false",
                    "isBusiness": "false",
                    "Leave": {
                        "taskType": "",
                        "origin": "",
                        "destination": "",
                        "targetPassengers": "",
                        "departDate": "",
                        "arriveDate": "",
                        "flightNumber": "",
                        "baggageMessageDOs": "",
                        "freeBaggageWeight": "0"
                    },
                    "payStatus": "false",
                    "liftStatus": ""
                }

                check_LM_logger.error("没有找到PNR")

            else:
                result = {"result": "ERROR", "code": app.error_code}
                check_LM_logger.error("请求失败，请重试")

        except Exception:

            check_LM_logger.error(f"{traceback.print_exc()}")

            result = {"result": "ERROR", "code": app.error_code}

        check_LM_logger.info(f"最后的结果为: {result}")
        # return result

    @classmethod
    def show_check_part_info(cls, last_name: str, pnr: str):

        """
        返回客户端（java）需要的数据
        :param last_name:
        :param pnr:
        :return:
        """

        result = None
        app = ALMCheckWeb(proxies_type=7)
        try:
            app.check(last_name, pnr)
            if app.error_code == "1":
                result = cls.__data_extra(app.check_response, app.sex)
            elif app.error_code == "0":
                result = {
                    "code": app.error_code,
                    "isFind": "false",
                    "isBusiness": "false",
                    "Leave": {
                        "taskType": "",
                        "origin": "",
                        "destination": "",
                        "targetPassengers": "",
                        "departDate": "",
                        "arriveDate": "",
                        "flightNumber": "",
                        "baggageMessageDOs": "",
                        "freeBaggageWeight": "0"
                    },
                    "payStatus": "false",
                    "liftStatus": ""
                }

                check_LM_logger.error("没有找到PNR")

            else:
                result = {"result": "ERROR", "code": app.error_code}
                check_LM_logger.error("请求失败，请重试")

        except Exception:

            check_LM_logger.error(f"{traceback.print_exc()}")

            result = {"result": "ERROR", "code": "-2"}

        check_LM_logger.info(f"最后的结果为: {result}")

        return result

    @classmethod
    def __data_extra(cls, check_response,sex):

        """
        数据解析
        :param all_info: 返回的所有数据的dict类型
        :return: 解析后的数据
        """

        try:
            # 定义出发地等列表，当航班为中转的时候方便拼接
            origin_list = []
            destination_list = []
            depart_date_list = []
            arrive_date_list = []
            flight_number_list = []

            # passenger_name_list的作用是帮助添加行李中乘客的名字
            passenger_name_list = []

            # lift_status noshow
            lift_status_list = []

            leave_passengers_list = []
            leave_bags_list = []
            all_info = etree.HTML(check_response)


            # 提取乘客信息
            divs = all_info.xpath('//*[@id="divPanelBody"]/div[2]/div[1]/div[1]/div[1]/div')
            persons_info = divs[1].xpath('//ul/li//span/text()')
            for passenger in persons_info:
                passenger_name = passenger.split(' ')[1] + "/" + passenger.split(' ')[0]

                # 去程乘客信息
                leave_passengers_list.append({
                    "passengerId": '',
                    "name": passenger_name.replace(" ",""),
                    "sex": sex,
                    "birthday": '',
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_LM_logger.info(f"乘客信息列表: {leave_passengers_list}")

            # 提取出发地，出发时间等信息
            airline_info = all_info.xpath('//*[@id="divPanelBody"]/div[2]/div[1]/div/div/div[1]/a//text()')
            Depart_index = airline_info.index([i for i in airline_info if 'depart' in i.lower()][0])
            Arrive_index = airline_info.index([i for i in airline_info if 'arrive' in i.lower()][0])
            flight_number_list.append(airline_info[2].replace(" ", ""))
            origin_list.append(airline_info[0].replace(" ", ""))
            destination_list.append(airline_info[1].replace(" ", ""))
            depart_time = str(datetime.now().year) + airline_info[Depart_index - 1] + airline_info[Depart_index + 1]
            arrive_time = str(datetime.now().year) + airline_info[Depart_index - 1] + airline_info[Arrive_index + 1]
            depart_date_list.append(datetime.strptime(depart_time, "%Y %d %b %H:%M").strftime("%Y-%m-%d %H:%M:%S"))
            arrive_date_list.append(datetime.strptime(arrive_time, "%Y %d %b %H:%M").strftime("%Y-%m-%d %H:%M:%S"))

            check_LM_logger.info(f"航班信息-> "
                                 f"航班号列表：{flight_number_list}"
                                 f"出发地列表:{origin_list}"
                                 f"目的地列表：{destination_list}"
                                 f"出发时间列表：{depart_date_list}"
                                 f"到达时间列表：{arrive_date_list}")

            # 提取行李信息， 以及noshow状态（Deflate：没到起飞时间，Boarded：已经起飞）



            # 提取PNR状态信息
            status = all_info.xpath('//*[@id="Content_divBookingConfirmation"]/div/div[1]/div/div[3]/h4/text()')
            if status[0].startswith('Confirmation'):
                payStatus = 'true'
            else:
                payStatus = ''

            result = {
                "code": "1",
                "isFind": "true",
                "isBusiness": "false",
                "Leave": {
                    "taskType": "SHUA_PIAO",
                    "origin": "|".join(origin_list),
                    "destination": "|".join(destination_list),
                    "targetPassengers": leave_passengers_list,
                    "departDate": "|".join(depart_date_list),
                    "arriveDate": "|".join(arrive_date_list),
                    "flightNumber": "|".join(flight_number_list),
                    "baggageMessageDOs": leave_bags_list,
                    "freeBaggageWeight": "0"
                },
                "payStatus": payStatus,
                "liftStatus": lift_status_list

            }
            return result
        except Exception:

            check_LM_logger.error(f"{traceback.format_exc()}")
