# -*- coding: UTF-8 -*-
from datetime import datetime
from utils.log import check_QG_logger
from auto_check.AQG.AQGCheckApi import AQGCheckWeb
from lxml import etree
import traceback


class AQGCheckService(object):
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
        app = AQGCheckWeb(proxies_type=7)
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

                check_QG_logger.error("没有找到PNR")

            else:
                result = {"result": "ERROR", "code": app.error_code}
                check_QG_logger.error("请求失败，请重试")

        except Exception:

            check_QG_logger.error(f"{traceback.print_exc()}")

            result = {"result": "ERROR", "code": app.error_code}

        check_QG_logger.info(f"最后的结果为: {result}")
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
        app = AQGCheckWeb(proxies_type=7)
        try:
            app.check(last_name, pnr)
            if app.error_code == "1":
                result = cls.__data_extra(app.check_response)
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

                check_QG_logger.error("没有找到PNR")

            else:
                result = {"result": "ERROR", "code": app.error_code}
                check_QG_logger.error("请求失败，请重试")

        except Exception:

            check_QG_logger.error(f"{traceback.print_exc()}")

            result = {"result": "ERROR", "code": "-2"}

        check_QG_logger.info(f"最后的结果为: {result}")

        return result

    @classmethod
    def __data_extra(cls, check_response):

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
            trs = all_info.xpath('//*[@id="selectMainBody"]/div/div[3]/table/tr')

            for persons_info in trs:
                passenger = persons_info.xpath('td//text()')
                if len(passenger) < 2:
                    continue
                p = [i for i in passenger[0].split(' ') if len(i) > 0]
                passenger_name = p[-1] + "/" + " ".join(p[:-1])
                sex = 'F' if passenger[-1] == 'Female' else 'M'
                passenger_name_list.append(passenger_name.replace(" ", ""))
                # 去程乘客信息
                leave_passengers_list.append({
                    "passengerId": '',
                    "name": passenger_name.replace(" ", ""),
                    "sex": sex,
                    "birthday": '',
                    "nationality": "",
                    "cardIssuePlace": "",
                    "cardExpired": "",
                    "certificateInformation": ""
                })
            check_QG_logger.info(f"乘客信息列表: {leave_passengers_list}")

            # 提取出发地，出发时间等信息
            flight_number_ = all_info.xpath('//*[@id="selectMainBody"]/div/div[5]/h6//text()')
            t = all_info.xpath('//*[@id="selectMainBody"]/div/div[5]/p/text()')
            airline_info = all_info.xpath('//*[@id="itinerarySeatAssignmentsTable"]/tbody/tr[1]//text()')
            flight_number_ = [i.replace(" ", '').replace("\n", "").replace(" ", "").replace("\r", "") for i in flight_number_]
            t = [i.replace(" ", '').replace("\n", "").replace(" ", "").replace("\r", "") for i in t]
            airline_info = [i.replace("\n", "").replace(" ", '').replace(" ", "").replace("\r", "") for i in airline_info]
            airline_info = [i for i in airline_info if i != '']

            flight_number = flight_number_[-1].split("Flight")[-1]
            year_m = datetime.now().strftime('%Y') + flight_number_[-1].split("22")[0]
            flight_number_list.append(flight_number)

            origin_depart = airline_info[-2].split('-')
            origin_list.append(origin_depart[0].replace(" ", ""))
            destination_list.append(origin_depart[1].replace(" ", ""))

            at = year_m+t[0].split('at')[-1]
            dt = year_m+t[-1].split('at')[-1]
            depart_date_list.append(datetime.strptime(at, "%Y%d%b%H:%M%p").strftime("%Y-%m-%d %H:%M:%S"))
            arrive_date_list.append(datetime.strptime(dt, "%Y%d%b%H:%M%p").strftime("%Y-%m-%d %H:%M:%S"))

            check_QG_logger.info(f"航班信息-> "
                                 f"航班号列表：{flight_number_list}"
                                 f"出发地列表:{origin_list}"
                                 f"目的地列表：{destination_list}"
                                 f"出发时间列表：{depart_date_list}"
                                 f"到达时间列表：{arrive_date_list}")

            # 提取行李信息， 以及noshow状态（Deflate：没到起飞时间，Boarded：已经起飞）
            td = all_info.xpath('//*[@id="selectMainBody"]/div/div[6]/table/tr[2]/td[1]')
            if len(td)>0:
                for i,passer in enumerate(passenger_name_list):
                        print(i)
                        baggage_weight = td[i].text.split("kg")[0]
                        baggageMessageDOs = {
                            "passengerName": passer,
                            "depCity": origin_depart[0].replace(" ", ""),
                            "arrCity": origin_depart[1].replace(" ", ""),
                            "baggageWeight": baggage_weight
                        }
                        leave_bags_list.append(baggageMessageDOs)

            check_QG_logger.info(f"行李信息列表：{leave_bags_list}")
            check_QG_logger.info(f"liftStatus列表: {lift_status_list}")


            # 提取PNR状态信息
            status = all_info.xpath('//*[@id="itineraryBody"]/table/tr[2]/td[2]/span/text()')
            if status[0].startswith('Confirmed'):
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

            check_QG_logger.error(f"{traceback.format_exc()}")
