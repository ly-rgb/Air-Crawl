import os
from airline import spider_map
from utils.common import get_worker_info, get_master_info
import time
from threading import Thread
from utils.log import logger
import json
from multiprocessing import Process
from utils.security import md5

grabConfig = None
grabConfigStrMD5 = None
crawlHeadGuide = []

base_spiders = {}
base_spiders_process = {}


def spiders_registered():
    global base_spiders, grabConfig, crawlHeadGuide
    urlGrabberMap = grabConfig['urlGrabberMap']
    for x in urlGrabberMap.keys():
        if x not in spider_map.keys():
            logger.warning("spiders registered: " + x + " not in spider_map")
            continue
        try:
            worker_host = select_outside_agent_ip(x.split("_")[-1])
            # restart()
            if x in base_spiders_process:
                base_spiders_process[x].kill()
                base_spiders_process[x].close()
            base_spiders_process[x] = Process(target=start_spider, args=(x, urlGrabberMap, worker_host))
            base_spiders_process[x].start()
            logger.info(f"starting {x} 启动")
        except Exception:
            logger.info(f"starting {x} 启动异常")
            import traceback
            logger.error(traceback.format_exc())


def restart():
    os.system(os.path.abspath(os.path.join(os.getcwd(), 'phasell_start.sh')))


def start_spider(name, urlGrabberMap, worker_host):
    spider = spider_map[name](name, urlGrabberMap[name], worker_host=worker_host)
    spider.run()


def update_grabConfig():
    """检测分配的任务是否有更新"""
    global grabConfig, crawlHeadGuide, grabConfigStrMD5
    while True:
        try:
            grabConfigStr = get_master_info()['grabConfig']
            new_md5 = md5(grabConfigStr)
            logger.info(f"old config: {grabConfigStrMD5}, new config: {new_md5}")
            if grabConfigStrMD5 != new_md5:
                grabConfig = json.loads(get_master_info()['grabConfig'])
                logger.info("update grabConfig: " + json.dumps(grabConfig))
                crawlHeadGuide = get_worker_info()
                logger.info("crawlHeadGuide: " + json.dumps(crawlHeadGuide))
                if grabConfigStrMD5:
                    restart()
                else:
                    grabConfigStrMD5 = new_md5
                    spiders_registered()
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
        time.sleep(10)


def select_outside_agent_ip(airline):
    global crawlHeadGuide
    for x in crawlHeadGuide:
        airlines = json.dumps(x['airline'])
        if airline in airlines:
            return x['outsideAgentIp']
    raise Exception(airline + "不能找到任务服务器")


base_thread = Thread(target=update_grabConfig)


def init():
    base_thread.start()


def run():
    time.sleep(5)
    for x in base_spiders.values():
        x.run()
