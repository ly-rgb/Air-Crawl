import requests
from config import config
from utils.log import logger


class GetMasterInfoException(Exception):
    pass


class GetWorkerInfoException(Exception):
    pass


class GetWorkerItemException(Exception):
    pass


def get_master_info():
    """
    flight.cfg
    agentMasterServiceEndpoint=http://47.104.108.85:8881/api/
    agent=47.91.19.86
    :return:
    {
      "urlGrabberMap": {
        "AFARE_TS": {
          "grabber": "LCC",
          "threadNum": 10,
          "grabSleep": 0
        },.....
          "roundTime": 90000,
          "redialing": false,
          "isProxy": false,
          "maxThreadNum": 90000,
          "currentNum": 95,
          "pushTaskPort": 10241,
          "country": "JP",
          "pushTaskIp": ""
        }
    """
    url = "{}GetConfig".format(config.agent_master_service_endpoint)
    body = {"agentGroup": "general",
            "outIp": config.agent,
            "version": "1.0",
            "agent": config.agent}
    try:
        rep = requests.post(url, json=body)
        rep_json = rep.json()
        if rep_json.get("errorCode", 999) != 0:
            raise GetMasterInfoException(rep.text)
        return rep_json
    except Exception as e:
        logger.error("master请求失败")
        raise e


def get_worker_info():
    url = "{}crawlHeadGuide".format(config.agent_master_service_endpoint)
    try:
        rep = requests.get(url)
        return rep.json()
    except Exception as e:
        logger.error("worker请求失败")
        raise e


def get_worker_item(outsideAgentIp, url_, version, agent):
    url = "http://{}/api/GetTask".format(outsideAgentIp)
    body = {"url": url_,
            "version": version,
            "agent": agent}
    try:
        rep = requests.post(url, json=body)
        return rep.json()
    except Exception as e:
        logger.error("worker请求失败")
        raise e


def push_date(outsideAgentIp, date):
    url = "http://{}/api/GetTask".format(outsideAgentIp)
    try:
        rep = requests.post(url, json=date)
        return rep.json()
    except Exception as e:
        logger.error("返回数据失败")
        raise e